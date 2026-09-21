# Weighted Exhaustive + Matched Simple/Multigraph Verification v0.4

Status: DURABLE RESEARCH RECORD
Repository target: Loofy147/Machine
Research branch: research/bidirectional-grounded-verification-v0
Prior durable commit: 39fd08990cd08461549b507af2395fabe4591b19
Recorded: 2026-09-21

## Scope

This report closes the two next discriminating experiments from v0.3:

1. weighted exhaustive scheduler validation under genuinely post-edge-only interruption;
2. matched simple-versus-multigraph comparison in which shortest-path geometry is held constant.

The active stopping claim remains scoped to positive-weight bidirectional Dijkstra/UCS.

## A. Weighted exhaustive verification

### A1. Exact n=3 weighted scheduler enumeration

Graph model:

- 3 vertices, source 0, target 2;
- every ordered edge state in {absent, 1, 2, 3};
- 4^6 = 4,096 graph states;
- 3,648 solvable graphs;
- every F/B scheduling sequence of length 6 (2n);
- post-edge-only interruption: check_before_first_edge=False.

Results:

- scheduler runs: 233,472;
- active-guard optimality failures: 0;
- active-guard expansion-floor failures: 0;
- explicit MX-cover failures: 0;
- König cardinality failures: 0;
- finite-cost naive-guard failures: 3,840.

A canonical 3-vertex post-edge failure is:

- 0 -> 1, weight 1
- 0 -> 2, weight 3
- 1 -> 2, weight 1
- C* = 2
- direction schedule begins FBFFFF
- naive guard stops at mu = 3
- active guard returns mu = 2.

Therefore a finite-cost post-edge failure already exists at n=3; no stronger n=4 minimality claim is needed.

### A2. Exact n=4 weighted graph space

Graph model:

- 4 vertices, source 0, target 3;
- every ordered edge state in {absent, 1, 2};
- 3^12 = 531,441 graph states;
- 488,430 solvable graphs;
- policy: exact smaller_frontier;
- post-edge-only interruption.

Results:

- completed policy runs: 976,860 (active + naive);
- active-guard failures: 0;
- explicit MX-cover failures: 0;
- König failures: 0;
- finite-cost naive-guard failures: 4,374.

Thus the active guard survived every solvable graph in this exhaustive weighted graph space under the specified policy.

The naive rule failed on 4,374 solvable graphs.

### A3. Random n=4 all-schedule stress

Graph model:

- 2,000 random directed simple weighted graphs;
- n=4;
- weights 1..3;
- every 8-step F/B sequence (2n) tested;
- post-edge-only interruption.

Results:

- 1,372 solvable graphs;
- 351,232 schedule runs;
- active-guard failures: 0;
- explicit MX-cover failures: 0;
- finite-cost naive-guard failures: 4,736.

This removes dependence on one scheduler policy while retaining exhaustive scheduling for every sampled graph.

## B. Correct finite-cost post-edge regression

The canonical post-edge regression is the exact 3-vertex fixture above. It requires no pre-first-edge check.

A secondary 4-vertex reduction also exists and remains useful as a different configuration:

- 0 -> 1, weight 5
- 0 -> 2, weight 1
- 1 -> 3, weight 1
- 2 -> 1, weight 1
- C* = 3
- naive mu = 6

The 3-vertex fixture is the canonical regression because it is smaller and is found inside the exact exhaustive n=3 weighted schedule space.

## C. Matched simple-versus-multigraph experiment

### Construction

For each of 2,000 seeds:

1. generate a simple positive-weight directed graph;
2. create a multigraph by adding parallel transitions whose weights are never smaller than the corresponding original transition;
3. project the multigraph back to a simple graph by retaining the minimum weight per ordered endpoint.

Therefore the simple and multigraph instances have identical shortest-path geometry:

- identical d(s,u);
- identical d(v,t);
- identical C*;
- identical G_MX;
- identical minimum vertex-cover cardinality.

Only transition multiplicity is changed.

### Results

Across 2,000 matched pairs and four policies:

- pair-level failures: 0;
- geometry/distance mismatches: 0;
- G_MX mismatches: 0;
- minimum-cover mismatches: 0;
- optimality mismatches: 0;
- expansion-count mismatches: 0.

Edge-work changed systematically because the multigraph contains additional transitions:

- mean simple edges: 123.13;
- mean multigraph edges: 206.246;
- mean multiplicity ratio: 1.6750x;
- median multiplicity ratio: 1.6774x;
- 8,000 policy-paired W-ratios;
- mean W_multigraph / W_simple = 1.6734x;
- minimum ratio = 1.0x;
- maximum ratio = 2.5x.

### Interpretation boundary

This experiment demonstrates a clean representation-level distinction:

same shortest-path geometry + same VC + same expansions + different edge-level work.

It does not by itself establish the theoretical multigraph/simple-graph instance-optimality separation from the cited literature.

In particular, it does not construct the simple-graph lower-bound family nor establish a practical Theta(m/n) regret gap.

## D. Updated evidence state

### Active-vertex stopping guard

Status: EXPERIMENTALLY_SUPPORTED.

Evidence now spans:

- 1,000 random weighted instances;
- exact n=3 weighted graph space x all F/B schedules;
- exact n=4 weighted graph space with smaller_frontier;
- random n=4 weighted graphs x all F/B schedules;
- previous unweighted exhaustive suites.

The claim remains scoped to positive-weight Dijkstra/UCS and the exact interrupt semantics implemented by the harness.

### Naive top-only stopping guard

Status: CONTRADICTED.

Finite-cost failures are now established under post-edge-only interruption, with an n=3 three-edge canonical regression.

### Structural lower bound

Status: EXPERIMENTALLY_SUPPORTED within the tested blind-search specialization.

No observed violation of N_pi >= VC(G_MX) or explicit MX endpoint coverage.

### Simple-versus-multigraph representation effect

Status: EXPERIMENTALLY_SUPPORTED for the limited matched construction.

Observed phenomenon:

same shortest-path geometry + same VC + same expansions + different edge-level work.

The stronger instance-optimality-regime claim remains OPEN.

## E. Corrections to v0.3

1. The previous 3-vertex regression was misclassified because it used a pre-first-edge check.
2. Under the intended post-edge-only semantics, finite naive failures also occur at n=3.
3. The exact n=3 weighted exhaustive result already contains finite post-edge failures; no n>=4 lower-bound claim is made.
4. The n=4 exhaustive result is used for broader coverage under the exact smaller_frontier policy and state space {absent,1,2}.

## F. Next discriminating actions

1. Search for the smallest post-edge naive counterexample under arbitrary admissible scheduling, not only smaller_frontier.
2. Construct and benchmark the cited simple-digraph worst-case family rather than using only dominated parallel-edge constructions.
3. Compare total cost: preprocessing + repeated predecessor queries against forward-only scanning at controlled query multiplicities.
4. Port the active-guard engine to native C and measure cycles/cache behavior separately from algorithmic work.

## Provenance

All numerical claims in this report correspond to executable artifacts in the same evidence pack. Repository integration should preserve the artifact hash, script version, exact scope, and branch/commit identity.
