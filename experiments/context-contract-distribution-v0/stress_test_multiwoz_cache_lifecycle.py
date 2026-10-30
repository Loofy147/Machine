#!/usr/bin/env python3
"""Exercise Rust cache correctness under a deterministic changing-context trace."""
from __future__ import annotations

import argparse
import json
import random
import sys
import tempfile
import time
from pathlib import Path
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


SCHEMA = "context-contract-multiwoz-cache-lifecycle.v0.1"


def _replace_context(
    context: ContractContext,
    *,
    facts: dict[str, Any] | None = None,
    needs: dict[str, Any] | None = None,
    utility: int | None = None,
) -> ContractContext:
    return ContractContext(
        context.context_id,
        dict(context.facts) if facts is None else facts,
        dict(context.needs) if needs is None else needs,
        utility=context.value if utility is None else utility,
    )


def _make_workloads(
    contexts: list[ContractContext],
    seed: int,
    base_size: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rng = random.Random(seed)
    anchor_sources = [context for context in contexts if len(context.facts) >= 2]
    if len(anchor_sources) < 4:
        raise ValueError("at least four fact-bearing dialogues are required")
    held_out = rng.sample(anchor_sources, 4)
    held_out_ids = {context.context_id for context in held_out}
    candidates = [context for context in contexts if context.context_id not in held_out_ids]

    anchor_a = anchor_from_context(held_out[0], rng)
    anchor_b = anchor_from_context(held_out[1], rng)
    eligible_a = [
        context for context in candidates if consistent(context.facts, anchor_a)
    ]
    if len(eligible_a) < base_size + 24:
        raise ValueError(
            f"not enough anchor-eligible contexts: {len(eligible_a)}; "
            f"need at least {base_size + 24}"
        )

    sampled = rng.sample(eligible_a, base_size + 24)
    base = sorted(sampled[:base_size], key=lambda item: item.context_id)
    extras = sorted(sampled[base_size:], key=lambda item: item.context_id)
    base_ids = {context.context_id for context in base}
    eligible_need = next(
        (context for context in base if context.needs),
        base[0],
    )
    eligible_fact = next(
        (context for context in base if context.facts),
        base[0],
    )

    fact_mutation = dict(eligible_fact.facts)
    fact_mutation["__cache_probe_fact__"] = f"mutation-{seed}"
    mutated_fact_context = _replace_context(eligible_fact, facts=fact_mutation)

    need_mutation = dict(eligible_need.needs)
    need_mutation["__cache_probe_need__"] = None
    mutated_need_context = _replace_context(eligible_need, needs=need_mutation)

    multi_mutated = list(base)
    for index, original in enumerate(base[:3]):
        changed_facts = dict(original.facts)
        changed_facts[f"__cache_probe_fact_{index}__"] = f"mutation-{seed}-{index}"
        multi_mutated[index] = _replace_context(original, facts=changed_facts)

    with_fact_mutation = [
        mutated_fact_context if item.context_id == eligible_fact.context_id else item
        for item in base
    ]
    with_need_mutation = [
        mutated_need_context if item.context_id == eligible_need.context_id else item
        for item in base
    ]

    workloads = [
        {
            "label": "base",
            "contexts": base,
            "anchor": anchor_a,
            "expect_graph_hit": False,
            "expect_graph_miss": True,
        },
        {
            "label": "utility_only_change",
            "contexts": [
                _replace_context(item, utility=item.value + 17) for item in base
            ],
            "anchor": anchor_a,
            "expect_graph_hit": True,
        },
        {
            "label": "alternate_anchor",
            "contexts": base,
            "anchor": anchor_b,
        },
        {
            "label": "add_8_contexts",
            "contexts": sorted(base + extras[:8], key=lambda item: item.context_id),
            "anchor": anchor_a,
            "expect_graph_miss": True,
        },
        {
            "label": "remove_8_contexts",
            "contexts": base[:-8],
            "anchor": anchor_a,
            "expect_graph_miss": True,
        },
        {
            "label": "replace_8_contexts",
            "contexts": sorted(base[:-8] + extras[8:16], key=lambda item: item.context_id),
            "anchor": anchor_a,
            "expect_graph_miss": True,
        },
        {
            "label": "mutate_one_fact",
            "contexts": with_fact_mutation,
            "anchor": anchor_a,
            "expect_graph_miss": True,
            "expect_pair_reuse_and_recompute": True,
        },
        {
            "label": "mutate_one_need",
            "contexts": with_need_mutation,
            "anchor": anchor_a,
            "expect_graph_miss": True,
            "expect_pair_reuse_and_recompute": True,
        },
        {
            "label": "mutate_three_contexts",
            "contexts": multi_mutated,
            "anchor": anchor_a,
            "expect_graph_miss": True,
            "expect_pair_reuse_and_recompute": True,
        },
        {
            "label": "restore_base",
            "contexts": base,
            "anchor": anchor_a,
            "expect_graph_hit": True,
        },
        {
            "label": "repeat_base_new_utility",
            "contexts": [
                _replace_context(item, utility=item.value + 101) for item in base
            ],
            "anchor": anchor_a,
            "expect_graph_hit": True,
        },
        {
            "label": "add_then_remove_different_members",
            "contexts": sorted(base[8:] + extras[:8], key=lambda item: item.context_id),
            "anchor": anchor_a,
            "expect_graph_miss": True,
        },
    ]

    for workload in workloads:
        current_ids = [context.context_id for context in workload["contexts"]]
        if len(current_ids) != len(set(current_ids)):
            raise ValueError(f"workload {workload['label']} contains duplicate IDs")

    provenance = {
        "seed": seed,
        "anchor_source_ids": [context.context_id for context in held_out],
        "candidate_context_count": len(candidates),
        "base_context_count": len(base),
        "extra_context_count": len(extras),
        "eligible_fact_mutation_context_id": eligible_fact.context_id,
        "eligible_need_mutation_context_id": eligible_need.context_id,
        "unused_sampled_base_ids": sorted(base_ids - {context.context_id for context in base}),
    }
    return workloads, provenance


def run_lifecycle(
    contexts: list[ContractContext],
    *,
    seed: int = SEED,
    base_size: int = 180,
) -> dict[str, Any]:
    workloads, provenance = _make_workloads(contexts, seed, base_size)
    rows: list[dict[str, Any]] = []

    with RustCompatibilityCacheClient() as cache:
        for workload in workloads:
            started = time.perf_counter()
            snapshot = workload["contexts"]
            anchor = workload["anchor"]
            eligible = [
                context for context in snapshot if consistent(context.facts, anchor)
            ]
            rust_graph, metrics = cache.build_graph(eligible)
            rust_graph_seconds = time.perf_counter() - started

            python_graph = build_compatibility_graph(snapshot, anchor)
            graph_matches = graph_signature(rust_graph) == graph_signature(python_graph)
            python_plan = plan_distribution(snapshot, anchor, prebuilt_graph=python_graph)
            rust_plan = plan_distribution(snapshot, anchor, prebuilt_graph=rust_graph)
            plan_matches = rust_plan.to_dict() == python_plan.to_dict()

            checks = {
                "graph_matches_python": graph_matches,
                "plan_matches_python": plan_matches,
            }
            if workload.get("expect_graph_hit"):
                checks["expected_graph_hit"] = bool(metrics["graph_cache_hit"])
            if workload.get("expect_graph_miss"):
                checks["expected_graph_miss"] = not metrics["graph_cache_hit"]
            if workload.get("expect_pair_reuse_and_recompute"):
                checks["unchanged_pairs_reused"] = metrics["cache_hits"] > 0
                checks["changed_pairs_recomputed"] = metrics["cache_misses"] > 0

            rows.append({
                "label": workload["label"],
                "registered_contexts": len(snapshot),
                "eligible_contexts": len(eligible),
                "edges": rust_graph.number_of_edges(),
                "utility_total": rust_plan.total_utility,
                "graph_cache_hit": bool(metrics["graph_cache_hit"]),
                "pair_cache_hits": metrics["cache_hits"],
                "pair_cache_misses": metrics["cache_misses"],
                "pair_cache_hit_rate": metrics["hit_rate"],
                "rust_graph_path_seconds": round(rust_graph_seconds, 9),
                "python_graph_equivalent": graph_matches,
                "python_plan_equivalent": plan_matches,
                "checks": checks,
                "passed": all(checks.values()),
            })

        total = cache.stats()

    checks_passed = sum(
        sum(bool(value) for value in row["checks"].values()) for row in rows
    )
    checks_total = sum(len(row["checks"]) for row in rows)
    return {
        "schema": SCHEMA,
        "status": "PASS" if all(row["passed"] for row in rows) else "FAIL",
        "source": {
            "repository": "budzianowski/multiwoz",
            "commit": SOURCE_COMMIT,
            "dataset": "MultiWOZ 2.2 test split",
            "dialogues_loaded": len(contexts),
        },
        "workload": provenance,
        "summary": {
            "snapshots": len(rows),
            "snapshots_passed": sum(row["passed"] for row in rows),
            "checks_passed": checks_passed,
            "checks_total": checks_total,
            "graph_cache_hits": total["graph_cache_hits"],
            "graph_cache_misses": total["graph_cache_misses"],
            "pair_cache_lookups": total["pair_lookups"],
            "pair_cache_hits": total["cache_hits"],
            "pair_cache_misses": total["cache_misses"],
            "pair_cache_hit_rate": total["hit_rate"],
            "pair_cache_entries_at_end": total["entries"],
            "graph_cache_entries_at_end": total["graph_cache_entries"],
        },
        "snapshots": rows,
        "interpretation_boundary": (
            "This is a deterministic cache-correctness and reuse trace over contexts "
            "derived from one pinned MultiWOZ test corpus. Synthetic probe facts/needs "
            "are introduced only to test cache invalidation; they are not claimed as "
            "observed dataset facts. This is not a production workload or latency SLA."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(tempfile.gettempdir()) / "multiwoz-v22-pinned",
    )
    parser.add_argument("--base-size", type=int, default=180)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("MULTIWOZ-CACHE-LIFECYCLE-RESULTS.json"),
    )
    args = parser.parse_args()
    if args.base_size < 32:
        parser.error("--base-size must be at least 32")

    dialogues, _ = load_corpus(args.cache_dir)
    contexts = make_contexts(dialogues)
    result = run_lifecycle(contexts, base_size=args.base_size)
    result["output_generated_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        **result["summary"],
        "output": str(args.output),
    }, ensure_ascii=False, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
