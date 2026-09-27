# HSDCR Reassessment v0.1

Status: **RESEARCH / NON-NORMATIVE / OPEN**
Recorded: 2026-09-28
Repository: `Loofy147/Machine`
Branch: `research/hsdcr-reassessment-v0`
Base: `research/bidirectional-substrate-v3@59fab62704875193801db77c7cb8361475297f48`

## 1. Purpose

The previous HSDCR pass was useful for discovery but overcounted candidate "atoms". It mixed domain semantics, known substrate capabilities, and research-method constraints. This revision separates them before any architectural claim.

## 2. What is currently established

- HSDCR remains a **working label only**.
- The real GitHub↔AT test found a narrow direct-substitution collision: GitHub PR #10 preserves a non-canonical proposal surface, while a native AT repository record is a repository mutation. An application-level proposal/acceptance layer is required for that direct substitution. This is not an AT impossibility claim.
- PORP is a candidate **control/orchestration capability source**, not a repository ontology. Its critical review identifies missing repository-native semantics for proposal, acceptance, canonical state, durable events, and authority provenance.
- Machine substrate work contributes a **contract-relative resource/evidence discipline**, not an HSDCR architecture claim.

## 3. Atom overcounting correction

### Domain semantics to keep under test

1. proposal/contribution;
2. observation;
3. evidence;
4. authority;
5. decision/acceptance;
6. canonical state;
7. reconstruction.

### Capabilities to adopt from known systems

Identity, content addressing, versioning, concurrent change, replication/synchronization, signal transport, persistence, and execution/orchestration are not HSDCR-specific primitives at present.

### Constraints, not atoms

The following are guards against semantic collapse:

```
identity != location
signal != evidence
evidence != authority
observation != mutation authority
reconstruction != synchronization
convergence != acceptance
semantic equivalence != resource equivalence
```

"High sensitivity without automatic canonical reaction" is currently a behavioral constraint, not a primitive.

"Decentralized contribution without decentralized authority assumption" is a topology/separation rule, not an atom.

"Contract-relative capability" is a Machine research method, not repository ontology.

## 4. External reduction pressure

Current primary-source checks confirm that neighboring systems already cover most required mechanics:

- GitHub pull requests, reviews, checks, and protected-branch/ruleset gates provide proposal/review/controlled merge mechanisms. citeturn958553search4turn958553search6turn958553search7
- AT Protocol provides self-certifying repositories, signed commits, Merkle state, exports and synchronization. citeturn958553search1turn958553search0
- Automerge provides local-first CRDT changes, persistent repository storage and peer synchronization. citeturn349578search2turn349578search4turn349578search6
- Pijul makes changes first-class and supports distributed change exchange and dependencies. citeturn979116search2turn979116search3turn979116search8
- W3C PROV already represents provenance over entities, activities, agents, derivation and revision. citeturn979116search0turn979116search5
- OpenTelemetry already standardizes signal categories and distinguishes event timestamp from observed timestamp. citeturn349578search0turn349578search1

Therefore the research burden is now composition irreducibility, not feature discovery.

## 5. Reassessment of the collision matrix

A source should be marked "collision" only when direct embedding collapses a required distinction under the declared boundary.

The current GitHub↔AT result satisfies that narrow criterion.

The remaining collision flags in the earlier atomic ledger are hypotheses until executed.

## 6. New reduction result

`experiments/hsdcr-composition-reduction-v0/` is an internal deterministic model check.

It finds that removing each domain-semantic role collapses a required distinction, but each role can still be represented as ordinary typed data plus explicit relations/transitions.

Thus:

```
semantic necessity != architectural novelty
```

No new execution primitive or repository primitive was detected by this reduction.

## 7. Strongest current kill hypothesis

The strongest current non-novelty model is:

```
repository/change substrate
+
signal/observation layer
+
evidence/provenance records
+
authority/capability records
+
explicit acceptance transition
+
orchestration/control layer
```

The candidate may therefore reduce to an ordinary composition pattern. This has not yet been fully confirmed end-to-end.

## 8. Branch hygiene

The prior HSDCR PR #11 currently contains 98 changed files and 153 commits relative to its declared base. Much of that surface belongs to earlier Machine research.

That is not a scientific contradiction, but it is poor evidence-surface isolation.

This branch is intentionally rooted at the same substrate base and contains only the new reassessment/reduction artifact set.

## 9. Next discriminating test

Run an end-to-end two-provider composition:

```
Contribution: GitHub PR <-> AT application proposal
Evidence: provenance record <-> signed attestation
Authority: capability/delegation <-> repository gate
Reconstruction: repository history <-> replay/event record
Control: PORP-like semantics <-> explicit state-machine semantics
```

The key test is whether all provider substitutions preserve the same abstract semantics without inventing a new semantic class.

## 10. Disposition

```
working_label_only = TRUE
known_capability_adoption = PREFERRED
single_family_absorption = NOT_IDENTIFIED
composition_absorption = OPEN
new_semantic_primitive = NOT_DETECTED
irreducible_residual = OPEN
architecture = NOT_ASSIGNED
protocol = NOT_ASSIGNED
novelty = NOT_CLAIMED
```
