# PORP-to-Repository Candidate Boundary Analysis v0.1

Status: **RESEARCH / NON-NORMATIVE / OPEN**

Recorded: **2026-09-28**

Repository: `Loofy147/Machine`

Branch: `research/hsdcr-neighborhood-crosswalk-v0`

## 1. Purpose

The supplied **Portable Orchestration Protocols — Enhanced Durable Baseline v1.0 (PORP-1.0)** is evaluated as a source of already-specified control-plane capabilities.

It must not be treated as the definition of the repository candidate.

The question is:

> Which PORP capabilities can be adopted directly, which are useful as boundary contracts, and which candidate semantics remain outside PORP?

## 2. Core result

PORP covers a large part of the **orchestration/control-plane** problem:

- capability discovery and classification;
- capability substitution;
- task decomposition and dependency graphs;
- authority separation;
- approval;
- verification;
- recovery and retry;
- contradiction handling;
- epistemic state;
- artifact provenance;
- durable event records;
- claims;
- reconstruction of execution state;
- provider/runtime portability.

Therefore, substantial portions should be treated as **known capability rather than reinvention targets**.

PORP does not, by itself, define:

- a decentralized contribution substrate;
- canonical repository state;
- independent contribution loci;
- proposal-versus-canonical repository semantics;
- replica convergence;
- repository-level identity independent of location;
- evidence as a repository-native semantic object;
- high-sensitivity observation as a native system property.

Therefore PORP is a **strong neighboring control-plane component**, not a demonstrated complete match.

## 3. Direct capability adoption

| PORP capability | Candidate role | Adoption |
|---|---|---|
| Capability Registry | capability discovery/addressability | HIGH-VALUE ADOPTION |
| Capability descriptor | normalized provider-independent interface | HIGH-VALUE ADOPTION |
| Capability substitution | provider replacement test | HIGH-VALUE ADOPTION |
| Task DAG | dependency/reconciliation structure | HIGH-VALUE ADOPTION |
| Context handoff | typed provenance boundary | HIGH-VALUE ADOPTION |
| Freshness | observation validity | HIGH-VALUE ADOPTION |
| Contradiction events | non-silent disagreement | HIGH-VALUE ADOPTION |
| Dynamic replanning | adaptive execution | HIGH-VALUE ADOPTION |
| Failure taxonomy | recovery classification | HIGH-VALUE ADOPTION |
| Idempotency/duplicate handling | safe replay | HIGH-VALUE ADOPTION |
| Authority boundary | mutation permission separation | HIGH-VALUE ADOPTION |
| Approval state | explicit acceptance gate | HIGH-VALUE ADOPTION |
| Verification levels | independent evidence strength | HIGH-VALUE ADOPTION |
| Artifact lifecycle | evidence/data handling | HIGH-VALUE ADOPTION |
| Cross-surface boundary | interoperability contract | HIGH-VALUE ADOPTION |
| Durable event record | reconstructible execution history | HIGH-VALUE ADOPTION |
| Claim model | durable epistemic record | HIGH-VALUE ADOPTION |
| Run manifest | execution reconstruction | HIGH-VALUE ADOPTION |
| Self-adversarial checks | validity/regression pressure | HIGH-VALUE ADOPTION |

## 4. PORP distinctions that directly reinforce the candidate work

PORP explicitly separates:

[
capability exists

eq
capability addressable

eq
capability invoked

eq
operation succeeded

eq
postcondition verified
]

This is exactly the kind of atomic distinction required by the present repository research.

Likewise:

[
tool success 
eq completion
]

[
documentation 
eq runtime evidence
]

[
user intent 
eq unlimited authority
]

[
alternative provider 
eq valid substitution
]

[
retry 
eq recovery
]

These should be treated as reusable control-plane invariants, not rediscovered.

## 5. Strong overlap with current Machine evidence discipline

The current Machine research already distinguishes:

[
Result 
eq Conclusion
]

and requires:

[
Observation
ightarrow
Evidence
ightarrow
Disposition
ightarrow
Regression
]

PORP gives an execution-oriented counterpart:

[
Action
ightarrow
Primary result
ightarrow
Independent observation
ightarrow
Comparison
ightarrow
Postcondition
]

The two should therefore be compared as complementary layers, not competing ontologies.

## 6. Where PORP does NOT close the repository problem

### R1 — Contribution locus

PORP can execute or orchestrate a task that creates a contribution.

It does not define a first-class decentralized contribution locus comparable to:
- Git branches/forks;
- CRDT replicas;
- AT repositories;
- Pijul change spaces.

Therefore:

[
Task 
eq Contribution
]

### R2 — Proposal versus canonical state

PORP has proposal/decision/approval notions, but its core object is an orchestration run.

It does not define repository semantics in which:

[
Contribution 
eq CanonicalState
]

as a persistent state model.

A repository-specific layer remains necessary.

### R3 — Canonical-state reconstruction

PORP can reconstruct **execution state** from its events/manifests.

That is not automatically:

[
reconstruct(durable repository history)
ightarrow canonical repository state
]

The latter belongs to the repository/state substrate.

### R4 — Replication and convergence

PORP describes portability and provider substitution.

It does not define a distributed replicated-state convergence model.

Therefore it cannot replace:
- CRDT semantics;
- authenticated repository synchronization;
- Git replication;
- or equivalent state-reconciliation mechanisms.

### R5 — Sensitivity

PORP allows event-driven execution, current observations, and re-observation.

But it does not define a formal sensitivity function.

The candidate's remaining sensitivity question therefore stays:

[
Sensitivity =
f(detection threshold, latency, granularity, false positive policy, retention)
]

and must not be inferred from the existence of an event loop.

### R6 — Evidence ontology

PORP has evidence-aware execution and provenance-bearing artifacts/claims.

However, it remains intentionally implementation-neutral.

It does not freeze an ontology equivalent to:

[
Observation, Evidence, Authority, Decision, CanonicalState
]

as repository-native durable classes.

That distinction remains part of the open investigation.

## 7. Architectural placement candidate

PORP is best modeled as:

[
oxed{	ext{Control / Orchestration Layer}}
]

over lower-level capability providers:

```
                CONTROL / ORCHESTRATION
                        PORP-like
                           |
             +-------------+-------------+
             |             |             |
         Capability     Evidence     Authority
          adapters       adapters      adapters
             |             |             |
             +-------------+-------------+
                           |
                  Repository / State
                    substrate(s)
```

The repository candidate can therefore **adopt PORP-like execution semantics without becoming PORP**.

## 8. Important negative result

If the complete candidate can be reduced to:

```
PORP
+
repository provider
+
evidence provider
+
authority provider
```

with no new semantic coupling, then the candidate is a composition and not an irreducible architecture.

This is a valid kill condition.

Conversely, if the composition requires a new semantic object that cannot be represented as ordinary data or an adapter, that object becomes the next research target.

## 9. Highest-value missing boundary

The most informative remaining junction is:

[
oxed{
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
}
]

PORP already supplies much of the **execution discipline around** this chain.

The unresolved question is whether a repository-native composition needs a special semantic relation between these stages.

## 10. Proposed experiment

Construct a minimal system from:

1. PORP-style orchestration core;
2. GitHub contribution surface;
3. one alternate contribution/state source (AT Protocol or CRDT);
4. provenance/evidence representation;
5. explicit authority provider.

Then test:

- semantic substitution;
- contribution non-canonicality;
- evidence/authority separation;
- reconstruction;
- interruption recovery;
- duplicate mutation prevention;
- provider replacement.

The experiment must report:

[
semantic equivalence
]

separately from:

[
resource equivalence
]

and must preserve provenance for every component.

## 11. Current disposition

PORP contribution to the investigation:

**HIGH-VALUE KNOWN CAPABILITY SOURCE**

PORP as a complete candidate replacement:

**NOT ESTABLISHED**

PORP as the candidate ontology:

**REJECTED FOR NOW**

PORP as an orchestration/control-plane layer:

**STRONG CANDIDATE**

Repository-specific residual:

**OPEN**

Architecture:

**NOT ASSIGNED**

Protocol:

**NOT ASSIGNED**

Novelty:

**NOT CLAIMED**

## 12. Governing rule

> Adopt PORP's proven distinctions and control-plane mechanisms where they fit; do not allow PORP's object model to determine the repository candidate's ontology.

The next experiment must test the boundary, not rename the boundary.
