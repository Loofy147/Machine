#!/usr/bin/env python3
"""Cross-check the Rust compatibility cache on an independent SGD corpus sample.

SGD is structurally different from MultiWOZ: dialogues use per-service frames,
schema-defined required slots, and requested slots. Facts and needs are
service-qualified so identically named fields from unrelated APIs do not collide.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import tempfile
import time
from pathlib import Path
from statistics import mean
from typing import Any
from urllib.request import Request as UrlRequest, urlopen

from context_contract_distribution import (
    ContractContext,
    build_compatibility_graph,
    consistent,
    plan_distribution,
)
from rust_compute_cache import RustCompatibilityCacheClient, graph_signature


SOURCE_REPOSITORY = "google-research-datasets/dstc8-schema-guided-dialogue"
SOURCE_COMMIT = "e852981ae34990f4358979625854259302feaa78"
SCHEMA_PATH = "test/schema.json"
SCHEMA_GIT_BLOB_SHA = "6cb0fc131da22b43bb4672ec89755f19e7d278ff"
SHARDS = (
    ("test/dialogues_001.json", "c5dd2b6494e9a1399e73103b8ebb232aec831d07"),
    ("test/dialogues_012.json", "0edb817c174fb7f704ac5163c91d2134574c8549"),
    ("test/dialogues_034.json", "5d73c7f6c43a05e3f7d64f8294f47b62ed080ed5"),
)
SCHEMA = "context-contract-sgd-independent-cache-benchmark.v0.1"


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _download_verified(
    relative_path: str,
    expected_sha: str,
    cache_dir: Path,
) -> bytes:
    target = cache_dir / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file():
        cached = target.read_bytes()
        if git_blob_sha1(cached) == expected_sha:
            return cached

    url = (
        f"https://raw.githubusercontent.com/{SOURCE_REPOSITORY}/"
        f"{SOURCE_COMMIT}/{relative_path}"
    )
    request = UrlRequest(
        url,
        headers={"User-Agent": "Machine-SGD-Cache-Verification/0.1"},
    )
    with urlopen(request, timeout=45) as response:
        data = response.read()

    actual_sha = git_blob_sha1(data)
    if actual_sha != expected_sha:
        raise ValueError(
            f"Git blob SHA-1 mismatch for {relative_path}: "
            f"expected {expected_sha}, got {actual_sha}"
        )
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(target)
    return data


def load_sgd_sample(cache_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    schema_bytes = _download_verified(
        SCHEMA_PATH, SCHEMA_GIT_BLOB_SHA, cache_dir
    )
    schemas = json.loads(schema_bytes.decode("utf-8"))
    dialogues: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    for relative_path, expected_sha in SHARDS:
        payload = _download_verified(relative_path, expected_sha, cache_dir)
        rows = json.loads(payload.decode("utf-8"))
        if not isinstance(rows, list):
            raise ValueError(f"{relative_path} did not contain a dialogue list")
        dialogues.extend(rows)
        provenance.append({
            "path": relative_path,
            "git_blob_sha1": expected_sha,
            "bytes": len(payload),
            "dialogues": len(rows),
        })
    return {item["service_name"]: item for item in schemas}, dialogues, provenance


def _slot_value(
    values: Any,
    slot_schema: dict[str, Any] | None,
    canonical: Any = None,
) -> str | None:
    if isinstance(canonical, list) and canonical:
        candidate = canonical[-1]
        return str(candidate) if candidate is not None and str(candidate) else None
    if canonical is not None and not isinstance(canonical, list):
        return str(canonical) if str(canonical) else None
    if not isinstance(values, list) or not values:
        return None
    nonempty = [str(value) for value in values if value is not None and str(value)]
    if not nonempty:
        return None

    if slot_schema and slot_schema.get("is_categorical"):
        possible = slot_schema.get("possible_values") or []
        for raw in reversed(nonempty):
            match = next(
                (str(value) for value in possible if str(value).casefold() == raw.casefold()),
                None,
            )
            if match is not None:
                return match
    # SGD state values can contain lexical paraphrases of the same value. When
    # no canonical INFORM action is available, use a deterministic last value.
    return nonempty[-1]


def dialogue_to_context(
    dialogue: dict[str, Any],
    schemas_by_service: dict[str, dict[str, Any]],
) -> tuple[ContractContext, dict[str, int]]:
    dialogue_id = str(dialogue.get("dialogue_id", "")).strip()
    if not dialogue_id:
        raise ValueError("SGD dialogue has no dialogue_id")

    slot_schema_by_service = {
        service: {
            slot["name"]: slot
            for slot in schema.get("slots", [])
            if isinstance(slot.get("name"), str)
        }
        for service, schema in schemas_by_service.items()
    }
    intent_schema_by_service = {
        service: {
            intent["name"]: intent
            for intent in schema.get("intents", [])
            if isinstance(intent.get("name"), str)
        }
        for service, schema in schemas_by_service.items()
    }

    facts: dict[str, str] = {}
    raw_needs: set[str] = set()
    requested_need_count = 0
    required_input_need_count = 0
    user_state_frames = 0
    service_names: set[str] = set()

    for turn in dialogue.get("turns", []):
        if turn.get("speaker") != "USER":
            continue
        for frame in turn.get("frames", []):
            service = frame.get("service")
            state = frame.get("state")
            if not isinstance(service, str) or not isinstance(state, dict):
                continue
            if service not in schemas_by_service:
                raise ValueError(
                    f"dialogue {dialogue_id} references unknown SGD service {service!r}"
                )
            service_names.add(service)
            user_state_frames += 1

            slot_schema = slot_schema_by_service[service]
            canonical_by_slot: dict[str, list[str]] = {}
            for action in frame.get("actions", []):
                if action.get("act") != "INFORM":
                    continue
                slot = action.get("slot")
                canonical_values = action.get("canonical_values") or []
                if isinstance(slot, str) and slot and canonical_values:
                    canonical_by_slot[slot] = [str(value) for value in canonical_values]

            state_values = state.get("slot_values") or {}
            if not isinstance(state_values, dict):
                raise ValueError(
                    f"dialogue {dialogue_id} has malformed state.slot_values"
                )
            for slot, values in state_values.items():
                if not isinstance(slot, str) or not slot:
                    continue
                key = f"{service}::{slot}"
                value = _slot_value(
                    values,
                    slot_schema.get(slot),
                    canonical_by_slot.get(slot),
                )
                if value is not None:
                    # State is cumulative; preserve an earlier canonical value
                    # when this turn contains only another lexical paraphrase.
                    if slot in canonical_by_slot or key not in facts:
                        facts[key] = value

            for slot in state.get("requested_slots") or []:
                if isinstance(slot, str) and slot:
                    raw_needs.add(f"{service}::{slot}")
                    requested_need_count += 1

            active_intent = state.get("active_intent")
            intent_schema = intent_schema_by_service[service].get(active_intent)
            if intent_schema:
                for slot in intent_schema.get("required_slots") or []:
                    if isinstance(slot, str) and slot:
                        key = f"{service}::{slot}"
                        if key not in facts:
                            raw_needs.add(key)
                            required_input_need_count += 1

    needs = {
        key: None
        for key in sorted(raw_needs)
        if key not in facts
    }
    context = ContractContext(
        context_id=f"sgd:{dialogue_id}",
        facts=facts,
        needs=needs,
        utility=len(facts),
    )
    metadata = {
        "user_state_frames": user_state_frames,
        "service_count": len(service_names),
        "requested_need_annotations": requested_need_count,
        "required_input_need_annotations": required_input_need_count,
        "facts": len(facts),
        "unresolved_needs": len(needs),
    }
    return context, metadata


def independently_validate_plan(
    plan: Any,
    contexts: list[ContractContext],
    anchor: dict[str, str],
) -> bool:
    by_id = {context.context_id: context for context in contexts}
    endpoints: set[str] = set()
    for pair in plan.pairs:
        if pair.left in endpoints or pair.right in endpoints:
            return False
        endpoints.update((pair.left, pair.right))
        left, right = by_id[pair.left], by_id[pair.right]
        if not consistent(left.facts, right.facts):
            return False
        left_served = any(
            key in right.facts and (value is None or right.facts[key] == value)
            for key, value in left.needs.items()
        )
        right_served = any(
            key in left.facts and (value is None or left.facts[key] == value)
            for key, value in right.needs.items()
        )
        if not left_served and not right_served:
            return False
    if endpoints != set(plan.selected_contexts):
        return False
    for context_id in endpoints:
        context = by_id[context_id]
        if any(
            key in anchor and anchor[key] != value
            for key, value in context.facts.items()
        ):
            return False
    return True


def _anchor_from_context(
    context: ContractContext,
    rng: random.Random,
    max_facts: int = 3,
) -> dict[str, str]:
    keys = sorted(context.facts)
    selected = rng.sample(keys, min(max_facts, len(keys)))
    return {key: context.facts[key] for key in sorted(selected)}


def run_benchmark(
    schemas_by_service: dict[str, dict[str, Any]],
    dialogues: list[dict[str, Any]],
    shard_provenance: list[dict[str, Any]],
    *,
    seed: int = 2026,
) -> dict[str, Any]:
    mapping_started = time.perf_counter()
    contexts: list[ContractContext] = []
    mapping_metadata: list[dict[str, int]] = []
    for dialogue in dialogues:
        context, metadata = dialogue_to_context(dialogue, schemas_by_service)
        if context.facts or context.needs:
            contexts.append(context)
            mapping_metadata.append(metadata)
    mapping_seconds = time.perf_counter() - mapping_started

    if len(contexts) < 40:
        raise ValueError(
            f"only {len(contexts)} usable SGD contexts; need at least 40"
        )
    fact_bearing = [context for context in contexts if context.facts]
    if len(fact_bearing) < 4:
        raise ValueError("not enough fact-bearing SGD contexts to construct anchors")

    rng = random.Random(seed)
    held_out = rng.sample(fact_bearing, 4)
    held_out_ids = {context.context_id for context in held_out}
    pool = [context for context in contexts if context.context_id not in held_out_ids]
    anchor = _anchor_from_context(held_out[0], rng)
    if not anchor:
        raise ValueError("SGD anchor is empty")

    python_started = time.perf_counter()
    python_graph = build_compatibility_graph(pool, anchor)
    python_graph_seconds = time.perf_counter() - python_started
    python_plan = plan_distribution(pool, anchor, prebuilt_graph=python_graph)

    eligible = [
        context for context in pool if consistent(context.facts, anchor)
    ]
    with RustCompatibilityCacheClient() as cache:
        rust_started = time.perf_counter()
        rust_graph, cold_metrics = cache.build_graph(eligible)
        rust_graph_seconds = time.perf_counter() - rust_started
        rust_plan = plan_distribution(pool, anchor, prebuilt_graph=rust_graph)

        utility_pool = [
            ContractContext(
                context.context_id,
                context.facts,
                context.needs,
                utility=context.value + 13,
            )
            for context in pool
        ]
        warm_graph, warm_metrics = cache.build_graph([
            context for context in utility_pool
            if consistent(context.facts, anchor)
        ])
        warm_plan = plan_distribution(
            utility_pool, anchor, prebuilt_graph=warm_graph
        )
        utility_python_graph = build_compatibility_graph(utility_pool, anchor)
        utility_python_plan = plan_distribution(
            utility_pool, anchor, prebuilt_graph=utility_python_graph
        )

        second_anchor = _anchor_from_context(held_out[1], rng)
        python_second_graph = build_compatibility_graph(pool, second_anchor)
        second_eligible = [
            context for context in pool
            if consistent(context.facts, second_anchor)
        ]
        rust_second_graph, second_metrics = cache.build_graph(second_eligible)
        second_python_plan = plan_distribution(
            pool, second_anchor, prebuilt_graph=python_second_graph
        )
        second_rust_plan = plan_distribution(
            pool, second_anchor, prebuilt_graph=rust_second_graph
        )
        total_metrics = cache.stats()

    graph_matches = graph_signature(rust_graph) == graph_signature(python_graph)
    plan_matches = rust_plan.to_dict() == python_plan.to_dict()
    warm_graph_matches = (
        graph_signature(warm_graph) == graph_signature(utility_python_graph)
    )
    warm_plan_matches = warm_plan.to_dict() == utility_python_plan.to_dict()
    second_graph_matches = (
        graph_signature(rust_second_graph) == graph_signature(python_second_graph)
    )
    second_plan_matches = (
        second_rust_plan.to_dict() == second_python_plan.to_dict()
    )
    raw_plan_valid = independently_validate_plan(python_plan, pool, anchor)
    warm_plan_valid = independently_validate_plan(utility_python_plan, utility_pool, anchor)

    services_observed = sorted({
        frame.get("service")
        for dialogue in dialogues
        for turn in dialogue.get("turns", [])
        if turn.get("speaker") == "USER"
        for frame in turn.get("frames", [])
        if frame.get("service")
    })
    intents_with_required = sum(
        bool(intent.get("required_slots"))
        for service in schemas_by_service.values()
        for intent in service.get("intents", [])
    )
    checks = {
        "all_dialogues_mapped_without_schema_misses": len(contexts) > 0,
        "context_ids_are_unique": len({context.context_id for context in contexts}) == len(contexts),
        "schemas_cover_all_observed_services": set(services_observed).issubset(schemas_by_service),
        "slot_keys_are_service_qualified": all(
            "::" in key
            for context in contexts
            for key in (*context.facts.keys(), *context.needs.keys())
        ),
        "compatibility_graph_is_nonempty": python_graph.number_of_edges() > 0,
        "planner_selects_at_least_one_pair": len(python_plan.pairs) > 0,
        "python_plan_passes_independent_raw_validation": raw_plan_valid,
        "rust_graph_matches_python": graph_matches,
        "rust_complete_plan_matches_python": plan_matches,
        "utility_only_change_hits_whole_graph_cache": bool(warm_metrics["graph_cache_hit"]),
        "warm_graph_matches_python": warm_graph_matches,
        "warm_complete_plan_matches_python": warm_plan_matches,
        "warm_plan_passes_independent_raw_validation": warm_plan_valid,
        "second_anchor_graph_matches_python": second_graph_matches,
        "second_anchor_plan_matches_python": second_plan_matches,
        "pair_cache_reuses_overlap_across_anchor_change": second_metrics["cache_hits"] > 0,
    }

    return {
        "schema": SCHEMA,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "source": {
            "repository": SOURCE_REPOSITORY,
            "commit": SOURCE_COMMIT,
            "split": "test",
            "license": "CC-BY-SA-4.0",
            "schema_git_blob_sha1": SCHEMA_GIT_BLOB_SHA,
            "shards": shard_provenance,
            "dialogues_in_sample": len(dialogues),
        },
        "schema_coverage": {
            "services_in_test_schema": len(schemas_by_service),
            "observed_services_in_sample": len(services_observed),
            "observed_service_names": services_observed,
            "intents_with_required_slots": intents_with_required,
        },
        "mapping": {
            "contexts_retained": len(contexts),
            "empty_contexts_excluded": len(dialogues) - len(contexts),
            "user_state_frames": sum(item["user_state_frames"] for item in mapping_metadata),
            "requested_need_annotations": sum(item["requested_need_annotations"] for item in mapping_metadata),
            "required_input_need_annotations": sum(item["required_input_need_annotations"] for item in mapping_metadata),
            "facts": sum(item["facts"] for item in mapping_metadata),
            "unresolved_needs": sum(item["unresolved_needs"] for item in mapping_metadata),
            "mapping_seconds": round(mapping_seconds, 6),
            "slot_key_policy": "service_name::slot_name",
            "canonical_value_policy": (
                "use latest USER INFORM canonical_values where available; otherwise "
                "use the deterministic last state.slot_values lexicalization; preserve "
                "earlier canonical values when later turns provide only paraphrases"
            ),
            "needs_policy": (
                "union USER requested_slots and missing required_slots for active schema "
                "intent; remove keys present in final accumulated facts"
            ),
            "facts_scope": "USER state only; SYSTEM service_results are not imported as facts",
        },
        "anchor": {
            "held_out_context_ids": [context.context_id for context in held_out],
            "facts": anchor,
            "eligible_contexts": len(eligible),
            "compatibility_edges": python_graph.number_of_edges(),
        },
        "planner": {
            "selected_contexts": len(python_plan.selected_contexts),
            "selected_pairs": len(python_plan.pairs),
            "utility": python_plan.total_utility,
            "independent_raw_validation": raw_plan_valid,
        },
        "cache": {
            "cold_graph_path_seconds": round(rust_graph_seconds, 9),
            "python_graph_path_seconds": round(python_graph_seconds, 9),
            "cold_metrics": cold_metrics,
            "utility_only_warm_metrics": warm_metrics,
            "second_anchor_metrics": second_metrics,
            "total_metrics": total_metrics,
        },
        "checks": checks,
        "checks_passed": sum(bool(value) for value in checks.values()),
        "checks_total": len(checks),
        "interpretation_boundary": (
            "This is an independent task-oriented dialogue corpus, not a business/legal "
            "contract dataset. The adapter deliberately qualifies slot keys by service "
            "to avoid equating homonymous fields across different APIs. User state is "
            "the evidence source; system service_results are excluded. SGD user states "
            "include lexical variants; canonical user INFORM actions are preferred, "
            "but fallback lexical values remain a proxy. The sample includes three "
            "pinned test shards, not the complete 4,201-dialogue test split."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(tempfile.gettempdir()) / "sgd-test-pinned-e852981",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("SGD-INDEPENDENT-DATASET-RESULTS.json"),
    )
    args = parser.parse_args()

    schemas, dialogues, shards = load_sgd_sample(args.cache_dir)
    result = run_benchmark(schemas, dialogues, shards)
    result["output_generated_at_utc"] = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "checks_passed": result["checks_passed"],
        "checks_total": result["checks_total"],
        "dialogues": result["source"]["dialogues_in_sample"],
        "contexts": result["mapping"]["contexts_retained"],
        "services": result["schema_coverage"]["observed_services_in_sample"],
        "eligible": result["anchor"]["eligible_contexts"],
        "edges": result["anchor"]["compatibility_edges"],
        "selected_contexts": result["planner"]["selected_contexts"],
        "rust_graph_seconds": result["cache"]["cold_graph_path_seconds"],
        "python_graph_seconds": result["cache"]["python_graph_path_seconds"],
        "output": str(args.output),
    }, ensure_ascii=False, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
