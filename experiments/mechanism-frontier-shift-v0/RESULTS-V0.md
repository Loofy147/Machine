# Mechanism Frontier Shift v0 — Results

**Status:** EXPERIMENTALLY_SUPPORTED / LOCAL REPLAY / NOT YET CI-PACKAGED  
**Branch:** `research/evidence-disposition-v0`  
**Code commit:** `8eeda6301e386446acdd9f28059144ad41967f3b`

## Contract

- `B_off = 0)
- `R = 0)
- no target-dependent persistent state
- same graph, query seed, instance set, and correctness criterion
- primary online budget: one candidate-edge examination = one tick
- forward baseline: BFS + visited set
- changed mechanism: bidirectional BFS + online predecessor access
- no reverse adjacency is stored or precomputed

The predecessor relation is derived from the fixed graph definition during the online run. Thus the bidirectional variant does not receive hidden offline state.

## Why this comparison is different from the naive lookahead comparison

The earlier forward lookahead had no visited set. Any bidirectional advantage against it could therefore be explained by a reusable search reorganization.

The present baseline already uses the strongest simple single-directional organization under the declared mechanism: complete BFS with a visited set.

The second family changes the available transition access itself by allowing online traversal from the target through predecessor relations.

## Fixed-budget results

| M | B_on | Forward | Bidirectional | Bidirectional-only instances |
|---:|---:|---:|---:|---:|
| 30 | 10 | 54/192 | 115/192 | 61 |
| 30 | 20 | 105/192 | 177/192 | 72 |
| 30 | 40 | 157/192 | 192/192 | 35 |
| 30 | 80 | 192/192 | 192/192 | 0 |
| 300 | 10 | 8/199 | 14/199 | 6 |
| 300 | 20 | 13/199 | 38/199 | 25 |
| 300 | 40 | 22/199 | 87/199 | 65 |
| 300 | 80 | 45/199 | 141/199 | 96 |
| 300 | 160 | 74/199 | 193/199 | 119 |
| 300 | 320 | 117/199 | 199/199 | 82 |
| 3000 | 10 | 1/200 | 2/200 | 1 |
| 3000 | 20 | 2/200 | 3/200 | 1 |
| 3000 | 40 | 2/200 | 7/200 | 5 |
| 3000 | 80 | 4/200 | 20/200 | 16 |
| 3000 | 160 | 8/200 | 52/200 | 44 |
| 3000 | 320 | 12/200 | 95/200 | 83 |

No sampled case had the reverse pattern at these caps: bidirectional failed while forward succeeded.

## Full-budget closure

At sufficiently large online budgets, both methods eventually solved every sampled query:

| M | Both eventually solved | Bidirectional cheaper | Forward cheaper | Equal |
|---:|---:|---:|---:|---:|
| 30 | 192/192 | 165 | 2 | 25 |
| 300 | 199/199 | 195 | 0 | 4 |
| 3000 | 200/200 | 200 | 0 | 0 |

Median minimum-budget ratio (bidirectional / forward):

- M=30: 0.5000
- M=300: 0.2336
- M=3000: 0.1257

## Interpretation

The fixed-budget results show a real measured Pareto-frontier shift:

```text
same artifact
same offline budget
same correctness requirement
same instance family
same online accounting
different transition access
            ↓
additional instances become feasible at the same tight B_on
```

However, full-budget closure shows that the sampled feasible set is ultimately the same: forward BFS eventually solves all sampled instances too.

Therefore the current result is **not evidence of an absolute increase in ultimate solvability**.

It is evidence of:

> a resource-bounded frontier shift caused by the tested change in transition access.

That separates two previously conflated claims:

1. **Capability under unlimited resources:** not shown to differ here.
2. **Capability under a fixed online resource contract:** differs measurably in this fixture.

The second is the actual observed effect.

## Critical interpretation boundary

The changed mechanism is specifically:

```text
successor access only
        ->
successor + predecessor access
```

This is not evidence that "mechanism change" in general creates new capability.

It establishes only that this particular transition-topology change can move the feasible-set boundary under a fixed tight online budget.

A further control is needed to test whether the same frontier shift can be reproduced by a representation/reorganization available to the original substrate without adding predecessor access.

## Next discriminating tests

1. Add a strongest justified single-direction baseline family, not just one implementation, while preserving the same resource contract.
2. Attempt to emulate predecessor access within the fixed substrate without offline state; charge all emulation work to `B_on`.
3. Compare compact precomputed representations under `B_off=0` and then under increasing `B_off,R`.
4. Repeat across independent graph families and size scales.
5. Evaluate whether the Pareto shift remains after normalization for the cost of inverse-relation computation itself.

