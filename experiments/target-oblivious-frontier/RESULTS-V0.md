# Target-Oblivious Precomputation / Online Computation Frontier v0 — Results

Status: EXECUTED / EXPLORATORY

Run: M in {30, 300, 3000}; 200 requested queries per M; budget = shortest-path length + 2; fixed lookahead depth = 2 for the frontier sweep.

## Main result

The strict-heldout control passed exactly.

For every tested prefix h <= M/2:

- cache hits = 0;
- success rate = identical to h=0;
- online work = identical to h=0.

Thus adding target-specific offline work that cannot cover the realized target did not silently change the online controller.

The IID workload shows the expected tradeoff: as more targets are precomputed, hit rate rises, success rises, and online work falls. The full all-target table reaches 100% sampled success while reducing policy selection to O(1) per executed transition, at offline cost/storage proportional to M^2 in this graph.

## IID workload

| M | h | offline states | hit rate | success | avg online work |
|---:|---:|---:|---:|---:|---:|
| 30 | 0 | 0 | 0.000 | 0.984 | 115.66 |
| 30 | 3 | 90 | 0.126 | 0.984 | 101.99 |
| 30 | 5 | 150 | 0.183 | 0.990 | 94.03 |
| 30 | 15 | 450 | 0.497 | 1.000 | 59.36 |
| 30 | 30 | 900 | 1.000 | 1.000 | 2.85 |
| 300 | 0 | 0 | 0.000 | 0.533 | 235.24 |
| 300 | 17 | 5,100 | 0.075 | 0.578 | 215.97 |
| 300 | 30 | 9,000 | 0.116 | 0.598 | 206.58 |
| 300 | 150 | 45,000 | 0.497 | 0.774 | 118.75 |
| 300 | 300 | 90,000 | 1.000 | 1.000 | 5.80 |
| 3000 | 0 | 0 | 0.000 | 0.115 | 380.62 |
| 3000 | 54 | 162,000 | 0.010 | 0.120 | 377.70 |
| 3000 | 300 | 900,000 | 0.090 | 0.195 | 347.31 |
| 3000 | 1500 | 4,500,000 | 0.495 | 0.545 | 194.22 |
| 3000 | 3000 | 9,000,000 | 1.000 | 1.000 | 9.40 |

## Strict-heldout control

| M | h | offline states | hits | success | avg online work |
|---:|---:|---:|---:|---:|---:|
| 30 | 0 | 0 | 0 | 1.000 | 123.62 |
| 30 | 3 | 90 | 0 | 1.000 | 123.62 |
| 30 | 5 | 150 | 0 | 1.000 | 123.62 |
| 30 | 15 | 450 | 0 | 1.000 | 123.62 |
| 300 | 0 | 0 | 0 | 0.470 | 239.56 |
| 300 | 17 | 5,100 | 0 | 0.470 | 239.56 |
| 300 | 30 | 9,000 | 0 | 0.470 | 239.56 |
| 300 | 150 | 45,000 | 0 | 0.470 | 239.56 |
| 3000 | 0 | 0 | 0 | 0.135 | 385.65 |
| 3000 | 54 | 162,000 | 0 | 0.135 | 385.65 |
| 3000 | 300 | 900,000 | 0 | 0.135 | 385.65 |
| 3000 | 1500 | 4,500,000 | 0 | 0.135 | 385.65 |

## Strict-heldout depth sweep at h=0

This measures the online-only side before target-specific persistent state is introduced.

| M | depth | success | avg online work |
|---:|---:|---:|---:|
| 30 | 0 | 0.567 | 12.54 |
| 30 | 1 | 0.902 | 41.37 |
| 30 | 2 | 1.000 | 123.62 |
| 30 | 3 | 1.000 | 292.73 |
| 30 | 4 | 1.000 | 570.87 |
| 300 | 0 | 0.217 | 23.05 |
| 300 | 1 | 0.369 | 82.39 |
| 300 | 2 | 0.470 | 239.56 |
| 300 | 3 | 0.707 | 631.64 |
| 300 | 4 | 0.909 | 1,577.30 |
| 3000 | 0 | 0.015 | 34.56 |
| 3000 | 1 | 0.055 | 129.05 |
| 3000 | 2 | 0.135 | 385.65 |
| 3000 | 3 | 0.285 | 1,075.80 |
| 3000 | 4 | 0.450 | 2,907.29 |

## What is established by this run

1. Target-oblivious partial caches behave as expected under strict held-out targets.
2. Full target-oblivious precomputation can move essentially all target-selection computation offline in this finite graph.
3. Fixed-depth online lookahead has bounded per-decision expansion at a fixed depth, but its success does not remain constant as M grows in this setup.
4. Therefore the immediate phenomenon is a resource/placement tradeoff, not yet evidence for mechanism change.

## What remains open

- compact target-oblivious structure between narrow heuristics and full tables;
- optimal online algorithms other than fixed-depth lookahead;
- whether a fixed executor plus bounded persistent state can match a changed transition topology under the same explicit resource limits;
- whether any residual gap is genuinely mechanistic rather than an artifact of this representation.

The current result does not justify implementing reflection.
