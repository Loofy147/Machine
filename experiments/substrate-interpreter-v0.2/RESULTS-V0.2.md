# Substrate Interpreter v0.2 — Results

Status: EXPERIMENTALLY_SUPPORTED / POST-REPAIR CI REPLAY
Branch: research/substrate-interpreter-v0

## Correction from v0.1

v0.1 compared direct lookup with an explicitly indexed relation representation. That left a representation confound.

v0.2 keeps the same persistent mapping in S1 and S2. The only substrate difference is:

S1:
    state_read + iteration + comparison + branching

S2:
    S1 + direct indexed relation lookup

## Target conformance correction

The pre-repair S2 target encoded both an absent key and a present key with value NIL as the same concrete result. Source inspection established that this violated the candidate semantic algebra:

    Miss | Hit(v)

The target was minimally repaired to use disjoint concrete encodings:

    RelationLookupMiss
    RelationLookupHit(value)

The abstract specification in `docs/S2-CANDIDATE-SPEC-v0.3.md` was not changed.

## Post-repair replay

The spec-derived conformance suite was replayed unchanged on commit:

    6100337bb75bd180c75ac874ea1021d3bd69c792

CI result:

    11 passed
    process exit = 0

The suite derives its assertions from the frozen semantic contract. The conformance matrix contains 15 semantic requirement IDs; those requirements are exercised by the current 11 executable test cases.

The updated interpreter audit was then executed:

    python experiments/substrate-interpreter-v0.2/run_audit.py

Audit result:

    audit exit = 0
    semantic_equivalence = true

A full resource-vector comparison was performed against the committed pre-replay result.

Comparison:

    same_persistent_representation     = true / unchanged
    offline construction_ticks         = 5 / unchanged
    offline stored_entries             = 5 / unchanged

S1 object-language traversal:

    results                         = [40, 0, 20, NIL, 30]
    transition_ticks_total         = 676
    access_ticks_total              = 291

S2 direct lookup:

    results                         = [40, 0, 20, NIL, 30]
    transition_ticks_total         = 20
    access_ticks_total              = 10

Measured ratios remain:

    transition cost = 33.8x
    access cost = 29.1x

All compared resource-vector fields were exactly equal to the committed baseline.

The replay is recorded by GitHub Actions run 10 (`s2-conformance-v0`) with replay artifact `s2-conformance-replay`.

## Interpretation

Because the persistent relation representation is the same, this experiment removes the major representation confound present in v0.1.

The post-repair replay establishes that the concrete result repair restores the required semantic distinction without changing the measured resource vector in this experiment.

The observation therefore supports a narrower statement:

Direct indexed lookup can provide a strong resource advantage over generic traversal under an otherwise matched substrate contract, without changing the observed relation semantics.

The S2 property/conformance suite additionally pins the current contract surface:

- S2 is additive over S1;
- tested S1 programs preserve result and machine-state contents under S2;
- direct lookup is explicitly charged;
- direct lookup is read-only for the current dict-backed fixture;
- the repaired target distinguishes missing keys from valid NIL-valued hits at the concrete boundary;
- the direct primitive itself performs no preprocessing.

This is still not a computability-power separation.

## Evidence disposition

The earlier resource evidence may remain active because the full replay reproduced the stored vector exactly.

The post-repair semantic conformance claim is now experimentally supported by execution, not merely by source inspection.

## Remaining limits

- one CEK-style interpreter;
- one finite mapping;
- five benchmark queries;
- property tests cover only the current implementation surface;
- abstract tick model;
- host-language Mapping/get semantics remain part of the implementation boundary;
- no asymptotic proof;
- canonical Machine substrate still not identified with this experimental substrate.
