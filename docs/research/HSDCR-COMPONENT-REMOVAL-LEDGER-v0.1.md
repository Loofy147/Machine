# HSDCR Component-Removal Ledger v0.1

Status: **RESEARCH / NON-NORMATIVE / OPEN**

Recorded: **2026-09-28**

This ledger is a reduction experiment, not an architecture specification.

| Component | Primary supplied atoms | Shared/overlapping atoms | What must remain distinguishable | Replacement candidates | Removal result | Status |
|---|---|---|---|---|---|---|
| Identity | immutable identity, actor/subject binding | lineage, authority | identity must not become location | Git object IDs, DID, actor IDs | Not removed yet | OPEN |
| Versioned state / repository | durable state, history, snapshots | contribution lineage, reconstruction | canonical state distinct from proposal | Git, AT repo, lakeFS, event log | Not removed yet | OPEN |
| Contribution/change | independent change locus, contribution lineage | state history, proposal | contribution must be able to remain non-canonical | Git branch/commit, Pijul change, CRDT change | Not removed yet | OPEN |
| Observation/signal | event/signal detection | evidence, telemetry history | observation must not itself authorize mutation | OpenTelemetry, event stream, webhook/event layer | Not removed yet | OPEN |
| Evidence/provenance | derivation/attestation/audit relation | observation, lineage | evidence must remain distinct from authority and decision | PROV, Rekor, signed attestations | Not removed yet | OPEN |
| Authority | ability to cause permitted effects | identity, provenance | authority must not arise from reachability or evidence | UCAN, GitHub rulesets, ACL/capability layer | Not removed yet | OPEN |
| Acceptance/decision | transition from proposed/non-canonical to canonical | authority, review | decision must be distinguishable from evidence and observation | PR merge rules, domain transition function | Not removed yet | OPEN |
| Reconstruction | derive canonical/temporal state from durable records | history, event log, repository | reconstruction must not be conflated with synchronization | Git history, AT repo, event sourcing | Not removed yet | OPEN |
| Sensitivity | early/weak signal detection | observation, observability | sensitivity must not imply automatic reaction | telemetry + durable observation rules | Not removed yet | OPEN |
| Synchronization | state propagation among loci | reconstruction, CRDT | synchronization must not be required for local reconstruction | AT sync, CRDT sync, Git fetch/push | Not removed yet | OPEN |

## Removal interpretation

A component is **removable** when all required atoms and collision invariants remain expressible without adding a semantic primitive or silently changing their meaning.

A component is **structurally necessary in the candidate composition** when removing it causes at least one required distinction to become unrepresentable or forces an existing component to absorb a different semantic class.

A component is **replaceable** when another existing family supplies the same required semantic role without changing the candidate's distinctions.

A component is **not proven necessary** merely because it is convenient or commonly used.

## First-order dependency graph

```
identity ───────────────┐
                        ↓
contribution ───────→ lineage
                        ↓
observation ───────→ evidence
                        ↓
authority ─────────→ acceptance/decision
                        ↓
                  canonical state
                        ↑
                  reconstruction
```

Sensitivity is currently treated as a property over observation acquisition:

```
signal
  -> observation
  -> evidence (optional)
  -> authority/decision (only if separately authorized)
```

Therefore the current non-collapse constraint is:

[
Sensitivity 
eq Authority
]

and:

[
Observation 
eq Mutation
]

## Highest-risk reduction

The highest-risk false reduction is:

```
event
 -> evidence
 -> authority
 -> state transition
```

because several existing systems can encode all four as events or activities while losing their semantic separation.

This must be tested explicitly rather than inferred from successful implementation.

## Next execution

Run the removal tests one component at a time and record:

```
removed_component
preserved_atoms
collapsed_atoms
new_ambiguities
replacement
new_semantic_primitive
resource_delta
reconstruction_delta
disposition
```

No architectural conclusion should be promoted from this ledger until the removal experiments are executed.
