# HSDCR Pairwise Embedding & Collision Matrix v0.1

Status: **RESEARCH / NON-NORMATIVE / OPEN**

Recorded: **2026-09-28**

Repository: `Loofy147/Machine`

Branch: `research/hsdcr-neighborhood-crosswalk-v0`

## Purpose

This artifact performs the next discriminating step after the neighborhood crosswalk:

> Test whether the candidate atoms can be embedded into an existing architectural family without semantic collapse.

It does **not** attempt to prove that the candidate is novel.

## Classification

| Symbol | Meaning |
|---|---|
| **N** | Native coverage in the family |
| **C** | Composable without changing the family identity |
| **X** | Requires a semantic extension |
| **K** | Collision risk: embedding would collapse a distinction we need to preserve |
| **U** | Unresolved |
| **E** | External/project-specific component, not part of the family itself |

The complete machine-readable matrix is in:

`docs/research/ATOMIC-REPOSITORY-CAPABILITY-LEDGER-v0.1.yaml`

## Results

| Family | Strongly covered | Main collision/extension boundary |
|---|---|---|
| Distributed VCS / code forge | identity, contribution locus, lineage, proposal, authority, deferred acceptance | evidence/sensitivity are not native; decentralized contribution must not be mistaken for decentralized authority |
| Federated forge | contribution objects, lineage, activities, federated actors | canonical reconstruction, evidence semantics, and sensitivity remain external/extended |
| Authenticated replicated repository | identity, repository state, lineage, events, reconstruction | contribution acceptance and deferred authority are application semantics |
| CRDT | independent changes, causal lineage, reconstruction, local-first replication | authority, evidence, acceptance, and sensitivity are not supplied by convergence |
| Change-oriented VCS | first-class changes, dependencies, identity, reconstruction | acceptance/evidence/authority/sensitivity are not intrinsic |
| Provenance | entities, activities, derivation, attribution | provenance is not itself contribution governance, authority, or state-transition control |
| Event sourcing | durable event history and state reconstruction | event ≠ evidence ≠ authority; distributed contribution is not inherent |
| Transparency log | durable append-only evidence/audit surface | no contribution/reconciliation/authority/state machine |
| UCAN | authority, delegation, proof lineage, decentralized control | no repository/contribution/evidence-state machine |
| DID | decentralized identity/control references | identity alone does not provide contribution, evidence, state or reconciliation |
| Software preservation | persistent identity, revision lineage, snapshots | archival state ≠ live contribution/authority workflow |
| Versioned data | branches, commits, lineage, review/protection, reconstruction | decentralized writers do not imply decentralized authority; sensitivity is external |
| Observability | signals, traces, metrics, logs | sensing is not contribution, evidence, authority or mutation semantics |

The external basis for these mappings includes the current AT Protocol repository/sync specifications, ForgeFed specification, Automerge documentation, Pijul theory/manual, W3C PROV overview, UCAN specifications, W3C DID Core, Sigstore/Rekor security model, lakeFS versioning documentation, OpenTelemetry signal model, and first-party/primary project documentation where available. citeturn608360search0turn608360search1turn423150search1turn314955search0turn314955search13turn608360search4turn608360search5turn911685search4turn314955search1turn314955search11

## Collision tests that survived the pass

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
eq Evidence
]

[
Evidence 
eq Authority
]

[
Observation 
eq MutationAuthority
]

[
DerivedState 
eq NewInformation
]

[
Reconstruction 
eq Synchronization
]

[
Convergence 
eq Acceptance
]

[
Sensitivity 
eq Reactivity
]

[
SemanticEquivalence 
eq ResourceEquivalence
]

These distinctions are not claimed to be unique; they are the current **non-collapse constraints** for the investigation.

## Highest-value collision findings

### 1. CRDT is not enough

Automerge already supplies local-first independent updates, causal history, merging, synchronization, and immutable state. It therefore absorbs a large part of “decentralized contribution + reconstruction.” citeturn423150search1turn423150search0

But automatic convergence does not by itself define evidence, authority, or acceptance. Automerge's own 2026 research material explicitly distinguishes convergence from correctness. citeturn423150search6

Thus:

[
CRDT supseteq 	ext{large contribution/reconciliation subset}
]

but not automatically:

[
CRDT supseteq 	ext{evidence/authority/acceptance semantics}
]

### 2. AT Protocol is a particularly strong reduction candidate

AT Protocol already combines authenticated repositories, revisions, signed commits, repository exports, event streams, and reconstruction/verification mechanisms. citeturn608360search8turn608360search0

Therefore a candidate based only on:

[
	ext{self-certifying state}+	ext{replication}+	ext{event stream}
]

would not be sufficiently differentiated.

The unresolved boundary is semantic: contribution acceptance, evidence status, authority, and deferred decision are not implied by the repository format itself.

### 3. GitHub already has a substantial acceptance machine

GitHub pull requests explicitly combine proposal, discussion, review, checks, and merge, while rulesets can require reviews, status checks, signed commits and other conditions. citeturn435211search5turn435211search0turn435211search4

Therefore “contribution + review + automated evidence + controlled acceptance” is not an architectural discovery.

The candidate must survive a stricter question:

> What remains after these existing mechanisms are decomposed into atomic state, relation, authority, evidence, and reconstruction semantics?

### 4. Event sourcing already owns the reconstruction problem

Event Sourcing explicitly stores state changes as events and supports complete state rebuild and temporal reconstruction. citeturn911685search0turn911685search1

Therefore:

[
	ext{event log}+	ext{replayable state}
]

cannot be treated as the differentiating core by itself.

### 5. Authority is already a separate architectural family

UCAN explicitly models delegable authority and cryptographically verifiable proof chains. citeturn608360search4turn608360search2

Therefore “decentralized authority” is prior art and must not be rediscovered under the word “decentralized.”

### 6. Sensitivity is also an existing system concern

OpenTelemetry explicitly models traces, metrics, logs and other signals as observable system outputs. citeturn314955search11

Therefore “high sensitivity” cannot mean merely collecting more telemetry.

The relevant residual is narrower:

[
oxed{
	ext{high sensitivity}
+
	ext{durable semantic treatment}
+
	ext{no automatic authority transfer}
}
]

This remains **OPEN**, not established.

## Current absorption verdict

No single family fully absorbs the current candidate atom set **without at least one extension or collision** in this pass.

However, this result does **not** establish a new architecture.

The composition may still reduce to an existing stack such as:

[
	ext{CRDT}
+
	ext{authenticated repository}
+
	ext{provenance}
+
	ext{capability authority}
+
	ext{observability}
]

The next test must therefore be against the **composition space**, not only individual families.

## Next discriminating experiment

Construct the smallest composition graph capable of satisfying all currently required distinctions:

[
	ext{identity}
ightarrow
	ext{contribution}
ightarrow
	ext{observation}
ightarrow
	ext{evidence}
ightarrow
	ext{authority}
ightarrow
	ext{decision}
ightarrow
	ext{canonical state}
]

Then minimize it:

1. remove one component at a time;
2. determine which distinction collapses;
3. determine whether the removed component can be represented by ordinary data rather than a new semantic primitive;
4. charge persistence, synchronization, and verification costs;
5. compare reconstructibility with the underlying components.

Only a surviving **irreducible semantic dependency** should qualify as architectural residual.

## Important preservation boundary

GitHub's hosted operational surfaces are not automatically durable evidence. GitHub currently documents default 90-day retention for workflow artifacts and logs, configurable by repository type, and from **October 1, 2026** the retention policies also apply to checks, workflow runs and commit statuses. citeturn435211search1turn435211search2

Likewise, webhook deliveries are only redeliverable for the previous three days. citeturn435211search3

Therefore a future candidate that relies on GitHub's transient operational history as its canonical evidence store would fail the reconstructibility test unless it persists the necessary records elsewhere.

## Disposition

```
full_absorption_identified = false
architectural_novelty = OPEN
protocol_status = NOT_ASSIGNED
production_status = NOT_ASSIGNED
candidate_label = working-label-only
```
