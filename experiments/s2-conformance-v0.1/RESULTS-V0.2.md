# S2 Conformance Results v0.2 — Experimental Target

Recorded: 2026-09-19
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0
Semantic source: docs/S2-CANDIDATE-SPEC-v0.3.md
Protocol: docs/S2-CONFORMANCE-FRONTIER-PROTOCOL-v0.2.md
Target: experiments/substrate-interpreter-v0.2/
Status: REPAIR APPLIED / CONFORMANCE EXECUTION NOT VERIFIED

## 1. Derived suite

The suite in `experiments/s2-conformance-v0.1/` is derived from the frozen candidate semantics only.

## 2. Previously identified defect

The pre-repair target encoded both an absent key and a present key with value NIL as the same concrete result.

Root expression:

    relation.get(key, NIL)

This was non-conformant with the required disjoint result algebra:

    Miss | Hit(v)

## 3. Minimal target repair

The experimental target now uses distinct concrete result encodings:

    RelationLookupMiss
    RelationLookupHit(value)

This changes concrete result representation only. It does not alter the abstract S2 semantic specification.

The audit harness normalizes these concrete results back to the benchmark-level value/NIL display without changing the conformance distinction.

## 4. Verification status

The target-side property tests, conformance suite, and audit must be replayed after the repair.

A GitHub Actions run was not registered for the latest repair commit at inspection time.

A direct local execution was not claimed because the current execution environment cannot fetch the repository over the network.

Therefore:

    semantic conformance = UNVERIFIED AFTER REPAIR
    static pre-repair non-conformance = ESTABLISHED
    specification change = NONE

## 5. Required replay

Execute unchanged:

    python -m pytest -q experiments/s2-conformance-v0.1
    python experiments/substrate-interpreter-v0.2/run_audit.py

Then record:

- conformance result;
- pytest result;
- audit result;
- resource totals;
- any new failures.

No specification change is permitted merely to make the repaired implementation pass.