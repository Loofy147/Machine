# HSDCR Gap Closure Matrix v0.1

Status: RESEARCH / DELIVERY AUDIT
Reviewed: 2026-09-29

| Gap / risk | Previous state | Action | Current state | Why this state |
|---|---|---|---|---|
| Candidate-atom overcounting | mixed semantics/capabilities/constraints | reclassified into domain semantics, known capabilities, guards | CLOSED FOR CURRENT MODEL | ontology is no longer inferred from implementation features |
| Direct GitHub↔AT comparison | narrow finding plus stale fixture risk | current GitHub metadata + explicitly pinned historical AT fixture | CLOSED AS PROVENANCE ISSUE | current and historical evidence are separated |
| Hard-coded signal-loss assertion | weakness | actual signal creation, drop, persistence, rehydration, reconstruction | CLOSED FOR THIS EXPERIMENT | perturbation is executed |
| Self-referential result hash ambiguity | weakness | canonical payload excludes hash field | CLOSED | hashing rule is explicit |
| Provider semantic-equivalence overclaim | wording risk | abstract-boundary equivalence only; provider equivalence remains open | CLOSED AS CLAIMING RISK | result reports what was actually measured |
| Evidence fixture realism | normalized | bounded explicitly | OPEN | independent real evidence providers still required |
| Authority fixture realism | normalized | bounded explicitly | OPEN | independent real authority providers still required |
| Crash/restart persistence | local serialization only | specified next | OPEN | no process/crash boundary was tested |
| Resource equivalence | not executed | retained as separate dimension | OPEN | no cost/resource comparison exists |
| Authority equivalence | intentionally not equalized | retained separately | OPEN | semantic authority and execution authority are distinct |
| Durability equivalence | not established | local rehydration only | OPEN | serialization is not production durability |
| Novel semantic primitive | not detected | composition reduction + E2E | OPEN | non-detection is not impossibility proof |
| New repository primitive | not detected | removal/reduction model | OPEN / NOT_DETECTED | broader substitutions remain |
| New execution primitive | not detected | reduction oracle | OPEN / NOT_DETECTED | broader substitutions remain |
| HSDCR as protocol | not assigned | no promotion | CLOSED AGAINST PREMATURE PROMOTION | evidence does not justify protocol assignment |
| HSDCR as architecture | not assigned | no promotion | CLOSED AGAINST PREMATURE PROMOTION | composition is a stronger current explanation |
| Literature coverage | broad but informal | frozen related-research baseline | CLOSED FOR REDUCTION STAGE | core neighboring families and foundational work are recorded |
| Historical evidence retention | risk of losing killed findings | retain v0.1/v0.2 and provenance | CLOSED | negative findings remain in the lineage |

## Delivery acceptance criteria

1. Current source state is distinguished from historical fixtures.
2. Every experiment has code, result, provenance, and reproducibility workflow.
3. Claims are classified by evidence status.
4. Negative findings and methodological failures are retained.
5. Related capability families are recorded with primary sources.
6. Open gaps are explicit and have a next discriminating test.
7. No architecture/protocol/novelty claim is made without satisfying the promotion gate.

Current acceptance:

PASS WITH OPEN RESEARCH GAPS

This is a delivery-ready research package, not a finished architecture.
