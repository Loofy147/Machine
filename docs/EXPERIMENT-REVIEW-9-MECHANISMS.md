# Experimental Review: Nine Operational Mechanisms

Status: EXPERIMENTALLY_SUPPORTED / OPEN

This document records an external experimental result supplied to the project and converts it into constraints for the abstract machine model. It does **not** promote the tested mechanisms into architectural primitives.

## 1. Experimental system

The reported system used nine operational mechanisms:

1. representation
2. transformation
3. invocation gating
4. composition
5. variation
6. testing/evaluation
7. control
8. reformation
9. accumulation

The testbed was bounded integer search: reach a target from a start value within a fixed application budget. The operation set included base arithmetic operations and pairwise compositions.

This is a toy operational-search environment. It is evidence about the tested mechanisms under these conditions, not evidence of cognitive or general machine intelligence.

## 2. Reported system-level results

Across 240 instances per condition, with three 80-instance repeats for each condition:

| Condition | Solve rate | Mean steps solved | Crash rate |
|---|---:|---:|---:|
| full | 71.7% | 7.45 | 0% |
| no variation | 1.7% | 6.50 | 0% |
| no testing | 88.8% | 6.19 | 0% |
| no reformation | 65.0% | 7.43 | 0% |
| no composition | 58.3% | 8.81 | 0% |
| no accumulation | 71.7% | 7.42 | 0% |
| no invocation gating | 25.8% | 4.71 | 72.9% |

Unit-level tests reported 12/12 passing for the corresponding mechanisms.

## 3. Interpretation by mechanism

### 3.1 Variation

**Status: EXPERIMENTALLY_SUPPORTED, TESTBED-SPECIFIC**

Removing variation caused near-total collapse. The mechanism was load-bearing in the tested system.

However, the no-variation condition used a deterministic alphabetical fallback. `add1` therefore became the selected operation whenever it was applicable, producing repeated `add1` paths even when the target was below the current value.

Therefore the causal conclusion is narrower than "variation is fundamental":

> Branch-and-compare materially improved search under the tested selection regime.

A fairer next ablation must replace the pathological alphabetical fallback with a competent single-path selector under equal information and compute budgets.

### 3.2 Invocation gating

**Status: EXPERIMENTALLY_SUPPORTED, CAUSALLY_CONFOUNDED**

Removing invocation gates caused 72.9% crashes because `sqrt_floor` could be applied to invalid negative values. Among the non-crashing runs, the unrestricted powerful operation solved 95.4%.

This combines at least three distinct functions:

- domain validity;
- resource/call budget;
- capability availability.

The result establishes that unconditional operation access can materially change system behavior and safety, but does not isolate which form of gating is essential.

Next experiment: split these gate types and ablate them independently.

### 3.3 Composition

**Status: EXPERIMENTALLY_SUPPORTED, MODERATE**

Removing composition reduced solve rate from 71.7% to 58.3% and increased mean solved steps from 7.45 to 8.81. The effect was directionally consistent across repeats.

The unresolved question is whether composition is conceptually important or simply provides a search/computation shortcut. A composed operation can represent a sequence that otherwise consumes multiple budgeted steps.

Next experiment: compare composed operations against equivalent decomposed sequences under matched search and execution budgets.

### 3.4 Reformation

**Status: EXPERIMENTALLY_SUPPORTED / SUGGESTIVE**

Removing reformation reduced solve rate to 65.0%. The effect is smaller than variation or invocation gating and overlaps the spread of full-system repeats.

Reformation is nevertheless structurally distinct from ordinary operation execution because it changes the available operating regime: operation set and/or scoring weights.

Do not collapse it with ordinary adaptation until operation-set expansion and scoring-rule change are tested separately.

### 3.5 Testing / evaluation

**Status: EXPERIMENTALLY_SUPPORTED AS A NEGATIVE RESULT**

The no-testing system outperformed the full system: 88.8% vs 71.7%.

This does not establish that testing is harmful. The testbed has a strong immediate heuristic (`abs(target-value)`), while the implemented rollout used only a small noisy sample. The result is therefore consistent with:

> A low-quality evaluation mechanism can degrade a system whose existing heuristic is already more predictive.

Testing should be re-evaluated in environments with deceptive or long-horizon consequences, and against matched evaluation budgets.

### 3.6 Accumulation

**Status: EXPERIMENTALLY_SUPPORTED AS A DESIGN WARNING**

The default accumulation mechanism had no measurable effect because its memory bonus was too small to change argmax decisions.

Increasing the memory weight produced a monotonic performance decline: approximately 71.7% -> 69.2% -> 60.0% -> 42.9% at increasing weights.

This strongly exposes a limitation of one scalar score per operation name: experience is context-blind. An operation that succeeded in one state can be promoted in another state where it is inappropriate.

Candidate correction:

```text
experience ~= (operation, context/state conditions, transition, consequence)
```

rather than:

```text
experience ~= score(operation)
```

This is a design hypothesis, not yet established.

### 3.7 Representation

**Status: STRUCTURAL SCAFFOLD IN THIS IMPLEMENTATION, NOT PROVEN PRIMITIVE**

The reported representation mechanism compresses several derived relations into a reusable hashable object. It was not cleanly ablated.

The important question is not whether some representation is required in this implementation; executable state must be encoded somehow. The research question is whether the particular relation-bundling mechanism contributes causal capability beyond an equivalent information-preserving encoding.

Future ablation should compare raw and structured representations under matched information, memory, and compute constraints.

### 3.8 Transformation

**Status: STRUCTURAL SCAFFOLD**

A system that executes an operational transition requires some transformation semantics. Removing the transformation mechanism therefore risks removing the notion of executable change itself rather than testing a specific architectural choice.

The right question is which transformation semantics are minimally sufficient, not whether transformation can be deleted from a runnable machine.

### 3.9 Control

**Status: STRUCTURAL SCAFFOLD, NOT PROVEN AS HUMAN-LIKE "SELECTION"**

Some mechanism must determine what executes next whenever more than one operation is available. The experiment therefore does not justify treating control as a special cognitive faculty.

The machine-native question is whether control can be reduced to transition scheduling over available executable structures, and what information that scheduler minimally needs.

## 4. Architectural consequence

The nine mechanisms should **not** become nine flat primitives in the abstract model.

The evidence instead suggests a layered decomposition:

```text
Structural execution
  State
  Operation / Transformation
  Transition
  Control / scheduling

Operation-space modulation
  Invocation constraints
  Variation / branching
  Composition

Regime adaptation
  Evaluation / testing
  Reformation
  Experience / accumulation
```

This decomposition is provisional. It is a classification of experimental roles, not a final architecture.

## 5. New candidate mechanism: contextual experience

The accumulation failure exposes a candidate mechanism that is not explicit in the current abstract model: experience may have to be indexed by conditions under which an operation produced a consequence.

Candidate abstract form:

```text
record_experience(
    operation,
    state_or_context,
    transition,
    consequence
)
```

Later control could query the record conditionally rather than reading a single global operation score.

This should remain **HYPOTHESIS** until tested against operation-only accumulation.

## 6. Required discriminating experiments

### E1 — Fair variation ablation

Compare:

- branching candidate set + selector;
- single-path selector with a competent deterministic or learned policy;
- equal operation evaluations and equal compute budget.

Goal: determine whether branching itself matters, rather than the current experiment only exposing a bad fallback selector.

### E2 — Gate decomposition

Separate:

- domain-validity constraints;
- resource/call-budget constraints;
- capability-availability constraints.

Ablate each independently.

### E3 — Evaluation quality

Compare:

- static heuristic;
- exact one-step evaluation;
- limited noisy rollout;
- deeper rollout;

under matched compute budgets and in an environment where local progress is not a reliable proxy for final success.

### E4 — Contextual experience

Compare:

- operation-only accumulation;
- operation + coarse state context;
- operation + transition/consequence context.

Measure transfer to states that differ from the states that produced the experience.

### E5 — Reformation decomposition

Separate:

- adding/changing operations;
- changing evaluation/scoring rules.

This determines whether reformation is one mechanism or a bundle of distinct regime modifications.

### E6 — Composition fairness

Compare a composed operation with its equivalent decomposed sequence under matched total computation and action budget.

### E7 — Representation equivalence

Compare different encodings that preserve the same relevant information. Treat improved performance as evidence only when the information and computational advantages of the encoding are controlled.

## 7. Current claim frontier

**EXPERIMENTALLY_SUPPORTED**

- The tested mechanisms are mechanically distinguishable in the toy system.
- Candidate branching materially affected search under the reported selector.
- Operation gating materially affected correctness and stability under the reported constraints.
- Composition and reformation produced measurable performance differences.
- Naive evaluation can reduce performance when its signal is noisy relative to a strong task heuristic.
- Context-free accumulation can distort control when given sufficient weight.

**INFERENCE**

- The nine mechanisms probably do not form one flat layer of equivalent primitives.
- Experience likely needs context if it is expected to transfer correctly across states.

**HYPOTHESIS**

- Regime-changing mechanisms may be more fundamental to adaptive machines than human-labeled "cognitive" components.
- Recomposition/reformation may be required for open-ended capability growth rather than merely task solving.

**UNKNOWN / OPEN**

- Whether any of these mechanisms generalize outside bounded search.
- Whether useful operation can arise without explicit semantic goals.
- Whether a smaller machine-native set exists underneath this decomposition.
- Whether an LLM is useful as one operation/control mechanism without being treated as the machine itself.

## 8. Research rule

Do not add a mechanism to the abstract machine model merely because an ablation changed performance.

An ablation establishes causal relevance inside an experimental regime. It does not by itself establish architectural primitivity, universality, or human-like functional equivalence.
