# S2 Conformance and Frontier Protocol v0.2

Recorded: 2026-09-19
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0
Status: DRAFT
Supersedes: docs/S2-CONFORMANCE-FRONTIER-PROTOCOL-v0.1.md
Semantic source: docs/S2-CANDIDATE-SPEC-v0.3.md
Decision record: docs/S2-SEMANTIC-DECISIONS-v0.1.md

## 1. Purpose

This document defines how implementations are checked against the S2 semantic contract and how separate frontier/resource experiments are controlled.

It is not the semantic definition of S2.

## 2. Semantic conformance layer

A target must declare:

- a concrete relation representation;
- a concrete key-domain representation;
- a concrete value representation;
- a concrete encoding of Miss and Hit(v);
- a mapping from the concrete equality mechanism to Eq_K.

Conformance is evaluated against the abstract domains and operations in the semantic specification.

## 3. Equality conformance

The target's concrete key comparison must implement an Eq_K satisfying the declared equivalence laws.

Conformance must test:

- reflexivity;
- symmetry;
- transitivity;
- lookup invariance across Eq_K-equivalent keys;
- distinction between non-equivalent keys.

Value equality is not required for S2 lookup unless another surrounding contract introduces it.

## 4. Partial relation conformance

Missing associations are normal semantic cases:

    no Eq_K-equivalent key -> Miss.

Invalid/non-relation inputs are outside the semantic core and must be handled by a declared substrate/input contract.

An unknown or incomplete association must not be silently treated as Miss unless that mapping is explicitly part of a separate contract.

## 5. Read-only conformance

Conformance checks preservation of the abstract relation:

    R_after = R_before.

The target may mutate internal caches, indexes, counters, or other auxiliary state.

Such effects are not semantic violations unless they change the abstract relation or result.

## 6. Required semantic cases

At minimum test:

- hit;
- miss;
- Eq_K-equivalent keys;
- non-equivalent keys;
- values from multiple valid value classes;
- value encodings resembling miss;
- repeated lookup;
- empty relation;
- multiple relations;
- representation variants denoting the same abstract relation.

## 7. Frontier controls

Any resource experiment must freeze separately:

    information available
    representation
    construction timing
    key/target revelation timing
    executor
    correctness contract
    resource accounting.

Target-dependent preprocessing must remain subject to the declared timing contract.

This is a frontier validity rule, not S2 semantic behavior.

## 8. Resource accounting

For a resource comparison, record at least:

    B_off
    R_size
    B_on
    C_access

and define which operations contribute to each component.

Direct access cannot be treated as free information.

An abstract tick model is an experimental accounting contract, not an asymptotic theorem.

## 9. S1 derivability experiment

The question:

    Can S1 derive the S2 semantic operation?

is separate from conformance.

Procedure:

1. freeze the concrete S1 substrate contract;
2. implement a lookup target using only S1-admissible operations;
3. check semantic conformance against the frozen S2 specification;
4. compare resource accounting with a direct S2 target;
5. report derivability and resource results separately from S2 semantics.

## 10. Evidence separation

Current experimental S2 artifacts remain implementation profiles/evidence.

They cannot retroactively define S2.

Semantic source:

    docs/S2-CANDIDATE-SPEC-v0.3.md

Experimental profile:

    docs/S2-EXPERIMENTAL-SUBSTRATE-PROFILE-v0.1.md

## 11. Decision outputs

The protocol may report separately:

    semantic_conformance
    Eq_K_conformance
    S1_derivability
    resource_advantage
    representation_closure
    substrate_extension_status

None of these outputs substitutes for the semantic specification.