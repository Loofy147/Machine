# MultiWOZ Anchor and Utility Sensitivity Check

**Status:** Added as a deterministic experimental robustness check; results are emitted by the Machine CI workflow.  
**Implementation:** `experiments/context-contract-distribution-v0/stress_test_multiwoz_sensitivity.py`  
**Result artifact:** `MULTIWOZ-SENSITIVITY-RESULTS.json`

## Question

Does the observed planner-vs-greedy utility difference remain similar when the real anchor source changes, and how often does the selected set change when the utility proxy changes?

## Method

- Reuse the exact pinned MultiWOZ 2.2 test split and the verified shard hashes from the primary benchmark.
- Run eight deterministic seeds (2026–2033). For each seed, hold out four actual fact-bearing dialogue contexts, derive the anchor from one held-out context, and plan over the remaining contexts.
- Compare two utility policies on the same eligible graph:
  1. populated annotated slot count;
  2. \(100 \times\) unresolved annotated requested-slot count plus populated slot count.
- Compare each plan against the same deterministic greedy edge-pair baseline for that utility. Revalidate selected pairs against raw facts, directed need satisfaction, and the anchor. Confirm selected utility reconciles with the selected IDs and that the plan does not score below the greedy baseline under the lexicographic objective.
- Save per-seed anchors, input digests, graph size, selected IDs, utility metrics, baseline metrics, and checks in machine-readable JSON.

The sensitivity test only varies deterministic anchor sampling over one fixed source corpus. The alternative request-priority formula is a competing proxy, not a measured business value.

## Interpretation boundaries

This is not an independent dataset replication, confidence interval, proof of generalization, production load benchmark, or validation on business/legal contracts. A positive uplift only means the matching planner achieved higher utility than the stated greedy edge-pair baseline for that particular seed, graph, and utility formula. Do not infer provider-token savings or production benefit from these results.

The purpose of the sweep is to expose instability and make the next research decision evidence-based. If results vary materially across anchors or objective policy, the next step should be a better value/need model and broader held-out data—not a claim of success based on a single seed.

## Observed result

The first full-corpus sensitivity run completed on implementation commit `b43f57135717892ee0bb79c61803b43430fce1c4` in [GitHub Actions run 40953820974](https://github.com/Loofy147/Machine/actions/runs/40953820974).

- Unit/property tests: 28 passed.
- Existing actual MultiWOZ checks: 5/5 passed.
- Supplementary synthetic-control suites: 8/8 passed.
- Sensitivity sweep: 48/48 checks passed across seeds 2026–2033.
- Slot-count utility uplift over the deterministic greedy baseline: minimum 1.1561%, median 2.1132%, mean 2.7512%, maximum 5.8050%.
- Requested-slot-priority utility uplift over its corresponding greedy baseline: minimum 7.7019%, median 11.0948%, mean 11.2772%, maximum 14.4779%.
- The selected context set changed under the alternative utility in 8/8 seeds.

The two uplift summaries are computed against separate baselines using separate utility functions; their percentage values are **not directly comparable across policies**. The result establishes sensitivity to the selected anchor and objective proxy. It does not validate either utility as business value, and the eight seeds are not an independent sample of datasets or grounds for a confidence interval.

The artifact uploaded for that run contains `MULTIWOZ-SENSITIVITY-RESULTS.json` alongside the original plan and benchmark results: [downloadable evidence artifact](https://github.com/Loofy147/Machine/actions/runs/40953820974/artifacts/12933490425).

## Rust computation-cache experiment

The Rust graph builder and its two-level Moka cache were exercised by the same primary and sensitivity runners. This is a **computation cache**, not the LLM response/token cache. Implementation and limits are documented in [RUST-COMPUTE-CACHE-EXPERIMENT-v0.1.md](RUST-COMPUTE-CACHE-EXPERIMENT-v0.1.md).

Corrected graph-path timings include eligible-context filtering, JSON payload construction, JSON-lines process transport, response parsing, and NetworkX graph reconstruction. They do not include maximum-weight matching; the exact matching algorithm remains Python/NetworkX.

Eight-seed results:
- Python reference for the repeated request-priority graph: mean 0.1965 s, median 0.2266 s.
- Rust warm whole-graph cache for the same graph under the alternative utility: mean 0.0312 s, median 0.0349 s; graph-cache hit in 8/8 seeds.
- Python slot-count graph: mean 0.2238 s, median 0.2523 s. Rust pair/graph path: mean 0.1945 s, median 0.1930 s; individual seeds vary.
- Across the eight seeds, the pair cache recorded 867,533 lookups, 467,202 hits, and 400,331 misses (53.85% hit rate).

Primary 1,000-dialogue benchmark: all 8/8 checks passed; Rust and Python graphs and complete plans matched. There were 402,030 pair hits and 380,699 pair misses. The initial cold Rust graph build took 0.3909 s versus 0.2472 s for Python, so cold-start performance is worse in this run; the benefit comes from pair reuse across anchors and whole-graph reuse for repeated identical eligible context sets.

Do not infer a 6.3× full-planner or production speedup from the warm graph-builder comparison. CI deliberately executes both implementations for equivalence, while the matching solver remains Python. The caches are process-local, have 30-minute TTLs and approximate weighted capacities, and do not survive process restart.

Exact verified head: `1a7734f6520fce5b43bc1a79a1946126dfb90bab`. CI passed 6 Rust tests, 32 Python tests, 8/8 synthetic controls, 8/8 primary MultiWOZ checks, and 88/88 sensitivity checks. Evidence: [run 40993076325](https://github.com/Loofy147/Machine/actions/runs/40993076325), [artifact](https://github.com/Loofy147/Machine/actions/runs/40993076325/artifacts/12950251652).


## Follow-up cache lifecycle and planner latency

The final cache follow-up is recorded in [RUST-COMPUTE-CACHE-EXPERIMENT-v0.1.md](RUST-COMPUTE-CACHE-EXPERIMENT-v0.1.md). On the same pinned corpus it passed:
- 12/12 changing-context snapshots and 41/41 checks;
- 9/9 Rust tests (including TTL expiry and pair/graph capacity-pressure eviction);
- 34/34 Python tests;
- a seven-request end-to-end comparison with 6/6 checks.

The separate request-path benchmark measured a 0.41995 s Python median and a 0.26531 s warm Rust-cache median (1.5829× ratio). The Rust process retained its whole-graph entry across all seven timed requests. A single cold Rust request was slower than Python, so this result applies to repeated graph identity, not cold-start workloads.

CI and artifact for the completed follow-up: [run 41009623330](https://github.com/Loofy147/Machine/actions/runs/41009623330) · [evidence artifact](https://github.com/Loofy147/Machine/actions/runs/41009623330/artifacts/12956722703).


## Independent SGD corpus and final runtime verification

The final run added a separately pinned Schema-Guided Dialogue sample from `google-research-datasets/dstc8-schema-guided-dialogue` commit `e852981ae34990f4358979625854259302feaa78` (CC-BY-SA-4.0). Three test shards supplied 310 dialogues across 10 observed services.

The dialogue-instance adapter deliberately kept fields service-qualified. It produced 310 mapped contexts and 119 anchor-eligible contexts, but **zero compatibility edges**. Rust and Python agreed on the empty graph and empty plan. This remains a negative result: those dialogue instances are not interchangeable partner contracts under that conservative mapping.

A separate schema-intent model produced a positive result:
- 38 service-intent contexts;
- 271 declared result slots and 96 required slots;
- 87 compatibility edges and 17 selected pairs (34 contexts);
- exact Rust/Python graph and complete-plan equivalence;
- utility-only change hit the whole-graph cache.

This is schema-level, exact slot-name matching across service APIs. It tests a name-level interface hypothesis, not semantic equivalence of fields. On this small graph the Rust bridge path (1.70 ms warm) was marginally slower than fresh Python graph construction (1.50 ms); it establishes parity and cache reuse, not a performance advantage.

The same final CI run completed 9/9 Rust tests, 39/39 Python tests, 8/8 synthetic checks, 8/8 primary MultiWOZ checks, 17/17 SGD checks, 88/88 sensitivity checks, 41/41 lifecycle checks, 8/8 runtime concurrency/process-isolation checks, and 6/6 end-to-end checks.

Final run: [41011900858](https://github.com/Loofy147/Machine/actions/runs/41011900858). Evidence artifact: [12958455327](https://github.com/Loofy147/Machine/actions/runs/41011900858/artifacts/12958455327).
