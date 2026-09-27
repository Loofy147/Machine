# HSDCR Composition-Space Reduction Plan v0.1

Status: **RESEARCH / NON-NORMATIVE / OPEN**

Recorded: **2026-09-28**

Repository: `Loofy147/Machine`

Branch: `research/hsdcr-neighborhood-crosswalk-v0`

## Purpose

The pairwise matrix did not identify a single existing family that absorbs all candidate distinctions without extension or collision.

That is insufficient to establish a distinct architecture.

The next task is therefore **composition-space reduction**:

> Determine whether the candidate can be expressed as an ordinary composition of existing families while preserving all required distinctions and without introducing a hidden new semantic primitive.

## Candidate atom set

Current atom IDs are defined in:

`docs/research/ATOMIC-REPOSITORY-CAPABILITY-LEDGER-v0.1.yaml`

The relevant set is:

```text
identity
contribution
lineage
proposal
observation
evidence
authority
deferred decision
reconstructible state
sensitivity
non-reactivity
decentralized loci
contract-relative capability
```

## Reference composition

The initial composition candidate is:

```
Identity
  + authenticated/versioned state
  + independent contribution/change layer
  + observation/signal layer
  + evidence/provenance layer
  + authority/capability layer
  + reconciliation/acceptance layer
  + reconstruction layer
```

This is deliberately assembled from existing families:

- DID / self-certifying identity;
- Git/AT Protocol/CRDT/change-oriented VCS for state and change;
- OpenTelemetry-like signaling for observation;
- W3C PROV / transparency logs for provenance/evidence;
- UCAN-like capabilities for authority;
- Event Sourcing / authenticated repository mechanisms for reconstruction.

No component is declared mandatory yet.

## Reduction procedure

For each candidate component C:

1. remove C;
2. attempt to represent its required semantics as ordinary data/relations in the remaining substrate;
3. attempt to preserve all atomic distinctions;
4. run the collision tests;
5. record the first distinction that becomes unrepresentable or semantically ambiguous;
6. record whether the missing behavior requires a new primitive or merely a different representation.

The result must be recorded as:

```text
REMOVE(C)
  -> preserved atoms
  -> collapsed atoms
  -> missing relations
  -> required extension
  -> resource effect
  -> disposition
```

## Required kill tests

### K1 — Pure version-control reduction

Try to express the complete candidate using only:
- versioned state;
- branches/change loci;
- review/merge;
- checks/rules.

Kill condition:

```text
evidence, authority, and sensitivity cannot remain distinct
without adding semantic structures.
```

### K2 — Pure CRDT reduction

Try to express the candidate as:
- replicated documents;
- changes;
- causal dependencies;
- deterministic merge.

Kill condition:

```text
acceptance/evidence/authority must be overloaded onto convergence.
```

### K3 — Pure event-sourcing reduction

Try to express the candidate as:
- event log;
- replay;
- projections.

Kill condition:

```text
observation/evidence/authority cannot remain distinct from
the events that update state.
```

### K4 — Pure capability reduction

Try to express the candidate using:
- principals;
- capabilities;
- delegations;
- invocations.

Kill condition:

```text
repository state and contribution lineage become secondary
application conventions rather than native state.
```

### K5 — Pure provenance reduction

Try to express the candidate as:
- entities;
- activities;
- agents;
- derivations.

Kill condition:

```text
there is no native transition semantics for contribution acceptance
or canonical-state evolution.
```

### K6 — Sensitivity-as-telemetry reduction

Try to express high sensitivity using observation/telemetry alone.

Kill condition:

```text
the system detects signals but has no durable semantic relation
between detection, evidence, authority, and subsequent transitions.
```

## Stronger test: composition equivalence

Let:

[
X = X_1 circ X_2 circ cdots circ X_n
]

be an existing-system composition.

We need to determine whether there exists an implementation-preserving mapping:

[
phi: H ightarrow X
]

such that:

1. all candidate atoms map injectively;
2. required relations remain distinguishable;
3. canonical state can be reconstructed;
4. authority cannot leak through reachability;
5. sensitivity does not imply reactivity;
6. no new semantic primitive is introduced in the mapping.

If such a mapping exists, the candidate remains a composition of known architectures.

If no such mapping exists, that only establishes an **unresolved residual**. It still does not establish novelty until the residual is independently specified and verified.

## Resource dimension

Composition must also be compared with:

[
(B_{off},R,B_{on},C_{access})
]

because two semantically equivalent compositions can have materially different substrate/resource contracts.

This is inherited from the current Machine substrate work.

## Evidence discipline

Every composition result must carry:

```text
source family
version/date
specific semantic feature
mapping
collision
evidence status
scope
limitations
```

The source's own claim must not be rewritten as if it were a claim about the candidate.

## Current disposition

```
single-family absorption: NOT IDENTIFIED
composition absorption: OPEN
irreducible residual: OPEN
architectural novelty: NOT CLAIMED
protocol status: NOT ASSIGNED
```

## Next artifact

Create a component-removal ledger from the reference composition.

The minimum useful output is:

```text
component
  -> atoms it alone supplies
  -> atoms it can share
  -> atoms that collapse without it
  -> replacement candidate
  -> extension required?
  -> evidence status
```

Only after that reduction should the investigation decide whether a new architectural object is justified.
