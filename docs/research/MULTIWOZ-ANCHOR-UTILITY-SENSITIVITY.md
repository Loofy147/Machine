# MultiWOZ Anchor and Utility Sensitivity Check

**Status:** Added as a deterministic experimental robustness check; results are emitted by the Machine CI workflow.  
**Implementation:** \`experiments/context-contract-distribution-v0/stress_test_multiwoz_sensitivity.py\`  
**Result artifact:** \`MULTIWOZ-SENSITIVITY-RESULTS.json\`

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
