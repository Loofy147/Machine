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

## Replay

Commands:

    python -m pytest -q
    python run_audit.py

Observed:

    pytest = 5 passed
    audit exit = 0
    semantic_equivalence = true

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

This is still not a computability-power separation.

## Remaining limits

- one CEK-style interpreter;
- one finite mapping;
- five queries;
- abstract tick model;
- no asymptotic proof;
- canonical Machine substrate still not identified with this experimental substrate.
