# M2 Representation-Level Closure v0.1

Status: **EXPERIMENT / DECISION SUPPORT**

This experiment strengthens the A↔M discriminator by replacing bucket-list mutation with
an explicit fixed-capacity mutable state representation.

The representation is ordinary state containing:

- target heads;
- next/previous links;
- source/action payloads;
- source/action → slot mapping;
- free-list metadata.

Capacity is fixed at (S\Sigma), so dynamic allocation is represented as ordinary state
and does not require an external allocator primitive.

## Question

Can M2 dynamic inverse-fiber maintenance be expressed under:

`A1_RW = generic indexed reads + writes + arithmetic + finite iteration`

without a relation-specific semantic update primitive?

## Result interpretation

If the experiment closes, the claim supported is existential:

> There exists a mutable inverse representation whose maintenance can be expressed using
> generic state addressing, without adding inverse-fiber semantics to the primitive set.

That is stronger than the earlier bucket model because allocation and unlink/relink metadata
are explicit ordinary state.

It still does **not** establish that the specific contiguous CSR representation of Rev 2.1
supports M2 with the same representation or resource cost.

## Required production consequence

The production contract must therefore expose at least one of:

- generic mutable state addressing + an admitted mutable representation strategy; or
- a structured mutation primitive such as the Rev 2.1 dynamic-index path.

The distinction is resource-level unless the structured operation itself is semantically
necessary.

## Evidence boundary

All predecessor queries and index invariants are checked after every committed update.
The same update sequence is applied to A1_RW and A2 replicas.

No wall-clock result is used for classification.
