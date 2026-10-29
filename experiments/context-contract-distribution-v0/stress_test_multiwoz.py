#!/usr/bin/env python3
"""Stress-test the contract-context planner on real MultiWOZ 2.2 test dialogues.

Source: budzianowski/multiwoz, pinned commit fe0c8e65cfcd8462bd33c86e35f21addc84ca82b.
Every dialogue becomes one context. Facts come from its annotated belief-state slot values;
needs come only from unresolved annotated requested slots. No random feature bins, fabricated
needs, or synthetic dialogue content are introduced. A few contexts are held out as real
anchor states. Utility is an explicitly limited proxy: the number of distinct populated slots.

Network access is used only to fetch the pinned, checksummed corpus files when not cached.
No model calls are made. All generated plans and benchmark summaries are local artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import sys
import tempfile
import time
import urllib.request
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

import networkx as nx

from context_contract_distribution import (
    ContractContext,
    build_compatibility_graph,
    plan_distribution,
)

SEED = 2026
SOURCE_REPO = "https://github.com/budzianowski/multiwoz"
SOURCE_COMMIT = "fe0c8e65cfcd8462bd33c86e35f21addc84ca82b"
DATA_ROOT = f"https://raw.githubusercontent.com/budzianowski/multiwoz/{SOURCE_COMMIT}/data/MultiWOZ_2.2/test"
SHARDS = (
    ("dialogues_001.json", "fd420005cc9dc259892f541b001d9d48608bd38d"),
    ("dialogues_002.json", "8ce97bc17acc3d1105d92d8d936520b8c93892ba"),
)
SCHEMA = "context-contract-multiwoz-real-data-results.v0.1"


def _log(*parts: Any) -> None:
    print(*parts, flush=True)


def git_blob_sha1(data: bytes) -> str:
    """Verify the exact Git blob object, not only an HTTP response or URL."""
    prefix = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(prefix + data).hexdigest()


def download_shard(filename: str, expected_git_sha1: str, cache_dir: Path) -> tuple[bytes, str]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / filename
    if path.exists():
        data = path.read_bytes()
        if git_blob_sha1(data) != expected_git_sha1:
            path.unlink()
    if not path.exists():
        url = f"{DATA_ROOT}/{filename}"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Machine-context-contract-benchmark/0.1"},
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
        actual = git_blob_sha1(data)
        if actual != expected_git_sha1:
            raise RuntimeError(
                f"pinned dataset integrity failure for {filename}: "
                f"expected Git blob {expected_git_sha1}, got {actual}"
            )
        path.write_bytes(data)
    else:
        data = path.read_bytes()
    actual = git_blob_sha1(data)
    if actual != expected_git_sha1:
        raise RuntimeError(f"cached dataset integrity failure for {filename}: {actual}")
    return data, hashlib.sha256(data).hexdigest()


def _scalar_values(raw: Any) -> list[str]:
    if raw is None:
        candidates = []
    elif isinstance(raw, (list, tuple, set)):
        candidates = list(raw)
    else:
        candidates = [raw]
    return sorted({str(value).strip().casefold() for value in candidates if value is not None and str(value).strip()})


def _qualify_slot(service: str, raw_slot: Any) -> str | None:
    slot = str(raw_slot).strip().casefold()
    if not slot or slot in {"none", "null", "not mentioned"}:
        return None
    # MultiWOZ v2.2 slot-values generally contain globally qualified names
    # (e.g. restaurant-area); requested_slots can be local (e.g. name).
    return slot if "-" in slot else f"{service.casefold()}-{slot}"


def dialogue_to_context(dialogue: dict[str, Any]) -> ContractContext:
    """Convert one real dialogue into a final-state contract context."""
    dialogue_id = dialogue.get("dialogue_id")
    if not isinstance(dialogue_id, str) or not dialogue_id.strip():
        raise ValueError("MultiWOZ dialogue is missing a valid dialogue_id")

    facts_by_service: dict[str, dict[str, str]] = {}
    requested_by_service: dict[str, set[str]] = {}

    for turn in dialogue.get("turns", []):
        # State and requests are taken from user turns only. System utterances
        # never become facts or needs in the contract context.
        if str(turn.get("speaker", "")).upper() != "USER":
            continue
        for frame in turn.get("frames", []):
            service = str(frame.get("service", "")).strip().casefold()
            if not service:
                continue
            state = frame.get("state")
            if not isinstance(state, dict):
                continue

            frame_facts: dict[str, str] = {}
            raw_values = state.get("slot_values", {})
            if isinstance(raw_values, dict):
                for raw_key, raw_value in raw_values.items():
                    key = str(raw_key).strip().casefold()
                    values = _scalar_values(raw_value)
                    if key and values:
                        # MultiWOZ documents alternative valid surface forms in a list.
                        # Canonical JSON keeps all aliases without depending on list order.
                        frame_facts[key] = json.dumps(values, ensure_ascii=False, separators=(",", ":"))
            requested: set[str] = set()
            raw_requests = state.get("requested_slots", [])
            if isinstance(raw_requests, list):
                for raw_slot in raw_requests:
                    key = _qualify_slot(service, raw_slot)
                    if key:
                        requested.add(key)

            # MultiWOZ may include inactive empty frames for services unrelated
            # to the current turn. Do not let them erase a previous state snapshot.
            active_intent = str(state.get("active_intent", "NONE")).strip().upper()
            if active_intent != "NONE" or frame_facts or requested:
                facts_by_service[service] = frame_facts

            # Requests express annotated user demand across the dialogue. Preserve
            # those observations and later remove any request key present in final
            # facts. Since system responses are excluded, this is a state-schema
            # proxy, not proof that a request was never answered in natural language.
            requested_by_service.setdefault(service, set()).update(requested)

    facts: dict[str, str] = {}
    for service in sorted(facts_by_service):
        for key, value in sorted(facts_by_service[service].items()):
            # The global slot key identifies ownership. If malformed data repeats
            # one key across frames, deterministic service order makes the winner stable.
            facts[key] = value

    needs = set().union(*requested_by_service.values()) if requested_by_service else set()
    # Do not keep a request as unresolved if the final dialogue state contains it.
    needs.difference_update(facts)
    return ContractContext(
        context_id=f"multiwoz-v2.2:{dialogue_id}",
        facts=facts,
        needs={key: None for key in sorted(needs)},
        utility=len(facts),
    )


def load_corpus(cache_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    dialogues: list[dict[str, Any]] = []
    provenance: list[dict[str, str]] = []
    for filename, expected_git_sha1 in SHARDS:
        raw, sha256 = download_shard(filename, expected_git_sha1, cache_dir)
        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            raise RuntimeError(f"{filename} did not decode to a list of dialogues")
        if any(not isinstance(row, dict) or "dialogue_id" not in row or "turns" not in row for row in parsed):
            raise RuntimeError(f"{filename} has an invalid MultiWOZ dialogue record")
        dialogues.extend(parsed)
        provenance.append({
            "filename": filename,
            "url": f"{DATA_ROOT}/{filename}",
            "expected_git_blob_sha1": expected_git_sha1,
            "verified_git_blob_sha1": git_blob_sha1(raw),
            "sha256": sha256,
            "bytes": str(len(raw)),
            "dialogues": str(len(parsed)),
        })
    ids = [row["dialogue_id"] for row in dialogues]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate dialogue IDs across the pinned MultiWOZ test shards")
    return dialogues, provenance


def anchor_from_context(context: ContractContext, rng: random.Random, max_facts: int = 3) -> dict[str, str]:
    keys = sorted(context.facts)
    chosen = rng.sample(keys, min(max_facts, len(keys)))
    return {key: context.facts[key] for key in sorted(chosen)}


def raw_consistent(left: ContractContext, right: ContractContext) -> bool:
    return all(left.facts[key] == right.facts[key] for key in left.facts.keys() & right.facts.keys())


def raw_served(left: ContractContext, right: ContractContext) -> bool:
    return bool(set(left.needs) & set(right.facts)) or bool(set(right.needs) & set(left.facts))


def raw_anchor_valid(context: ContractContext, anchor: dict[str, str]) -> bool:
    return all(key not in anchor or context.facts[key] == anchor[key] for key in context.facts)


def independently_validate_plan(
    plan: Any,
    context_by_id: dict[str, ContractContext],
    anchor: dict[str, str],
) -> tuple[bool, str]:
    selected = set(plan.selected_contexts)
    pair_endpoints: set[str] = set()
    for pair in plan.pairs:
        if pair.left in pair_endpoints or pair.right in pair_endpoints:
            return False, "a selected context appears in more than one pair"
        pair_endpoints.update((pair.left, pair.right))
        left, right = context_by_id[pair.left], context_by_id[pair.right]
        if not raw_consistent(left, right):
            return False, f"pair {pair.left}, {pair.right} conflicts on a fact"
        if not raw_served(left, right):
            return False, f"pair {pair.left}, {pair.right} has no directed need witness"
    if pair_endpoints != selected:
        return False, "selected context IDs differ from the union of returned pair endpoints"
    for context_id in selected:
        if not raw_anchor_valid(context_by_id[context_id], anchor):
            return False, f"selected context {context_id} conflicts with the anchor"
    return True, "each selected context is uniquely paired; raw facts, service relation, and anchor revalidated"


def greedy_edge_baseline(graph: nx.Graph, utility: dict[str, int]) -> tuple[set[str], int]:
    used: set[str] = set()
    selected: set[str] = set()
    for left, right in sorted(
        graph.edges,
        key=lambda edge: (-(utility[edge[0]] + utility[edge[1]]), str(edge[0]), str(edge[1])),
    ):
        if left not in used and right not in used:
            used.update((left, right))
            selected.update((left, right))
    return selected, sum(utility[node] for node in selected)


def exact_objective_reference(graph: nx.Graph, utility: dict[str, int]) -> tuple[int, int]:
    reference = nx.Graph(graph)
    eligible_count = reference.number_of_nodes()
    scale = eligible_count + 1
    for left, right in reference.edges:
        reference[left][right]["weight"] = (utility[left] + utility[right]) * scale + 2
    matching = nx.max_weight_matching(reference, maxcardinality=False, weight="weight")
    selected = {node for edge in matching for node in edge}
    return sum(utility[node] for node in selected), len(selected)


def family_walk(graph: nx.Graph, start: set[str], target: set[str]) -> dict[str, Any]:
    cache: dict[frozenset[str], bool] = {}
    def feasible(values: set[str]) -> bool:
        key = frozenset(values)
        if key not in cache:
            if len(key) % 2:
                cache[key] = False
            else:
                cache[key] = 2 * len(nx.max_weight_matching(graph.subgraph(key), maxcardinality=True)) == len(key)
        return cache[key]

    current = set(start)
    path: list[list[str]] = []
    while current != target:
        difference = sorted(current ^ target)
        moved = False
        for x in difference:
            for y in difference:
                step = {x} if x == y else {x, y}
                candidate = current ^ step
                if feasible(candidate):
                    path.append(sorted(step))
                    current = candidate
                    moved = True
                    break
            if moved:
                break
        if not moved:
            return {"connected": False, "moves": path, "checked_sets": len(cache)}
    return {
        "connected": True,
        "moves": path,
        "checked_sets": len(cache),
        "all_moves_are_two_context": all(len(step) == 2 for step in path),
        "optimal_path_length": len(path) == len(start ^ target) // 2,
        "nontrivial": bool(path),
    }


def make_contexts(dialogues: list[dict[str, Any]]) -> list[ContractContext]:
    return [dialogue_to_context(dialogue) for dialogue in dialogues]


def run_benchmark(
    dialogues: list[dict[str, Any]],
    provenance: list[dict[str, str]],
    limit: int | None = None,
    anchor_updates: int = 3,
) -> dict[str, Any]:
    started = time.time()
    rng = random.Random(SEED)
    contexts = make_contexts(dialogues)
    if limit is not None:
        contexts = contexts[:limit]
    if len(contexts) < 20:
        raise ValueError("at least 20 MultiWOZ dialogue contexts are required for this benchmark")

    eligible_anchor_sources = [context for context in contexts if len(context.facts) >= 2]
    if len(eligible_anchor_sources) < anchor_updates + 1:
        raise ValueError("not enough fact-bearing real dialogues for anchor updates")
    anchor_sources = rng.sample(eligible_anchor_sources, min(anchor_updates + 1, len(eligible_anchor_sources)))
    anchor_source_ids = {context.context_id for context in anchor_sources}
    pool = [context for context in contexts if context.context_id not in anchor_source_ids]
    by_id = {context.context_id: context for context in pool}
    anchor = anchor_from_context(anchor_sources[0], rng)
    if not anchor:
        raise ValueError("selected real anchor dialogue has no fact-bearing slots")

    _log("== MultiWOZ 2.2 actual test-corpus benchmark ==")
    _log(f"source dialogues: {len(dialogues)}; contexts in planner pool: {len(pool)}; anchor facts: {len(anchor)}")
    t_plan = time.time()
    plan = plan_distribution(pool, anchor)
    plan_seconds = time.time() - t_plan
    graph = build_compatibility_graph(pool, anchor)
    utilities = {context.context_id: context.value for context in pool}
    independent_ok, independent_detail = independently_validate_plan(plan, by_id, anchor)
    ref_utility, ref_count = exact_objective_reference(graph, utilities)
    greedy_ids, greedy_utility = greedy_edge_baseline(graph, utilities)
    objective_ok = (plan.total_utility, len(plan.selected_contexts)) == (ref_utility, ref_count)
    _log(f"[{'PASS' if independent_ok else 'FAIL'}] raw-fact and anchor validation: {independent_detail}")
    _log(f"[{'PASS' if objective_ok else 'FAIL'}] planner objective equals separately recomputed encoded-weight matching objective")
    _log(f"   eligible {graph.number_of_nodes()}, edges {graph.number_of_edges()}, selected {len(plan.selected_contexts)}, utility {plan.total_utility}; greedy-edge utility {greedy_utility}; planner {plan_seconds:.2f}s")

    # Reconfiguration must be non-trivial to count as a positive test. Search
    # deterministic real-data subpools/anchors until the two data-derived utility
    # policies actually produce different selected sets; never pass on a zero-step walk.
    walk_pool_source = [context for context in pool if context.facts or context.needs]
    walk: dict[str, Any] = {
        "connected": False,
        "moves": [],
        "checked_sets": 0,
        "all_moves_are_two_context": False,
        "optimal_path_length": False,
        "nontrivial": False,
    }
    walk_pool: list[ContractContext] = []
    walk_attempts = 0
    walk_found_difference = False
    for attempt in range(1, 21):
        walk_attempts = attempt
        walk_pool = rng.sample(walk_pool_source, min(80, len(walk_pool_source)))
        walk_anchor_source = anchor_sources[attempt % len(anchor_sources)]
        walk_anchor = anchor_from_context(walk_anchor_source, rng)
        facts_policy = [ContractContext(c.context_id, c.facts, c.needs, utility=len(c.facts)) for c in walk_pool]
        # Requests receive priority, while observed slot count remains a deterministic
        # tie-breaker. Both quantities come from the actual annotated dialogue.
        requests_policy = [
            ContractContext(c.context_id, c.facts, c.needs, utility=100 * len(c.needs) + len(c.facts))
            for c in walk_pool
        ]
        p_facts = plan_distribution(facts_policy, walk_anchor)
        p_requests = plan_distribution(requests_policy, walk_anchor)
        first = set(p_facts.selected_contexts)
        target = set(p_requests.selected_contexts)
        if first == target:
            continue
        walk_found_difference = True
        walk_graph = build_compatibility_graph(walk_pool, walk_anchor)
        walk = family_walk(walk_graph, first, target)
        break
    walk_ok = (
        walk_found_difference
        and walk["connected"]
        and walk["nontrivial"]
        and walk["all_moves_are_two_context"]
        and walk["optimal_path_length"]
    )
    _log(f"[{'PASS' if walk_ok else 'FAIL'}] non-trivial real-context reconfiguration between facts- and request-priority policies")
    _log(f"   attempts {walk_attempts}, subpool {len(walk_pool)}, different selected sets {walk_found_difference}, transitions {len(walk['moves'])}, connected {walk['connected']}, checked subsets {walk['checked_sets']}")

    # Anchor updates use other held-out real dialogue states. Repair drops each old
    # selected pair touching a context excluded by the new real anchor.
    updates: list[dict[str, Any]] = []
    current_anchor = anchor
    current_plan = plan
    current_graph = graph
    repair_all_valid = True
    repair_bound_all_valid = True
    for index, new_anchor_context in enumerate(anchor_sources[1:anchor_updates + 1], start=1):
        new_anchor = anchor_from_context(new_anchor_context, rng)
        new_graph = build_compatibility_graph(pool, new_anchor)
        newly_broken = set(current_plan.selected_contexts) - set(new_graph.nodes)
        old_pairs = [(pair.left, pair.right) for pair in current_plan.pairs]
        repaired = {
            node
            for pair in old_pairs
            if not (set(pair) & newly_broken)
            for node in pair
        }
        repair_feasible = repaired <= set(new_graph.nodes) and (
            2 * len(nx.max_weight_matching(new_graph.subgraph(repaired), maxcardinality=True)) == len(repaired)
        )
        repair_distance = len(set(current_plan.selected_contexts) ^ repaired)
        repair_bound = repair_distance <= 2 * len(newly_broken)
        repair_all_valid &= repair_feasible
        repair_bound_all_valid &= repair_bound

        replanned = plan_distribution(pool, new_anchor)
        churn_reopt = len(set(current_plan.selected_contexts) ^ set(replanned.selected_contexts))
        updates.append({
            "step": index,
            "anchor_dialogue_id": new_anchor_context.context_id,
            "old_anchor_fact_count": len(current_anchor),
            "new_anchor_fact_count": len(new_anchor),
            "new_graph_eligible_contexts": new_graph.number_of_nodes(),
            "newly_broken_selected_contexts": len(newly_broken),
            "repair_feasible": repair_feasible,
            "repair_context_symmetric_difference": repair_distance,
            "repair_bound_2x_broken_contexts": 2 * len(newly_broken),
            "repair_bound_holds": repair_bound,
            "reoptimization_context_churn": churn_reopt,
            "reoptimized_utility": replanned.total_utility,
            "repair_utility": sum(utilities[node] for node in repaired),
            "reoptimization_utility_regret": replanned.total_utility - sum(utilities[node] for node in repaired),
        })
        current_anchor, current_plan, current_graph = new_anchor, replanned, new_graph
    anchor_ok = repair_all_valid and repair_bound_all_valid
    _log(f"[{'PASS' if anchor_ok else 'FAIL'}] replacement anchors derived from held-out real dialogues preserve bounded pair-drop repair")
    _log(f"   {len(updates)} updates; repair infeasible {sum(not x['repair_feasible'] for x in updates)}; bound violations {sum(not x['repair_bound_holds'] for x in updates)}")

    # A scarce-supply subset uses actual contexts with facts and at least one
    # requested-slot key absent from final facts. No need is fabricated.
    scarce_source = [context for context in pool if context.facts and context.needs]
    scarce_pool = rng.sample(scarce_source, min(250, len(scarce_source)))
    scarce_anchor_source = anchor_sources[-1]
    scarce_anchor = anchor_from_context(scarce_anchor_source, rng)
    scarce_plan = plan_distribution(scarce_pool, scarce_anchor)
    scarce_graph = build_compatibility_graph(scarce_pool, scarce_anchor)
    scarce_utility = {context.context_id: context.value for context in scarce_pool}
    scarce_ref = exact_objective_reference(scarce_graph, scarce_utility)
    scarce_ok = (scarce_plan.total_utility, len(scarce_plan.selected_contexts)) == scarce_ref
    scarce_valid, scarce_detail = independently_validate_plan(scarce_plan, {c.context_id: c for c in scarce_pool}, scarce_anchor)
    scarce_ok &= scarce_valid
    _log(f"[{'PASS' if scarce_ok else 'FAIL'}] actual-data scarce-supply subset: {scarce_detail}")
    _log(f"   {len(scarce_pool)} contexts with observed facts and requested-slot keys absent from final facts; eligible {scarce_graph.number_of_nodes()}, edges {scarce_graph.number_of_edges()}, selected {len(scarce_plan.selected_contexts)}")

    checks = [
        {"name": "full_test_split_plan_raw_fact_validation", "passed": independent_ok, "details": independent_detail},
        {"name": "full_test_split_exact_objective_reference", "passed": objective_ok, "details": f"plan=({plan.total_utility},{len(plan.selected_contexts)}); oracle=({ref_utility},{ref_count})"},
        {"name": "real_context_policy_reconfiguration", "passed": walk_ok, "details": f"{len(walk['moves'])} moves; connected={walk['connected']}"},
        {"name": "real_anchor_replacement_repair", "passed": anchor_ok, "details": f"{len(updates)} anchor changes; no infeasibility or 2x-bound violation"},
        {"name": "actual_request_scarcity_subset", "passed": scarce_ok, "details": f"{len(scarce_pool)} contexts; oracle={scarce_ref}; {scarce_detail}"},
    ]
    contexts_with_facts = sum(bool(context.facts) for context in contexts)
    contexts_with_needs = sum(bool(context.needs) for context in contexts)
    service_counts = Counter(service for dialogue in dialogues for service in dialogue.get("services", []))
    output = {
        "schema": SCHEMA,
        "status": "PASS" if all(check["passed"] for check in checks) else "FAIL",
        "seed": SEED,
        "source": {
            "repository": SOURCE_REPO,
            "commit": SOURCE_COMMIT,
            "version": "MultiWOZ 2.2",
            "split": "test",
            "shards": provenance,
            "dataset_description_url": f"https://github.com/budzianowski/multiwoz/tree/{SOURCE_COMMIT}/data/MultiWOZ_2.2",
            "format_reference": "Each dialogue has turns; user turns contain per-service frames with state.slot_values and state.requested_slots.",
            "fact_encoding": "Each qualified slot key maps to compact canonical JSON of the distinct normalized strings in the dataset's slot_values list; value aliases are retained as a set.",
            "need_encoding": "Only annotated requested_slots still absent from the final facts; no synthetic needs are added.",
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "networkx": nx.__version__,
        },
        "corpus": {
            "dialogues_loaded": len(dialogues),
            "contexts_after_limit": len(contexts),
            "contexts_with_facts": contexts_with_facts,
            "contexts_with_requested_slots_absent_from_final_facts": contexts_with_needs,
            "unique_services_in_source": dict(sorted(service_counts.items())),
            "held_out_anchor_dialogues": [context.context_id for context in anchor_sources],
            "initial_anchor_fact_count": len(anchor),
        },
        "main_plan": {
            "input_digest_sha256": plan.input_digest,
            "eligible_contexts": graph.number_of_nodes(),
            "compatibility_edges": graph.number_of_edges(),
            "selected_contexts": len(plan.selected_contexts),
            "paired_contexts": 2 * len(plan.pairs),
            "unmatched_eligible_contexts": len(plan.unmatched_eligible),
            "isolated_eligible_contexts": len(plan.isolated_eligible),
            "total_slot_coverage_utility": plan.total_utility,
            "oracle_slot_coverage_utility": ref_utility,
            "oracle_selected_context_count": ref_count,
            "greedy_edge_baseline_utility": greedy_utility,
            "utility_uplift_over_greedy_fraction": (plan.total_utility - greedy_utility) / max(greedy_utility, 1),
            "plan_runtime_seconds": round(plan_seconds, 6),
            "raw_validation_detail": independent_detail,
        },
        "reconfiguration": {
            "pool_size": len(walk_pool),
            "first_policy": "utility = count of distinct belief-state slots",
            "second_policy": "utility = count of unresolved annotated requested slots",
            **walk,
        },
        "anchor_updates": updates,
        "scarce_request_pool": {
            "source": "contexts with actual facts and at least one annotated requested-slot key absent from final facts",
            "contexts": len(scarce_pool),
            "eligible": scarce_graph.number_of_nodes(),
            "edges": scarce_graph.number_of_edges(),
            "selected_contexts": len(scarce_plan.selected_contexts),
            "utility": scarce_plan.total_utility,
            "oracle": {"utility": scarce_ref[0], "selected_context_count": scarce_ref[1]},
            "raw_validation_detail": scarce_detail,
        },
        "checks": checks,
        "checks_passed": sum(check["passed"] for check in checks),
        "checks_total": len(checks),
        "runtime_seconds": round(time.time() - started, 3),
        "interpretation_boundary": (
            "This benchmark uses actual MultiWOZ 2.2 annotated test dialogues and belief-state/requested-slot values. "
            "A dialogue is converted to a context deterministically; anchors are partial states from held-out real dialogues. "
            "Utility is only a slot-count proxy. MultiWOZ's crowd-sourced travel dialogues are not business/legal contracts, "
            "so results establish planner behavior on this corpus, not production contract performance or a universal theorem."
        ),
    }
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path(tempfile.gettempdir()) / "multiwoz-v22-pinned")
    parser.add_argument("--limit", type=int, default=0, help="optional deterministic dialogue limit for smoke tests; default uses the full pinned test split")
    parser.add_argument("--anchor-updates", type=int, default=3)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("MULTIWOZ-REAL-DATA-RESULTS.json"))
    args = parser.parse_args()
    if args.limit < 0 or args.anchor_updates < 1:
        parser.error("--limit must be >= 0 and --anchor-updates must be >= 1")

    corpus, provenance = load_corpus(args.cache_dir)
    started = time.time()
    result = run_benchmark(
        corpus,
        provenance,
        limit=args.limit or None,
        anchor_updates=args.anchor_updates,
    )
    result["download_and_load_seconds"] = round(time.time() - started, 3)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    _log("\nSUMMARY: " + json.dumps({
        "status": result["status"],
        "checks_passed": result["checks_passed"],
        "checks_total": result["checks_total"],
        "dialogues_loaded": result["corpus"]["dialogues_loaded"],
        "contexts_after_limit": result["corpus"]["contexts_after_limit"],
        "eligible_contexts": result["main_plan"]["eligible_contexts"],
        "selected_contexts": result["main_plan"]["selected_contexts"],
        "compatibility_edges": result["main_plan"]["compatibility_edges"],
        "runtime_seconds": result["runtime_seconds"],
        "output": str(args.output),
    }, ensure_ascii=False, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
