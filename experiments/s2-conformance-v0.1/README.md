# S2 Conformance v0.1

This package derives conformance tests from `docs/S2-CANDIDATE-SPEC-v0.3.md`.

## Separation

Semantic oracle:

    specification -> abstract expected result

Target adapter:

    concrete target -> declared abstract representation

Current experimental S2 is only one target. Its implementation details are not normative.

## Required adapter contract

A target adapter must implement the semantic operation:

    lookup(relation, key) -> AbstractResult

where:

    AbstractResult = Miss | Hit(value)

and declare its Eq_K semantics.

The adapter must not infer `Miss` from the input relation's membership after receiving an ambiguous concrete result. Doing so would hide an output-encoding defect.

## Current target

The first target is the experimental CEK-style interpreter in:

    experiments/substrate-interpreter-v0.2/

The target-specific adapter is intentionally kept separate from the semantic tests.

## Expected disposition

The suite can produce:

    PASS
    FAIL
    ADAPTER-DEFECT
    SPECIFICATION-DEFECT

A target failure does not modify the semantic specification.