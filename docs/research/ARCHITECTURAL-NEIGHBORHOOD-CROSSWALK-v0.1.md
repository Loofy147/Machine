# Architectural Neighborhood Crosswalk v0.1

Status: **RESEARCH / NON-NORMATIVE / OPEN**

Recorded: 2026-09-28

Repository: `Loofy147/Machine`

Branch: `research/hsdcr-neighborhood-crosswalk-v0`

Parent: `research/machine-substrate-primitive-closure-v0@12dade33f708d66890c6c10b754f85c1d3ae13e3`

## 1. Purpose

This document prevents premature architectural closure around the working label:

> **HSDCR — Highly Sensitive Decentralized Contribution Repository**

The label is not treated as a protocol, product, specification, or established architecture.

The immediate question is:

> Can the candidate be reduced without loss to an existing architectural family, or does a non-trivial residual remain after precise embedding tests?

No novelty claim is made.

## 2. Required comparison dimensions

Every neighboring system is decomposed across:

1. identity;
2. locus/location;
3. contribution/change unit;
4. state model;
5. relation model;
6. authority;
7. timing;
8. evidence;
9. persistence;
10. mutation;
11. reconstruction;
12. synchronization;
13. cost/resource model;
14. observability/sensitivity;
15. canonicality.

Similarity by vocabulary is not sufficient.

## 3. Neighbor families

### N1 — Distributed version control / code forges

Examples: Git, GitHub, distributed forges.

Strong coverage:
- content-addressed history;
- branches/refs;
- independent contribution loci;
- proposed changes;
- review and merge;
- executable validation.

Potential collision:
- contribution may collapse to a commit/change;
- collaboration state may remain platform-specific;
- authority may remain centrally administered.

Result:
**PARTIAL EMBEDDING**.

It can supply a substrate for contribution lineage, but does not by itself establish the candidate's full semantics.

### N2 — Federated forge models

Example: ForgeFed.

ForgeFed models version-control and project-management objects as linked data and defines ActivityPub-based representations of forge events and action sequences.

Potential collision:
- candidate could be only a forge-federation vocabulary;
- activity/event representation may absorb contribution semantics.

Result:
**PARTIAL EMBEDDING / NEEDS COUNTERTEST**.

Question left open:
Can a federated activity model preserve distinct states for signal, evidence, authority, decision, and canonical state without collapsing them into activity semantics?

### N3 — Self-certifying personal repositories / authenticated replication

Example: AT Protocol repositories.

AT Protocol repositories are content-addressed Merkle structures with signed commits; repositories can be exported as CAR files, synchronized over firehose streams, and independently verified.

Potential collision:
- self-certifying repository + event stream + replication is already a powerful decentralization substrate;
- candidate may reduce to authenticated replicated personal repositories plus application semantics.

Result:
**STRONG PARTIAL EMBEDDING**.

Missing question:
Does authenticated replicated state natively distinguish contribution, observation, evidence, authority, and deferred decision as separate semantic classes?

### N4 — CRDT / convergence-oriented systems

Examples: Automerge and related state-based / operation-based CRDT systems.

Strong coverage:
- independent mutation;
- causal history;
- replication;
- convergence;
- merge semantics.

Potential collision:
- "decentralized contributions" may simply be concurrent replicated changes;
- reconciliation may be reducible to CRDT merge.

Result:
**PARTIAL EMBEDDING**.

Boundary:
convergence does not itself define evidentiary validity or authorization semantics, and conflict-free merge is not equivalent to approval/acceptance.

### N5 — Change-oriented version control

Example: Pijul.

Pijul treats changes/patches as first-class entities and uses a formal patch theory.

Potential collision:
- contribution may be exactly a first-class change object;
- dependencies among changes may cover lineage/reconciliation.

Result:
**PARTIAL EMBEDDING**.

Countertest:
Can change identity remain distinct from the evidence that validates it and the authority that accepts it?

### N6 — Provenance systems

Example: W3C PROV.

Strong coverage:
- entity;
- activity;
- agent;
- derivation;
- revision;
- attribution;
- reproducibility/provenance exchange.

Potential collision:
- almost any contribution/evidence lineage can be represented as provenance.

Result:
**PARTIAL EMBEDDING**.

Boundary:
PROV is a provenance model; it does not by itself define a decentralized contribution substrate, authority-transition system, or repository replication protocol.

### N7 — Event sourcing / event-log state reconstruction

Strong coverage:
- immutable event sequence;
- state reconstruction;
- replay;
- projections.

Potential collision:
- candidate could be an event-sourced repository with distributed writers.

Result:
**PARTIAL EMBEDDING**.

Required countertest:
Can an event log preserve a distinction between an observed event and an event that has evidentiary status or transition authority?

### N8 — Transparency / append-only evidence logs

Example: Rekor / Sigstore transparency infrastructure.

Strong coverage:
- append-only log;
- inclusion/consistency evidence;
- signed artifacts and attestations;
- externally verifiable history.

Potential collision:
- candidate's "evidence sensitivity" could collapse to transparency logging.

Result:
**PARTIAL EMBEDDING**.

Boundary:
transparency establishes publication/audit properties, not the complete contribution/authority/state machine.

### N9 — Distributed authorization / capability systems

Example: UCAN.

Strong coverage:
- decentralized principals;
- delegable capabilities;
- proof chains;
- invocation and execution;
- revocation;
- authority without a central authorization server.

Potential collision:
- candidate's authority layer could be entirely a capability graph.

Result:
**PARTIAL EMBEDDING**.

Boundary:
authorization is not evidence, contribution, repository state, or reconciliation by itself.

### N10 — Digital identity

Examples: DIDs and self-certifying identity schemes.

Coverage:
- subject identity;
- key material;
- verifiable relationships.

Result:
**SUBSTRATE COMPONENT**, not a complete embedding.

Identity does not answer contribution/evidence/reconciliation semantics.

### N11 — Software preservation / archival systems

Example: Software Heritage.

Strong coverage:
- persistent identifiers;
- origin;
- snapshots;
- revisions;
- historical preservation and provenance.

Result:
**PARTIAL EMBEDDING**.

Boundary:
preservation is not the same as live contribution and authority transition.

### N12 — Versioned data systems

Examples: Dolt, lakeFS.

Strong coverage:
- branches;
- commits;
- merges;
- versioned state/data;
- reproducible snapshots.

Result:
**PARTIAL EMBEDDING**.

Boundary:
data versioning provides state evolution, not necessarily decentralized contribution authority or evidence semantics.

### N13 — Observability / telemetry

General family:
- signals;
- traces;
- logs;
- metrics;
- event detection.

Result:
**SENSITIVITY SUBSTRATE COMPONENT**.

Important boundary:
high signal detection is not equivalent to authority, decision, or state mutation.

## 4. Collision tests

The following distinctions must survive every attempted embedding.

### C1 — Signal vs evidence

A system may notice an event without that event becoming validated evidence.

Required invariant:

[
Signal 
eq Evidence
]

### C2 — Evidence vs authority

A piece of evidence may support a transition without possessing the authority to cause it.

[
Evidence 
eq Authority
]

### C3 — Contribution vs canonical state

A proposed contribution can exist without being accepted into canonical state.

[
Contribution 
eq CanonicalState
]

### C4 — Identity vs locus

The identity of a contribution/actor must not be identical to a mutable branch, server, or current hosting location.

[
Identity 
eq Location
]

### C5 — Observation vs mutation

Detection of a state change must not automatically be a permission to cause another state change.

[
Observation 
eq MutationAuthority
]

### C6 — Derived state vs new information

Materializing a derived index must not silently count as acquiring new information.

[
DerivedState 
eq NewInformation
]

### C7 — Reconstruction vs synchronization

A system that can reconstruct state from a local durable record is not necessarily a synchronization protocol, and synchronization does not guarantee complete reconstructibility.

[
Reconstruction 
eq Synchronization
]

### C8 — Convergence vs acceptance

Two replicas converging to the same state does not imply that the state was authorized or evidentially accepted.

[
Convergence 
eq Acceptance
]

### C9 — Sensitivity vs reactivity

The ability to detect weak or early signals must not imply automatic state transition.

[
Sensitivity 
eq Reactivity
]

### C10 — Semantic equivalence vs resource equivalence

Two systems may compute the same result but expose very different access and resource contracts.

[
SemanticEquivalence 
eq ResourceEquivalence
]

This follows directly from the currently frozen Machine substrate work.

## 5. Current residual

After the first neighborhood pass, no single neighboring family subsumes all dimensions without introducing one or more of the collisions above.

The strongest candidate reductions are:

[
	ext{CRDT/VCS}
ightarrow
	ext{distributed contribution + reconciliation}
]

[
	ext{ATProto-like repository}
ightarrow
	ext{self-certifying replicated state + event stream}
]

[
	ext{PROV + transparency}
ightarrow
	ext{evidence/provenance layer}
]

[
	ext{UCAN/DID}
ightarrow
	ext{authority/identity layer}
]

[
	ext{Observability}
ightarrow
	ext{sensitivity layer}
]

The unresolved question is whether these are merely composable existing layers or whether their composition creates a genuinely distinct architectural object.

## 6. Non-novelty pressure test

Before using terms such as "new architecture", require at least one of:

1. a required semantic distinction that the neighboring family cannot preserve without extension;
2. a required transition/reconstruction invariant absent from the neighboring family;
3. a formally different canonical-state rule;
4. an experimentally demonstrated property that survives reduction to each candidate neighboring model.

Without one of these, retain the candidate as a composition/hybrid rather than claiming architectural novelty.

## 7. Current status

- Git/GitHub contribution substrate: **ESTABLISHED**
- federated forge representation: **EXTERNAL PRIOR ART**
- self-certifying replicated repository: **EXTERNAL PRIOR ART**
- CRDT convergence: **EXTERNAL PRIOR ART**
- provenance model: **EXTERNAL PRIOR ART**
- event-sourced reconstruction: **EXTERNAL PRIOR ART**
- transparency/evidence log: **EXTERNAL PRIOR ART**
- capability-based authority: **EXTERNAL PRIOR ART**
- sensitivity/observability layer: **EXTERNAL PRIOR ART**
- complete candidate absorption by any one family: **OPEN**
- architectural novelty: **OPEN / NOT CLAIMED**
- protocol status: **NOT ASSIGNED**
- production status: **NOT ASSIGNED**

## 8. Next discriminating work

The next stage is not implementation.

Build a machine-readable atomic crosswalk with one row per capability/primitive and the following fields:

[
(source, atom, relation, semantics, authority, persistence, mutation, timing, evidence, reconstruction, cost, status)
]

Then run pairwise embedding tests against the strongest neighboring candidates rather than performing another broad feature inventory.

## 9. Source basis

Primary or first-party specifications used for the initial pass:

- AT Protocol Repository and Sync specifications.
- ForgeFed specification.
- W3C PROV Overview / Primer / Semantics.
- UCAN 1.0 specification and Delegation specification.
- Project specifications/documentation for the remaining named systems.

This document intentionally records the external landscape without treating any source's terminology as our own ontology.
