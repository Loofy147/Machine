# Machine — Foundation

Status: RESEARCH / OPEN HYPOTHESES

## Core question

> What is the smallest composable set of machine-native operations that can produce behavior we would describe as intelligent, without directly encoding human cognitive primitives?

## Non-goals

This repository does not begin by implementing human-like thinking, emotion, attention, personality, memory, planning, or general intelligence as first-class concepts.

Those may emerge later as compositions, but none is accepted as a primitive merely because humans use the corresponding concept.

## Working principles

1. Machines should be machines, not human clones.
2. Abstract the function we need, not the human mechanism that appears to perform it.
3. Knowledge is not the same as the ability to use knowledge during operation.
4. Operation should not require a semantic task or explicit goal in every cycle.
5. A state transition may be driven by change, consequence, availability, conflict, uncertainty, or other operational conditions without requiring a human-style goal.
6. The machine should be able to change how it operates, not only what it stores.
7. A failed or surprising operation is evidence about the current operating regime, not merely a request to repeat the same computation.
8. Persistent state should preserve future utility and meaning, not merely bytes.
9. Remembering does not imply activation; activation does not imply influence.
10. Generality is an open hypothesis: it may belong to the machine's ability to acquire and compose capabilities rather than to possession of one universal intelligence.
11. Experimental relevance does not imply architectural primitivity. An ablation can show that a mechanism matters within a regime without proving that the mechanism is fundamental or universal.
12. Mechanisms should be separated by causal role before being named primitives: execution structure, operation-space modulation, and regime adaptation are currently distinct research layers.

## Current architectural classification

The latest nine-mechanism experiment suggests that a flat primitive list is misleading. The current classification is provisional:

### Structural execution

These define what it means for an executable machine to change state.

- State
- Operation / Transformation
- Transition
- Control / scheduling

The presence of these elements is partly definitional: removing them may remove the runnable system rather than cleanly ablate a capability.

### Operation-space modulation

These alter which executable paths are available or how they are formed.

- Invocation constraints
- Variation / branching
- Composition

Their causal value can be tested without removing execution semantics entirely.

### Regime adaptation

These alter how the machine evaluates or modifies future operation.

- Evaluation / testing
- Reformation
- Experience / accumulation

These are candidates for mechanisms that change the operating regime rather than simply execute an operation.

## Experience hypothesis

A recent accumulation ablation exposed a limitation of context-free experience. A single score attached to an operation name can promote an operation because it worked elsewhere, even when it is unsuitable in the current state.

Candidate representation:

```text
experience ~= (operation, context/state conditions, transition, consequence)
```

rather than:

```text
experience ~= score(operation)
```

Status: HYPOTHESIS. This must be experimentally compared against operation-only accumulation before entering the abstract model.

## Reconsidering the baseline candidate set

The previous six-element candidate set (`State`, `Represent`, `Select`, `Operate`, `Observe`, `Recompose`) remains useful as a provisional vocabulary, but it should no longer be treated as six equivalent primitives.

In particular:

- `Represent` may be an operation or state transformation rather than a mandatory stage.
- `Select` may be better understood as transition scheduling/control.
- `Operate` may be the general execution semantics behind all executable operations.
- `Observe` may be one class of state/result transformation rather than a human-like perceptual faculty.
- `Recompose` may be a family of regime-changing mechanisms, including composition, variation, and reformation.

The next experiments must determine whether these distinctions are merely vocabulary or correspond to irreducible causal mechanisms.

## Baseline operational loop

The current abstract loop therefore remains deliberately weak:

```text
State
  -> determine executable transition
  -> execute operation
  -> obtain consequence
  -> update state and/or operation structure
  -> State'
```

Representation, branching, composition, evaluation, and experience may participate in this loop, but none is assumed to execute on every cycle.

## Goalless operation

The system must be able to remain operational without receiving a semantic task such as "solve X".

This does not imply arbitrary randomness. A transition can be driven by operational conditions such as:

- state change,
- environmental change,
- failed execution,
- unexpected consequence,
- missing information,
- resource pressure,
- available experiment,
- inconsistency,
- or another machine-native transition condition.

The distinction is:

```text
semantic goal != required condition for state transition
```

## Intelligence criterion

Do not define success as the presence of a component named `intelligence`.

Initial operational criterion:

> Can a small machine, through executable transitions and changes to its operating regime, acquire reusable behavior on tasks and conditions that were not explicitly encoded as fixed procedures?

If not, the hypothesis fails.

## Current unknowns

- Whether the structural execution layer can be reduced further.
- Whether operation-space modulation requires all of invocation constraints, variation, and composition.
- Whether evaluation/testing can be useful when its signal is reliable and downstream-sensitive.
- Whether contextual experience outperforms operation-only accumulation.
- Whether reformation decomposes into independent regime-changing mechanisms.
- Whether state must have multiple timescales.
- Whether goalless operation can produce useful direction without hidden objectives.
- Whether regime modification produces generalization rather than merely search.
- Whether a coherent persistent identity is necessary for cumulative learning.
- Whether an LLM is useful as one operation among many rather than as the machine's cognitive core.
