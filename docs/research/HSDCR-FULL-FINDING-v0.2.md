# HSDCR Full Research Finding v0.2

Status: RESEARCH / FINALIZED CURRENT FINDING / NON-NORMATIVE
Recorded: 2026-09-29
Repository: Loofy147/Machine

## 1. Executive finding

HSDCR remains a working research label. It is not promoted to a protocol, standard, product, repository implementation, decentralized network, or proven architecture.

The strongest current explanation remains composition of already-known capabilities with explicit semantic boundaries.

Current frontier:

new repository primitive  = NOT_DETECTED
new execution primitive   = NOT_DETECTED
irreducible residual       = OPEN
composition absorption     = OPEN
architecture              = NOT_ASSIGNED
protocol                  = NOT_ASSIGNED
novelty                   = NOT_CLAIMED

## 2. Reconstructed model

Seven semantic boundaries remain under test:

1. contribution / proposal;
2. observation;
3. evidence;
4. authority;
5. decision / acceptance;
6. canonical state;
7. reconstruction.

Removing one changes the modeled semantics, but that does not make the role a new primitive.

Known capabilities are adoption targets:

- identity and content addressing;
- versioning;
- concurrent change;
- replication/synchronization;
- signal transport;
- persistence;
- replay;
- orchestration.

Rule:

adopt(capability) != adopt(ontology)

## 3. Protected semantic separations

The current invariant set is:

identity != location
contribution != canonical state
signal != observation
observation != evidence
evidence != authority
observation != mutation authority
decision != canonical state
reconstruction != synchronization
convergence != acceptance
semantic equivalence != resource equivalence
semantic equivalence != authority equivalence
semantic equivalence != durability equivalence

High sensitivity without automatic canonical reaction is a behavioral constraint.

Decentralized contribution without a decentralized authority assumption is a topology/separation rule.

Contract-relative capability is a Machine research method rather than HSDCR ontology.

## 4. Related research conclusion

The frozen related-research baseline covers the material neighborhood:

GitHub provides proposal/review/check/gated-merge mechanics; AT Protocol provides signed self-certifying Merkle repositories and synchronization; Automerge provides CRDT history, storage and synchronization; Pijul makes changes and dependencies first-class; W3C PROV models provenance; OpenTelemetry separates event time and observation time; UCAN models delegable authority; Rekor models append-only verifiable transparency; ForgeFed models federated forge collaboration; lakeFS provides versioned data with pull requests and controlled merge; Event Sourcing provides reconstruction from stored events.

Foundational distributed-systems research additionally covers state-based CRDTs, delta-state CRDTs, Merkle Search Trees, and compositional authority/concurrency reasoning.

Therefore the literature is sufficient to establish strong reduction pressure. It is not sufficient to prove that no novel composition could exist.

## 5. Direct GitHub -> AT boundary finding

Current GitHub PR #10 metadata observed on 2026-09-29:

- state: open;
- merged: false;
- base: research/bidirectional-substrate-v3@59fab62704875193801db77c7cb8361475297f48;
- current head: research/machine-substrate-primitive-closure-v0@5db33b068c0973606e08b596a300e99952764aeb.

The AT side is a pinned historical public record fixture:

at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.post/3mp54n7zccc2j2

type: app.bsky.feed.post

A live recheck on 2026-09-29 through the available fetch path returned a temporary gateway 504. The record is therefore retained as historical evidence, not stated as current live state.

At the declared abstract boundary:

GitHub PR -> PROPOSED and non-canonical

AT native repository record -> SOURCE_REPOSITORY_RECORD and canonical within the source repository

Result:

DIRECT_COLLISION

This is a narrow substitution collision. It is not evidence that AT Protocol cannot implement proposal semantics. An ordinary application proposal wrapper restores the tested boundary in the model.

## 6. Composition reduction

The component-removal model shows:

- remove observation -> signal/evidence separation collapses;
- remove evidence -> observations must carry evidentiary semantics;
- remove authority -> permission becomes implicit;
- remove decision/acceptance -> canonicalization becomes implicit;
- remove proposal/contribution -> the pre-canonical locus disappears;
- remove reconstruction -> replay/rebuild semantics disappear.

But every remaining role can still be represented as ordinary typed data plus explicit relations/transitions.

Therefore:

semantic necessity != new primitive

The deterministic reduction experiment did not detect a new repository or execution primitive.

A previous CI failure exposed a byte-level evidence-fixture mismatch. It was corrected and revalidated in run 36360126367. That negative finding is retained as evidence-integrity history.

## 7. Final hardened E2E experiment

Experiment: experiments/hsdcr-e2e-composition-v0.3/

The final oracle closes the known local methodological defects:

- actual signal loss;
- serialization of acceptance history;
- clearing in-memory history;
- rehydration from persisted representation;
- reconstruction after signal loss;
- non-self-referential result hashing;
- current GitHub metadata fixture;
- explicit historical status for the AT fixture;
- abstract-boundary equivalence separated from provider semantic equivalence.

The recorded result is reproducible in CI. The finalized experiment commit was b90f3a07ade917ff7bc8b663b7de3269fd5a40fd and CI run 36616680163 completed successfully with both the oracle and byte-level fixture comparison passing.

The recorded result is:

all declared boundary tests = PASS
new repository primitive = NOT_DETECTED
new execution primitive = NOT_DETECTED
provider semantic equivalence = NOT_ESTABLISHED
resource equivalence = NOT_EXECUTED
authority equivalence = NOT_EQUALIZED
durability = LOCAL_PERSISTENCE_REHYDRATION_ONLY
architectural novelty = OPEN

The v0.3 experiment is a composition oracle, not a production-system proof.

## 8. Satisfied gates for this research stage

The following are satisfied:

- semantic/capability/constraint separation;
- explicit invariant vocabulary;
- real-source contribution boundary test;
- current versus historical provenance separation;
- deterministic reduction harness;
- CI byte-for-byte evidence reproduction at the finalized v0.3 experiment commit;
- actual signal perturbation;
- serialized-history rehydration;
- explicit reconstruction;
- non-self-referential hashing;
- related-research baseline;
- gap-closure matrix;
- negative-finding retention;
- explicit non-promotion gate.

## 9. Remaining open gaps

The following remain intentionally OPEN:

- independent real evidence implementations;
- independent real authority implementations;
- crash/restart persistence and crash consistency;
- resource/cost equivalence;
- production durability;
- production security/authority guarantees;
- deeper provider substitution beyond the current boundary;
- proof of irreducible composition, if any.

These remain open because no existing evidence justifies upgrading them.

## 10. Strongest current kill hypothesis

The strongest current non-novelty composition remains:

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

Current evidence is consistent with HSDCR being a composition pattern rather than a new architecture.

The next discriminating test is independent real-provider substitution at evidence and authority boundaries, followed by a crash/restart persistence experiment.

## 11. Promotion gate

Promotion beyond a working label requires all of:

1. the semantic relation is required;
2. it survives multiple provider substitutions;
3. ordinary data and explicit transitions cannot express it;
4. adapters do not eliminate the residual;
5. at least two independent realizations require the residual;
6. the resource contract is explicit;
7. independent reproduction succeeds.

Until then:

architecture = NOT_ASSIGNED
protocol = NOT_ASSIGNED
novelty = NOT_CLAIMED

## 12. Delivery disposition

This is delivery-ready as a falsifiable research package.

It is not a product/protocol/architecture specification.

The canonical delivery set is:

- HSDCR-RESEARCH-CURRENT.md
- HSDCR-FULL-FINDING-v0.2.md
- HSDCR-RELATED-RESEARCH-BASELINE-v0.1.md
- HSDCR-GAP-CLOSURE-MATRIX-v0.1.md
- experiments/hsdcr-e2e-composition-v0.3/
- experiments/hsdcr-composition-reduction-v0/
- historical v0.1/v0.2 E2E artifacts

Final finding:

The research has successfully moved from feature accumulation to composition falsification.

At the present frontier, no irreducible HSDCR semantic, repository, or execution primitive has been experimentally detected.

The remaining question is sharply bounded: does independent real-provider substitution reveal a semantic relation that ordinary typed data, adapters, explicit acceptance transitions, and known capabilities cannot express?

Until such a residual is demonstrated, HSDCR remains a research label.
