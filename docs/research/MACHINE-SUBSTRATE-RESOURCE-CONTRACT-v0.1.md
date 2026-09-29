# Machine Substrate Resource Contract v0.1

Status: **FROZEN SCHEMA / RESEARCH CONTRACT**

This document freezes the **resource-accounting schema and disclosure requirements** for
Machine substrate comparisons. It does **not** silently choose an access profile.

The abstract Machine model remains at:
`docs/ABSTRACT-MACHINE.md@f752aac015d9f837bc6a89d44eed50e0325b60a6`.

## 1. Purpose

A primitive/representation claim is valid only after the compared substrates expose the
same declared resource dimensions.

The canonical object is:

[
C_{sub} =
(A, T, D, 	au, B_{off}, R_{extra}, B_{on}, M, K)
]

where:

- (A) = **state-addressing contract**;
- (T) = **semantic transition-access contract**;
- (D) = **derived-state policy**;
- (	au) = **timing / information-reveal boundary**;
- (B_{off}) = offline construction work;
- (R_{extra}) = persistent representation cost;
- (B_{on}) = online computational work;
- (M) = mutation model;
- (K) = correctness/observability contract.

All nine dimensions are mandatory in experiment metadata.

## 2. Access profiles

The schema permits explicit profiles.

### A0 — OPAQUE

State is semantically available through declared machine operations, but internal
representation cells are not directly addressable.

A stored derived relation therefore cannot be consumed unless a declared operation
provides that access.

### A1 — RANDOM_ACCESS

The substrate exposes generic indexed reads over a declared state-address space.

A representation stored in ordinary state may be decomposed using those generic reads,
arithmetic, and finite iteration. No relation-specific semantic primitive is implied.

### A2 — SPECIALIZED_INDEX

The substrate exposes a dedicated operation whose semantics directly name the
derived relation, such as:

`fiber_lookup(u)`.

This is an explicit access capability and must never be classified as a mere
representation change unless a lower-level admitted contract can expand it without
adding that semantic operation.

## 3. Semantic vs representation rule

A **semantic primitive** changes the admitted transition relation or observable
operation semantics.

A **representation operation** changes how already-admitted information is encoded or
located.

A **resource primitive** changes the feasible cost envelope without changing the
admitted information or transition semantics.

No classification may be made from wall-clock speed alone.

## 4. Derived-state rule

Derived state is admissible only when all of the following are declared:

1. source information;
2. derivation procedure;
3. target-dependence;
4. construction timing;
5. persistent storage cost;
6. invalidation/update semantics.

For the inverse-fiber case:

[
R^{-1}=g(delta)
]

with target-oblivious (g) is a derived representation, not a new information source.

## 5. Information boundary

The experiment must distinguish:

- **I0**: no new information;
- **I1**: target-independent derived information;
- **I2**: target-dependent preprocessing;
- **I3**: external/new information source.

Only I0/I1 comparisons may support the claim that a result is due to representation/access
rather than information acquisition.

## 6. Timing boundary

The target or query may be revealed:

- **T0** before preprocessing;
- **T1** after target-oblivious preprocessing;
- **T2** before target-dependent preprocessing.

A target-oblivious index must be built at T1 or earlier.

Comparisons across timing classes are contract mismatches unless the timing cost is explicitly
included in the frontier.

## 7. Cost accounting

Every run must report:

[
(B_{off},R_{extra},B_{on})
]

with units defined before execution.

Permitted examples:

- (B_{off}): transition entries inspected / writes / arithmetic units;
- (R_{extra}): exact serialized bytes;
- (B_{on}): indexed reads, probes, iterator entries, or equivalent declared units.

Wall-clock measurements may be reported separately but cannot silently replace the structural
cost contract.

## 8. Mutation

Every representation must declare one of:

- **M0 STATIC** — no online mutation;
- **M1 BATCHED** — mutation followed by explicit rebuild/materialization;
- **M2 DYNAMIC** — updates preserve the declared access contract online.

A comparison is invalid if one side receives free rebuilds while the other is charged for updates.

## 9. Correctness

Correctness must be semantic, not merely representation-level.

For inverse fibers the required predicate is:

[
F(u)={(s,a):delta(s,a)=u}
]

with exact label/multiplicity semantics.

For derived algorithms, the final fixpoint/value/decision result must also match the designated
semantic reference.

## 10. Primitive-closure decision rule

Given a frozen contract:

### R — representation closure

If an operation can be expressed using already-admitted state access, arithmetic, iteration,
and derived-state rules, then it is **representation-level closure**.

### E — access extension

If the operation requires a capability not expressible using the admitted access contract,
then it is an **access/substrate extension**.

### F — resource-frontier shift

If semantics and admissible information are unchanged, but the representation changes
the feasible ((B_{off},R_{extra},B_{on})) set, classify it as a **resource-bounded frontier shift**.

R and F may both apply. E is separate: it indicates a changed admitted access contract.

### X — contract mismatch

If any mandatory contract axis is unaligned, the comparison is **INCONCLUSIVE / CONTRACT MISMATCH**.

## 11. Canonicality rule

This schema is canonical for **disclosure and comparison**, not for selecting one physical
access profile.

The repository must never infer A0/A1/A2 from implementation details after the fact.
A substrate declares its profile before execution.

Therefore:

> "primitive" is a property of an operation **relative to a declared substrate contract**,
> not a property that can be assigned from algorithmic speed or from implementation syntax.

## 12. Promotion gate

Do not promote a capability to the abstract Machine primitive set unless:

1. the substrate contract is frozen;
2. the operation is non-derivable under that frozen contract;
3. the access extension survives representation substitution tests;
4. the result is semantically reproducible;
5. the relevant resource frontier is explicitly reported.

This contract is deliberately implementation-neutral: no language, container, database, or storage
library is normative.
