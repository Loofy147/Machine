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

## Primitive candidate set

The initial candidate set is deliberately small.

### State

A persistent or transient machine condition that can affect later operations and can itself change.

Conceptual contract:

```text
State_t -> State_{t+1}
```

### Represent

Convert an input, observation, or state fragment into a representation that available operations can act upon.

```text
represent(input, state) -> representation
```

Representation is not required to be linguistic.

### Select

Choose one or more executable operations from the currently available operation set.

```text
select(state, operations, history) -> selection
```

`Select` is not defined as human attention. It is an operational allocation decision.

### Operate

Execute a concrete operation over a representation and state.

```text
operate(operation, representation, state) -> result
```

Operations may be functions, programs, tools, transformations, queries, simulations, comparisons, or other executable units.

### Observe

Extract operationally relevant consequences from execution.

```text
observe(state, operation, result) -> observation
```

The observation is an artifact for subsequent state transition, not a claim about inner experience.

### Recompose

Change the arrangement, choice, or representation of operations when the current operating path is insufficient.

```text
recompose(history, observation, operations) -> new_operation_graph
```

`Recompose` is a primary research target, not an implementation detail.

## Baseline operational loop

The smallest proposed loop is:

```text
State
  -> Represent
  -> Select
  -> Operate
  -> Observe
  -> Recompose
  -> State'
```

This is a hypothesis, not an assertion that these are the final primitives.

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

> Can a small machine, through operation, observation, and recomposition, acquire reusable behavior on tasks and conditions that were not explicitly encoded as fixed procedures?

If not, the hypothesis fails.

## Current unknowns

- Whether six primitives are sufficient.
- Whether `Observe` and `Recompose` should be split further.
- Whether state must have multiple timescales.
- Whether goalless operation can produce useful direction without hidden objectives.
- Whether recomposition produces generalization rather than merely search.
- Whether a coherent persistent identity is necessary for cumulative learning.
- Whether an LLM is useful as one operation among many rather than as the machine's cognitive core.
