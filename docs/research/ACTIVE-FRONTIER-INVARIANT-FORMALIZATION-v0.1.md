# Active-Vertex Stopping Invariant — Formalization Target v0.1

Status: OPEN PROOF TARGET
Repository: Loofy147/Machine
Evidence basis: research/bidirectional-grounded-verification-v0.4
Related claim: CL-ACTIVE-GUARD-DIJKSTRA-V0.4

## 1. Scope

This note formalizes the exact model currently supported by the durable evidence line:
- directed graph;
- positive edge weights;
- bidirectional Dijkstra/UCS;
- forward and reverse shortest-path keys;
- interruption only after an edge relaxation;
- one side may therefore be part-way through an expansion when the stop test is evaluated.

It does not claim correctness for arbitrary consistent heuristics.

## 2. State model

Let
- g_F(x) be the current forward tentative distance;
- g_B(x) be the current reverse tentative distance;
- top_F = min{g_F(x) : x is currently open on F};
- top_B = min{g_B(x) : x is currently open on B};
- mu be the best complete s-t path cost discovered so far.

During an interruptible edge-granular expansion, define the active vertex on each side, when one exists:
- u_active on F with current key_F(u_active);
- v_active on B with current key_B(v_active).

Define the interrupt-safe frontier lower bounds:

L_F = min(top_F, key_F(u_active))

L_B = min(top_B, key_B(v_active))

with the active term omitted on a side having no in-progress vertex.

Candidate stopping certificate:

L_F + L_B >= mu

The important semantic point is that the active vertex is part of the proof state. It is not equivalent to the ordinary open-set minimum once an expansion has begun but has not completed.

## 3. Required proof obligations

### Lemma A — Active-state lower bound

For every interruption state, every not-yet-certified forward prefix of an s-t path has remaining cost bounded below by L_F.
The reverse analogue must hold for L_B.

This lemma must explicitly account for the fact that the active vertex may have generated some, but not all, outgoing/incoming relaxations.

### Lemma B — Path decomposition

For every s-t path P that has not already certified a path cost <= mu, identify a forward and backward boundary on P at the interruption state such that:

cost(P) >= L_F + L_B.

The proof must handle:
- no active vertex;
- active vertex on F only;
- active vertex on B only;
- active vertices on both sides;
- meeting discovered during the same interruption step.

### Lemma C — Monotonicity

Under positive-weight Dijkstra/UCS, keys exposed by each side are nondecreasing in the completed expansion order.
The proof must state exactly which quantities remain valid while an edge-level expansion is active.

### Theorem target — Interrupt-safe termination

Under the model in §1, if

L_F + L_B >= mu

at a legal post-edge interruption point, then mu = C*.

This is the theorem required to upgrade the current implementation claim from EXPERIMENTALLY_SUPPORTED to a formal result for the exact model.

## 4. Canonical adversarial witness

The durable v0.4 regression is:
- 0 -> 1 weight 1
- 0 -> 2 weight 3
- 1 -> 2 weight 1
- true optimum C* = 2
- schedule prefix FBFFFF
- naive top-only guard returns mu = 3
- active-state guard returns mu = 2
- interruption semantics: post-edge-only

The witness demonstrates the logical gap a proof must close: a stop test based only on top_F + top_B can ignore the key of an active/in-progress vertex.

## 5. Negative boundaries

The following are intentionally not theorem statements here:
- arbitrary consistent-heuristic correctness;
- arbitrary scheduler correctness outside the exact tested interruption model;
- correctness for non-positive weights;
- correctness when the reported active key does not correspond to the actual in-progress expansion state.

## 6. Kill conditions

The proof program fails if either of the following is produced:
1. a reachable state satisfying the proposed certificate but containing an s-t path of cost < mu;
2. a semantic ambiguity in the interruption model that permits two implementations with the same recorded state to have different valid lower bounds.

A failed proof must be recorded as OPEN/CONTRADICTED rather than repaired by silently changing the state model.