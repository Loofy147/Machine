# S2 Semantic Decisions v0.1

Recorded: 2026-09-19
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0
Status: REVIEW DECISION / PRE-FREEZE
Source specification: docs/S2-CANDIDATE-SPEC-v0.2.md

## Decision 1 — S2 scope

Decision:

S2 is a **direct point-access relation capability**, not a binary-membership-only capability.

Core operation:

    lookup(R, k) -> Miss | Hit(v)

The value domain V is not restricted to booleans. Binary membership is a specialization obtained when the relation's value domain carries only presence information, or by projecting:

    present(R,k) = true  if lookup(R,k) = Hit(v)
    present(R,k) = false if lookup(R,k) = Miss.

S2 does not, by this decision, include every possible direct relation operation. Operations such as enumeration, reverse lookup, range query, predecessor-set retrieval, mutation, or aggregation require separate semantic contracts.

Rationale:
- preserves a minimal semantic core;
- permits values that encode richer relation facts;
- makes membership a derived special case rather than the definition;
- prevents scope expansion into an unconstrained 'direct relation family'.

Status: ACCEPTED FOR CANDIDATE SPECIFICATION

## Decision 2 — Equality algebra

Decision:

Define equality as a typed family of equivalence relations, not as one untyped universal primitive.

For each domain D that participates in equality:

    Eq_D : D × D -> {equal, not-equal}

with the algebraic laws:

    reflexive:  Eq_D(x,x)
    symmetric:  Eq_D(x,y) => Eq_D(y,x)
    transitive: Eq_D(x,y) and Eq_D(y,z) => Eq_D(x,z).

For S2 semantics, the required equality is the key-domain relation:

    Eq_K

and lookup membership is interpreted modulo Eq_K.

The abstract relation must therefore be extensional under key equality: equivalent keys denote the same abstract association.

Eq_D is a semantic relation/algebraic contract, not necessarily an exposed machine primitive.

No value-domain Eq_V is required merely for lookup semantics because S2 treats values as opaque.

Rationale:
- avoids hidden host-language equality assumptions;
- provides a common algebra where other typed domains later need equality;
- prevents an untyped cross-domain equality primitive from becoming accidental S2 semantics.

Status: ACCEPTED FOR CANDIDATE SPECIFICATION

## Decision 3 — Read-only boundary

Decision:

Read-only is a property of the S2 operation with respect to the abstract relation, not a requirement that the entire substrate be immutable.

Normative semantic condition:

    lookup(R,k) leaves R unchanged.

An implementation may mutate internal state, including caches, indexes, counters, compiled forms, or other auxiliary state, provided that:

- the abstract relation R is unchanged;
- the specified semantic result is unchanged;
- such internal effects are not silently treated as part of the semantic contract.

If an internal mutation becomes externally observable or changes resource accounting, it belongs to the implementation/resource profile and must be declared there.

Rationale:
- separates semantic purity from machine implementation state;
- permits legitimate caching/indexing without redefining S2;
- keeps the semantic obligation testable.

Status: ACCEPTED FOR CANDIDATE SPECIFICATION

## Decision 4 — Partiality and undefined cases

Decision:

The relation is normally partial:

    R : K ⇀ V

and missing keys are defined semantic cases:

    k ∉ dom(R) => Miss.

Therefore lookup is total over valid semantic inputs `(R,k)`.

Undefined cases are not represented by a normal S2 result. They are outside the semantic domain when:

- R is not a valid relation in Rel;
- k is not a valid element of K;
- required representation invariants have not produced a valid abstract relation.

An implementation may expose an error, trap, exception, or another substrate-specific failure for such cases, but that encoding is outside the S2 semantic core.

An incomplete or unknown relation is distinct from a partial relation. If a system needs 'unknown/unresolved association' semantics, that must be represented by an explicit domain/value extension; it must not be silently converted into Miss.

Rationale:
- distinguishes absent information from unavailable information;
- keeps the normal operation deterministic;
- prevents undefined behavior from becoming a hidden third lookup result.

Status: ACCEPTED FOR CANDIDATE SPECIFICATION

## Summary

S2 semantic core:

    abstract relation R : K ⇀ V
    typed key equality Eq_K
    lookup(R,k) -> Miss | Hit(v)
    lookup preserves R

Non-core:

    representation
    indexing strategy
    caching
    preprocessing
    timing protocol
    resource cost
    S1 derivability
    substrate mutability

Those remain separate conformance/frontier questions.