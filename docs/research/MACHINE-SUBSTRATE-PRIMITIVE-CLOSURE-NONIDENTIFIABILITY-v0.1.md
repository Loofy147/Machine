# Primitive-Closure Non-Identifiability at the Current Abstract Machine Level

Status: **ESTABLISHED / FORMAL + EXPERIMENTAL**

## Source model

The abstract Machine model at:

`Loofy147/Machine@f752aac015d9f837bc6a89d44eed50e0325b60a6`

defines:
`T(S,O,input) -> (S',result)`

and explicitly states that:
- state may include any machine-relevant condition;
- the model does not prescribe a data structure;
- the model does not specify a minimal state representation;
- resource/cost semantics are not part of the current abstraction.

The model therefore does not freeze a primitive such as arbitrary word-addressed state read, semantic transition probing, or inverse-fiber access.

## Proposition

At the current abstract level, the status of Rev 2.1 inverse-fiber access is **not identifiable** as either:
1. an already-derived representation-level operation, or
2. a new substrate capability.

### Proof sketch

Fix one abstract transition system with state set and deterministic transition relation `delta`.

Construct two concrete substrates that implement the same abstract transition semantics:

**Implementation A — opaque forward access**

The concrete state exposes semantic transition probes `delta(s,a)` but does not expose arbitrary addresses of auxiliary state. Exact predecessor enumeration requires an adversarial `Omega(E)` probe lower bound.

**Implementation B — generic random-access state**

The concrete state contains the same `delta` plus target-obliviously derived CSR arrays
`(offs,src,act)`. A generic state-word read plus arithmetic reconstructs

[
F(u)=\{(src[i],act[i]) : offs[u]\le i<offs[u+1]\}.
]

No fiber-specific semantic primitive is required in this implementation.

Both implementations realize the same abstract transition semantics. They differ only in concrete representation/access contracts.

Therefore the abstract model alone cannot determine whether inverse-fiber access is:
- a representation-level composite,
- an access-capability extension,
- or a resource-bounded frontier shift.

That classification is necessarily delegated to the future substrate/resource contract.

## Experimental confirmation

The companion CI experiment at:

`experiments/machine-substrate-primitive-closure-v0/run_primitive_closure.py`

tested 72 systems, 720 lookups, and 72 basin fixpoints.

Verification:
- builder failures: 0
- predecessor semantic failures: 0
- basin semantic failures: 0
- all semantic comparisons equal: true

Online structural work:
- forward-only control: 751,560 probes
- generic random-access state: 6,320 reads
- explicit fiber primitive: 3,160 operations

The raw result is reproducible across two successful CI executions. The second execution produced raw-result SHA-256:

`d9752a6b7d0bc0bc26a65f5005d6198209105d040a184f9e5b00024a24407331`

## Durable disposition

The correct repository-level statement is:

> **The current abstract Machine specification is intentionally too weak to classify inverse-fiber access.**

More specifically:

- **Under RANDOM_ACCESS_STATE:** inverse-fiber access is experimentally supported as representation-level closure.
- **Under OPAQUE_FORWARD:** inverse-fiber access requires an explicit access extension.
- **Under the current abstract Machine model:** both are conforming implementation possibilities because state representation and access/cost semantics are intentionally unspecified.

This is not an implementation failure. It is an explicit specification boundary.

## Promotion gate

Do not promote `F(u)` to an abstract Machine primitive merely because Rev 2.1 makes it efficient.

Do not remove it from the primitive set merely because one implementation can derive it from generic state reads.

First freeze a machine-substrate resource contract containing at least:

[
\mathcal{C}_{sub}=
(\text{state addressing},
\text{transition access},
\text{derived-state policy},
\text{offline work},
\text{persistent representation},
\text{online access cost},
\text{mutation semantics}).
]

Only then is primitive-vs-representation classification well-posed.

## Next discriminating action

Freeze that substrate-neutral resource contract without choosing an implementation language or storage library. Then rerun the closure experiment with the frozen contract as the acceptance boundary.
