# Deeper Questions About Machine Intelligence

Status: RESEARCH / OPEN

This document records questions that emerged from the project's earlier conceptual work and the later operational analysis. They are research questions, not architectural primitives and not evidence for any answer.

## 1. What changes?

### 1.1 When should an outcome change state versus structure?

> What gives an event the ability to change the machine's future operating structure, rather than only its transient state?

Candidate distinction:

```text
observation
  -> state update

observation
  -> policy update

observation
  -> executable-structure update
```

These are different claims and require separate controls.

### 1.2 When should the model change?

> When a prediction fails, how can the machine distinguish a local prediction error from evidence that the model producing the prediction is inadequate?

Candidate update levels:

```text
prediction error
-> parameter update
-> policy update
-> representation update
-> model replacement
```

This is an open hierarchy, not a proposed fixed architecture.

### 1.3 When should the problem representation change?

> How can the machine detect that failure comes from the way the problem was represented or decomposed rather than from the operation chosen inside that representation?

This question targets changes to the hypothesis space itself rather than better search inside a fixed space.

## 2. What matters?

### 2.1 Operational significance

> What gives a state, consequence, or uncertainty the ability to change the relative value of available transitions?

A candidate relation is:

```text
significance(S, consequence, conditions) -> transition preference
```

The relation must not silently import a hidden human objective.

### 2.2 Suppression and irrelevance

> How does a machine determine that an available signal, memory, or operation should not receive additional computational influence?

This is the dual of salience:

```text
relevance
vs
irrelevance / suppression
```

A system that only detects what matters may still fail because irrelevant information can consume computation or alter policy.

### 2.3 Stale significance

> When does an old signal remain correct but cease to deserve operational influence?

This separates correctness from current relevance and connects significance to persistence and decay.

## 3. What should be inferred?

### 3.1 Same observation, different interpretation

> How can the machine detect that identical observations have different meanings under different operating regimes?

Candidate relation:

```text
interpretation(observation | context)
```

This is stronger than context-conditioned action selection because the context may alter the representation of the observation itself.

### 3.2 Prediction versus model failure

A wrong prediction can mean:

```text
model correct, parameter wrong
model correct, state changed
model incomplete
model class wrong
```

The machine needs evidence that distinguishes these cases before changing higher-level structure.

## 4. What should persist?

### 4.1 Value of retention

> When should an event survive beyond its immediate context, given that future utility is unknown at the time of retention?

Candidate variables:

```text
future utility estimate
reuse frequency
causal relevance
uncertainty
storage / retrieval cost
staleness risk
```

### 4.2 When is forgetting corrective?

> When does retaining a correct historical record become harmful because its context has expired or its influence is stale?

Forgetting is therefore potentially a correctness mechanism, not merely resource management.

### 4.3 What survives an operation?

Possible retained objects should be distinguished:

```text
raw event
relation
consequence
causal explanation
policy change
executed structure
lineage
```

The project must not assume that one is the universal memory unit.

## 5. What may influence what?

### 5.1 Allowed influence

> Which pieces of state or history should be permitted to influence which future transitions?

Technical possibility does not imply causal permission.

```text
possible connection
    !=
permitted influence
```

### 5.2 Isolation

> What should remain deliberately disconnected even when a connection could improve local performance?

This may matter for safety, stale knowledge, conflicting regimes, and experimental isolation.

### 5.3 Preserving ambiguity

> When several interpretations remain compatible with evidence, when should the machine retain them concurrently rather than collapse to one?

Candidate operational behavior:

```text
retain candidate set
    -> gather discriminating evidence
    -> commit only when justified
```

This should be compared against forced early commitment.

## 6. What should be explored?

### 6.1 Value of information

> When does acquiring new information justify its computational, temporal, or environmental cost?

Candidate relation:

```text
information_value
    vs
acquisition_cost
    vs
expected downstream consequence
```

### 6.2 Novelty is not enough

A novel transition is not automatically useful.

The research question is:

> Can exploration target uncertainty or decision relevance rather than novelty alone?

### 6.3 Before or after danger?

For avoidance-like behavior:

> Should the machine change policy from predicted costly consequences, from experienced costly consequences, or from a combination of both?

This separates predictive and history-based adaptation.

## 7. What should change under pressure?

### 7.1 Urgency without a human label

> Can increasing cost of delay, decreasing reversibility, or shrinking resource slack produce a measurable change in transition priority without introducing an explicit variable called urgency?

Candidate signature:

```text
predicted consequence cost  ↑
time to consequence         ↓
reversibility                ↓
mitigation priority          ↑
```

### 7.2 Frustration-like regime change

> When repeated attempts fail, what evidence should trigger a change of operating regime rather than another retry?

This can be tested without implementing a module named frustration.

## 8. What constitutes learning?

### 8.1 Strategy change versus model change

> When should an outcome alter the strategy for using a model, and when should it alter the model itself?

### 8.2 Generalization versus adaptation

> How can the machine distinguish learning a transferable relation from fitting a local regime?

Candidate controls:

```text
held-out states
held-out contexts
held-out task families
fresh-search baseline
```

### 8.3 Learning-mechanism failure

> How can the machine discover that its own learning procedure systematically favors the wrong proxy or regime?

This is a meta-level failure-detection problem distinct from ordinary task performance.

## 9. What changes the reachable space?

### 9.1 Better selection versus new capability

A critical distinction:

```text
better selection within a fixed operation space
```

versus:

```text
changing the operation space itself
```

The second may be necessary for reusable capability growth.

### 9.2 New executable structure

> What is the smallest mechanism that allows a machine to produce an executable structure that was not already present in its candidate palette?

This is the next major frontier after fixed-palette credit assignment.

## 10. Continuity and identity

### 10.1 What makes the machine the same machine?

> If state, executable structure, and policies change over time, which invariants define continuity of one machine rather than replacement by another?

Candidate dimensions:

```text
process continuity
state lineage
provenance
persistent constraints
execution history
```

No one dimension is currently privileged.

### 10.2 Continuity as a causal variable

> Does preserving lineage and state across changes produce capabilities that cannot be reproduced by restarting from an equivalent summary?

This distinguishes genuine continuity effects from merely retained statistics.

## 11. The strongest questions

The project should repeatedly test whether the current conceptual partition is itself wrong.

> What important distinction in reality cannot currently be represented by the machine's state or operation language?

> What does the current architecture make impossible to ask?

> Which apparent mechanism is only an artifact of the current representation?

> What changes the hypothesis space rather than merely optimizing inside it?

> Can the machine discover that its criterion for deciding what matters is itself defective?

These questions are intentionally upstream of any proposed architecture.

## 12. Classification rule

Do not add any item here as a primitive merely because it has a useful name.

For each candidate phenomenon, require the chain:

```text
phenomenon
  -> functional distinction
  -> operational relation
  -> competing implementation
  -> discriminating experiment
  -> evidence status
```

The current purpose is to expand the space of questions while keeping the executable primitive set small and evidence-driven.
