# HSDCR Full Research Finding v0.1

Status: **RESEARCH / NON-NORMATIVE / OPEN**  
Recorded: 2026-09-29  
Repository: `Loofy147/Machine`

## 1. Scope and naming

HSDCR (working label: "Highly Sensitive Decentralized Contribution Repository") is **not** promoted here to a protocol, standard, product, repository implementation, decentralized network, or proven architecture.

The working label identifies a research target. The ontology must be determined by experiments rather than by the name.

The governing research loop is:

`Observe -> Identify -> Evidence -> Interpret -> Decide -> Record -> Revalidate`

Unproven material remains `UNKNOWN` or `OPEN`.

---

## 2. Why the reassessment was necessary

The first HSDCR pass treated too many things as candidate primitives.

The correction was to separate three classes.

### A. Domain semantics under test

1. contribution / proposal;
2. observation;
3. evidence;
4. authority;
5. decision / acceptance;
6. canonical state;
7. reconstruction.

These are semantic distinctions worth preserving because collapsing any one changes the modeled behavior.

### B. Known capabilities to adopt rather than reinvent

- identity;
- immutable/content-addressed data;
- versioning;
- concurrent change;
- replication/synchronization;
- signal transport;
- persistence;
- replay;
- execution/orchestration.

Current evidence does not justify treating any of these as HSDCR-specific primitives.

### C. Constraints and guards

The following protect semantic separation:

```
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
```

"High sensitivity without automatic canonical reaction" is currently a behavioral constraint, not a primitive.

"Decentralized contribution without decentralized authority assumption" is currently a separation/topology rule, not a primitive.

"Contract-relative capability" belongs to the Machine evidence/research method, not to the HSDCR ontology.

---

## 3. Evidence accumulated

### 3.1 Real GitHub -> AT direct substitution

The strongest direct provider test used:

- GitHub `Loofy147/Machine` PR #10;
- base `research/bidirectional-substrate-v3@59fab62704875193801db77c7cb8361475297f48`;
- head `research/machine-substrate-primitive-closure-v0@12dade33f708d66890c6c10b754f85c1d3ae13e3`;
- PR remained open and unmerged at observation time.

At the AT side, the test used a real public record:

- DID `did:plc:z72i7hdynmk6r22z27h6tvur`;
- record `at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.post/3mp54n7zccc2j2`;
- record type `app.bsky.feed.post`.

The direct projection did **not** preserve the specific boundary "proposal exists before canonical acceptance":

```
GitHub PR surface:
PROPOSED + canonical=false

AT native repository record surface:
CANONICAL_RECORD + canonical=true
```

Disposition:

`DIRECT_COLLISION`

This is a narrow semantic collision under the declared direct-substitution boundary. It is **not** evidence that AT Protocol cannot implement proposals; the experiment itself adds an ordinary application-level proposal record and restores the distinction.

### 3.2 Application-level adapter test

The AT record was wrapped by an explicit application proposal record carrying:

- a proposal identity;
- base state;
- target/result reference;
- non-canonical proposal status;
- reference to the underlying AT record.

The semantic boundary was restored without introducing a new repository or execution primitive in the test model:

`SEMANTIC_BOUNDARY_PRESERVED`

The adapter is therefore treated as ordinary application representation plus an explicit transition, not as proof of a new primitive.

### 3.3 Composition reduction

The composition-reduction experiment removed each domain-semantic role one at a time.

Each removal collapses a required distinction at the modeled boundary, for example:

- remove observation -> signal/evidence separation disappears;
- remove evidence -> observation must carry evidentiary semantics;
- remove authority -> permission becomes implicit in evidence or decision;
- remove decision/acceptance -> canonicalization becomes implicit;
- remove proposal/contribution -> pre-canonical locus disappears;
- remove reconstruction -> durable replay semantics disappear.

The critical result is:

`semantic necessity != new primitive`

Each role can still be represented as typed data plus explicit relations/transitions in a known substrate model.

Therefore the reduction did **not** identify an irreducible execution or repository primitive.

The composition-reduction evidence package was corrected after an initial CI failure caused by byte-level fixture mismatch. That first failure was an evidence-integrity/reproducibility defect, not a semantic negative result. After correction, the gate reproduced the stored fixture successfully in CI run `36360126367`.

### 3.4 End-to-end composition v0.1

PR #13 tested the semantic junction:

`proposal -> evidence -> authority -> decision -> canonical state -> reconstruction`

The CI run:

`36360225545`

completed successfully. The job executed the composition oracle and then compared its output with the recorded evidence.

The v0.1 test established a passing contract-composition check, but review identified a methodological weakness: signal loss had been represented by a boolean rather than actually simulated, and the stored result hash used a self-reference convention that was not sufficiently explicit.

### 3.5 Hardened v0.2 revalidation

The v0.2 harness corrects those weaknesses.

The signal stream is now created, counted, actually dropped, and reconstruction is performed from durable acceptance history rather than from the signal stream.

The result digest is computed over a canonical payload that explicitly excludes its own digest field.

The expected v0.2 result is:

- all declared boundary tests pass;
- direct GitHub -> native AT substitution remains a collision;
- AT + ordinary proposal wrapper preserves the boundary;
- no new repository primitive is detected;
- no new execution primitive is detected;
- semantic equivalence is tested only at the declared abstract boundary;
- resource, authority, and durability equivalence remain un-equalized.

The v0.2 evidence must still be CI-revalidated before its status is upgraded from `PENDING`.

---

## 4. What is currently established

### ESTABLISHED / RESEARCH-LOCAL

The following distinctions are useful and repeatedly survive the current modeled tests:

`proposal/contribution`, `observation`, `evidence`, `authority`, `decision/acceptance`, `canonical state`, and `reconstruction`.

They should remain explicit semantic boundaries in future experiments.

### EXPERIMENTALLY_SUPPORTED

Under the tested GitHub/AT boundary, a direct native AT repository record is not semantically equivalent to the GitHub PR proposal surface for "proposal before canonical acceptance".

An ordinary application-level proposal wrapper restores the tested distinction without a detected new repository/execution primitive.

The deterministic composition-reduction model did not detect an irreducible primitive.

### USER_REPORTED / CONTEXT

The motivation for HSDCR is to combine highly sensitive contribution intake with explicit separation of observation, evidence, authority, acceptance, and durable reconstruction while avoiding automatic mutation from signals.

These motivations are not treated as external empirical proof.

### UNKNOWN / OPEN

- whether the composition remains irreducible when evidence and authority are replaced by independent real implementations;
- whether a common minimal semantic kernel survives broader provider substitution;
- whether resource, durability, security, or authority guarantees introduce an irreducible dependency;
- whether any residual warrants a distinct architecture at all.

---

## 5. Strongest current kill hypothesis

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

Current evidence is consistent with the candidate reducing to this composition.

The critical conclusion is therefore **not** "HSDCR is a new architecture".

The current conclusion is:

`composition absorption = OPEN`

and

`new semantic primitive = NOT_DETECTED`

That is a stronger and more useful research state than an early architecture claim because it identifies the exact remaining burden of proof.

---

## 6. Negative findings that must not be lost

1. Naming the semantic roles does not make them new primitives.
2. Removing a semantic role can prove that the role matters without proving architectural novelty.
3. Direct GitHub -> AT substitution collision is boundary-specific; it is not a claim of provider incapability.
4. Normalized evidence/authority fixtures cannot establish live-provider equivalence.
5. CI pass validates reproducibility of the declared experiment; it does not validate novelty.
6. Resource, authority, durability, and semantic equivalence must remain separate dimensions.
7. Signal loss must be exercised as an actual state perturbation, not represented by a hard-coded expected value.
8. A result digest must have explicit self-reference semantics; v0.2 defines it over the payload excluding the digest field.

---

## 7. Current capability-adoption rule

The working adoption principle is:

`adopt(capability) != adopt(ontology)`

Use mature systems for capabilities they already implement well rather than rebuilding them merely to make the candidate look self-contained.

Current adoption map:

| Capability | Existing family candidates |
|---|---|
| identity / content identity | Git, AT Protocol, Software Heritage |
| contribution/change | Git/GitHub, CRDTs, Pijul |
| concurrent reconciliation | CRDTs, Pijul |
| versioned canonical state | Git, AT Protocol, lakeFS, event sourcing |
| replay/reconstruction | event sourcing, AT repository history |
| evidence/provenance | W3C PROV and provenance records |
| tamper-evident publication | transparency-log families such as Rekor |
| fine-grained authority | UCAN-style capability systems, GitHub gates |
| high-sensitivity signals | OpenTelemetry/event streams |
| orchestration/control | PORP-like control-plane semantics |
| contract-relative capability | Machine substrate/research contracts |

This table is a research adoption map, not a claim that the providers are semantically interchangeable.

---

## 8. The actual residual question

The next test should not ask:

"Can we build HSDCR?"

It should ask:

"After replacing each normalized boundary with an independent real implementation, is there any semantic relation that cannot be represented without introducing a new primitive?"

Required replacement matrix:

```
Contribution:
  GitHub PR <-> AT application proposal

Evidence:
  provenance record <-> signed attestation / transparency record

Authority:
  capability/delegation <-> repository gate

Reconstruction:
  repository/history <-> replay/event record

Control:
  explicit transition state machine <-> PORP-like orchestration semantics
```

The comparison must report at least:

```
semantic equivalence
resource equivalence
authority equivalence
durability equivalence
```

independently.

---

## 9. Promotion gate

HSDCR must remain a working label until all of the following survive:

1. the semantic boundary is shown to be required;
2. the boundary survives multiple provider substitutions;
3. ordinary data representation and explicit transitions cannot express it;
4. the residual survives implementation/adaptor reduction;
5. at least two independent realizations require the same residual behavior;
6. the resource contract is explicit;
7. the result is independently reproducible.

Failure of any one gate keeps the result at `OPEN`, `UNKNOWN`, or `COMPOSITION` rather than promoting it to a protocol or architecture.

---

## 10. Current disposition

```
HSDCR working label              = ACTIVE
known-capability adoption        = PREFERRED
semantic boundaries               = PRESERVE
direct GitHub<->AT collision      = EXPERIMENTALLY_SUPPORTED
composition reduction             = PASSING MODEL CHECK
hardened E2E v0.2                 = PENDING CI REVALIDATION
new execution primitive           = NOT_DETECTED
new repository primitive          = NOT_DETECTED
irreducible residual              = OPEN
composition absorption             = OPEN
architecture                      = NOT_ASSIGNED
protocol                         = NOT_ASSIGNED
novelty                          = NOT_CLAIMED
```

The research target is therefore narrower than the original HSDCR framing.

The productive next move is independent-provider substitution at the evidence and authority boundaries. If that also reduces cleanly, the correct artifact may be a capability composition/design pattern rather than a new architecture or protocol.

---

## 11. Provenance index

### Machine
- Repository: `Loofy147/Machine`
- substrate base: `research/bidirectional-substrate-v3@59fab62704875193801db77c7cb8361475297f48`
- reassessment branch: `research/hsdcr-reassessment-v0`
- E2E branch: `research/hsdcr-e2e-composition-v0`
- hardened finding branch: `research/hsdcr-full-finding-v0`

### Pull requests
- PR #10: substrate primitive-closure source used as a real GitHub proposal fixture
- PR #11: earlier broad HSDCR neighborhood/research surface; retained as historical evidence but not used as the clean isolation baseline
- PR #12: HSDCR reassessment and reduction
- PR #13: HSDCR E2E composition v0.1

### CI evidence
- composition-reduction corrected/revalidated: run `36360126367`
- HSDCR E2E composition v0.1: run `36360225545`
- hardened v0.2: new branch/workflow to be CI-revalidated

---

## 12. Final finding for this revision

The research has moved from feature accumulation to falsifiable composition reduction.

At the present frontier, the candidate HSDCR does **not** have an experimentally detected irreducible semantic, repository, or execution primitive.

The strongest surviving structure is a composition of already-known capabilities with explicit semantic boundaries and acceptance transitions.

That does not kill the idea. It changes the burden of proof.

The remaining work is to determine whether the separation of proposal, evidence, authority, acceptance, canonical state, and reconstruction still requires an irreducible semantic relation when independent real implementations are substituted at each boundary.

Until that residual is demonstrated, HSDCR remains a research label, not a protocol or architecture claim.
