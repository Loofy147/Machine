# Substrate Interpreter v0.2 — Same-Representation Control

Purpose: isolate direct relation access from representation differences.

Both S1 and S2 receive the same persistent relation representation:

    state["rel"] = mapping(key -> value)

S1 may use only generic state read, comparison, branching, and iteration over that mapping.

S2 has the same S1 contract plus direct indexed relation lookup.

The target/query is revealed only online. No target-specific offline state is introduced.

Offline construction and stored entry count are reported separately.

The decisive comparison is therefore:

    same information
    same persistent representation
    same timing
    same correctness
    different access primitive

Interpretation boundary:
This remains one experimental interpreter and a finite five-query fixture. It is evidence for the explicit contract, not proof about the canonical Machine substrate.
