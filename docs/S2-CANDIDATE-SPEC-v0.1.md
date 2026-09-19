# S2 Candidate Specification v0.1

Recorded: 2026-09-19
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0
Status: CANDIDATE SPECIFICATION / PRE-IMPLEMENTATION FREEZE

## 0. Provenance rule

This specification is intentionally written independently of the properties of any current S2 implementation.

No implementation artifact, host-language type, current benchmark result, current tick count, or current test property is normative for this document.

After this document is frozen, implementations are conformance targets. Implementation evidence may show that the specification is satisfied, violated, under-specified, or in need of revision; it must not silently redefine the specification.

## 1. Scope

S2 specifies an abstract relation-access capability that augments a substrate capable of evaluating expressions over an already available relation.

S2 is concerned with the semantic contract of relation access and with the information/access boundary exposed by that contract.

Representation choices, host-language data structures, compilation strategy, indexing layout, caching strategy, and concrete cost-accounting units are non-normative unless explicitly adopted by a later resource contract.

## 2. Abstract domains

Let:

    K = key domain
    V = value domain
    R = relation domain

A relation is an abstract finite mapping:

    R : K ⇀ V

where ⇀ denotes a partial function.

The specification does not prescribe how R is represented or stored.

## 3. S2 primitive

S2 provides one abstract operation:

    lookup(R, k)

for R ∈ R and k ∈ K.

The operation has two semantic outcomes:

    hit(v)     when R(k) = v
    miss       when k is outside dom(R)

The miss result is an abstract semantic outcome. Its concrete encoding is implementation-defined and must not be assumed to be any particular host-language or object-language sentinel.

## 4. Semantic determinism

For a fixed relation R and key k, lookup(R,k) has exactly one semantic outcome:

    if k ∈ dom(R), return hit(R(k));
    otherwise, return miss.

No other semantic behavior is required or permitted by this specification.

## 5. Information boundary

S2 does not create information about R or k.

The operation may access information already contained in the supplied relation R and the supplied key k.

S2 does not require or imply access to:

- a relation not supplied to the operation;
- hidden predecessor/successor state outside R;
- future target information;
- an auxiliary representation not included in the declared input.

## 6. Timing boundary

For frontier experiments, the relation R and key k have an explicit availability point.

S2 lookup is an online operation performed after that availability point.

Any construction, transformation, indexing, compression, caching, or preprocessing of R that occurs before the availability point belongs to the declared representation/preprocessing mechanism, not to the semantic definition of lookup itself.

A conformance target must not move target-dependent work into the pre-availability phase while claiming S2 semantics are unchanged.

## 7. State effect

lookup is semantically observational with respect to the supplied relation:

    lookup(R,k) does not change R.

The specification does not require a particular machine-store discipline. A conforming implementation may use internal state, provided the externally observable S2 semantics remain unchanged.

## 8. Relation identity

The relation supplied to lookup is the semantic object being queried.

S2 does not specify or require that the relation be stored as:

- an array;
- a hash table;
- a tree;
- a reverse index;
- a graph object;
- a host-language Mapping;
- any other concrete structure.

Any such structure is an implementation choice.

## 9. Duplicate associations

A relation in this specification is a partial function, not an ordered multimap.

For each key k, at most one value R(k) exists semantically.

If a target representation permits duplicate physical entries, conformance requires an explicitly defined representation invariant or construction rule that yields a single abstract relation before lookup semantics are observed.

S2 itself does not define a duplicate-resolution policy.

## 10. Values and miss

Values are opaque elements of V to the lookup primitive.

The primitive does not assign special semantic meaning to any particular value.

In particular, a valid stored value may be any element of V; miss is a distinct semantic outcome and must remain distinguishable from every valid value.

## 11. Composition

S2 lookup may be composed with the surrounding substrate's existing computation.

Composition may use the result of lookup to:

- branch;
- construct another value;
- perform further relation accesses;
- invoke other substrate operations;
- terminate with an observation/result.

Those surrounding operations are not part of the S2 lookup primitive unless independently specified by the substrate.

## 12. Failure conditions

The following are outside the normal lookup semantics:

- supplying an object that is not a relation;
- supplying an invalid key representation for the declared key domain;
- violating representation invariants required by a separate implementation contract;
- exceeding a separately declared resource budget.

A conforming implementation must define how such invalid executions are surfaced, but the particular error encoding is outside this candidate semantic core.

## 13. S1 relationship

S2 is intended as an access-level extension relative to an S1 substrate.

The candidate specification does not assume that S1 can derive lookup.

It also does not assume that S1 cannot derive lookup.

That question is deliberately external to the S2 semantic definition and is decided by conformance and derivability experiments.

Therefore:

    S2 semantics != claim about S1 expressibility

## 14. Resource separation

Semantic correctness and resource cost are separate obligations.

A later resource contract may define quantities such as:

    C_lookup(R,k)
    B_on
    B_off
    R_size

but no concrete cost unit is fixed here.

In particular, this candidate specification does not assert:

- O(1) lookup;
- one machine tick;
- one host operation;
- any particular asymptotic bound.

Those are resource hypotheses to be specified and tested separately.

## 15. Conformance observations

A conforming implementation must demonstrate at minimum:

1. hit correctness: lookup returns the abstract value for every tested present key;
2. miss correctness: absent keys produce the distinct miss outcome;
3. relation preservation: lookup does not semantically mutate the queried relation;
4. value opacity: arbitrary valid values remain valid lookup results;
5. timing discipline: the operation does not obtain information unavailable at its declared invocation point;
6. representation independence: concrete storage layout is not observable through the S2 semantic result;
7. determinism: repeated lookup over the same abstract R and k has the same semantic outcome.

These are conformance obligations derived from this specification, not observations about a particular implementation.

## 16. Non-goals

This specification does not define:

- the canonical Machine substrate;
- the concrete interpreter architecture;
- the concrete object-language syntax;
- the physical/index representation;
- preprocessing policy;
- memory layout;
- asymptotic complexity;
- performance thresholds;
- a theorem that S2 adds absolute computability.

## 17. Candidate decision boundary

The candidate S2 abstraction is satisfied when an implementation realizes the abstract operation lookup(R,k) with the semantics above.

Whether the implementation is:

- derivable from S1;
- a more efficient realization of an S1 computation;
- a distinct substrate operation;
- resource-dominant under a given budget;
- or representation-closed under another substrate

is not decided by this specification.

Those are separate research questions.

## 18. Freeze protocol

Once this candidate specification is accepted for the conformance round:

    specification
        ↓
    conformance targets
        ↓
    tests/evidence
        ↓
    pass / fail / specification defect

An implementation property that is absent from this document is not normative merely because an existing S2 implementation happens to have it.

Conversely, a requirement in this document must be tested even if no current implementation currently exposes it.

## 19. Current status

    semantic S2 candidate = DRAFT / PRE-IMPLEMENTATION FREEZE
    implementation conformance = NOT YET ASSESSED
    canonical Machine S2 = OPEN
    S1 derivability of S2 = OPEN
    resource classification = OPEN