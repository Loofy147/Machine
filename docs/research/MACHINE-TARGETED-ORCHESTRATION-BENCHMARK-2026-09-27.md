# Machine-Targeted Orchestration Benchmark — 2026-09-27

Run ID: `MACHINE-ORCH-2026-09-27-001`

## Target identity

Repository: `Loofy147/Machine`
Default branch verified: `main`
Default head: `1626bac2f5c478294afa4b9463f694608c322117`
Research branch used for current frontier state: `research/evidence-disposition-v0`
Research head: `137f76bc7fb56138a40b3bc98ed2a3291fe7acf5`
Experimental substrate branch: `research/substrate-interpreter-v0`
Experimental substrate head: `d935495355ac6b827a17d6147d7f38fbcaaeb15f`

## Benchmark purpose

Test whether orchestration can correctly select, reconcile, and verify the next discriminating Machine research action without collapsing branch identity, specification, implementation, execution, or evidence status.

## Executed orchestration trace

DISCOVER → BRANCH-RECONCILE → EVIDENCE-SELECT → OPEN-GAP-DETECT → CI-VERIFY → CANONICAL-SUBSTRATE-CHECK → BOUNDARY-DECISION

## Discovery

Relevant research branches were enumerated and the active substrate/frontier line was narrowed to:
- `research/evidence-disposition-v0`
- `research/substrate-interpreter-v0`
- `research/machine-native-primitives-v0`
- bidirectional/frontier research branches

The repository protocol explicitly requires repository + branch + commit as the minimum provenance identity.

## Evidence selection and verification

The substrate/relation-lookup line was selected because the current Machine evidence explicitly marks canonical-substrate correspondence as OPEN and names reconciliation as the next discriminating action.

Verified:
- experimental S1/S2 finite same-representation semantic equivalence;
- experimental resource vector `(B_off,R,B_on,C_access)`:
  - S1 = `(5,5,676,291)`
  - S2 = `(5,5,20,10)`;
- repaired S2 candidate-target CI replay:
  - semantic suite: 13 passed;
  - implementation property suite: 8 passed;
  - audit: exit 0;
  - canonical vector equality: true;
- latest `research/substrate-interpreter-v0` workflow run at head `d935495355ac6b827a17d6147d7f38fbcaaeb15f`: successful.

## Critical discrepancy / frontier finding

`research/substrate-interpreter-v0` contains an explicit CEK-style experimental interpreter and its audit.

The current `main` branch does not contain a canonical executable interpreter corresponding to that experimental S1/S2 implementation. The `research/machine-native-primitives-v0` tree likewise contains the abstract Machine model and experiment documentation, but no canonical interpreter source; its executable source inventory returned only `experiments/error-source-localization/harness.py`.

Therefore the experimental result cannot be promoted to either:
- `canonical Machine substrate is S1`; or
- `canonical Machine substrate is S2`.

Correct current disposition:

`canonical substrate classification = OPEN / SPECIFICATION-DEBT`

## Orchestrator decisions

Demonstrated decisions:
- branch-specific evidence was preferred over default-branch assumptions;
- experimental implementation was separated from canonical project state;
- CI evidence remained tied to exact verification commit/run;
- conditional/stale claims were not promoted;
- the next action was narrowed to canonical substrate reconciliation rather than reflective-substrate expansion.

## Benchmark verdict

**DEMONSTRATED:** branch/evidence discovery, provenance reconciliation, claim/evidence separation, targeted experiment selection, CI verification, open-gap detection, and bounded decision-making.

**PARTIALLY DEMONSTRATED:** fresh execution orchestration. Existing CI executions could be verified, but the available GitHub action surface did not expose workflow dispatch for creating a new Machine run during this benchmark.

**BLOCKING FRONTIER:** canonical-substrate execution. The decisive minimal pair requires a concrete canonical interpreter/execution substrate to be explicitly identified or promoted.

## Next discriminating action

Audit and explicitly identify the canonical Machine execution substrate, then define a matched minimal pair:

Control = S1 generic state computation only.
Treatment = S1 + direct indexed relation access.

Hold fixed:
- relation information;
- target timing;
- persistent representation;
- correctness semantics;
- offline/online accounting.

Measure:
`(B_off,R,B_on,C_access)` plus semantic equivalence.

Promotion rule:
- traversal derivable + lower cost → resource primitive/optimization;
- required access absent from fixed substrate → substrate extension;
- traversal derivable but closure fails under fixed resources → resource-bounded frontier advantage; closure remains OPEN.

## Epistemic disposition

No new Machine scientific claim is promoted by this benchmark.

The supported procedural result is narrower: the current research frontier can be orchestrated without losing branch/provenance/evidence distinctions, and the remaining blocker is localized to the canonical execution-substrate boundary.

Artifact SHA-256: `2e146ea7d4f32a35b9e690b3530288ed552e70f9a19757e1096dce1b58650b27`
