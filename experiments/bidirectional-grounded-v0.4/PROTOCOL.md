# Bidirectional Grounded Verification v0.4 Protocol

## Objective

Validate independently:

1. active-vertex stopping under positive-weight Dijkstra/UCS;
2. naive top-only stopping failure under true post-edge interruption;
3. Must-Expand vertex-cover lower bound in the blind-search specialization;
4. representation-level simple-versus-multigraph work separation while preserving shortest-path geometry.

## Semantics

- `check_before_first_edge=False` for the canonical post-edge interruption condition.
- An active vertex remains outside CLOSED until all its incident transitions have been scanned.
- `N_pi` counts completed vertex selections/expansions.
- `W_pi` counts transition/edge scans.
- Positive integer edge weights only.
- Source = 0; target = n-1.

## Exhaustive schedules

For an n-vertex run, a direction schedule of length 2n is sufficient to enumerate every sequence of direction choices up to the maximum number of vertex selections, because a valid run cannot expand more than n distinct vertices in either direction.

Schedules that request an unavailable direction are treated as invalid execution traces and skipped.

## A. Exact weighted n=3

All ordered edge states in `{absent,1,2,3}` and all 64 direction schedules.

## B. Exact weighted n=4 graph space

All ordered edge states in `{absent,1,2}`. The complete graph state space is 3^12 = 531,441.

The active and naive rules are each run under the exact `smaller_frontier` policy.

## C. Random weighted n=4 all-schedule stress

2,000 random graphs; every 256 direction schedules; post-edge-only interruption.

## D. Matched simple/multigraph

2,000 random graph pairs. The multigraph is generated only by adding parallel transitions with weights >= the original transition weight. The simple projection keeps the minimum weight per ordered endpoint. Therefore shortest-path distances, C*, G_MX, and VC are held equal.

Completed-expansion bidirectional Dijkstra is used for the work comparison to avoid mixing representation effects with interrupt timing.

## Required invariants

For each active-guard run:

- returned mu == Dijkstra C*;
- N_pi >= nu(G_MX);
- every MX edge has at least one endpoint expanded on the corresponding side.

For matched representation pairs:

- C*_simple == C*_multi;
- G_MX_simple == G_MX_multi;
- VC_simple == VC_multi;
- N_pi_simple == N_pi_multi for matched policy;
- W_pi may differ and must be reported separately.

## Non-goals

These experiments do not prove:

- the full general consistent-heuristic active guard;
- practical attainment of the theoretical simple-graph Theta(m/n) worst case;
- universal "new computational capability" of predecessor indexing;
- native hardware/cache performance.
