# Operational Phenomena — Machine

Status: RESEARCH / OPEN

This document separates **phenomena described with human vocabulary** from the machine-operational relations that may produce analogous effects.

It does not claim that a machine must implement human emotions, motives, or cognitive faculties. The purpose is to identify phenomena that may be useful to implement, measure, or explain, even when the eventual implementation is entirely machine-native.

## 1. Core rule

```text
human label
    -> observed operational effect
    -> candidate machine relations
    -> discriminating experiment
```

A label is not a primitive.

A phenomenon is not established merely because a candidate mechanism can be named for it.

## 2. Candidate phenomenon map

| Human-facing label | Machine-operational phenomenon | Candidate relations | Current status |
|---|---|---|---|
| attention | allocation of computation or transition opportunities | resource budget, scheduling, context sensitivity, interruption | OPEN |
| curiosity | preference for informative or novel transitions | uncertainty, information gain, novelty, experiment value | OPEN |
| fear / avoidance | strong policy shift away from costly or irreversible consequences | consequence estimate, risk, reversibility, urgency, persistence | OPEN |
| urgency | increasing priority of transitions as cost of delay rises | time pressure, resource decay, predicted loss, scheduling | OPEN |
| motivation | persistent bias toward some transition classes | history, state variables, consequence value, persistence/decay | OPEN |
| preference | stable differential selection among otherwise available operations | history, context, cost, consequence, policy state | PARTLY TESTED |
| surprise | mismatch between predicted and observed consequence | prediction, observation, prediction error, state update | OPEN |
| frustration | repeated failure increasing pressure to alter the operating regime | failure history, threshold, reformation trigger | OPEN |
| exploration | deliberate allocation toward unfamiliar or uncertain transitions | uncertainty, novelty, diversity, resource allocation | OPEN |
| avoidance | suppression of transitions associated with costly outcomes | consequence history, context-conditioned credit, gating | PARTLY TESTED |
| confidence | state-dependent estimate of reliability of a transition or representation | calibration, outcome variance, evidence count | OPEN |
| doubt | retention of competing candidate transitions under insufficient evidence | uncertainty, candidate diversity, delayed commitment | OPEN |
| boredom / stagnation | declining utility of repeated transitions without useful state change | recurrence, marginal consequence, novelty, resource cost | OPEN |
| attachment / persistence | continued preservation or reuse of a state/artifact because future utility remains high | persistence value, reuse frequency, dependency, decay | OPEN |
| identity | stable continuity constraints over state, history, and executable structure | lineage, persistent state, continuity, provenance | OPEN |
| self-preservation | preference for transitions that preserve operational viability | failure cost, resource state, reversibility, survival constraint | OPEN |
| learning | history-dependent change in future operation policy or structure | outcome history, credit assignment, proposal distribution | EXPERIMENTALLY_SUPPORTED in limited forms |
| reflection | causal access to and modification of execution machinery | reification, mutable evaluator state, causal consultation | OPEN |

The terms in the first column are descriptive handles, not architectural requirements.

## 3. Important relation classes

The current research suggests that many apparently different phenomena may be constructed from a smaller set of relations.

### State relation

A machine state differs from a previous state in ways that can affect later transition selection.

```text
S_t != S_{t-1}
```

### Consequence relation

A transition produces an observable result or successor state whose properties can influence later operation.

```text
T(S, O) -> (S', result)
```

### Predictive relation

The machine can compare expected and observed consequences.

```text
predict(S, O) -> e
observe(S, O) -> r
compare(e, r) -> delta
```

This is a candidate basis for phenomena described as surprise, error, or uncertainty. It is not yet implemented in the current project.

### Significance relation

A state/consequence difference changes the relative operational value or urgency of available transitions.

```text
significance(S, consequence, conditions) -> weight
```

This is deliberately abstract. It is a candidate relation for phenomena such as urgency, avoidance, preference, or motivation.

### Persistence relation

An effect survives beyond the event that produced it and changes later transitions.

```text
persistence(event, future_utility, context) -> retained_state
```

The project currently tests limited history persistence but does not yet have a general persistence/decay model.

### Context relation

The same operation has different consequences or utility under different operational conditions.

```text
value(O | C_1) != value(O | C_2)
```

The contextual-credit experiment provides evidence for this pattern when the context label is supplied.

### Regime-change relation

The machine modifies the conditions or structures that determine future operation.

```text
operation
    -> regime modification
    -> different future operation distribution
```

This is broader than changing a parameter in a single operation.

### Continuity relation

A modification remains part of the same ongoing computational process rather than producing a separate fresh execution.

This becomes important when distinguishing online modification from offline iteration.

## 4. A useful factorization

A working hypothesis is that many human-described phenomena could be decomposed into combinations such as:

```text
phenomenon
≈
state difference
+ consequence estimate
+ context
+ significance
+ persistence/decay
+ scheduling change
```

For example, a machine-native analogue of a high-urgency state might involve:

```text
predicted consequence cost ↑
time-to-consequence ↓
reversibility ↓
policy weight for mitigation ↑
```

No variable named `fear` is required.

This factorization is a hypothesis and must not be promoted into the abstract machine model without discriminating experiments.

## 5. Relation to current experiments

### Nine-mechanism ablation

Provided evidence that gating, branching, composition, reformation, evaluation, and accumulation can alter outcomes in a bounded search environment. It did not identify a complete set of primitive relations.

### Executable representation experiments

Established that changing executable representation can change future behavior. It did not establish a general mechanism for learning or significance assignment.

### History ablation

Established that outcome history bound to operator identity can causally affect later proposal policy over a fixed candidate palette.

### Contextual credit

Established testbed-specific evidence that `(context, operator)` history preserves useful credit when the context is supplied and recurs.

### Online hot-swap

Established same-process replacement of an executable operation. It did not establish causal reflection of evaluator semantics.

## 6. Near-term experiments

The following should be tested before adding these phenomena as named mechanisms.

### P1 — Operational significance

Construct an environment where the same available operation set is exposed under conditions with different consequence costs or reversibility.

Test whether a compact machine state variable can alter scheduling in a way that improves downstream cost without receiving a human label such as `fear` or `urgency`.

Controls:

- no significance state;
- explicit significance label;
- machine-derived significance variable;
- random/shuffled significance.

### P2 — Prediction error

Provide a deterministic transition model and introduce controlled changes in the environment.

Measure whether prediction/observation mismatch can alter future operation choice more efficiently than raw history alone.

### P3 — Persistence and decay

Compare persistent, rapidly decaying, and context-indexed records under recurring and changing regimes.

Measure adaptation benefit, stale-state cost, and recovery after regime change.

### P4 — Novelty / exploration

Create environments where useful transitions are initially unknown but discoverable.

Measure whether novelty or uncertainty can improve discovery without merely increasing random exploration.

### P5 — Identity / continuity

Compare adaptation with and without preserved lineage/state across evaluator changes and regime switches.

Measure whether continuity provides a measurable operational advantage beyond simple retained statistics.

## 7. Research boundary

Do not implement a module called `emotion`, `motivation`, `curiosity`, or `attention` merely because the corresponding human concept is useful for discussion.

Instead identify the required machine relation and test it directly.

The desired sequence is:

```text
phenomenon
  -> functional decomposition
  -> machine-native relation
  -> controlled experiment
  -> evidence
  -> mechanism status
```

## 8. Current frontier

### EXPERIMENTALLY_SUPPORTED

- executable mutation can alter future behavior;
- history can causally alter proposal policy in a fixed candidate space;
- context-indexed credit can preserve useful operator credit when context is supplied;
- same-process hot-swap can preserve operation continuity.

### OPEN

- operational significance as a general relation;
- prediction-error-driven adaptation;
- persistence/decay as an independently useful mechanism;
- discovered context representations;
- novelty-driven exploration;
- machine-native identity/continuity effects;
- causal reflective execution;
- whether combinations of these relations produce reusable operational structure.

The purpose of this frontier is to expand the research space without prematurely expanding the architectural primitive set.
