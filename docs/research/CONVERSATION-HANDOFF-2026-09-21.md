# Conversation Handoff — 2026-09-21

## Purpose

This file is the durable exit point for the current conversation. It records what was changed, what is established, what remains open, and where to resume.

## Machine branches

### Substrate

Branch:
research/substrate-interpreter-v0

Pre-change head:
d935495355ac6b827a17d6147d7f38fbcaaeb15f

New commit:
created by this handoff commit

Scope:
unified Machine Substrate Rev 2.1 implementation profile.

### Bidirectional verification

Branch:
research/bidirectional-grounded-verification-v0

Current verified head before this handoff:
cc61765d6939788ab9c075f04ec3572203c89347

Key durable record:
docs/research/BIDIRECTIONAL-SEARCH-GROUNDED-VERIFICATION-v0.4.md

## Durable bidirectional state

Structural lower bound:
N_pi >= VC(G_MX)

Metric separation:
N_pi is expansion count; W_pi is edge-scan work.

Active Dijkstra stopping:
experimentally supported in the declared positive-weight post-edge interruption model.

Naive top-only stopping:
contradicted by finite-cost post-edge counterexamples.

Weighted exhaustive n=3:
4096 graph states, 233472 schedules, 0 active failures, 3840 finite naive failures.

Weighted exhaustive n=4:
531441 graph states, 488430 solvable, 976860 policy runs, 0 active failures, 4374 finite naive failures.

Random n=4 all-schedule:
351232 runs, 0 active failures, 4736 finite naive failures.

Matched simple/multigraph:
2000 matched pairs, 8000 policy runs, geometry/G_MX/VC/expansion equivalence observed; mean W ratio 1.6734 under dominated parallel-transition construction.

Important correction:
v0.3 incorrectly described a pre-first-edge failure as post-edge. The v0.3 erratum and v0.4 report supersede that wording.

## Durable substrate state

The new unified module adds:

- adaptive unsigned CSR dtypes;
- Fiber contract metadata;
- explicit raw-edge vs deduplicated-record semantics;
- attractor counter derivation from Fiber.deduped;
- tests for attractor labeled/deduped/dense-reference agreement;
- basin, retrograde, and Hopcroft/Moore reference checks.

This module is an implementation profile, not the canonical semantic specification.

## Open questions

1. Formal proof of the active-vertex guard and extension to general consistent front-to-end heuristics.
2. Smallest post-edge naive counterexample under arbitrary scheduling.
3. Practical simple-digraph worst-case family corresponding to the cited theoretical gap.
4. Predecessor preprocessing plus repeated-query total-cost separation.
5. Native C and hardware/cache measurements.
6. General randomized 400-game attractor regression with multiple duplicate-transition rates.
7. Independent canonical Machine substrate conformance versus the experimental S2 profile.

## Explicit non-claims

Do not promote:
- active-guard experimental success into a universal heuristic theorem;
- simple/multigraph work separation into a Theta(m/n) practical worst-case claim;
- predecessor fibers into a universal new-computational-capability claim;
- experimental S2 properties into the canonical Machine specification.

## Resume protocol

Start from repository state, not this conversation.

Use:
repository + branch + commit + artifact.

Re-run the relevant executable tests before changing claim status.

Conversation-local packs produced in this line:
- bidirectional_grounded_research_pack_v4.zip
  SHA-256 68e065bff5ca06aaf180ebf062088e98764358454c6e3c2accfa291025b6b315

No claim should be treated as canonical solely because it appears in this handoff.
