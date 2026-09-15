# Abstract Machine Model

Status: RESEARCH / OPEN

This document is the reference model for the current phase. It intentionally contains no programming language, class model, neural architecture, or human cognitive primitive.

## 1. What the machine is

For this phase, a machine is an evolving operational state together with executable transformations and a mechanism by which executable transitions are determined and applied.

We do not assume that the machine contains objects corresponding to human thinking, attention, emotion, memory, or intelligence.

## 2. Structural elements

The current model distinguishes structural execution semantics from optional mechanisms that alter the operation space or operating regime.

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

A valid machine model must make this semantic change observable and replayable at the abstract level.

### Control / scheduling

When more than one executable transition is available, some mechanism must determine which transition or set of transitions can proceed next.

```text
schedule(S, available_operations, context) -> executable_transition
```

This replaces the stronger earlier claim that a primitive named `Select` is necessarily fundamental. The current interpretation is deliberately mechanical: scheduling is a property of executable transition flow, not human attention.

## 3. Optional operation-space mechanisms

The machine may alter or constrain its executable operation space.

### Invocation constraints

An operation may be conditionally executable because of domain validity, resource limits, capability availability, or other explicit constraints.

```text
enable(S, O, constraints) -> allowed | blocked
```

The nine-mechanism experiment showed that unconditional operation access can materially alter both failure rate and performance, but did not isolate all gate types.

### Variation / branching

The machine may produce multiple candidate operation paths rather than immediately committing to one.

```text
vary(S, operations, context) -> candidate_structures
```

Current evidence supports this as useful in the tested search system, but a fair single-path selector has not yet been compared.

### Composition

The machine may construct a new operation from existing executable operations.

```text
compose(O1, O2, ...) -> O'
```

Composition is currently a candidate operation-space mechanism, not a proven primitive.

## 4. Consequence and observation

A machine can derive operational information from the consequence of a transition:

```text
observe(S, O, result, S') -> observation
```

The observation is not assumed to be human-like perception. It is information that can affect later state transition or operation structure.

Observation is therefore treated as an information-producing relation over transitions, not necessarily as a dedicated cognitive component.

## 5. Regime adaptation

A machine may modify how future operations are generated, evaluated, constrained, or scheduled.

A generic abstract form is:

```text
adapt(state, history, observations, operations) -> state' and/or new_operation_structure
```

Candidate mechanisms include evaluation/testing, reformation of the available operation regime, and accumulation of experience. They are not yet reduced to a single primitive.

A useful distinction is:

```text
execute an operation
    !=
change the regime that determines future operations
```

Whether regime modification is necessary for general reusable behavior is an open experimental question.

## 6. Current machine cycle

The model is intentionally weaker than the earlier six-stage loop:

```text
S
 -> determine an executable transition
 -> execute
 -> obtain consequence
 -> update state and/or operation structure
 -> S'
```

Representation, branching, composition, testing, and experience may participate when required, but none is assumed to occur on every cycle.

`represent` therefore remains a candidate executable transformation rather than a mandatory architectural stage.

## 7. No semantic goal requirement

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

This does **not** claim that useful autonomous behavior will emerge without a goal. That remains an open experiment, and hidden objectives must be controlled for.

## 8. Machine-native requirement

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

## 9. Implementation independence

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

## 10. What this model deliberately does not answer

It does not yet specify:

- the minimal structural representation of state;
- the minimal scheduling rule;
- how operations are learned;
- whether operation-space modulation needs branching, composition, or constraints;
- whether experience must be context-sensitive;
- whether regime adaptation is fundamental;
- whether state is persistent indefinitely;
- whether a machine needs identity;
- whether useful behavior can emerge without explicit goals;
- whether recomposition is a single mechanism or a family of mechanisms;
- whether an LLM is useful inside the machine;
- whether different state timescales are necessary;
- whether any resulting behavior should be called intelligence.

Those questions belong to experiments after the abstract semantics are sufficiently stable.

## 11. First invariants

1. Implementation language must not define the machine model.
2. Human cognitive labels must not define primitives.
3. Every transition must be observable and replayable at the abstract level.
4. A successful output is not evidence that the internal transition regime is correct.
5. A changed operation regime must be distinguishable from a repeated fixed procedure.
6. The model must permit a machine to change how it operates, not merely what state it stores.
7. Ablation relevance does not by itself prove architectural primitivity or universality.
