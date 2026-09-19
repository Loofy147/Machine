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
