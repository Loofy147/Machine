# Abstract Machine Model

Status: RESEARCH / OPEN

This document is the reference model for the current phase. It intentionally contains no programming language, class model, neural architecture, or human cognitive primitive.

## 1. What the machine is

For this phase, a machine is an evolving operational state together with a set of executable transformations and a mechanism that determines which transformation occurs next.

We do not assume that the machine contains objects corresponding to human thinking, attention, emotion, memory, or intelligence.

## 2. Minimal elements

### State

A machine has a state `S`.

State can include any machine-relevant condition, including persistent and transient components. The model does not prescribe a data structure.

### Operation

An operation `O` is an executable transformation available to the machine.

An operation may be implemented later as code, a program, a tool call, a hardware operation, a simulation, a transformation, or another executable mechanism.

### Transition

A transition applies an operation to a state and produces a result and a successor state:

```text
T(S, O, input) -> (S', result)
```

### Observation

The machine can derive an observation from the result and transition:

```text
observe(S, O, result, S') -> observation
```

The observation is not assumed to be a human-like perception. It is simply information that can participate in later transitions.

### Selection

A selection mechanism determines which available operation or operation set may execute next:

```text
select(S, available_operations, history) -> selection
```

This is not defined as human attention. It is only operational selection.

### Recomposition

The machine may alter the structure of its future operation sequence when its current operating path is insufficient:

```text
recompose(S, history, observations, operations) -> new_operation_structure
```

The new structure may change order, composition, branching, repetition, or representation.

## 3. Minimal cycle

A provisional cycle is:

```text
S
 -> represent/change-state as needed
 -> select O
 -> execute O
 -> observe consequence
 -> possibly recompose
 -> S'
```

`represent` remains a candidate operation rather than a mandatory architectural stage. The model must not hard-code a human-like pipeline merely to make it readable.

## 4. No semantic goal requirement

The abstract machine does not require a semantic task such as `solve X` before every transition.

A transition can arise from any explicit machine condition that the implementation exposes, for example:

- state change;
- environmental change;
- available executable work;
- failed execution;
- unexpected consequence;
- conflict or inconsistency;
- resource pressure;
- missing information;
- an experiment opportunity;
- a scheduled event.

This does **not** claim that useful autonomous behavior will emerge without a goal. That is an open experimental question.

## 5. Machine-native requirement

The model rejects the following inference:

```text
human function -> human mechanism -> machine component
```

The allowed direction is:

```text
observed requirement
 -> machine-operational function
 -> minimal executable mechanism
```

Human concepts may be used to describe observations after the fact, but may not become primitives merely because they are familiar human categories.

## 6. Implementation independence

The abstract model must be implementable by more than one substrate.

A substrate is acceptable only if it can represent the same transition semantics without changing their meaning.

Candidate future substrates may include:

- a small interpreter;
- a virtual machine;
- a graph executor;
- native code;
- a systems-language implementation;
- another executable substrate.

These are implementation candidates, not architectural commitments.

## 7. What this model deliberately does not answer

It does not yet specify:

- how operations are learned;
- how selection is learned;
- whether state is persistent indefinitely;
- whether a machine needs identity;
- whether useful behavior can emerge without explicit goals;
- whether recomposition is fundamental;
- whether an LLM is useful inside the machine;
- whether different state timescales are necessary;
- whether any resulting behavior should be called intelligence.

Those questions belong to experiments after the abstract semantics are stable.

## 8. First invariants

1. Implementation language must not define the machine model.
2. Human cognitive labels must not define primitives.
3. Every transition must be observable and replayable at the abstract level.
4. A successful output is not evidence that the internal transition regime is correct.
5. A changed operation regime must be distinguishable from a repeated fixed procedure.
6. The model must permit a machine to change how it operates, not merely what state it stores.
