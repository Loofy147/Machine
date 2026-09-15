# Operational Phenomena — Machine

Status: RESEARCH / OPEN

This document catalogs phenomena that humans may describe with words such as attention, curiosity, fear, motivation, surprise, confidence, identity, or emotion. Those labels are **descriptive handles**, not architectural primitives.

The purpose is to identify the machine-operational relations that could produce analogous observable effects and to determine which relations are independently necessary, redundant, or merely consequences of other mechanisms.

## 1. Core rule

```text
human label
    -> observable effect
    -> functional requirement
    -> candidate machine relation
    -> discriminating experiment
```

A label is not a mechanism.
A candidate relation is not established because it sounds plausible.
A successful behavior does not prove the particular internal relation that produced it.

## 2. Four layers that must stay separate

The earlier phenomenon list mixed different kinds of things. We now separate them.

### A. State variables / stored quantities

Something represented in machine state and potentially retained over time.

Examples:

- evidence count;
- prediction error;
- estimated consequence cost;
- uncertainty;
- resource level;
- lineage / continuity information;
- context signature;
- recent failure count.

### B. Relations / computations

A transformation or comparison over state and consequences.

Examples:

```text
prediction
comparison
credit assignment
valuation / significance estimation
context discrimination
persistence / decay
```

### C. Policies / control effects

A change in how executable transitions are scheduled, proposed, gated, or committed.

Examples:

```text
priority shift
avoidance
exploration allocation
candidate retention
commitment threshold
regime change
```

### D. Observable phenomena

A pattern visible at the behavior level that may result from combinations of A-C.

Examples:

```text
urgency
curiosity-like exploration
hesitation
confidence-like commitment
frustration-like regime change
identity / continuity behavior
```

This distinction is essential. For example, `urgency` is not automatically a state variable, and `prediction error` is not automatically a policy.

## 3. Phenomenon map after separation

| Human-facing label | Observable operational phenomenon | Candidate underlying relations | Status |
|---|---|---|---|
| attention | computation or transition allocation changes with conditions | scheduling, resource constraints, interruption, significance | OPEN |
| curiosity | allocation toward informative or unfamiliar transitions | uncertainty, novelty, information value, exploration policy | OPEN |
| fear / avoidance | transition probability falls when predicted consequence is costly or hard to reverse | consequence estimation, significance, reversibility, persistence, gating | OPEN |
| urgency | mitigation transitions gain priority as cost of delay rises | consequence cost, time-to-consequence, scheduling, persistence | OPEN |
| motivation | a policy bias persists across multiple transitions | retained state, consequence value, decay, scheduling | OPEN |
| preference | stable differential selection among alternatives under comparable conditions | estimated value, context, cost, history, policy state | PARTLY TESTED |
| surprise | observed consequence differs from predicted consequence | prediction, observation, comparison, state update | OPEN |
| frustration | repeated failure causes a regime or strategy change | failure history, threshold, persistence, reformation | OPEN |
| exploration | resources are allocated to uncertain/unfamiliar alternatives | uncertainty, novelty, budget allocation, candidate diversity | OPEN |
| avoidance | proposals correlated with costly outcomes are suppressed | consequence history, contextual credit, gating | PARTLY TESTED |
| confidence-like behavior | commitment becomes more or less decisive as evidence accumulates | evidence count, calibration, uncertainty, commitment threshold | OPEN |
| doubt-like behavior | competing candidates remain available when evidence is insufficient | uncertainty, candidate diversity, delayed commitment | OPEN |
| stagnation / boredom-like behavior | repeated transitions with low marginal consequence trigger redistribution or regime change | recurrence, marginal consequence, novelty, resource cost | OPEN |
| attachment / persistence | state or artifact remains preserved/reused because future utility remains nonzero | persistence value, reuse, dependency, decay | OPEN |
| identity / continuity | later operation remains constrained by lineage and persistent state | continuity, provenance, lineage, persistent state | OPEN |
| self-preservation | transitions that preserve a defined viability condition are favored | viability state, consequence cost, reversibility, resource state | OPEN |
| learning | future proposal or executable structure changes as a function of retained outcomes | history, credit assignment, proposal distribution, structural change | **SUPPORTED in limited forms** |
| reflection | executable machinery is represented and its representation is causally consulted after modification | reification, mutable evaluator state, causal consultation, continuity | OPEN |

The table describes **behavioral targets**, not proposed modules.

## 4. The first major reduction: many labels collapse onto a few relation families

The current working decomposition is smaller than the human vocabulary.

### 4.1 Consequence estimation

A transition has consequences that can be observed and, optionally, estimated before execution.

```text
T(S, O) -> (S', result)
predict(S, O, C) -> e
```

The estimate may be absent, approximate, or state-dependent.

### 4.2 Prediction error

Observed and expected consequences can be compared.

```text
error = compare(expected, observed)
```

This is a candidate relation for surprise-like behavior and one possible trigger for updating other state. It is not a synonym for learning.

### 4.3 Significance / valuation

Some consequence or state difference can alter the relative operational value of available transitions.

```text
value(O | S, C, H) -> v
```

A critical unresolved question is **where `v` comes from**. It must not be smuggled in as an unexplained human objective.

Possible sources include measured cost, resource pressure, predicted state change, externally specified task criteria, or learned consequence statistics. These sources must be separated experimentally.

### 4.4 Context discrimination

The same operation can have different consequences, costs, or utility under different conditions.

```text
value(O | C1) != value(O | C2)
```

The contextual-credit experiment supports this pattern when the context is explicitly supplied. Discovering `C` is still open.

### 4.5 Persistence and decay

A consequence remains influential for some interval and then may lose influence.

```text
influence_t+1 = decay(influence_t, conditions)
```

This is distinct from merely storing a history record. The research question is whether retention, activation, and decay have independent operational effects.

### 4.6 Scheduling / proposal control

The machine maps available operations plus current operational information into a next-step distribution or decision.

```text
policy(S, available, evidence, constraints) -> proposal / distribution
```

Many labels in the first table may reduce to **different causes of changes to this policy**, rather than separate faculties.

### 4.7 Regime change

The machine changes the structure or rule set used for future operation.

```text
current regime
    -> modification
    -> future regime
```

This is distinct from merely choosing another action once.

### 4.8 Continuity / lineage

A later state can be constrained by provenance and the history of the same ongoing process.

```text
state_t = f(previous_state, lineage, retained_artifacts)
```

This may produce identity-like behavior without requiring a primitive named identity.

## 5. What should be removed as separate mechanisms for now

The following should **not** become distinct primitives merely because they have familiar names:

```text
attention
curiosity
fear
motivation
confidence
        ↓
likely policy phenomena / combinations
```

Likewise:

```text
surprise
frustration
boredom
        ↓
likely consequence/history patterns
```

And:

```text
identity
attachment
self-preservation
        ↓
likely continuity/persistence/viability combinations
```

This is a hypothesis about compression, not a theorem. The burden is on experiments to show when a phenomenon cannot be reproduced by a smaller relation set.

## 6. A stricter machine-native factorization

A candidate high-level decomposition is:

```text
state
  + observable consequence
  + optional prediction
  + comparison
  + consequence significance
  + context
  + persistence / decay
  + constraints
  + scheduling / proposal policy
  + regime modification
```

Possible behavioral phenomena then become configurations of these relations.

For example, a high-pressure avoidance regime might be represented as:

```text
predicted consequence cost      ↑
time-to-consequence              ↓
reversibility                    ↓
retained significance            ↑
mitigation priority              ↑
exploration budget               ↓
```

No variable named `fear` is required.

But this factorization is still only a **HYPOTHESIS**. We do not yet know which terms are independent, which can be derived, or which are unnecessary.

## 7. Critical hidden-variable problem

The largest risk in this line of research is importing the missing variable through the benchmark.

For example:

```text
"fear" experiment
```

can secretly provide:

```text
cost_of_failure
importance_of_survival
preferred action
```

through the environment or reward function.

Therefore every phenomenon experiment must record separately:

```text
external condition
machine-observable state
measured consequence
candidate internal variable
policy effect
```

A label such as `fear`, `curiosity`, or `urgency` must never be the only source of its corresponding effect.

## 8. Relation to existing experiments

### Nine-mechanism ablation

Demonstrated that gating, branching, composition, evaluation, reformation, and accumulation can alter outcomes in a bounded search system. It did not establish the reduced relation set above.

### Executable representation experiments

Demonstrated that executable representation can be changed to alter future behavior. They did not establish consequence significance, prediction, or emotion-like phenomena.

### History ablation

Demonstrated that retained outcome history bound to operator identity can causally alter proposal policy over a fixed candidate palette.

### Contextual credit

Demonstrated testbed-specific context-conditioned credit when an explicit context label is supplied.

### Online hot-swap

Demonstrated same-process executable replacement. It did not establish causal reflection of the evaluator itself.

## 9. Near-term discriminating experiments

### P1 — Significance without a semantic emotion label

Use the same available operation set in two regimes where the measured consequences differ in cost or reversibility.

The machine receives only machine-observable conditions. Do **not** provide `fear`, `urgency`, or an equivalent label.

Compare:

```text
C0: no retained significance
C1: explicitly supplied consequence cost
C2: machine-estimated consequence cost
C3: shuffled/randomized significance
```

Measure downstream cost, recovery, policy shift, and stale-state effects.

The goal is to determine whether a compact operational significance variable provides predictive/control value beyond raw state and history.

### P2 — Prediction error

Use a deterministic transition family with controlled environment changes.

Compare:

```text
raw outcome history
vs
prediction error + history
```

Measure adaptation speed, false updates, and recovery after environment changes.

### P3 — Persistence / decay

Use recurring regimes with controlled switches.

Compare:

```text
no history
persistent history
fast-decay history
context-indexed history
```

Measure:

- adaptation benefit;
- stale-state cost;
- recovery time;
- cumulative regret;
- robustness after regime change.

### P4 — Context discovery

Remove explicit `REPEAT` / `UNIQUE` labels.

Derive context candidates only from machine-observable state/event history.

Compare:

```text
history erased
history global
history indexed by supplied context
history indexed by discovered context
```

### P5 — Exploration / novelty

Create environments where useful operations are initially unknown but discoverable.

Control total compute and candidate evaluations.

Compare targeted novelty/uncertainty allocation against matched random exploration and exploitation-only policies.

### P6 — Continuity / identity

Use identical post-switch tasks with and without preserved lineage and state.

Measure whether continuity changes adaptation beyond the information content of the retained statistics themselves.

### P7 — Causal reflection

Only after the above relations are sufficiently controlled, construct the minimal reflective substrate:

```text
Q = <R, S, K, rho, H>
```

and test whether modifying `rho` changes later transitions while the same continuation remains active.

## 10. Claim discipline

Current status of the reduced relation set:

### EXPERIMENTALLY_SUPPORTED

- executable representation can be modified;
- retained history can alter later proposal policy in a fixed candidate space;
- context-indexed credit can preserve useful operator credit when context is supplied;
- same-process executable replacement is feasible in the tested harness.

### HYPOTHESIS

- many human-facing phenomena compress into a small number of machine relations;
- significance/valuation is a useful independent relation;
- prediction error is useful as a distinct control signal;
- persistence/decay has a distinct operational role;
- continuity/lineage can produce identity-like behavior without a human identity primitive.

### OPEN

- context discovery;
- useful novelty-driven exploration;
- general consequence valuation without hidden objective injection;
- reusable executable structure;
- causal reflection;
- self-modification of the proposal mechanism.

## 11. Research rule

Do not add a module named `emotion`, `motivation`, `curiosity`, or `attention` because the label is convenient.

First ask:

```text
What changes?
What relation causes it?
What persists?
What is observable?
What is controlled?
What alternative mechanism explains the same result?
```

Only a relation that survives these comparisons should become a candidate architectural mechanism.
