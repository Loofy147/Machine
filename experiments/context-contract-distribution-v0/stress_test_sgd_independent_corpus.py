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


def schema_intent_contexts(
    schemas_by_service: dict[str, dict[str, Any]],
) -> tuple[list[ContractContext], dict[str, Any]]:
    """Represent each service intent as a schema-level provider/consumer contract.

    `result_slots` are output facts; `required_slots` are
    required inputs. Slot names are kept exact and intentionally unqualified here:
    this benchmark tests the schema's declared cross-service parameter interfaces,
    not dialogue-instance value equality.
    """
    contexts: list[ContractContext] = []
    rows: list[dict[str, Any]] = []
    for service_name in sorted(schemas_by_service):
        service = schemas_by_service[service_name]
        for intent in sorted(
            service.get("intents", []),
            key=lambda item: str(item.get("name", "")),
        ):
            intent_name = intent.get("name")
            if not isinstance(intent_name, str) or not intent_name:
                continue
            outputs = sorted({
                slot for slot in (intent.get("result_slots") or [])
                if isinstance(slot, str) and slot
            })
            required = sorted({
                slot for slot in (intent.get("required_slots") or [])
                if isinstance(slot, str) and slot
            })
            context_id = f"sgd-schema:{service_name}::{intent_name}"
            contexts.append(
                ContractContext(
                    context_id,
                    facts={slot: None for slot in outputs},
                    needs={slot: None for slot in required},
                    utility=len(outputs),
                )
            )
            rows.append({
                "context_id": context_id,
                "service": service_name,
                "intent": intent_name,
                "result_slot_count": len(outputs),
                "required_slot_count": len(required),
            })
    metadata = {
        "intent_contexts": len(contexts),
        "result_slot_count": sum(row["result_slot_count"] for row in rows),
        "required_slot_count": sum(row["required_slot_count"] for row in rows),
        "unique_result_slots": len({
            key for context in contexts for key in context.facts
        }),
        "unique_required_slots": len({
            key for context in contexts for key in context.needs
        }),
        "context_rows": rows,
        "key_policy": (
            "exact schema slot names shared across service APIs; this is a "
            "name-level interface hypothesis, not proof of semantic equivalence"
        ),
    }
    return contexts, metadata


def run_benchmark(
    schemas_by_service: dict[str, dict[str, Any]],
    dialogues: list[dict[str, Any]],
    shard_provenance: list[dict[str, Any]],
    *,
    seed: int = 2026,
) -> dict[str, Any]:
    # Track A: dialogue-instance mapping. Its zero-edge result is retained as a
    # negative diagnostic; it must not be relabelled as a successful composition.
    mapping_started = time.perf_counter()
    dialogue_contexts: list[ContractContext] = []
    mapping_metadata: list[dict[str, int]] = []
    for dialogue in dialogues:
        context, metadata = dialogue_to_context(dialogue, schemas_by_service)
        if context.facts or context.needs:
            dialogue_contexts.append(context)
            mapping_metadata.append(metadata)
    mapping_seconds = time.perf_counter() - mapping_started
    if len(dialogue_contexts) < 40:
        raise ValueError(
            f"only {len(dialogue_contexts)} usable SGD dialogue contexts; need at least 40"
        )
    fact_bearing = [context for context in dialogue_contexts if context.facts]
    if len(fact_bearing) < 4:
        raise ValueError("not enough fact-bearing SGD dialogue contexts to construct anchors")

    rng = random.Random(seed)
    held_out = rng.sample(fact_bearing, 4)
    held_out_ids = {context.context_id for context in held_out}
    dialogue_pool = [
        context for context in dialogue_contexts
        if context.context_id not in held_out_ids
    ]
    dialogue_anchor = _anchor_from_context(held_out[0], rng)
    if not dialogue_anchor:
        raise ValueError("SGD dialogue anchor is empty")

    dialogue_python_graph = build_compatibility_graph(
        dialogue_pool, dialogue_anchor
    )
    dialogue_python_plan = plan_distribution(
        dialogue_pool, dialogue_anchor, prebuilt_graph=dialogue_python_graph
    )
    dialogue_eligible = [
        context for context in dialogue_pool
        if consistent(context.facts, dialogue_anchor)
    ]

    # Track B: schema-intent composition. Each of the 38 schema intents becomes
    # one API contract: declared result slots are outputs and required slots are
    # inputs. This is the appropriate unit for cross-service schema composition.
    schema_contexts, schema_metadata = schema_intent_contexts(schemas_by_service)
    if len(schema_contexts) < 10:
        raise ValueError("the SGD schema contains too few intent contexts")
    schema_anchor: dict[str, Any] = {}
    schema_python_started = time.perf_counter()
    schema_python_graph = build_compatibility_graph(schema_contexts, schema_anchor)
    schema_python_graph_seconds = time.perf_counter() - schema_python_started
    schema_python_plan = plan_distribution(
        schema_contexts, schema_anchor, prebuilt_graph=schema_python_graph
    )
    schema_eligible = [
        context for context in schema_contexts
        if consistent(context.facts, schema_anchor)
    ]

    with RustCompatibilityCacheClient() as cache:
        dialogue_rust_graph, dialogue_cold_metrics = cache.build_graph(
            dialogue_eligible
        )
        dialogue_rust_plan = plan_distribution(
            dialogue_pool, dialogue_anchor, prebuilt_graph=dialogue_rust_graph
        )

        schema_rust_started = time.perf_counter()
        schema_rust_graph, schema_cold_metrics = cache.build_graph(schema_eligible)
        schema_rust_graph_seconds = time.perf_counter() - schema_rust_started
        schema_rust_plan = plan_distribution(
            schema_contexts, schema_anchor, prebuilt_graph=schema_rust_graph
        )

        schema_utility_contexts = [
            ContractContext(
                context.context_id,
                context.facts,
                context.needs,
                utility=context.value + 13,
            )
            for context in schema_contexts
        ]
        schema_warm_eligible = [
            context for context in schema_utility_contexts
            if consistent(context.facts, schema_anchor)
        ]
        schema_warm_graph, schema_warm_metrics = cache.build_graph(
            schema_warm_eligible
        )
        schema_warm_plan = plan_distribution(
            schema_utility_contexts,
            schema_anchor,
            prebuilt_graph=schema_warm_graph,
        )
        schema_utility_python_graph = build_compatibility_graph(
            schema_utility_contexts, schema_anchor
        )
        schema_utility_python_plan = plan_distribution(
            schema_utility_contexts,
            schema_anchor,
            prebuilt_graph=schema_utility_python_graph,
        )
        total_metrics = cache.stats()

    dialogue_graph_matches = (
        graph_signature(dialogue_rust_graph)
        == graph_signature(dialogue_python_graph)
    )
    dialogue_plan_matches = (
        dialogue_rust_plan.to_dict() == dialogue_python_plan.to_dict()
    )
    dialogue_raw_valid = independently_validate_plan(
        dialogue_python_plan, dialogue_pool, dialogue_anchor
    )
    dialogue_diagnostic = {
        "status": (
            "NO_EDGES" if dialogue_python_graph.number_of_edges() == 0
            else "EDGES_FOUND"
        ),
        "registered_contexts": len(dialogue_pool),
        "anchor_eligible_contexts": len(dialogue_eligible),
        "compatibility_edges": dialogue_python_graph.number_of_edges(),
        "selected_pairs": len(dialogue_python_plan.pairs),
        "selected_contexts": len(dialogue_python_plan.selected_contexts),
        "python_rust_graph_equal": dialogue_graph_matches,
        "python_rust_plan_equal": dialogue_plan_matches,
        "raw_plan_valid": dialogue_raw_valid,
        "interpretation": (
            "The sampled dialogue instances are not interchangeable partner "
            "contracts under the conservative service-qualified slot mapping. "
            "The empty graph is retained as a negative dataset diagnostic."
            if dialogue_python_graph.number_of_edges() == 0
            else "Dialogue-level contexts produced compatibility edges."
        ),
    }

    schema_graph_matches = (
        graph_signature(schema_rust_graph) == graph_signature(schema_python_graph)
    )
    schema_plan_matches = (
        schema_rust_plan.to_dict() == schema_python_plan.to_dict()
    )
    schema_raw_valid = independently_validate_plan(
        schema_python_plan, schema_contexts, schema_anchor
    )
    schema_warm_graph_matches = (
        graph_signature(schema_warm_graph)
        == graph_signature(schema_utility_python_graph)
    )
    schema_warm_plan_matches = (
        schema_warm_plan.to_dict() == schema_utility_python_plan.to_dict()
    )
    schema_warm_raw_valid = independently_validate_plan(
        schema_utility_python_plan, schema_utility_contexts, schema_anchor
    )

    services_observed = sorted({
        frame.get("service")
        for dialogue in dialogues
        for turn in dialogue.get("turns", [])
        if turn.get("speaker") == "USER"
        for frame in turn.get("frames", [])
        if frame.get("service")
    })

    checks = {
        "dialogue_contexts_mapped": len(dialogue_contexts) == len(dialogues),
        "dialogue_context_ids_unique": (
            len({context.context_id for context in dialogue_contexts})
            == len(dialogue_contexts)
        ),
        "schemas_cover_all_observed_dialogue_services": (
            set(services_observed).issubset(schemas_by_service)
        ),
        "dialogue_slots_are_service_qualified": all(
            "::" in key
            for context in dialogue_contexts
            for key in (*context.facts.keys(), *context.needs.keys())
        ),
        "dialogue_rust_graph_matches_python_even_when_empty": dialogue_graph_matches,
        "dialogue_rust_plan_matches_python_even_when_empty": dialogue_plan_matches,
        "dialogue_plan_passes_raw_validation": dialogue_raw_valid,
        "schema_intent_context_count_is_38": schema_metadata["intent_contexts"] == 38,
        "schema_intent_graph_is_nonempty": schema_python_graph.number_of_edges() > 0,
        "schema_intent_planner_selects_pairs": len(schema_python_plan.pairs) > 0,
        "schema_intent_raw_plan_valid": schema_raw_valid,
        "schema_rust_graph_matches_python": schema_graph_matches,
        "schema_rust_complete_plan_matches_python": schema_plan_matches,
        "schema_utility_only_change_hits_whole_graph_cache": bool(
            schema_warm_metrics["graph_cache_hit"]
        ),
        "schema_warm_graph_matches_python": schema_warm_graph_matches,
        "schema_warm_complete_plan_matches_python": schema_warm_plan_matches,
        "schema_warm_plan_passes_raw_validation": schema_warm_raw_valid,
    }
    facts_in_contexts = sum(len(context.facts) for context in dialogue_contexts)
    needs_in_contexts = sum(len(context.needs) for context in dialogue_contexts)
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
            "observed_services_in_dialogue_sample": len(services_observed),
            "observed_service_names": services_observed,
            "schema_intent_contexts": schema_metadata["intent_contexts"],
            "intents_with_required_slots": sum(
                bool(intent.get("required_slots"))
                for service in schemas_by_service.values()
                for intent in service.get("intents", [])
            ),
        },
        "dialogue_instance_diagnostic": dialogue_diagnostic,
        "dialogue_mapping": {
            "contexts_retained": len(dialogue_contexts),
            "empty_contexts_excluded": len(dialogues) - len(dialogue_contexts),
            "user_state_frames": sum(
                item["user_state_frames"] for item in mapping_metadata
            ),
            "requested_need_annotations": sum(
                item["requested_need_annotations"] for item in mapping_metadata
            ),
            "required_input_need_annotations": sum(
                item["required_input_need_annotations"] for item in mapping_metadata
            ),
            "facts": facts_in_contexts,
            "unresolved_needs": needs_in_contexts,
            "mapping_seconds": round(mapping_seconds, 6),
            "slot_key_policy": "service_name::slot_name",
            "canonical_value_policy": (
                "latest USER INFORM canonical_values preferred; otherwise "
                "deterministic last state.slot_values lexicalization"
            ),
            "needs_policy": (
                "USER requested_slots plus schema required_slots absent from "
                "accumulated user facts"
            ),
            "facts_scope": "USER state only; SYSTEM service_results excluded",
        },
        "schema_intent_composition": {
            "context_count": schema_metadata["intent_contexts"],
            "result_slot_count": schema_metadata["result_slot_count"],
            "required_slot_count": schema_metadata["required_slot_count"],
            "unique_result_slots": schema_metadata["unique_result_slots"],
            "unique_required_slots": schema_metadata["unique_required_slots"],
            "context_rows": schema_metadata["context_rows"],
            "key_policy": schema_metadata["key_policy"],
            "anchor": schema_anchor,
            "eligible_contexts": len(schema_eligible),
            "compatibility_edges": schema_python_graph.number_of_edges(),
            "selected_pairs": len(schema_python_plan.pairs),
            "selected_contexts": len(schema_python_plan.selected_contexts),
            "total_utility": schema_python_plan.total_utility,
            "raw_plan_valid": schema_raw_valid,
        },
        "cache": {
            "dialogue_graph_metrics": dialogue_cold_metrics,
            "schema_cold_graph_seconds": round(schema_rust_graph_seconds, 9),
            "schema_python_graph_seconds": round(schema_python_graph_seconds, 9),
            "schema_cold_metrics": schema_cold_metrics,
            "schema_warm_utility_metrics": schema_warm_metrics,
            "total_metrics": total_metrics,
        },
        "checks": checks,
        "checks_passed": sum(bool(value) for value in checks.values()),
        "checks_total": len(checks),
        "interpretation_boundary": (
            "The sampled dialogue-instance model produced zero compatible pairs "
            "under conservative service-qualified slots; this negative result is "
            "reported, not hidden. The positive composition test uses 38 API intent "
            "schemas, where result_slots are provider outputs and required_slots "
            "are consumer inputs. Exact slot-name matching across service schemas "
            "is only a name-level interface hypothesis, not semantic equivalence. "
            "This is not a business/legal contract dataset. The sample contains "
            "three pinned test shards (310 dialogues), not the full SGD test split."
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
