# Erratum — Bidirectional Search Grounded Verification v0.3

**Status:** DURABLE CORRECTION
**Supersedes:** the finite-cost regression/minimality wording in `BIDIRECTIONAL-SEARCH-GROUNDED-VERIFICATION-v0.3.md`
**Recorded:** 2026-09-21

## Correction

The v0.3 record incorrectly classified the 3-vertex fixture as a finite-cost failure under post-edge-only interruption.

That fixture fails only when `check_before_first_edge=True`, i.e. when the guard is evaluated before the first edge of an active expansion.

After re-running the exact weighted scheduler enumeration with the intended post-edge-only semantics (`check_before_first_edge=False`), finite-cost naive-guard failures are also present at n=3.

Exact n=3 scope:

- 4^6 = 4,096 directed graph states with edge states `{absent,1,2,3}`;
- 3,648 solvable graphs;
- 64 F/B schedules per graph;
- 233,472 schedule runs;
- active-guard failures: 0;
- finite-cost naive-guard failures: 3,840.

Canonical post-edge regression:

- 0 -> 1, weight 1
- 0 -> 2, weight 3
- 1 -> 2, weight 1
- C* = 2
- fixed direction schedule begins `FBFFFF`;
- naive guard returns mu = 3;
- active guard returns mu = 2.

The earlier v0.3 claim that a finite post-edge failure first appears at n=4 is therefore withdrawn.

## Disposition

- v0.3 wording: **SUPERSEDED**.
- v0.4 report and executable runner: **CURRENT** for this line of evidence.
- No claim of global graph-theoretic minimality is made beyond the explicitly enumerated finite state space.
