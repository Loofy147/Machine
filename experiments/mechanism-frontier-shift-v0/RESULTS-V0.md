# Mechanism Frontier Shift v0 — Results

**Status:** EXPERIMENTALLY_SUPPORTED / LOCAL REPLAY / NOT YET CI-PACKAGED
**Branch:** `research/evidence-disposition-v0`
**Primary code commit:** `8eeda6301e386446acdd9f28059144ad41967f3b`
**Emulation-control commit:** `5f0c4a1b74cfff52fe5743758bc9bc0d666832dc`

## Contract

- `B_off = 0`
- `R = 0`
- no target-dependent persistent state
- same graph, query seed, instance set, and correctness criterion
- primary online budget: one candidate-edge examination = one tick
- baseline: forward BFS + visited set
- changed mechanism: bidirectional BFS + online predecessor access
- no reverse adjacency is stored or precomputed
- predecessor emulation control derives predecessors using only the original successor operations and charges every tested edge to `B_on`

## Baseline vs native bidirectional

The strongest simple single-direction baseline is BFS with a visited set. The earlier naive forward recursion is not used.

The native bidirectional mechanism adds online predecessor access. Fixed-budget replay produced:

| M | B_on | Forward | Native bidi | Native-only |
|---:|---:|---:|---:|---:|
| 30 | 10 | 54/192 | 177/192 | 123 |
| 30 | 20 | 105/192 | 192/192 | 87 |
| 30 | 40 | 157/192 | 192/192 | 35 |
| 30 | 80 | 192/192 | 192/192 | 0 |
| 300 | 10 | 6/200 | 33/200 | 27 |
| 300 | 20 | 9/200 | 80/200 | 71 |
| 300 | 40 | 17/200 | 144/200 | 127 |
| 300 | 80 | 37/200 | 197/200 | 160 |
| 300 | 160 | 71/200 | 200/200 | 129 |
| 300 | 320 | 118/200 | 200/200 | 82 |
| 300 | 640 | 179/200 | 200/200 | 21 |
| 3000 | 10 | 0/200 | 3/200 | 3 |
| 3000 | 20 | 0/200 | 8/200 | 8 |
| 3000 | 40 | 2/200 | 15/200 | 13 |
| 3000 | 80 | 3/200 | 38/200 | 35 |
| 3000 | 160 | 8/200 | 94/200 | 86 |
| 3000 | 320 | 10/200 | 172/200 | 162 |
| 3000 | 640 | 18/200 | 200/200 | 182 |

These are the corrected figures under the unified edge-examination accounting. The earlier prose table with smaller native counts used a different accounting convention and is superseded.

## Emulation control

The key control keeps the original successor-only substrate and attempts to obtain the same reverse traversal by exhaustive online predecessor discovery:

```text
candidate state v
  -> apply A/B/C
  -> test successor(v) == requested predecessor target
```

Every candidate-edge test costs one tick. No reverse index and no inverse formula are available to the baseline.

| M | B_on | Forward | Native bidi | Successor-only emulated bidi | Emulated-only vs forward |
|---:|---:|---:|---:|---:|---:|
| 30 | 10 | 54 | 177 | 19 | 0 |
| 30 | 20 | 105 | 192 | 19 | 0 |
| 30 | 40 | 157 | 192 | 19 | 0 |
| 30 | 80 | 192 | 192 | 19 | 0 |
| 30 | 160 | 192 | 192 | 91 | 0 |
| 30 | 320 | 192 | 192 | 189 | 0 |
| 30 | 640 | 192 | 192 | 192 | 0 |
| 300 | 10 | 6 | 33 | 3 | 0 |
| 300 | 20 | 9 | 80 | 3 | 0 |
| 300 | 40 | 17 | 144 | 3 | 0 |
| 300 | 80 | 37 | 197 | 3 | 0 |
| 300 | 160 | 71 | 200 | 3 | 0 |
| 300 | 320 | 118 | 200 | 3 | 0 |
| 300 | 640 | 179 | 200 | 3 | 0 |
| 3000 | 10 | 0 | 3 | 0 | 0 |
| 3000 | 20 | 0 | 8 | 0 | 0 |
| 3000 | 40 | 2 | 15 | 0 | 0 |
| 3000 | 80 | 3 | 38 | 0 | 0 |
| 3000 | 160 | 8 | 94 | 0 | 0 |
| 3000 | 320 | 10 | 172 | 0 | 0 |
| 3000 | 640 | 18 | 200 | 0 | 0 |

At higher budgets the same pattern closes gradually because brute-force inverse discovery is eventually paid for:

| M | B_on | Forward | Native bidi | Emulated bidi |
|---:|---:|---:|---:|---:|
| 30 | 640 | 192 | 192 | 192 |
| 300 | 1280 | 200 | 200 | 8 |
| 3000 | 10000 | 200 | 200 | 1 |
| 3000 | 30000 | 200 | 200 | 3 |

The emulated mechanism therefore does not recover the native frontier at the tight budgets tested.

## Interpretation

The experiment now supports a narrower and stronger claim than the original "bidirectional is smarter" framing.

Under the declared contract:

```text
B_off = 0
R = 0
same instances
same correctness requirement
same online tick accounting
```

adding direct predecessor access creates a measured shift in the feasible set at fixed tight `B_on`.

The original successor-only substrate can imitate predecessor access only by paying a large online search cost. Under the tested budgets that emulation does not reproduce the native frontier.

This is evidence for a **resource-bounded mechanism capability difference**:

> The changed transition access provides information at a lower online computational cost than the original successor-only substrate can obtain under the same budget.

It is still not an absolute claim that the mechanisms have different ultimate computational power. At sufficiently high budgets, brute-force emulation can eventually recover some or all of the behavior.

## What is now distinguished

1. **Optimization:** same feasible set, lower cost.
2. **Allocation/representation:** same mechanism, computation moved offline or encoded in state.
3. **Mechanism-induced frontier shift:** under the same frozen-state and online-resource contract, a changed transition access makes additional instances feasible.

The current experiment supports (3) for this specific transition-topology change and graph family.

It does not establish (3) for "mechanism change" as a universal category.

## Remaining confounds

- one arithmetic graph family;
- one query seed;
- one inverse-access implementation;
- the changed mechanism has a direct predecessor operation available by definition;
- the baseline's exhaustive predecessor emulation is generic but not necessarily optimal for every possible successor-only representation;
- no independent CI replay yet.

## Next discriminating tests

1. Repeat across graph families where predecessor access has different computational costs.
2. Test a stronger successor-only baseline family, not only BFS.
3. Add successor-only compact representations whose construction is forbidden offline in this contract but whose construction is charged online.
4. Normalize the cost of predecessor access itself across mechanisms.
5. Repeat with independent query seeds and report confidence intervals over the frontier shift.

