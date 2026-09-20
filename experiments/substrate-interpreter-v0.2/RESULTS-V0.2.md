# Substrate Interpreter v0.2 — Results

Status: EXPERIMENTALLY_SUPPORTED / POST-REPAIR CI REPLAY
Branch: research/substrate-interpreter-v0

## Post-repair verification

The candidate-spec-derived semantic suite now executes 13 tests, covering all 15 matrix IDs through shared assertions. The implementation property suite executes 8 tests. GitHub Actions run #14 (`35534437003`) passed both suites, the updated audit, and the canonical vector comparison.

The current candidate source `docs/S2-CANDIDATE-SPEC-v0.3.md` remains PRE-FREEZE; this report therefore does not claim frozen/canonical S2 conformance.

## Semantic target repair

The pre-repair target conflated absent keys with present NIL-valued keys. The repair uses disjoint concrete results:

    RelationLookupMiss
    RelationLookupHit(value)

The candidate specification was not changed.

The strengthened semantic suite now includes:

- oracle-backed ordinary Hit/Miss expectations;
- adversarial Miss versus Hit(NIL) separation;
- explicit non-equivalent Eq_K keys;
- two concrete Mapping representations for C13;
- an information-boundary test with irrelevant hidden state;
- invalid relation/key boundary tests for C15.

## Resource replay

The experiment now maps explicitly to `(B_off,R,B_on,C_access)`:

    B_off = 5
    R = 5 stored entries

    S1: B_on = 676, C_access = 291
    S2: B_on = 20,  C_access = 10

Workload outputs remain:

    [40, 0, 20, NIL, 30]

Ratios remain:

    transition = 33.8x
    access     = 29.1x

`B_off` is measured by the explicit fixture construction loop at one abstract construction unit per inserted entry. It is an experiment accounting unit, not physical runtime cost.

The CI gate canonicalizes old/new result documents to the numeric vector plus semantic observations and now fails on drift. Run #14 returned `EQUAL=True`.

Artifact: `10612023877`.

## Evidence boundaries

Supported for the current experiment:

- repaired Miss/Hit(NIL) distinction;
- current candidate-spec executable obligations;
- current finite resource-vector replay;
- finite same-representation resource comparison.

Still open:

- frozen/canonical S2 conformance;
- canonical Machine substrate correspondence;
- asymptotic complexity theorem;
- universal computability-power separation;
- general representation closure.
