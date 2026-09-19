# S2 Conformance and Frontier Protocol v0.1

Recorded: 2026-09-19
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0
Status: DRAFT / DERIVED FROM S2-CANDIDATE-SPEC-v0.2

## 1. Purpose

This document is not the S2 semantic definition.
It defines how a concrete implementation is evaluated against the S2 semantic core and, separately, how S2 is compared under a resource/frontier experiment.

Normative semantic source:

    docs/S2-CANDIDATE-SPEC-v0.2.md

Frontier alignment source:

    docs/SUBSTRATE-FRONTIER-CONTRACT-v0.1.md

## 2. Conformance layer

A target implementation must expose a concrete operation corresponding to abstract:

    lookup(R,k)

and provide a declared mapping from its concrete relation/result representation to the abstract domains Rel, K, V and LookupResult(V).

The target passes semantic conformance when its observations match the abstract specification for the declared valid domain.

## 3. Required semantic tests

Minimum tests derived from the specification:

- present-key hit;
- absent-key miss;
- multiple valid value forms;
- value equal/equivalent to a concrete implementation sentinel;
- repeated lookup on unchanged R;
- multiple relations;
- empty relation;
- preservation of the abstract relation.

An implementation-specific test that is not derivable from the specification is diagnostic, not normative.

## 4. Representation rule

Concrete auxiliary structures are permitted.

A target may use indexes, caches, compiled forms, or other internal representations.

Such structures must not change the abstract result for a valid (R,k) pair.

Representation choice therefore belongs to the implementation profile and resource contract, not to S2 semantics.

## 5. Timing/frontier rule

For any frontier experiment, freeze separately:

    information available
    representation
    construction timing
    query/target revelation timing
    online executor
    correctness criterion
    resource accounting

Target-dependent preprocessing must not be counted as offline construction if the experimental contract requires the target to be unknown during preprocessing.

This is a frontier validity rule, not a semantic property of lookup.

## 6. Resource rule

Semantic conformance is necessary but does not by itself imply a resource claim.

For a resource experiment, record at least:

    B_off
    R_size
    B_on
    C_access

and state exactly which operations contribute to each component.

A direct-access primitive must not receive uncharged information merely because its implementation exposes it as a primitive.

An abstract tick count is an experimental cost model, not an asymptotic theorem.

## 7. Matched-pair rule

When testing whether direct access changes only resource position, use a minimal pair in which the following are held constant:

- abstract information;
- relation semantics;
- representation, when representation is not the variable under study;
- timing of information/query availability;
- correctness contract;
- surrounding executor;
- declared resource accounting.

The treatment changes only the access mechanism under investigation.

## 8. S1/S2 derivability experiment

The question:

    Can S1 derive the S2 semantic operation?

is separate from conformance.

Procedure:

1. establish the concrete S1 substrate contract;
2. implement lookup using only S1-admissible operations;
3. verify semantic conformance against the frozen S2 specification;
4. compare resource accounting with the direct S2 target;
5. keep the resulting classification separate from the S2 semantic definition.

## 9. Evidence status

Current experimental S2 results are evidence about an implementation profile.
They do not retroactively define S2.

Current profile:

    docs/S2-EXPERIMENTAL-SUBSTRATE-PROFILE-v0.1.md

Canonical Machine status:

    conformance = OPEN

## 10. Decision outputs

The protocol may produce separate outputs:

semantic_conformance
derivability_from_S1
resource_advantage
representation_closure
substrate_extension_status

None of these outputs may be substituted for the semantic definition itself.