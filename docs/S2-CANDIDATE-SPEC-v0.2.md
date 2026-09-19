# S2 Candidate Specification v0.2

Recorded: 2026-09-19
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0
Status: CANDIDATE SPECIFICATION / PRE-FREEZE
Supersedes: docs/S2-CANDIDATE-SPEC-v0.1.md

## 0. Provenance and non-circularity

This specification is authored independently of the current experimental S2 implementation and of its observed property suite.

No host-language type, primitive name, sentinel, benchmark result, tick count, storage layout, or implementation-specific behavior is normative merely because an existing target happens to exhibit it.

After semantic freeze, implementations are conformance targets. Evidence may establish conformance, non-conformance, or specification defects. Evidence must not silently redefine the semantic contract.

## 1. Semantic scope

S2 specifies the semantics of an abstract relation-access operation.

The semantic core intentionally does not define:

- machine architecture;
- programming-language syntax;
- representation or indexing layout;
- preprocessing;
- timing of construction;
- resource units or complexity;
- implementation strategy;
- whether S1 can derive the operation.

Those concerns belong to separate contracts.

## 2. Abstract domains

Let:

    K = key domain
    V = value domain
    Rel = relation domain

A relation is a partial function:

    R : K ⇀ V

Finiteness is not part of the semantic definition. A finite-only restriction, if required by a particular task or frontier experiment, must be stated by that external contract.

The relation is an abstract mathematical object. No concrete representation is implied.

## 3. Core operation

S2 defines:

    lookup(R, k)

for R ∈ Rel and k ∈ K.

The result space is the disjoint sum:

    LookupResult(V) = Miss | Hit(v)

with:

    lookup(R,k) = Hit(R(k))   when k ∈ dom(R)
    lookup(R,k) = Miss        when k ∉ dom(R).

`Miss` is a semantic outcome distinct from every `Hit(v)`.

A conforming implementation may encode these outcomes in any way, provided the encoding preserves the abstract distinction.

## 4. Determinism

For a fixed abstract relation R and key k, lookup(R,k) has exactly one semantic result.

Repeated evaluation against the same abstract R and k is semantically equivalent unless an external substrate contract explicitly changes R between evaluations.

## 5. Abstract state effect

lookup is observational with respect to the abstract relation:

    R_after = R_before

at the semantic level.

Internal implementation state may change for any reason that is invisible at the specified semantic boundary.

The specification therefore constrains the abstract relation, not the internal machine store.

## 6. Value opacity

Values in V are opaque to lookup.

lookup does not inspect, normalize, rank, compare, or otherwise assign special semantic meaning to a value merely because it is a value.

A valid value remains a valid `Hit(v)` result even when v resembles a concrete miss sentinel used by some implementation; the implementation must maintain the abstract distinction between `Miss` and `Hit(v)`.

## 7. Relation uniqueness

Because R is a partial function, an abstract key has at most one associated value.

S2 does not define how an implementation constructs an abstract relation from a physical structure that contains duplicate entries.

Any duplicate-resolution policy belongs to the representation/construction contract that produces the abstract R presented to lookup.

## 8. Representation abstraction

The semantics of lookup are independent of whether R is represented by:

- an array;
- a hash table;
- a tree;
- a reverse index;
- a graph structure;
- a database index;
- a host-language object;
- or another implementation structure.

An implementation may maintain auxiliary representation, caches, or indexes internally, provided the externally observed operation conforms to the abstract lookup semantics.

This specification does not grant or deny any particular auxiliary representation.

## 9. Information boundary

lookup receives exactly two semantic inputs: the abstract relation R and key k.

The operation is not defined to obtain semantic information from an undeclared relation or from hidden domain state outside those inputs.

An implementation may maintain auxiliary internal state, but auxiliary state cannot alter the abstract result for the same R and k.

This section constrains semantic inputs, not the physical implementation mechanism.

## 10. Invalid inputs

The semantic domain of lookup is restricted to valid pairs (R,k) with R ∈ Rel and k ∈ K.

Behavior for values outside those domains is unspecified by this core specification.

Validation, error reporting, exceptions, traps, and diagnostics are implementation or substrate concerns unless a separate contract specifies them.

## 11. Composition boundary

The result of lookup may be consumed by the surrounding substrate.

For example, the substrate may branch on `Miss` versus `Hit(v)`, extract v, construct another value, perform another lookup, or terminate with an observation.

Those surrounding operations are not themselves part of the S2 semantic core.

## 12. Relationship to S1

S2 is an abstract access capability intended to be comparable with an S1 substrate.

This specification deliberately makes no claim that:

- S1 can derive lookup;
- S1 cannot derive lookup;
- direct lookup is computationally stronger than S1;
- direct lookup is merely an optimization.

Those are external scientific questions to be answered by derivability and resource experiments.

Therefore:

    S2 semantic definition != S1 expressibility claim

## 13. Resource separation

Semantic conformance does not imply any particular resource bound.

A separate resource contract may define:

    C_access
    B_off
    R_size
    B_on

or another declared resource vector.

This candidate specification makes no claim about:

- O(1) lookup;
- constant machine ticks;
- constant host operations;
- asymptotic complexity;
- storage overhead;
- preprocessing cost.

## 14. Semantic conformance criterion

An implementation conforms to S2 when, for every valid tested abstract pair (R,k), its externally observable result is equivalent to:

    lookup(R,k)

under the result abstraction `Miss | Hit(v)`, and the abstract relation remains unchanged by the operation.

The conformance mapping must be stated when the implementation uses a concrete result encoding.

Conformance tests should include:

- present keys;
- absent keys;
- values from multiple valid value classes;
- values that resemble any concrete implementation sentinel;
- repeated lookups;
- relations containing multiple entries;
- relations with empty domains.

These are tests derived from this specification, not observations imported from the current S2 implementation.

## 15. Non-goals

This specification does not define:

- the canonical Machine interpreter;
- S1 or its concrete primitive alphabet;
- a particular object-language syntax;
- host-language types;
- a concrete relation representation;
- offline preprocessing policy;
- target-revelation timing;
- access-cost accounting;
- performance thresholds;
- a computability-separation theorem.

## 16. Separation from frontier protocol

The semantic core above answers:

    What does S2 lookup mean?

A separate frontier/conformance protocol must answer:

    When is R available?
    When is k revealed?
    Is preprocessing allowed?
    What representation/storage budget is allowed?
    What online work is charged?
    What access cost is charged?
    Which auxiliary structures are admissible?

Those protocol choices must be frozen before making resource-frontier claims.

The current governing reference for those questions is:

    docs/SUBSTRATE-FRONTIER-CONTRACT-v0.1.md

## 17. Freeze rule

Once the semantic core is accepted:

    S2 specification
        ↓
    derive conformance obligations
        ↓
    select implementation targets
        ↓
    execute tests
        ↓
    classify PASS / FAIL / SPECIFICATION-DEFECT

Implementation properties absent from this specification are non-normative.

Specification requirements not present in an implementation are conformance failures or specification defects; they are not to be removed merely to match an existing target.

## 18. Current status

    semantic S2 candidate = DRAFT / PRE-FREEZE
    independence from implementation = maintained
    semantic conformance = NOT YET ASSESSED
    frontier protocol alignment = REQUIRED
    canonical Machine conformance = OPEN
    S1 derivability = OPEN
    resource classification = OPEN