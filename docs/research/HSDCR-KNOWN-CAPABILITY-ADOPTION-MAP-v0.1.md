# HSDCR Known-Capability Adoption Map v0.1

Status: **RESEARCH / NON-NORMATIVE / OPEN**

Recorded: **2026-09-28**

## Principle

> Adopt proven capabilities from mature systems; do not reinvent a capability merely to make the candidate look internally complete.

The working candidate is not a protocol or architecture. The purpose of this map is to identify **known capability sources** and define the smallest semantic boundary at which each could be adopted.

The adoption of a capability does not imply adoption of the source system's complete ontology.

## 1. Capability map

| Required capability | Known capability source | What can be adopted | What must remain separate | Adoption status |
|---|---|---|---|---|
| Immutable artifact/content identity | Git; AT Protocol; Software Heritage | content-addressed identity, immutable object/reference lineage | identity must not equal mutable hosting location | CANDIDATE |
| Independent contribution loci | Git/GitHub; CRDTs; Pijul; lakeFS | branches, changes, causal/concurrent loci | locus must not imply authority | CANDIDATE |
| Change lineage | Git; Pijul; AT Protocol; PROV | parent/dependency/derivation relations | lineage is not evidence or acceptance | CANDIDATE |
| Concurrent independent mutation | Automerge/CRDT; Pijul | causal changes, merge/reconciliation mechanics | convergence is not acceptance | CANDIDATE |
| Versioned canonical state | Git; AT Protocol; lakeFS; event sourcing | immutable checkpoints + reconstructible snapshots | proposed contribution must remain distinct from canonical state | CANDIDATE |
| Replay/reconstruction | Event Sourcing; AT Protocol repositories | reconstruct state from durable history | reconstruction is not synchronization | CANDIDATE |
| Evidence lineage | W3C PROV | entity/activity/agent/derivation relations | provenance does not grant authority | CANDIDATE |
| Tamper-evident publication/audit | Rekor/Sigstore-style transparency log | append-only verifiable evidence anchoring | transparency does not decide acceptance | CANDIDATE |
| Fine-grained authority | UCAN; GitHub rulesets | capability/delegation or explicit enforcement rules | authority must not arise from evidence, reachability, or sensitivity | CANDIDATE |
| Repository transition gates | GitHub rulesets/status checks; lakeFS branch protection | required validation, protected canonical loci, controlled merge | checks are evidence; gate policy decides applicability | CANDIDATE |
| Fast signal acquisition | OpenTelemetry; repository event streams | traces/metrics/logs/events and correlation | signal is not automatically durable evidence | CANDIDATE |
| Durable event feed | AT Protocol sync/event streams; event-sourcing patterns | append/stream/replay boundary | network delivery is not canonical history by itself | CANDIDATE |
| Data-state versioning | lakeFS; Dolt | Git-like versioning over non-code state | versioning alone does not define contribution authority | CANDIDATE |
| Self-certifying replicated repository | AT Protocol | signed commits, Merkle structure, repository export/sync | application semantics remain outside the repository format | CANDIDATE |
| Contract-relative capability analysis | Machine substrate work | classify an operation relative to an explicit substrate contract | do not promote a capability globally from one implementation | ESTABLISHED IN PROJECT |

## 2. Adoption rule

For any source system X:

```
adopt(X.capability)
    !=
adopt(X.ontology)
```

The candidate should import only the smallest semantic contract needed.

Example:

```
adopt: signed immutable commit identity
do not automatically adopt:
    account model
    network topology
    application objects
    social semantics
```

## 3. Layering rule

A capability should be attached at the layer where its semantics are strongest:

```
identity
  -> content/state
  -> contribution/change
  -> observation
  -> evidence/provenance
  -> authority
  -> acceptance
  -> canonical state
  -> reconstruction/replication
```

A source system may supply more than one layer, but the layers are not merged merely because one system bundles them.

## 4. The proposed composition skeleton

This is a **test object**, not a design commitment:

```
[content-addressed durable state]
             |
             v
[independent contribution/change loci]
             |
             v
[fast observation/event surface]
             |
             +------> [evidence/provenance record]
             |                    |
             |                    v
             +--------------> [authority evaluation]
                                  |
                                  v
                            [accept/reject/hold]
                                  |
                                  v
                         [canonical state update]
                                  |
                                  v
                           [reconstructible history]
```

The key property is that the arrows do not identify the nodes.

In particular:

```
observation != evidence
evidence != authority
authority != acceptance
acceptance != canonical state
canonical state != replica
```

## 5. Why this may be better than inventing a native primitive

Known systems already provide strong, independently developed machinery for:

- authenticated state;
- concurrent change;
- provenance;
- authorization;
- telemetry;
- transparency;
- reconstruction;
- versioned state.

Reimplementing those mechanisms before establishing a need would add implementation surface without adding evidence.

The research should therefore target the **composition boundary** where existing capabilities must interact.

## 6. Composition questions

### Q1 — Identity boundary

Can a single contribution remain stably identifiable across:
- branch changes;
- repository migration;
- replication;
- reconstruction;
- acceptance/rejection?

### Q2 — Contribution/evidence boundary

Can a contribution be observed and evaluated without changing its semantic status?

### Q3 — Evidence/authority boundary

Can evidence affect an acceptance decision without itself becoming authorization?

### Q4 — Sensitivity/non-reactivity boundary

Can the system ingest weak/early signals at high sensitivity while requiring a separate authority transition before durable canonical mutation?

### Q5 — Reconstruction boundary

Can the canonical state be reconstructed from durable state/history even if the fast signal/event layer disappears?

### Q6 — Cross-source substitution

Can one known capability source be replaced by another without changing the surrounding semantics?

This is the strongest test against accidental vendor/platform lock-in.

## 7. Substitution pairs

The first controlled substitutions should be:

```
Git          <-> AT Protocol repository
Git/PR       <-> lakeFS change workflow
Automerge    <-> Pijul/change DAG
PROV         <-> provenance records encoded as ordinary state
Rekor        <-> repository-native hash/evidence anchoring
UCAN         <-> GitHub ruleset enforcement
OpenTelemetry <-> repository event stream
Event Sourcing <-> repository-history reconstruction
```

The goal is not to benchmark these systems globally.

The goal is to determine whether the candidate semantics survive substitution.

## 8. Kill conditions

Kill the "new architecture" hypothesis if the complete candidate can be represented as:

```
existing capability composition
+
ordinary data mappings
+
ordinary transition rules
```

with no irreducible semantic dependency.

Conversely, do not claim novelty merely because the composition is inconvenient to implement.

An irreducible dependency must first be:
- explicitly specified;
- independently tested;
- reproducible;
- shown not to be an artifact of one platform.

## 9. Resource discipline

All substitutions inherit the Machine rule:

```
semantic equivalence != resource equivalence
```

Where relevant record:

```
(B_off, R, B_on, C_access)
```

and separately:
- synchronization cost;
- verification cost;
- retention/persistence behavior;
- mutation/update cost.

## 10. Current disposition

Known capability adoption is now the preferred construction strategy.

No capability in this map is declared an HSDCR-specific primitive.

No complete architecture is declared.

No protocol is declared.

No novelty claim is declared.

## 11. Next experimental artifact

Build a **composition substitution harness** around the collision invariants.

For each candidate component:
1. select one established implementation;
2. encode its minimum interface;
3. replace it with another established implementation;
4. run identical semantic tests;
5. compare reconstruction, authority separation, evidence separation, and sensitivity/non-reactivity;
6. record any required semantic adapter.

The adapter itself is the object of scrutiny: it may be ordinary translation, or it may reveal a genuine missing abstraction.
