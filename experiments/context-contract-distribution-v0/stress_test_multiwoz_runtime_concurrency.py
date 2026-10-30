#!/usr/bin/env python3
"""Test concurrent cache clients, process-local restart behavior, and child RSS."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
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
    SEED,
    SOURCE_COMMIT,
    anchor_from_context,
    load_corpus,
    make_contexts,
)


SCHEMA = "context-contract-multiwoz-runtime-concurrency.v0.1"


def _percentile95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[max(0, min(len(ordered) - 1, int(len(ordered) * 0.95 + 0.999999) - 1))]


def _summary(values: list[float]) -> dict[str, float | int]:
    return {
        "count": len(values),
        "min_seconds": round(min(values), 6),
        "median_seconds": round(median(values), 6),
        "mean_seconds": round(mean(values), 6),
        "p95_seconds": round(_percentile95(values), 6),
        "max_seconds": round(max(values), 6),
    }


def _sample_contexts(
    contexts: list[ContractContext],
    *,
    seed: int,
    subset_size: int,
) -> tuple[list[ContractContext], dict[str, Any]]:
    rng = random.Random(seed)
    anchor_candidates = [context for context in contexts if len(context.facts) >= 2]
    if len(anchor_candidates) < 4:
        raise ValueError("at least four fact-bearing contexts are required")
    held_out = rng.sample(anchor_candidates, 4)
    held_out_ids = {context.context_id for context in held_out}
    candidates = [
        context for context in contexts if context.context_id not in held_out_ids
    ]
    anchor = anchor_from_context(held_out[0], rng)
    eligible = [
        context for context in candidates if consistent(context.facts, anchor)
    ]
    if len(eligible) < subset_size:
        raise ValueError(
            f"only {len(eligible)} anchor-eligible contexts; need {subset_size}"
        )
    selected = sorted(
        rng.sample(eligible, subset_size),
        key=lambda item: item.context_id,
    )
    provenance = {
        "seed": seed,
        "anchor_source_ids": [context.context_id for context in held_out],
        "registered_candidates": len(candidates),
        "anchor_eligible_contexts": len(eligible),
        "sampled_contexts": len(selected),
        "anchor_fact_count": len(anchor),
    }
    return selected, {"anchor": anchor, "provenance": provenance}


def run_runtime_stress(
    dialogues: list[dict[str, Any]],
    *,
    seed: int = SEED,
    subset_size: int = 160,
    concurrent_requests: int = 64,
    worker_count: int = 8,
    independent_processes: int = 4,
) -> dict[str, Any]:
    if subset_size < 20:
        raise ValueError("subset_size must be at least 20")
    if concurrent_requests < worker_count:
        raise ValueError("concurrent_requests must be at least worker_count")
    if worker_count < 2:
        raise ValueError("worker_count must be at least 2")
    if independent_processes < 2:
        raise ValueError("independent_processes must be at least 2")

    contexts = make_contexts(dialogues)
    base, sample_metadata = _sample_contexts(
        contexts, seed=seed, subset_size=subset_size
    )
    anchor = sample_metadata["anchor"]
    variants = [
        [
            ContractContext(
                item.context_id,
                item.facts,
                item.needs,
                utility=item.value + offset,
            )
            for item in base
        ]
        for offset in (0, 3, 11, 29)
    ]

    python_reference = build_compatibility_graph(base, anchor)
    reference_signatures = [
        graph_signature(python_reference)
    ] * len(variants)
    expected_pair_lookups = len(base) * (len(base) - 1) // 2

    # Multiple Python threads share one JSON-lines client. The adapter must
    # serialize request/response I/O atomically; Moka work in this process is
    # therefore sequential, while Python graph reconstruction may overlap.
    request_latencies: list[float] = []
    request_results: list[dict[str, Any]] = []
    with RustCompatibilityCacheClient() as client:
        memory_before = client.process_memory_bytes()

        def invoke(index: int) -> tuple[int, list[dict[str, Any]], dict[str, Any], float]:
            variant_index = index % len(variants)
            started = time.perf_counter()
            graph, metrics = client.build_graph(variants[variant_index])
            elapsed = time.perf_counter() - started
            return index, graph_signature(graph), metrics, elapsed

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            concurrent_results = list(
                executor.map(invoke, range(concurrent_requests))
            )

        memory_after = client.process_memory_bytes()
        shared_stats = client.stats()

    concurrent_results.sort(key=lambda item: item[0])
    request_latencies = [item[3] for item in concurrent_results]
    request_results = [
        {
            "index": index,
            "variant": index % len(variants),
            "graph_matches_reference": signature == reference_signatures[index % len(variants)],
            "graph_cache_hit": bool(metrics["graph_cache_hit"]),
            "pair_cache_hits": metrics["cache_hits"],
            "pair_cache_misses": metrics["cache_misses"],
        }
        for index, signature, metrics, _ in concurrent_results
    ]

    # Start independent Rust processes concurrently. Each should begin cold:
    # the cache is process-local, not shared between workers.
    small_base = base[: min(80, len(base))]
    small_expected_pairs = len(small_base) * (len(small_base) - 1) // 2
    small_python_graph = build_compatibility_graph(small_base, anchor)
    small_expected_signature = graph_signature(small_python_graph)

    def independent_worker(worker_index: int) -> dict[str, Any]:
        before = time.perf_counter()
        with RustCompatibilityCacheClient() as client:
            startup = time.perf_counter() - before
            memory_before_request = client.process_memory_bytes()
            request_started = time.perf_counter()
            graph, metrics = client.build_graph(small_base)
            request_seconds = time.perf_counter() - request_started
            memory_after_request = client.process_memory_bytes()
            return {
                "worker": worker_index,
                "pid": client.process.pid,
                "startup_seconds": round(startup, 9),
                "request_seconds": round(request_seconds, 9),
                "graph_matches_python": graph_signature(graph) == small_expected_signature,
                "initial_graph_cache_hit": bool(metrics["graph_cache_hit"]),
                "initial_pair_lookups": metrics["pair_lookups"],
                "initial_pair_misses": metrics["cache_misses"],
                "rss_before_bytes": (
                    memory_before_request.get("vmrss_bytes")
                    if memory_before_request else None
                ),
                "rss_after_bytes": (
                    memory_after_request.get("vmrss_bytes")
                    if memory_after_request else None
                ),
                "rss_hwm_after_bytes": (
                    memory_after_request.get("vmhwm_bytes")
                    if memory_after_request else None
                ),
            }

    independent_started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=independent_processes) as executor:
        process_results = list(
            executor.map(independent_worker, range(independent_processes))
        )
    independent_wall_seconds = time.perf_counter() - independent_started

    shared_checks = {
        "all_concurrent_graphs_match_python": all(
            row["graph_matches_reference"] for row in request_results
        ),
        "exactly_one_initial_graph_miss": shared_stats["graph_cache_misses"] == 1,
        "all_other_concurrent_requests_hit_graph_cache": (
            shared_stats["graph_cache_hits"] == concurrent_requests - 1
        ),
        "no_pair_recomputation_after_initial_population": (
            shared_stats["cache_misses"] == expected_pair_lookups
        ),
    }
    process_checks = {
        "all_independent_graphs_match_python": all(
            row["graph_matches_python"] for row in process_results
        ),
        "each_process_starts_with_cold_graph_cache": all(
            not row["initial_graph_cache_hit"] for row in process_results
        ),
        "each_process_computes_its_own_pair_set": all(
            row["initial_pair_lookups"] == small_expected_pairs
            and row["initial_pair_misses"] == small_expected_pairs
            for row in process_results
        ),
        "worker_pids_are_distinct": (
            len({row["pid"] for row in process_results}) == independent_processes
        ),
    }
    checks = {**shared_checks, **process_checks}

    return {
        "schema": SCHEMA,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "source": {
            "repository": "budzianowski/multiwoz",
            "commit": SOURCE_COMMIT,
            "dataset": "MultiWOZ 2.2 test split",
            "dialogues_loaded": len(dialogues),
            **sample_metadata["provenance"],
        },
        "shared_client_concurrency": {
            "python_worker_count": worker_count,
            "requests": concurrent_requests,
            "request_latency": _summary(request_latencies),
            "request_protocol": (
                "thread-safe serialized JSON-lines request/response; "
                "one Rust process executes one request at a time"
            ),
            "rss_before_bytes": (
                memory_before.get("vmrss_bytes") if memory_before else None
            ),
            "rss_after_bytes": (
                memory_after.get("vmrss_bytes") if memory_after else None
            ),
            "rss_hwm_after_bytes": (
                memory_after.get("vmhwm_bytes") if memory_after else None
            ),
            "rss_delta_bytes": (
                memory_after.get("vmrss_bytes", 0) - memory_before.get("vmrss_bytes", 0)
                if memory_before and memory_after else None
            ),
            "cache_metrics": shared_stats,
            "request_results": request_results,
        },
        "independent_process_concurrency": {
            "process_count": independent_processes,
            "parallel_wall_seconds": round(independent_wall_seconds, 9),
            "per_process": process_results,
            "interpretation": (
                "Each process has an isolated, initially cold cache. This verifies "
                "parallel process correctness and confirms that cache entries are "
                "not shared across processes."
            ),
        },
        "checks": checks,
        "checks_passed": sum(bool(value) for value in checks.values()),
        "checks_total": len(checks),
        "interpretation_boundary": (
            "Concurrency on one client is protocol-safe but serializes Rust requests; "
            "separate client processes execute independently and do not share cache "
            "state. RSS is sampled from Linux /proc and is observational, not a hard "
            "memory limit. This is a pinned MultiWOZ service-proxy workload, not a "
            "production concurrency or memory SLA."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(tempfile.gettempdir()) / "multiwoz-v22-pinned",
    )
    parser.add_argument("--subset-size", type=int, default=160)
    parser.add_argument("--concurrent-requests", type=int, default=64)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--independent-processes", type=int, default=4)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("MULTIWOZ-RUNTIME-CONCURRENCY-RESULTS.json"),
    )
    args = parser.parse_args()

    dialogues, _ = load_corpus(args.cache_dir)
    result = run_runtime_stress(
        dialogues,
        subset_size=args.subset_size,
        concurrent_requests=args.concurrent_requests,
        worker_count=args.workers,
        independent_processes=args.independent_processes,
    )
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
        "shared_requests": result["shared_client_concurrency"]["requests"],
        "shared_worker_count": result["shared_client_concurrency"]["python_worker_count"],
        "shared_cache_hits": result["shared_client_concurrency"]["cache_metrics"]["graph_cache_hits"],
        "shared_rss_delta_bytes": result["shared_client_concurrency"]["rss_delta_bytes"],
        "independent_processes": result["independent_process_concurrency"]["process_count"],
        "independent_parallel_wall_seconds": result["independent_process_concurrency"]["parallel_wall_seconds"],
        "output": str(args.output),
    }, ensure_ascii=False, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
