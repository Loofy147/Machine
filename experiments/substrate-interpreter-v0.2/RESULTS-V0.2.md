# Substrate Interpreter v0.2 — Results

Status: EXPERIMENTALLY_SUPPORTED / LOCAL REPLAY
Branch: research/substrate-interpreter-v0

## Correction from v0.1

v0.1 compared direct lookup with an explicitly indexed relation representation. That left a representation confound.

v0.2 keeps the same persistent mapping in S1 and S2. The only substrate difference is:

S1:
    state_read + iteration + comparison + branching

S2:
    S1 + direct indexed relation lookup

## Baseline replay

Commands:

    python -m pytest -q
    python run_audit.py

The original five-test baseline recorded:

    pytest = 5 passed
    audit exit = 0
    semantic_equivalence = true

After adding the S2 property tests, a reconstructed replay of the exact source files at the recorded branch ref produced:

    property suite = 8 passed
    process exit = 0

This reconstructed replay executed the fetched repository source in a clean temporary directory. It is not a GitHub Actions run; no workflow run was registered for the commit.

Five online queries:

    [k4, k0, k2, missing, k3]

Results:

    [40, 0, 20, NIL, 30]

S1 object-language traversal:

    transition_ticks = 676
    access_ticks = 291

S2 direct lookup:

    transition_ticks = 20
    access_ticks = 10

Offline representation:

    construction_ticks = 5
    stored_entries = 5

Measured ratio:

    transition cost = 33.8x
    access cost = 29.1x

## Interpretation

Because the persistent relation representation is the same, this experiment removes the major representation confound present in v0.1.

The observation therefore supports a narrower statement:

Direct indexed lookup can provide a strong resource advantage over generic traversal under an otherwise matched substrate contract, without changing the observed relation semantics.

The added property suite further pins the S2 contract:

- S2 is additive over S1;
- tested S1 programs preserve result and machine-state contents under S2;
- direct lookup is explicitly charged;
- direct lookup is read-only for the current dict-backed fixture;
- missing keys return NIL;
- the direct primitive itself performs no preprocessing.

This is still not a computability-power separation.

## Remaining limits

- one CEK-style interpreter;
- one finite mapping;
- five benchmark queries;
- property tests cover only the current implementation surface;
- abstract tick model;
- host-language Mapping/get semantics remain part of the implementation boundary;
- no asymptotic proof;
- canonical Machine substrate still not identified with this experimental substrate.
