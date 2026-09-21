
# Bidirectional Search Grounded Verification v0.3

Status: DURABLE RESEARCH RECORD
Repository: Loofy147/Machine
Branch: research/bidirectional-grounded-verification-v0
Parent branch: research/evidence-disposition-v0
Parent head at branch creation: 8f16e5dcc57c59025e3cc9ec5607d294a1c8b8e3
Recorded: 2026-09-21

## Purpose

Freeze the grounded state reached while auditing four linked but distinct claims:

1. Must-Expand vertex-cover lower bound.
2. Policy dependence of realized work on a fixed instance.
3. Output-sensitive predecessor-fiber access.
4. Active-vertex stopping for interruptible bidirectional Dijkstra.

This record separates theorem scope, executable evidence, falsifications, and unresolved questions.

## Metric correction

The structural theorem is about vertex expansions:

N_pi(I) >= VC(G_MX(I)).

Edge scans are a separate work metric:

W_pi(I).

The tested decomposition is:

N_pi(I) = VC(G_MX(I)) + epsilon_pi^(N)(I).

No equality between W_pi and VC is assumed.

## Structural lower bound

For the front-to-end bidirectional-search model, the established must-expand result implies that every must-expand pair must be covered by at least one corresponding forward/backward expansion. The expanded copies therefore form a vertex cover of G_MX.

For the blind-search/Dijkstra specialization used by the executable harness:

(u_F, v_B) in E_MX iff d(s,u) + d(v,t) < C*.

Therefore:

N_pi >= tau(G_MX) = nu(G_MX).

The harness checks both the cardinality bound and explicit endpoint coverage for every materialized MX edge.

The simplified distance-only MX definition is not promoted as the general heuristic MEP definition.

## Policy dependence

The same exact (G,s,t,w) is evaluated under isolated policies.

Random suite:
- 1,000 solvable instances.
- n = 24.
- out-degree = 5.
- positive integer weights 1..10.
- policies: alternate, smaller-frontier, smaller-top, forward-biased.

Observed:
- zero N_pi >= VC violations.
- zero MX endpoint-cover violations.
- 932/1000 instances had non-constant N_pi and/or W_pi across the four policies.

Interpretation:
Realized search work is not uniquely determined by the static instance alone.

This does not imply that geometry has no predictive value.

## Active-vertex stopping invariant

The executable claim is restricted to positive-weight bidirectional Dijkstra/UCS.

During an edge-granular expansion, the popped vertex remains explicitly ACTIVE until the incident transitions for that expansion have been scanned.

Tested guard:

min(top_F, g_F(u_active)) + min(top_B, g_B(v_active)) >= mu.

Naive guard:

top_F + top_B >= mu.

Random evidence:
- 1,000 solvable instances.
- 0 active-guard correctness failures.

Exhaustive unit-weight simple digraphs:
- n=3: 64 graphs; 40 solvable; 0 active-guard failures.
- n=4: 4,096 graphs; 3,072 solvable; 0 active-guard failures.

Bounded all-F/B scheduler sequences, post-edge-only interruption:
- n=3: 10,240 trials; 0 failures.
- n=4: 3,145,728 trials; 0 failures.

This removes dependence on the four hand-selected policies within the tested graph class and decision horizon.

## Canonical finite-cost failure of the naive guard

Vertices: 0, 1, 2
Source: 0
Target: 2

Edges:
- 0 -> 1, weight 1
- 1 -> 2, weight 1
- 0 -> 2, weight 3

Optimal cost: C* = 2.

Under post-edge-only interruption, the naive guard can terminate with mu = 3 after the expensive direct edge has been scanned while 0 remains ACTIVE and the cheaper 0 -> 1 transition remains unscanned.

The active-vertex guard returns mu = 2.

## Bounded minimality

Exhaustive ordered-edge-state search with edge states {absent,1,2,3}, s=0, t=n-1:

- n=2: 16 states; 12 solvable; no finite-cost counterexample.
- n=3: 4,096 states; 3,648 solvable; finite-cost counterexample with 3 edges.

This is scope-bounded experimental minimality only.

## Multigraph smoke evidence

2,000 positive-weight directed multigraph instances were tested while preserving parallel transitions.

Observed:
- zero Dijkstra optimality failures.
- zero N_pi >= VC failures.
- zero endpoint-coverage failures.
- zero Konig cardinality failures.

This is implementation/model evidence, not a proof of the literature theorem.

## Predecessor-fiber contract

Under a forward-adjacency-only access model, exact predecessor enumeration has worst-case Omega(E) edge examinations.

With a materialized CSR inverse index, exact enumeration costs Theta(1 + deg^-(u)) after Theta(n+E) preprocessing.

Current interpretation:
- output-sensitive query separation: ESTABLISHED under the stated access model.
- universally new computational capability: OPEN.

The stronger claim requires matched accounting of preprocessing plus repeated-query workload.

## Literature/model boundary

The research distinguishes labeled/parallel-transition multigraph access from simple directed graph access. The cited instance-optimality literature treats these regimes differently.

The repository claim is therefore model-sensitive, not universal.

## Retired/corrected claims

1. E_res approximately 22-25 as an invariant.
   Status: REFUTED by scaling exponent 0.95-0.98.

2. open_work as a materially useful replacement for Pohl cardinality.
   Status: WITHDRAWN after <=1.9% improvement and non-significance on 4/6 graphs.

3. Previous Wilcoxon W=0, p=1.74e-16 result.
   Status: INVALIDATED as a normal-approximation/underflow artifact.

4. Naive interruptible guard top_F + top_B >= mu.
   Status: CONTRADICTED by the finite-cost regression above.

## Current claim ledger

Must-Expand -> vertex-cover lower bound: SUPPORTED.
Scope: theorem scope; blind specialization experimentally exercised.

Blind G_MX definition: ESTABLISHED.
Scope: Dijkstra/blind case.

Policy intervention changes realized work: EXPERIMENTALLY_SUPPORTED.
Scope: tested policy/instance corpus.

N_pi = VC + epsilon^(N): SUPPORTED AS DECOMPOSITION.
Scope: measured expansion work relative to the structural floor.

Active-vertex Dijkstra stopping guard: EXPERIMENTALLY_SUPPORTED.
Scope: positive-weight Dijkstra/UCS and the enumerated/randomized test scopes above.

Naive top-only interrupt guard: CONTRADICTED.
Scope: true mid-expansion semantics.

Predecessor enumeration output sensitivity: ESTABLISHED.
Scope: stated forward-only access model.

Predecessor access as universal new capability: OPEN.
Scope: preprocessing/accounting separation still required.

Practical simple-vs-multigraph separation: OPEN.
Scope: matched benchmark pending.

General consistent-heuristic active guard: OPEN.
Scope: not established by this harness.

## Reproduction artifact

Conversation-local verification pack:
bidirectional_grounded_research_pack_v3.zip

SHA-256:
cd2b1dc1b75524079d7bef3aec5fc35a9593c287806c54a379b1f1569c1298b2

The pack contains executable harnesses, exhaustive outputs, regression fixtures, literature grounding, manifests, and per-artifact SHA-256 values.

The conversation-local pack is evidence input for this record; it does not imply repository integration of every executable file.

## Next discriminating work

1. Extend weighted exhaustive scheduler enumeration beyond the present bounded scope.
2. Expand finite-cost naive-guard search to larger n and multiple policies.
3. Run matched simple-vs-multigraph experiments with identical underlying transition structure.
4. Compare predecessor preprocessing plus repeated-query total cost against forward-only scans over controlled query counts.
5. Continue to large real directed graphs, adversarial simple-digraph constructions, native C, and cache/hardware measurements.

## Provenance rule

No result from this record should be detached from:

repository + branch + commit + artifact + exact experiment scope.

This record does not upgrade the unresolved substrate-capability question.
