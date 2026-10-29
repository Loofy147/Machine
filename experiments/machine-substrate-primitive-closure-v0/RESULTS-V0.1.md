# Machine Substrate Primitive Closure v0.1 — Results

Status: **EXPERIMENTALLY_SUPPORTED / CONTRACT-BOUND**

Execution:
- Workflow run: `36350976788`
- Job: `108709474992`
- Head: `35c5f21aef945170f42b64f4f3feefc209659747`
- Base: `research/bidirectional-substrate-v3@59fab62704875193801db77c7cb8361475297f48`
- CI artifact: `10942640440`
- Artifact SHA-256: `72716cbdba4027dfd7d9ad90d6d83f9eddcc09322b9be029263d48646b98537e`
- Raw result SHA-256: `d9752a6b7d0bc0bc26a65f5005d6198209105d040a184f9e5b00024a24407331`

## Question

Is the Rev 2.1 inverse-fiber access path already derivable from generic random-access state reads, or does it require a new substrate capability?

## Frozen access contracts

### A. OPAQUE_FORWARD

Allowed semantic access:
`delta_read(s,a)`, finite iteration, comparison.

The inverse representation is not addressable through the machine API.

For exact predecessor enumeration, an adversary can keep an unprobed transition capable of mapping to the queried target. Therefore exact enumeration has an `Omega(E)` defined-transition-probe lower bound in this access model.

### B. RANDOM_ACCESS_STATE

Allowed access:
`generic_state_read(array,index)`, arithmetic, finite iteration.

The same derived CSR arrays
`offs, src, act`
are ordinary machine state.

For a target `u` with `d=deg^-(u)`:
[
F(u)=\{(src[i],act[i]) : offs[u]\le i<offs[u+1]\}.
]

This decomposition uses two boundary reads plus two word reads per labeled entry:
[
B_{on}=2+2d.
]

No fiber-specific semantic primitive is added.

### C. FIBER_PRIMITIVE

A dedicated `fiber_lookup(u)` operation is exposed.

This is explicitly a substrate access extension, independent of whether the underlying bytes are stored in ordinary state.

## Executed workload

- 72 generated systems
- 720 predecessor lookups
- 72 exact backward-basin fixpoints
- 6 system families
- deterministic seeds

## Verification

- CSR builder failures: **0**
- predecessor semantic failures: **0**
- basin semantic failures: **0**
- all compared semantics equal: **TRUE**

## Aggregate structural result

- Control online probes: **751,560**
- Random-access state reads: **6,320**
- Fiber-primitive operations: **3,160**
- Control / random-state online ratio: **118.9177×**
- Mean inverse extra representation: **5,774.22 bytes**
- Mean offline build accounting: **2,175.89 units**
- All 720 tested lookups had lower online cost under the random-access representation.

## Feasible-resource frontier

Each lookup is represented by:
[
(B_{off},R_{extra},B_{on},C_{access}).
]

Control:
[
(0,0,E,\texttt{delta\_probe})
]

Random-access state:
[
(2E+n,;4(n+1)+4E+E,;2+2\deg^-(u),;\texttt{generic\_state\_read})
]

Dedicated fiber primitive:
[
(2E+n,;4(n+1)+4E+E,;1+\deg^-(u),;\texttt{fiber\_lookup})
]

The resource trade is therefore explicit rather than hidden:
the online advantage is purchased with offline construction and persistent inverse representation.

## Disposition

### Established by this experiment

**Under the RANDOM_ACCESS_STATE contract, inverse-fiber access is representation-level closure.**

The fiber query is computable from the same information (`delta`) after target-oblivious preprocessing, using only generic state addressing plus arithmetic. The experiment confirms exact semantic preservation on the tested workload.

### Also established by the contract split

**Under OPAQUE_FORWARD, the same access path is not derivable without adding an access capability.**

This is not a contradiction. The two statements use different machine access contracts.

### Not established

- Absolute computational-power separation.
- Canonical status of RANDOM_ACCESS_STATE for the abstract Machine model.
- Canonical status of Rev 2.1 as the repository-wide resource contract.

The current repository tip does not expose a frozen generic state-access primitive contract that lets this experiment identify one of these access models as canonical. That remains **OPEN**.

## Relation to the previous crosswalk

The earlier crosswalk result showed that Rev 2.1 moves predecessor discovery from online scans into offline construction + persistent inverse representation.

This experiment sharpens the interpretation:

> The shift is a representation/resource relocation whenever generic random-access state is part of the substrate contract; it becomes a genuine substrate-capability extension only when that generic state addressing is absent from the allowed access interface.

Therefore the appropriate durable claim is **contract-conditional**, not universal.

## Falsification boundary

Held fixed:
- same `delta`
- same target-oblivious inverse construction
- same predecessor semantics
- same basin semantics
- offline work charged
- extra representation charged
- no wall-clock timing used for classification

A future canonical closure test must first freeze the abstract Machine primitive contract. Without that freeze, claiming that Rev 2.1 is either a primitive or not a primitive would be specification debt.



## Re-execution check

The same committed experiment was re-executed at the later branch head
`7d5a33e27c8aa14ebf817d1c5d9dd7e308b8a943`.

- workflow run: `36351038863`
- job: `108709642134`
- conclusion: **success**
- artifact: `10941734374`
- artifact SHA-256: `e1ebd6d0baa7b9e741b0975c75618324b3cc98b8f25724fa3251c034e089cac9`
- raw result SHA-256: `d9752a6b7d0bc0bc26a65f5005d6198209105d040a184f9e5b00024a24407331`

The raw result bytes are identical to the first successful execution. This
strengthens reproducibility of the measured disposition, but it does not
change the contract-conditional interpretation.
