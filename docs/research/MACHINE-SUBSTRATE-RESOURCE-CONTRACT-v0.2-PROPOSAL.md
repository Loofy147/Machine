# Machine Substrate Resource Contract v0.2 — Mutation Coupling Proposal

Status: **PROPOSED / NOT FROZEN**

## Why v0.2 exists

v0.1 correctly separated state addressing (A) from mutation (M), but A1 was defined only
as a read capability. That is enough for M0 and compatible with M1 batch rebuilds, but it is
not enough to characterize M2 dynamic maintenance.

The ambiguity is:

> Does "generic random access" mean read-only addressing, or read/write addressing?

v0.2 therefore makes the coupling explicit without modifying the frozen v0.1 schema.

## Proposed access tuple

For v0.2, treat A as:

```
A = (A_r, A_w)
```

where:

- `A_r ∈ {A0_OPAQUE, A1_RANDOM_ACCESS, A2_SPECIALIZED_INDEX}`
- `A_w ∈ {W0_NONE, W1_GENERIC_CELL_WRITE, W2_STRUCTURED_UPDATE}`

Interpretation:

- `W0_NONE`: state representation is not writable through the machine substrate.
- `W1_GENERIC_CELL_WRITE`: ordinary addressable cells can be read/written.
- `W2_STRUCTURED_UPDATE`: the substrate exposes an operation that preserves the
  declared derived-index invariant as part of the update.

This is deliberately a contract dimension, not an implementation requirement.

## Mutation compatibility

### M0_STATIC

Requires only the read side of A.

### M1_BATCHED

Requires:
- mutation authority outside the query path;
- explicit rebuild/materialization;
- charged rebuild work `B_off`;
- no promise of index validity between rebuild boundaries.

A1 read-only can therefore coexist with M1 only when rebuild is explicitly outside
the read substrate contract.

### M2_DYNAMIC

Requires the substrate to express and account for every committed update.

Two legitimate constructions exist:

1. `A1_RANDOM_ACCESS + W1_GENERIC_CELL_WRITE` plus ordinary state operations that
   can maintain the derived representation;
2. `A2_SPECIALIZED_INDEX + W2_STRUCTURED_UPDATE`.

The important point is that M2 does not automatically imply A2. It implies a **write/update
surface** strong enough to preserve the access invariant.

## Promotion rule

Do not classify A2 as necessary merely because Rev 2.1 provides P-05.

First ask whether the required M2 update can be expressed under A1+W1 without importing
specialized inverse semantics.

Conversely, do not classify A1 as sufficient for M2 merely because A1 read queries close.

## Required evidence

A production contract claiming M2 must report, per update:

- source state mutation;
- derived-index mutation;
- consistency point;
- `B_on/update`;
- persistent representation delta;
- correctness after the commit.

The v0.2 discriminator tests these conditions structurally.

## Experimental support added\n\nThe follow-up M2 representation experiment now provides a stronger existence test: a fixed-capacity mutable inverse representation using only ordinary mutable state links and generic addressing can preserve predecessor correctness after every committed update. The local replay covered 100 cases and 19,720 updates with zero semantic/invariant failures. This supports A1+generic-write closure as an existence result, while leaving the resource cost and exact compatibility with Rev 2.1 CSR open.\n\n## Current relationship to Rev 2.1

The existing concrete instance remains:

- read profile: A2_SPECIALIZED_INDEX;
- inverse read: P-05;
- dynamic mutation: documented as a separate M2 variant.

v0.2 does not reclassify Rev 2.1. It determines what additional coupling information
is needed before choosing a production contract.

## Gate

No production profile is frozen until:

1. A_r is fixed;
2. A_w is fixed;
3. M0/M1/M2 applicability is fixed;
4. derived-state consistency boundary is fixed;
5. the complete `(B_off,R_extra,B_on)` frontier is reported.
