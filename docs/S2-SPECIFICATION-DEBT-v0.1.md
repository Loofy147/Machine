# S2 Specification Debt v0.1

Recorded: 2026-09-19
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0

## Question

What is the canonical semantic definition of S2?

## Current disposition

OPEN / SPECIFICATION DEBT

The current evidence does not establish a canonical S2 specification. It establishes an experimental profile of the concrete implementation currently labeled S2.

## What is established by evidence

The experimental implementation named S2 is:

    S1 + relation_lookup_direct

with matched persistent relation representation and explicit abstract access accounting.

Those facts are implementation/protocol facts, not yet the semantic definition of S2.

## What remains to be specified independently

A proper S2 specification must determine, independently of the current implementation:

- whether S2 denotes a direct indexed relation-access primitive specifically, or a broader class of indexed access;
- whether relation is a first-class object-language value or a host-language Mapping;
- whether lookup has defined behavior for missing keys, duplicate keys, NIL-valued entries, and arbitrary values;
- whether lookup is semantically read-only;
- whether access cost is part of S2 semantics or belongs solely to the resource model;
- whether S2 adds only access capability or may include an associated representation invariant/index;
- which timing constraints apply to the representation/index;
- what the minimal S2 extension is relative to S1.

## Non-circularity requirement

The experimental S2 profile must not be used as the specification and then used again as evidence that the implementation satisfies that same specification.

The correct direction is:

    independent S2 specification
            ↓
    implementation / tests
            ↓
    experimental evidence
            ↓
    specification verification or revision

## Current relation to the profile

The experimental profile is docs/S2-EXPERIMENTAL-SUBSTRATE-PROFILE-v0.1.md.
This document records the unresolved canonical specification question.

## Next discriminating action

Define a candidate S2 specification independently, then construct the smallest implementation and property suite capable of falsifying it before classifying the experimental profile as canonical.