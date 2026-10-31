#!/usr/bin/env python3
"""Measure MultiWOZ planner sensitivity to real-anchor selection and utility policy.

This is a robustness probe, not a statistical confidence interval. It repeatedly
uses the same pinned, actual test corpus while varying deterministic anchor seeds.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import tempfile
import time
from pathlib import Path
from statistics import mean, median
from typing import Any

from context_contract_distribution import (
    ContractContext,
    build_compatibility_graph,
    consistent,
    plan_distribution,
)
from rust_compute_cache import RustCompatibilityCacheClient, graph_signature
from stress_test_multiwoz import (
    SOURCE_COMMIT,
    anchor_from_context,
    independently_validate_plan,
    load_corpus,
    make_contexts,
    greedy_edge_baseline,
)

SCHEMA = "context-contract-multiwoz-sensitivity-results.v0.1"


def _number_summary(values: list[float | int | None]) -> dict[str, Any]:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return {"count": 0, "min": None, "median": None, "mean": None, "max": None}
    return {
        "count": len(usable),
        "min": round(min(usable), 4),
        "median": round(median(usable), 4),
        "mean": round(mean(usable), 4),
        "max": round(max(usable), 4),
    }


def _uplift_percent(planner_utility: int, baseline_utility: int) -> float | None:
    if baseline_utility == 0:
        return 0.0 if planner_utility == 0 else None
    return round((planner_utility - baseline_utility) * 100.0 / baseline_utility, 4)


def _measure_policy(
    label: str,
    contexts: list[ContractContext],
    graph: Any,
    anchor: dict[str, str],
    plan: Any,
) -> dict[str, Any]:
    by_id = {context.context_id: context for context in contexts}
    utility = {context.context_id: context.value for context in contexts}
    greedy_ids, greedy_utility = greedy_edge_baseline(graph, utility)
    raw_valid, raw_detail = independently_validate_plan(plan, by_id, anchor)
    selected = set(plan.selected_contexts)
    reconciled_utility = sum(utility[context_id] for context_id in selected)
    planner_score = (plan.total_utility, len(selected))
    greedy_score = (greedy_utility, len(greedy_ids))
    dominates_greedy = planner_score >= greedy_score
    return {
        "policy": label,
        "input_digest_sha256": plan.input_digest,
        "eligible_contexts": graph.number_of_nodes(),
        "compatibility_edges": graph.number_of_edges(),
        "selected_context_count": len(selected),
        "selected_fraction": round(len(selected) / graph.number_of_nodes(), 6)
        if graph.number_of_nodes()
        else 0.0,
        "planner_utility": plan.total_utility,
        "reconciled_selected_utility": reconciled_utility,
        "greedy_baseline_utility": greedy_utility,
        "greedy_baseline_selected_context_count": len(greedy_ids),
        "uplift_vs_greedy_pct": _uplift_percent(plan.total_utility, greedy_utility),
        "raw_plan_valid": raw_valid,
        "raw_validation_detail": raw_detail,
        "utility_reconciles": plan.total_utility == reconciled_utility,
        "planner_dominates_greedy_lexicographically": dominates_greedy,
        "selected_contexts": sorted(selected),
    }


def run_sensitivity_sweep(
    contexts: list[ContractContext],
    provenance: list[dict[str, str]],
    *,
    seed_count: int = 8,
    start_seed: int = 2026,
    anchor_context_count: int = 4,
    rust_cache_client: RustCompatibilityCacheClient | None = None,
) -> dict[str, Any]:
    """Run the same actual corpus against several deterministic anchor samples."""
    if seed_count < 1:
        raise ValueError("seed_count must be at least 1")
    if anchor_context_count < 2:
        raise ValueError("anchor_context_count must be at least 2")
    ids = [context.context_id for context in contexts]
    if len(ids) != len(set(ids)):
        raise ValueError("context IDs must be unique")
    anchor_candidates = [context for context in contexts if len(context.facts) >= 2]
    if len(anchor_candidates) < anchor_context_count:
        raise ValueError("not enough fact-bearing contexts for the requested anchor count")
    if len(contexts) - anchor_context_count < 2:
        raise ValueError("at least two candidate contexts must remain after anchor holdout")

    started = time.time()
    rows: list[dict[str, Any]] = []

    for seed in range(start_seed, start_seed + seed_count):
        rng = random.Random(seed)
        anchor_sources = rng.sample(anchor_candidates, anchor_context_count)
        held_out_ids = {context.context_id for context in anchor_sources}
        pool = [context for context in contexts if context.context_id not in held_out_ids]
        anchor = anchor_from_context(anchor_sources[0], rng)
        if not anchor:
            raise ValueError(f"seed {seed} produced an empty anchor")

        slot_python_started = time.perf_counter()
        python_graph = build_compatibility_graph(pool, anchor)
        slot_python_graph_seconds = time.perf_counter() - slot_python_started
        slot_plan = plan_distribution(pool, anchor, prebuilt_graph=python_graph)
        graph = python_graph
        rust_metrics: dict[str, Any] | None = None
        rust_slot_graph_seconds: float | None = None
        rust_slot_graph_equivalent: bool | None = None
        rust_slot_plan_equivalent: bool | None = None
        request_python_graph_seconds: float | None = None
        rust_request_graph_seconds: float | None = None
        rust_request_graph_equivalent: bool | None = None
        rust_request_plan_equivalent: bool | None = None
        request_cache_metrics: dict[str, Any] | None = None

        if rust_cache_client is not None:
            rust_slot_started = time.perf_counter()
            eligible = [context for context in pool if consistent(context.facts, anchor)]
            rust_graph, rust_metrics = rust_cache_client.build_graph(eligible)
            rust_metrics["elapsed_seconds"] = round(time.perf_counter() - rust_slot_started, 9)
            rust_slot_graph_seconds = rust_metrics["elapsed_seconds"]
            rust_slot_graph_equivalent = (
                graph_signature(rust_graph) == graph_signature(python_graph)
            )
            rust_plan = plan_distribution(pool, anchor, prebuilt_graph=rust_graph)
            rust_slot_plan_equivalent = rust_plan.to_dict() == slot_plan.to_dict()
            if rust_slot_graph_equivalent and rust_slot_plan_equivalent:
                slot_plan = rust_plan

        # This second, explicitly alternative utility gives observed unresolved
        # requested-slot annotations priority. Facts, needs, and graph structure
        # remain identical; only the utility values change.
        request_priority_pool = [
            ContractContext(
                context.context_id,
                context.facts,
                context.needs,
                utility=100 * len(context.needs) + len(context.facts),
            )
            for context in pool
        ]

        request_python_started = time.perf_counter()
        request_python_graph = build_compatibility_graph(request_priority_pool, anchor)
        request_python_graph_seconds = time.perf_counter() - request_python_started
        request_plan = plan_distribution(
            request_priority_pool, anchor, prebuilt_graph=request_python_graph
        )

        if rust_cache_client is not None:
            rust_request_started = time.perf_counter()
            request_eligible = [
                context for context in request_priority_pool
                if consistent(context.facts, anchor)
            ]
            request_rust_graph, request_cache_metrics = rust_cache_client.build_graph(
                request_eligible
            )
            request_cache_metrics["elapsed_seconds"] = round(
                time.perf_counter() - rust_request_started, 9
            )
            rust_request_graph_seconds = request_cache_metrics["elapsed_seconds"]
            rust_request_graph_equivalent = (
                graph_signature(request_rust_graph) == graph_signature(request_python_graph)
            )
            request_rust_plan = plan_distribution(
                request_priority_pool, anchor, prebuilt_graph=request_rust_graph
            )
            rust_request_plan_equivalent = (
                request_rust_plan.to_dict() == request_plan.to_dict()
            )
            if rust_request_graph_equivalent and rust_request_plan_equivalent:
                request_plan = request_rust_plan

        slot_metrics = _measure_policy("populated-slot-count", pool, graph, anchor, slot_plan)
        request_metrics = _measure_policy(
            "requested-slot-priority",
            request_priority_pool,
            request_python_graph,
            anchor,
            request_plan,
        )
        checks = {
            "slot_policy_raw_plan_valid": slot_metrics["raw_plan_valid"],
            "slot_policy_utility_reconciles": slot_metrics["utility_reconciles"],
            "slot_policy_dominates_greedy": slot_metrics["planner_dominates_greedy_lexicographically"],
            "request_policy_raw_plan_valid": request_metrics["raw_plan_valid"],
            "request_policy_utility_reconciles": request_metrics["utility_reconciles"],
            "request_policy_dominates_greedy": request_metrics["planner_dominates_greedy_lexicographically"],
        }
        if rust_cache_client is not None:
            checks.update({
                "rust_slot_graph_matches_python": bool(rust_slot_graph_equivalent),
                "rust_slot_plan_matches_python": bool(rust_slot_plan_equivalent),
                "rust_request_graph_matches_python": bool(rust_request_graph_equivalent),
                "rust_request_plan_matches_python": bool(rust_request_plan_equivalent),
                "utility_only_change_reuses_graph_cache": (
                    request_cache_metrics is not None
                    and request_cache_metrics["graph_cache_hit"] is True
                ),
            })
        rows.append({
            "seed": seed,
            "anchor_source_dialogue_id": anchor_sources[0].context_id,
            "held_out_anchor_context_ids": sorted(held_out_ids),
            "anchor_facts": dict(sorted(anchor.items())),
            "candidate_contexts": len(pool),
            "slot_count_policy": slot_metrics,
            "request_priority_policy": request_metrics,
            "rust_compute_cache": (
                {
                    "slot_policy": {
                        "python_graph_seconds": round(slot_python_graph_seconds, 9),
                        "rust_graph_seconds": rust_slot_graph_seconds,
                        "graph_equivalent": rust_slot_graph_equivalent,
                        "plan_equivalent": rust_slot_plan_equivalent,
                        "cache": rust_metrics,
                    },
                    "request_policy": {
                        "python_graph_seconds": round(request_python_graph_seconds, 9),
                        "rust_graph_seconds": rust_request_graph_seconds,
                        "graph_equivalent": rust_request_graph_equivalent,
                        "plan_equivalent": rust_request_plan_equivalent,
                        "cache": request_cache_metrics,
                    },
                }
                if rust_cache_client is not None else None
            ),
            "selected_set_changed_under_alternative_utility": (
                set(slot_plan.selected_contexts) != set(request_plan.selected_contexts)
            ),
            "checks": checks,
            "passed": all(checks.values()),
        })

    slot_rows = [row["slot_count_policy"] for row in rows]
    request_rows = [row["request_priority_policy"] for row in rows]
    check_count = sum(len(row["checks"]) for row in rows)
    check_passed = sum(
        1 for row in rows for passed in row["checks"].values() if passed
    )
    return {
        "schema": SCHEMA,
        "source_repository": "https://github.com/budzianowski/multiwoz",
        "source_commit": SOURCE_COMMIT,
        "dataset_provenance": provenance,
        "method": {
            "seed_count": seed_count,
            "seed_values": list(range(start_seed, start_seed + seed_count)),
            "anchor_contexts_held_out_per_seed": anchor_context_count,
            "anchor_facts_per_run": "up to three facts sampled from one held-out real dialogue",
            "slot_count_utility": "number of distinct populated annotated belief-state slots",
            "request_priority_utility": "100 * count of unresolved annotated requested-slot keys + populated slot count",
            "baseline": "deterministic greedy edge-pair selection ordered by endpoint utility sum",
            "comparison": "planner and greedy baseline are evaluated on the same compatibility graph for each policy",
        },
        "summary": {
            "seed_count": len(rows),
            "all_seed_runs_passed": all(row["passed"] for row in rows),
            "rust_compute_cache_enabled": rust_cache_client is not None,
            "rust_slot_graph_seconds": _number_summary([
                row["rust_compute_cache"]["slot_policy"]["rust_graph_seconds"]
                for row in rows if row["rust_compute_cache"] is not None
            ]),
            "python_slot_graph_seconds": _number_summary([
                row["rust_compute_cache"]["slot_policy"]["python_graph_seconds"]
                for row in rows if row["rust_compute_cache"] is not None
            ]),
            "rust_request_graph_seconds": _number_summary([
                row["rust_compute_cache"]["request_policy"]["rust_graph_seconds"]
                for row in rows if row["rust_compute_cache"] is not None
            ]),
            "python_request_graph_seconds": _number_summary([
                row["rust_compute_cache"]["request_policy"]["python_graph_seconds"]
                for row in rows if row["rust_compute_cache"] is not None
            ]),
            "rust_cache_total": (
                rust_cache_client.stats() if rust_cache_client is not None else None
            ),
            "slot_count_uplift_vs_greedy_pct": _number_summary([
                row["uplift_vs_greedy_pct"] for row in slot_rows
            ]),
            "request_priority_uplift_vs_greedy_pct": _number_summary([
                row["uplift_vs_greedy_pct"] for row in request_rows
            ]),
            "slot_count_selected_fraction": _number_summary([
                row["selected_fraction"] for row in slot_rows
            ]),
            "request_priority_selected_fraction": _number_summary([
                row["selected_fraction"] for row in request_rows
            ]),
            "eligible_context_count": _number_summary([
                row["eligible_contexts"] for row in slot_rows
            ]),
            "compatibility_edge_count": _number_summary([
                row["compatibility_edges"] for row in slot_rows
            ]),
            "seeds_with_different_selected_sets_under_alternative_utility": sum(
                row["selected_set_changed_under_alternative_utility"] for row in rows
            ),
            "checks_passed": check_passed,
            "checks_total": check_count,
        },
        "runs": rows,
        "runtime_seconds": round(time.time() - started, 3),
        "interpretation_boundary": (
            "This sweep reuses one immutable MultiWOZ 2.2 test split and varies deterministic "
            "anchor-source samples. It is a sensitivity analysis, not an independent dataset "
            "replication, confidence interval, production workload measurement, or validation "
            "of business/legal-contract semantics. Utility policies are proxies, not ground truth. "
            "Uplift is relative to a deterministic greedy baseline and must not be generalized "
            "beyond the recorded corpus conversion, seeds, anchors, and policies."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(tempfile.gettempdir()) / "multiwoz-v22-pinned",
    )
    parser.add_argument("--limit", type=int, default=0, help="optional prefix limit for smoke testing")
    parser.add_argument("--seed-count", type=int, default=8)
    parser.add_argument("--start-seed", type=int, default=2026)
    parser.add_argument("--anchor-context-count", type=int, default=4)
    parser.add_argument(
        "--rust-cache",
        action="store_true",
        help="use and verify the Rust pair-compatibility computation cache",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("MULTIWOZ-SENSITIVITY-RESULTS.json"),
    )
    args = parser.parse_args()
    if args.limit < 0 or args.seed_count < 1 or args.anchor_context_count < 2:
        parser.error("--limit must be >= 0, --seed-count >= 1, and --anchor-context-count >= 2")

    dialogues, provenance = load_corpus(args.cache_dir)
    contexts = make_contexts(dialogues)
    if args.limit:
        contexts = contexts[:args.limit]
    try:
        if args.rust_cache:
            with RustCompatibilityCacheClient() as rust_cache:
                result = run_sensitivity_sweep(
                    contexts,
                    provenance,
                    seed_count=args.seed_count,
                    start_seed=args.start_seed,
                    anchor_context_count=args.anchor_context_count,
                    rust_cache_client=rust_cache,
                )
        else:
            result = run_sensitivity_sweep(
                contexts,
                provenance,
                seed_count=args.seed_count,
                start_seed=args.start_seed,
                anchor_context_count=args.anchor_context_count,
            )
    except ValueError as exc:
        parser.error(str(exc))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = result["summary"]
    print("== MultiWOZ anchor and utility sensitivity ==")
    print(f"seeds: {summary['seed_count']}; checks: {summary['checks_passed']}/{summary['checks_total']}")
    print(f"slot-count uplift vs greedy (%): {summary['slot_count_uplift_vs_greedy_pct']}")
    print(f"request-priority uplift vs greedy (%): {summary['request_priority_uplift_vs_greedy_pct']}")
    print(
        "selected sets changed under alternative utility: "
        f"{summary['seeds_with_different_selected_sets_under_alternative_utility']}/{summary['seed_count']}"
    )
    print(f"result artifact: {args.output}")
    if not summary["all_seed_runs_passed"]:
        print(json.dumps([
            {"seed": row["seed"], "checks": row["checks"]}
            for row in result["runs"] if not row["passed"]
        ], sort_keys=True), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
