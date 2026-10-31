#!/usr/bin/env python3
"""Compare separate Python and Rust end-to-end planner request paths."""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import tempfile
import time
from pathlib import Path
from statistics import mean, median
from typing import Any

from context_contract_distribution import (
    ContractContext,
    consistent,
    plan_distribution,
)
from rust_compute_cache import RustCompatibilityCacheClient, graph_signature
from stress_test_multiwoz import (
    SEED,
    SOURCE_COMMIT,
    anchor_from_context,
    load_corpus,
    make_contexts,
)
from context_contract_distribution import build_compatibility_graph


SCHEMA = "context-contract-multiwoz-end-to-end-cache-benchmark.v0.1"


def _utility_variant(
    contexts: list[ContractContext],
    variant: int,
) -> list[ContractContext]:
    """Change scores only; IDs, facts, needs, and graph identity remain fixed."""
    fact_weight = variant + 1
    request_weight = 100 + (variant % 3) * 10
    return [
        ContractContext(
            item.context_id,
            item.facts,
            item.needs,
            utility=request_weight * len(item.needs) + fact_weight * len(item.facts),
        )
        for item in contexts
    ]


def _summary(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    p95_index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return {
        "count": len(values),
        "min_seconds": round(min(values), 6),
        "median_seconds": round(median(values), 6),
        "mean_seconds": round(mean(values), 6),
        "p95_seconds": round(ordered[p95_index], 6),
        "max_seconds": round(max(values), 6),
    }


def run_benchmark(
    dialogues: list[dict[str, Any]],
    *,
    repetitions: int = 7,
    seed: int = SEED,
) -> dict[str, Any]:
    if repetitions < 3:
        raise ValueError("at least three repetitions are required")

    rng = random.Random(seed)
    contexts = make_contexts(dialogues)
    anchor_sources = [context for context in contexts if len(context.facts) >= 2]
    if len(anchor_sources) < 4:
        raise ValueError("at least four fact-bearing dialogues are required")
    held_out = rng.sample(anchor_sources, 4)
    held_out_ids = {context.context_id for context in held_out}
    pool = [context for context in contexts if context.context_id not in held_out_ids]
    anchor = anchor_from_context(held_out[0], rng)
    if not anchor:
        raise ValueError("benchmark anchor is empty")

    eligible = [
        context for context in pool if consistent(context.facts, anchor)
    ]
    if len(eligible) < 20:
        raise ValueError("fewer than 20 contexts remain eligible under the sampled anchor")

    variants = [_utility_variant(pool, index) for index in range(repetitions)]
    eligible_variants = [
        [context for context in variant if consistent(context.facts, anchor)]
        for variant in variants
    ]

    # Cold Python request: full reference planner builds the graph and matches.
    cold_python_started = time.perf_counter()
    cold_python_plan = plan_distribution(variants[0], anchor)
    cold_python_seconds = time.perf_counter() - cold_python_started

    # Cold Rust request: process startup is recorded separately from request latency.
    rust_startup_started = time.perf_counter()
    cold_client = RustCompatibilityCacheClient()
    rust_process_startup_seconds = time.perf_counter() - rust_startup_started
    try:
        cold_request_started = time.perf_counter()
        cold_graph, cold_metrics = cold_client.build_graph(eligible_variants[0])
        cold_rust_plan = plan_distribution(
            variants[0], anchor, prebuilt_graph=cold_graph
        )
        cold_rust_seconds = time.perf_counter() - cold_request_started
        cold_graph_matches = (
            graph_signature(cold_graph)
            == graph_signature(build_compatibility_graph(variants[0], anchor))
        )
        cold_plan_matches = cold_rust_plan.to_dict() == cold_python_plan.to_dict()
        cold_metrics_after = cold_client.stats()
    finally:
        cold_client.close()

    # Timed reference requests are run independently: each performs the complete
    # Python graph construction and exact matching without involving the Rust path.
    python_seconds: list[float] = []
    python_plans = []
    python_started = time.perf_counter()
    for variant in variants:
        request_started = time.perf_counter()
        python_plans.append(plan_distribution(variant, anchor))
        python_seconds.append(time.perf_counter() - request_started)
    python_total_seconds = time.perf_counter() - python_started

    # The Rust service remains alive across requests. One warm-up populates the
    # whole-graph entry; timed requests then use Rust cache + Python matching.
    rust_seconds: list[float] = []
    rust_graph_seconds: list[float] = []
    rust_matching_seconds: list[float] = []
    rust_graph_hits: list[bool] = []
    rust_plans = []
    rust_total_started = time.perf_counter()
    with RustCompatibilityCacheClient() as warm_client:
        warm_client.build_graph(eligible_variants[0])
        for index, variant in enumerate(variants):
            request_started = time.perf_counter()
            graph, metrics = warm_client.build_graph(eligible_variants[index])
            graph_seconds = time.perf_counter() - request_started
            matching_started = time.perf_counter()
            plan = plan_distribution(variant, anchor, prebuilt_graph=graph)
            matching_seconds = time.perf_counter() - matching_started
            total_seconds = time.perf_counter() - request_started
            rust_plans.append(plan)
            rust_seconds.append(total_seconds)
            rust_graph_seconds.append(graph_seconds)
            rust_matching_seconds.append(matching_seconds)
            rust_graph_hits.append(bool(metrics["graph_cache_hit"]))
        rust_metrics = warm_client.stats()
    rust_total_seconds = time.perf_counter() - rust_total_started

    # Check representative full outputs outside the timed request path. The timed
    # paths above do not run both implementations for the same request.
    parity_indices = sorted({0, repetitions // 2, repetitions - 1})
    parity_checks = {
        str(index): rust_plans[index].to_dict() == python_plans[index].to_dict()
        for index in parity_indices
    }

    python_summary = _summary(python_seconds)
    rust_summary = _summary(rust_seconds)
    ratio = (
        python_summary["median_seconds"] / rust_summary["median_seconds"]
        if rust_summary["median_seconds"] > 0
        else None
    )

    checks = {
        "cold_graph_matches_python": cold_graph_matches,
        "cold_plan_matches_python": cold_plan_matches,
        "representative_warm_plans_match_python": all(parity_checks.values()),
        "all_timed_warm_requests_hit_graph_cache": all(rust_graph_hits),
        "python_timed_request_count_correct": len(python_seconds) == repetitions,
        "rust_timed_request_count_correct": len(rust_seconds) == repetitions,
    }

    return {
        "schema": SCHEMA,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "source": {
            "repository": "budzianowski/multiwoz",
            "commit": SOURCE_COMMIT,
            "dataset": "MultiWOZ 2.2 test split",
            "dialogues_loaded": len(dialogues),
            "registered_contexts": len(pool),
            "eligible_contexts": len(eligible),
            "compatibility_edge_count_python": build_compatibility_graph(pool, anchor).number_of_edges(),
            "held_out_anchor_ids": [context.context_id for context in held_out],
            "anchor_fact_count": len(anchor),
        },
        "design": {
            "repetitions": repetitions,
            "utility_changes_between_requests": True,
            "graph_identity_changes_between_requests": False,
            "timing_paths_are_separate": True,
            "python_timed_path": "plan_distribution: Python graph construction + exact NetworkX matching",
            "rust_timed_path": "Rust whole-graph cache request + NetworkX graph reconstruction + prebuilt-graph validation + exact NetworkX matching",
            "reference_parity_execution": "cold request plus representative warm plans only; parity work is outside timed intervals",
            "rust_process_startup_is_separate": True,
        },
        "cold_request": {
            "python_end_to_end_seconds": round(cold_python_seconds, 9),
            "rust_process_startup_seconds": round(rust_process_startup_seconds, 9),
            "rust_end_to_end_seconds_excluding_process_startup": round(cold_rust_seconds, 9),
            "rust_graph_cache_hit": bool(cold_metrics["graph_cache_hit"]),
            "rust_pair_cache_hits": cold_metrics["cache_hits"],
            "rust_pair_cache_misses": cold_metrics["cache_misses"],
            "cold_graph_matches_python": cold_graph_matches,
            "cold_plan_matches_python": cold_plan_matches,
            "cache_metrics_after_request": cold_metrics_after,
        },
        "warm_repeated_requests": {
            "python_end_to_end": python_summary,
            "rust_end_to_end": rust_summary,
            "rust_graph_request": _summary(rust_graph_seconds),
            "rust_matching_and_prebuilt_validation": _summary(rust_matching_seconds),
            "python_total_seconds": round(python_total_seconds, 9),
            "rust_total_seconds_including_one_warmup": round(rust_total_seconds, 9),
            "median_python_over_rust_ratio": round(ratio, 4) if ratio is not None else None,
            "rust_whole_graph_hits": sum(rust_graph_hits),
            "rust_whole_graph_requests": len(rust_graph_hits),
            "cache_metrics_after_requests": rust_metrics,
        },
        "parity": {
            "representative_indices": parity_indices,
            "plans_match": parity_checks,
        },
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "interpretation_boundary": (
            "This is an end-to-end planner microbenchmark on one pinned actual dialogue corpus. "
            "Python is the matching engine in both paths. The Rust process is kept alive across "
            "warm requests; process startup is measured separately. Warm and cold paths are "
            "reported separately. Timing excludes the parity work, which is performed outside "
            "the timed paths. This is not a production SLA or independent dataset replication."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(tempfile.gettempdir()) / "multiwoz-v22-pinned",
    )
    parser.add_argument("--repetitions", type=int, default=7)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("MULTIWOZ-END-TO-END-CACHE-RESULTS.json"),
    )
    args = parser.parse_args()
    if args.repetitions < 3:
        parser.error("--repetitions must be at least 3")

    dialogues, _ = load_corpus(args.cache_dir)
    result = run_benchmark(dialogues, repetitions=args.repetitions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "checks_passed": result["checks_passed"],
        "checks_total": result["checks_total"],
        "python_median_seconds": result["warm_repeated_requests"]["python_end_to_end"]["median_seconds"],
        "rust_median_seconds": result["warm_repeated_requests"]["rust_end_to_end"]["median_seconds"],
        "median_python_over_rust_ratio": result["warm_repeated_requests"]["median_python_over_rust_ratio"],
        "rust_whole_graph_hits": result["warm_repeated_requests"]["rust_whole_graph_hits"],
        "cold_python_seconds": result["cold_request"]["python_end_to_end_seconds"],
        "cold_rust_seconds": result["cold_request"]["rust_end_to_end_seconds_excluding_process_startup"],
        "output": str(args.output),
    }, ensure_ascii=False, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
