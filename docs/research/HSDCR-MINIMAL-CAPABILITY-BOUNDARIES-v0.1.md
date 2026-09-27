# HSDCR Minimal Capability Boundary Set v0.1

Status: **RESEARCH / NON-NORMATIVE / OPEN**

Recorded: **2026-09-28**

This document defines a **test interface bundle**, not an architecture or protocol.

Its purpose is to make capability adoption and component substitution concrete.

## 1. Design rule

Use the strongest known implementation for each capability, but depend only on a minimal semantic contract:

[
implementation ightarrow capability interface leftarrow consumer
]

The consumer must not depend on the source system's full ontology.

## 2. Minimal boundaries

### B01 — Identity

Required semantics:

[
identify(x)ightarrow id
]

Properties:
- stable under replication;
- distinguishable from current location;
- verifiable when verification is supported.

Non-requirement:
- a specific DID, GitHub actor, account, or key system.

### B02 — Content/State Object

Required semantics:

[
store(content)ightarrow immutable_identity
]

and:

[
resolve(id)ightarrow content
]

Non-requirement:
- a specific object store;
- a specific hash;
- a hosted repository.

### B03 — Contribution/Change

Required semantics:

[
propose(base, change)ightarrow contribution
]

Contribution must carry:
- identity;
- base/reference;
- resulting content or state delta;
- lineage.

A contribution is not canonical merely because it exists.

### B04 — Observation

Required semantics:

[
observe(signal)ightarrow observation
]

An observation records that a signal was detected.

It does not imply:
- validity;
- evidence status;
- authority;
- mutation.

### B05 — Evidence

Required semantics:

[
evaluate(observation, subject)ightarrow evidence
]

Evidence must identify:
- what was evaluated;
- evaluator/source;
- result;
- scope;
- time/context;
- provenance where available.

Evidence is a semantic object distinct from observation.

### B06 — Authority

Required semantics:

[
authorize(principal, capability, subject, context)ightarrow authorization
]

An authorization can permit an action but does not assert that the action is true or useful.

Authority must not be inferred from:
- repository reachability;
- branch existence;
- observation;
- evidence alone.

### B07 — Decision/Acceptance

Required semantics:

[
decide(evidence, authority, policy, proposal)ightarrow disposition
]

Possible dispositions remain open, but the minimum model needs to distinguish:
- accepted/canonical;
- rejected;
- held/deferred;
- invalid/inconclusive.

Decision is not identical to evidence.

### B08 — Canonical State

Required semantics:

[
apply(accepted_changes)ightarrow canonical_state
]

The canonical-state transition must be explicitly attributable to an acceptance/authority condition.

### B09 — Reconstruction

Required semantics:

[
reconstruct(durable_records)ightarrow state
]

The result must be independently checkable against the designated state identity when possible.

Reconstruction is not the same operation as synchronization.

### B10 — Synchronization

Required semantics:

[
sync(peer_state)ightarrow local_state
]

Synchronization transports/updates state between loci.

It does not itself define acceptance.

### B11 — Signal Ingress

Required semantics:

[
ingest(source_event)ightarrow signal
]

Properties:
- low-latency where available;
- correlation metadata;
- source identity;
- ordering/cursor information where available.

Signal ingress must not become canonical history merely by arriving.

### B12 — Resource Contract

Required semantics:

[
cost(operation, contract)ightarrow resource_vector
]

For Machine-style analysis, the minimum vector is:

[
(B_{off},R,B_{on},C_{access})
]

and may be extended with synchronization, verification, and retention costs.

## 3. Known implementation candidates

| Boundary | Candidate implementations |
|---|---|
| B01 Identity | DID, AT Protocol account identity, Git identities/keys |
| B02 Content/State | Git objects, AT Protocol repository, content-addressed stores |
| B03 Contribution | Git branch/commit/PR, CRDT change, Pijul change, lakeFS branch/commit |
| B04 Observation | OpenTelemetry signal/log/event surfaces, repository event streams |
| B05 Evidence | W3C PROV relations, Rekor transparency entries, signed validation results |
| B06 Authority | UCAN delegation/invocation, GitHub rulesets/permissions |
| B07 Decision | GitHub review/merge gate, lakeFS protected merge, explicit application transition |
| B08 Canonical State | Git protected branch, AT repository head, lakeFS commit |
| B09 Reconstruction | Git history, AT repository export, event replay |
| B10 Synchronization | AT firehose/CAR sync, CRDT sync, Git fetch/push |
| B11 Signal Ingress | OpenTelemetry, AT repository event stream, GitHub events |
| B12 Resources | explicit contract as defined by the application/experiment |

## 4. Substitution requirement

Two implementations are substitutable for boundary B if they satisfy the same declared boundary semantics.

The test is:

[
Impl_A sim_B Impl_B
]

only when every required observable of B is preserved.

Implementation-specific features must not leak into the boundary.

## 5. Adapter rule

An adapter is allowed when it translates representation or wire format without adding a new semantic class.

Examples:

[
GitCommit ightarrow ChangeRecord
]

[
ATCommit ightarrow ChangeRecord
]

[
UCANDelegation ightarrow Authority
]

[
GitHubCheck ightarrow Evidence
]

An adapter becomes architecturally significant only if it must invent a missing semantic concept rather than translate an existing one.

## 6. First composition candidate

The minimal graph under test is:

[
Identity
ightarrow
Content/State
ightarrow
Contribution
ightarrow
Observation
ightarrow
Evidence
ightarrow
Authority
ightarrow
Decision
ightarrow
CanonicalState
ightarrow
Reconstruction
]

with:

[
SignalIngressightarrow Observation
]

and:

[
CanonicalStateleftrightarrow Synchronization
]

This graph is deliberately provisional.

## 7. Non-collapse constraints

The following must hold at the boundary level:

[
Identity 
eq Location
]

[
Contribution 
eq CanonicalState
]

[
Signal 
eq Observation
]

[
Observation 
eq Evidence
]

[
Evidence 
eq Authority
]

[
Authority 
eq Decision
]

[
Decision 
eq CanonicalState
]

[
Reconstruction 
eq Synchronization
]

[
Sensitivity 
eq Reactivity
]

[
SemanticEquivalence 
eq ResourceEquivalence
]

## 8. Sensitivity boundary

The term "highly sensitive" is deliberately not defined as a numeric threshold yet.

The current testable interpretation is:

> A system may accept signals at a finer temporal/spatial/semantic granularity than the canonical transition mechanism requires.

This allows the following separation:

[
many observations
ightarrow
few accepted transitions
]

rather than:

[
many observations
ightarrow
many automatic mutations
]

A future quantitative sensitivity definition must specify:
- detection threshold;
- latency;
- false-positive policy;
- sampling/granularity;
- retention;
- authority threshold for transition.

## 9. Composition reduction test

Given the boundary bundle B01..B12:

For each B_i, remove it and determine:
1. which observables disappear;
2. which distinctions collapse;
3. whether another B_j can supply them without semantic overloading;
4. whether a known implementation already supplies the missing behavior;
5. resource and reconstruction effects.

This produces the component-removal ledger update.

## 10. Acceptance criteria for a surviving residual

A residual capability may be considered irreducible only if:

1. its semantics cannot be represented by another boundary as ordinary data;
2. removing it causes a required distinction to collapse;
3. at least two independent implementations or emulations can realize it;
4. the claim survives component substitution;
5. its resource/access contract is explicit.

Until all five conditions hold, the residual remains OPEN.

## 11. Current status

- boundary bundle: **PROVISIONAL**
- implementation choices: **SUBSTITUTABLE CANDIDATES**
- composition: **TEST OBJECT ONLY**
- irreducible residual: **OPEN**
- architecture: **NOT ASSIGNED**
- protocol: **NOT ASSIGNED**
- novelty: **NOT CLAIMED**
