# S2 Candidate Specification v0.3

Recorded: 2026-09-19
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0
Status: CANDIDATE SPECIFICATION / PRE-FREEZE
Supersedes: docs/S2-CANDIDATE-SPEC-v0.2.md
Decision record: docs/S2-SEMANTIC-DECISIONS-v0.1.md

## 0. Provenance and non-circularity

This specification is authored independently of current implementation properties.

No host-language type, implementation primitive, sentinel, benchmark result, tick count, storage layout, or observed property is normative merely because an existing target exhibits it.

After semantic freeze, implementations are conformance targets. Evidence may establish conformance, non-conformance, or specification defects. Evidence must not silently redefine the semantic contract.

## 1. Semantic scope

S2 specifies an abstract direct point-access capability over a relation.

S2 is not defined as binary membership alone, and it is not an unconstrained family of all direct relation operations.

The semantic core is one operation:

    lookup(R,k) -> Miss | Hit(v)

The broader scope comes from the fact that V is not restricted to booleans. Membership is a derived specialization, while other relation operations require separate contracts.

The semantic core does not define:

- machine architecture;
- programming-language syntax;
- physical representation;
- index/cache layout;
- preprocessing;
- target timing;
- resource units or complexity;
- implementation strategy;
- whether S1 can derive lookup.

## 2. Abstract domains

Let:

    K   = key domain
    V   = value domain
    Rel = relation domain

A relation is a partial function:

    R : K ⇀ V

Finiteness is not part of the semantic definition.

The abstract relation is a mathematical object, independent of storage representation.

## 3. Equality algebra

Equality used by a domain is a typed equivalence relation.

For each domain D for which semantic equality is required:

    Eq_D ⊆ D × D

with laws:

    reflexive:  x Eq_D x
    symmetric:  x Eq_D y => y Eq_D x
    transitive: x Eq_D y and y Eq_D z => x Eq_D z.

S2 requires the key-domain equality Eq_K.

Lookup membership is interpreted modulo Eq_K.

The abstract relation is extensional under Eq_K: if x Eq_K y, then either both are outside dom(R), or both are in dom(R) and denote the same abstract value.

No value-domain equality Eq_V is required merely to perform lookup, because lookup treats values as opaque.

Eq_D is a semantic algebraic contract. It need not correspond to an exposed machine primitive.

## 4. Core operation

S2 defines:

    lookup(R,k)

for R ∈ Rel and k ∈ K.

The abstract result is the disjoint sum:

    LookupResult(V) = Miss | Hit(v)

with:

    lookup(R,k) = Hit(v)  when k is Eq_K-equivalent to a key in dom(R) whose value is v;
    lookup(R,k) = Miss    when no key Eq_K-equivalent to k is in dom(R).

`Miss` is distinct from every `Hit(v)`.

An implementation may encode these outcomes in any concrete form, provided the abstract distinction is preserved.

## 5. Membership as a derived operation

Binary membership is not the definition of S2.

It is derivable from lookup:

    present(R,k) = true   iff lookup(R,k) = Hit(v) for some v
    present(R,k) = false  iff lookup(R,k) = Miss.

A relation whose codomain carries only presence information is therefore a specialization of the same lookup semantics.

S2 does not thereby include enumeration, reverse lookup, predecessor queries, successor queries, range queries, mutation, aggregation, or other relation operations.

Each such operation requires its own semantic contract.

## 6. Determinism

For a fixed abstract relation R and key k, lookup(R,k) has exactly one semantic result.

Repeated lookup against the same abstract R and k is semantically equivalent unless an external contract changes the abstract relation between evaluations.

## 7. State effect and read-only boundary

Read-only is a property of the lookup operation with respect to the abstract relation, not a requirement that the entire substrate be immutable.

Normatively:

    R_after = R_before.

An implementation may mutate internal auxiliary state, including caches, indexes, counters, or compiled forms, provided those mutations do not alter the specified abstract result or abstract relation.

If such internal effects become externally observable or affect a declared resource model, they belong to the implementation/resource profile and not to the S2 semantic core.

## 8. Value opacity

Values in V are opaque to lookup.

Lookup does not inspect, normalize, rank, compare, or assign special semantic meaning to a value merely because it is a value.

A valid stored value remains a valid Hit(v), even if a concrete implementation uses some representation that resembles its own miss encoding. The implementation must preserve the abstract distinction between Miss and Hit(v).

## 9. Relation identity and representation

The relation supplied to lookup is the abstract semantic object being queried.

S2 is representation-independent.

An implementation may represent or accelerate R using arrays, hash tables, trees, indexes, caches, graph structures, database structures, host-language objects, or other mechanisms.

Auxiliary representations are permitted, but they do not change the abstract meaning of lookup.

Duplicate physical entries do not define S2 semantics. A separate representation/construction contract must produce a valid abstract relation before conformance is evaluated.

## 10. Information boundary

lookup has exactly two semantic inputs:

    R
    k

The operation is not defined to obtain semantic information from an undeclared relation or hidden domain state outside those inputs.

Internal auxiliary state may exist, but it cannot change the abstract result for the same abstract R and k.

## 11. Partial relations and undefined cases

Partiality of the relation is a normal semantic case:

    R : K ⇀ V

If k has no Eq_K-equivalent association in R, the defined result is Miss.

Thus lookup is total over valid semantic inputs (R,k).

Undefined/out-of-domain behavior is reserved for inputs that are not members of the declared semantic domains, such as:

- an object that is not a valid relation in Rel;
- a key not in K;
- a representation that has not been converted into a valid abstract relation;
- a violated external representation invariant.

Those cases are outside the S2 semantic result algebra.

An implementation may expose an error, trap, exception, or another substrate-specific failure, but that encoding is outside the semantic core unless separately specified.

An incomplete or unknown relation is not the same as a partial relation. If the system needs an unknown/unresolved association, that requires an explicit extension to the relevant domain; it must not be silently mapped to Miss.

## 12. Composition boundary

The result of lookup may be consumed by the surrounding substrate.

The surrounding substrate may branch on Miss versus Hit(v), extract v, construct another value, perform another lookup, or terminate with an observation.

Those surrounding operations are not part of the S2 semantic core.

## 13. Relationship to S1

This S2 specification makes no claim that S1 can or cannot derive lookup.

Therefore:

    S2 semantic definition != S1 expressibility claim.

Derivability, resource equivalence, and substrate-extension status are external research questions.

## 14. Resource separation

Semantic conformance does not imply a resource guarantee.

A separate protocol may define:

    C_access
    B_off
    R_size
    B_on

or another explicit resource vector.

This specification does not assert:

- O(1) lookup;
- constant machine ticks;
- constant host operations;
- a storage bound;
- a preprocessing bound;
- an asymptotic theorem.

## 15. Semantic conformance criterion

A target conforms when, for each valid tested abstract pair (R,k), the declared concrete-to-abstract mapping yields the specified LookupResult and leaves the abstract relation unchanged.

Minimum semantic conformance classes should include:

- present key -> Hit(v);
- absent key -> Miss;
- keys related by Eq_K;
- multiple valid value forms;
- values that resemble concrete miss encodings;
- repeated lookup;
- multiple relations;
- empty relations;
- abstractly equivalent representations of the same relation.

These tests are derived from the specification.

## 16. Non-goals

This specification does not define:

- the canonical Machine interpreter;
- S1 primitive alphabet;
- object-language syntax;
- host-language types;
- concrete relation representation;
- preprocessing policy;
- target revelation timing;
- resource accounting;
- performance thresholds;
- a computability-separation theorem.

## 17. Separation from frontier protocol

The semantic core answers:

    What does S2 lookup mean?

The separate conformance/frontier protocol answers:

    When is R available?
    When is k revealed?
    Which preprocessing is admissible?
    What representation/storage budget is charged?
    What online work is charged?
    What access cost is charged?
    Which auxiliary structures are permitted for a particular comparison?

Those protocol choices are not semantic definitions of S2.

## 18. Freeze rule

Once accepted:

    S2 semantic specification
        ↓
    derive conformance obligations
        ↓
    select implementation targets
        ↓
    execute tests
        ↓
    classify PASS / FAIL / SPECIFICATION-DEFECT

Implementation properties absent from this document are non-normative.

Specification requirements absent from an implementation are conformance failures or specification defects, not reasons to silently rewrite the specification.

## 19. Current status

    semantic S2 candidate = DRAFT / PRE-FREEZE
    independent semantic decisions = recorded
    implementation conformance = NOT YET ASSESSED
    frontier protocol alignment = REQUIRED
    canonical Machine conformance = OPEN
    S1 derivability = OPEN
    resource classification = OPEN