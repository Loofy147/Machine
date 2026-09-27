# PORP Critical Adoption Review v0.1

Status: **RESEARCH / NON-NORMATIVE / OPEN**

Recorded: **2026-09-28**

## 1. Purpose

PORP-1.0 is useful as a source of control-plane semantics, but importing it verbatim would create a second premature ontology.

This review identifies what is strong enough to adopt and what requires refinement before any adoption.

## 2. Strong parts

The following distinctions are already sufficiently explicit to be valuable:

[
capability existence

eq
addressability

eq
invocation

eq
success

eq
verification
]

[
tool success 
eq completion
]

[
retry 
eq recovery
]

[
user intent 
eq unlimited authority
]

[
provider substitution 
eq semantic equivalence
]

[
result 
eq conclusion
]

The task DAG, capability binding, contradiction handling, approval state, verification levels, artifact lifecycle, run manifest, and durable claim concepts are all useful.

## 3. Issues that must not be imported unchanged

### P1 — Capability identity/addressability

A capability descriptor has:
`capability_id, provider, operation`

but does not fully specify the identity of the **bound invocation target**.

A future boundary should separate:

[
capability class

eq
capability instance

eq
binding

eq
invocation
]

Example:

```
"read_repository"
    !=
"Loofy147/Machine"
    !=
"bound connector instance"
    !=
"this invocation"
```

### P2 — Authorization is multidimensional

The linear authorization state:

```
DENY -> APPROVAL_REQUIRED -> APPROVED -> EXECUTABLE -> EXECUTED -> VERIFIED
```

should not be interpreted as one state machine because approval, executability, execution, and verification are logically independent dimensions.

Use:

[
AuthState
	imes
ExecutionState
	imes
EpistemicState
	imes
CompletionState
]

or equivalent independent records.

The PORP text already says these are independent; the formal model should enforce that statement.

### P3 — Acceptance is under-specified

PORP has `DECIDE`, `PROPOSE`, `ACT`, approval and completion states.

It does not define a repository-level transition:

[
proposal
ightarrow
accepted
ightarrow
canonical state
]

as a persistent semantic relation.

This is precisely the boundary exposed by the real GitHub↔AT substitution test.

### P4 — Durable event semantics

"event SHOULD be append-only" is too weak if reconstructibility is a requirement.

Need explicit distinction:

[
event observation

eq
event durability

eq
state transition
]

For reconstruction, the durable record needs:
- stable event identity;
- source identity;
- causal/order metadata where available;
- payload hash/content;
- provenance;
- retention contract;
- schema version.

### P5 — Timestamp semantics

`timestamp`, `observed_at`, and `source_timestamp` have different meanings.

A future contract should prohibit silently replacing source time with local observation time.

At minimum:

[
t_{source}

eq
t_{observed}

eq
t_{persisted}
]

unless equality is explicitly established.

### P6 — Artifact durability

The artifact lifecycle is strong, but content hash alone does not define durability.

Need:

[
artifact identity
+
content address
+
retention
+
retrievability
]

A transient CI artifact is not automatically canonical evidence.

### P7 — Authority provenance

PORP establishes an authority gate but does not fully require that an authorization record itself have provenance sufficient to reconstruct:
- issuer/principal;
- capability;
- scope;
- delegation chain;
- validity interval;
- revocation state.

This boundary should borrow ideas from capability systems rather than invent a provider-specific authorization object.

### P8 — Claim lifecycle

The claim model is useful, but "VERIFIED" should not be treated as an absolute truth state.

A claim needs:
- scope;
- evidence set;
- verifier identity;
- verification method;
- verification time;
- freshness;
- limitations;
- contradictions;
- invalidation/revalidation state.

This matches the stricter Machine evidence discipline.

### P9 — Provider substitution

PORP's substitution contract is valuable but should distinguish:

[
semantic equivalence
]

from:

[
resource equivalence
]

and:

[
authority equivalence
]

and:

[
durability equivalence
]

Two providers may implement the same semantic operation while differing materially in authority, retention, latency, reconstruction, or cost.

### P10 — Canonical state

The run manifest is explicitly descriptive rather than a replacement for systems of record. This is correct.

The missing question is:

> What object is the canonical source of durable domain state?

That question must be answered by the repository/state substrate, not by the orchestration layer.

## 4. Correct placement

PORP should therefore be treated as:

[
oxed{	ext{portable execution/control semantics}}
]

not:

[
oxed{	ext{repository ontology}}
]

and not:

[
oxed{	ext{canonical state model}}
]

## 5. Adoption contract

The safest rule is:

[
PORP capability
ightarrow
portable boundary
ightarrow
repository/state/evidence provider
]

with no reverse dependency in which the provider forces the control-plane ontology.

## 6. Relation to Machine

The current Machine substrate research supplies a complementary rule:

[
primitive = f(contract)
]

PORP should therefore expose contracts rather than naming capabilities as universally primitive.

This prevents:
- provider-specific operations becoming abstract primitives;
- direct lookup being mistaken for a new computational capability;
- execution convenience being mistaken for semantic necessity.

## 7. Most valuable inherited machinery

The highest-value components to reuse are:

1. capability discovery/addressability/invocation distinction;
2. task dependency graph;
3. capability substitution tests;
4. contradiction protocol;
5. explicit authority boundary;
6. idempotency and duplicate mutation guard;
7. verification levels;
8. artifact provenance;
9. durable run/event reconstruction;
10. self-adversarial validation.

## 8. Most valuable repository-specific additions still required

The repository layer still needs explicit contracts for:

[
Contribution
]

[
CanonicalState
]

[
Proposal
]

[
Acceptance
]

[
Replication
]

[
Reconciliation
]

and their relations to:

[
Observation, Evidence, Authority, Decision
]

## 9. Current disposition

PORP control-plane capabilities:
**ADOPTABLE IN PRINCIPLE**

PORP ontology as a complete replacement:
**NOT ADOPTED**

PORP as canonical repository state:
**NOT SUITABLE / NOT SHOWN**

Repository-specific contribution/acceptance semantics:
**OPEN**

Irreducible residual:
**OPEN**

Architecture:
**NOT ASSIGNED**

Protocol:
**NOT ASSIGNED**

Novelty:
**NOT CLAIMED**
