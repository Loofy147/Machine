# Reflection Frontier

Status: RESEARCH / OPEN

This document records a narrower architectural question that emerged after the executable-representation experiments.

## 1. Scope

The project is no longer asking only whether a machine can modify executable state. It now distinguishes:

```text
program/value mutation
    -> executable structure mutation
    -> modification of the modification mechanism
    -> online causal reflection
```

The target of interest is the last transition: a running system modifies a representation or mechanism that participates causally in the execution that continues after the modification.

This is a research target, not an established requirement for intelligence.

## 2. Important correction: homoiconicity is sufficient, not necessary

A unified code/data representation plus `eval` is a convenient minimal construction for self-reference in Lisp-like systems, but it is not a theorem-level prerequisite for computational self-reference.

Kleene's recursion theorem applies to acceptable programming systems more generally. A system can obtain fixed points without being homoiconic and without exposing a primitive named `eval`.

Therefore:

```text
homoiconicity + eval
```

is one simple construction of self-reference, not the universal minimum.

The stronger invariant is:

> the system must have some effective representation/encoding through which a computation can denote, transform, or otherwise obtain a description of a computation that can affect subsequent execution.

## 3. Offline versus online modification

The project distinguishes:

### Offline structural modification

A system produces a new program/artifact, terminates or checkpoints, and a later execution starts from the new artifact.

Examples include program synthesis, library learning, evolutionary algorithm search, and many recursive self-improvement systems.

### Online causal reflection

A running execution reifies or accesses a representation of execution state, control, program structure, interpreter behavior, or meta-level policy; a modification is made; and the modified representation participates in the continuation of the same execution without requiring a fresh external generation step.

The causal criterion is stronger than introspection:

```text
reified state
    -> modify
    -> modified state participates in subsequent execution
    -> observable behavior changes
```

A side-channel description of the running system does not satisfy this criterion.

## 4. Reflective towers are a model, not necessarily the minimum implementation

3-Lisp provides a canonical reflective-tower model in which interpreters are themselves expressed in the reflective language. Smith's work explicitly uses the tower construction.

Wand and Friedman showed that useful semantics of the reflective tower can be given without literally requiring an infinite concrete tower of interpreters.

Therefore this research should not hard-code:

```text
online reflection == infinite interpreter tower
```

The engineering question is instead:

> what is the smallest operational mechanism that gives causal access to, and modification of, the execution machinery while preserving a well-defined continuation?

## 5. Reflection and causal connection

Following the reflection literature, the important property is not merely self-description but causal relevance.

A candidate reflective mechanism must make it possible to distinguish:

```text
inspect-only representation
```

from:

```text
causally connected representation
```

The latter changes subsequent execution when modified.

This becomes an experimental invariant for Machine.

## 6. Relation to CLOS-style reflection

Metaobject protocols provide a practical example of customizable meta-level behavior whose effects are causally connected to ordinary object operations. They are evidence that meta-level execution policy can be exposed as programmable structure.

They should not be treated as proof that an arbitrary evaluator can rewrite itself online. A MOP and a self-modifying universal evaluator are different capabilities.

## 7. Research ladder

Current working ladder:

```text
L0  fixed execution
L1  parameter mutation
L2  executable-structure mutation
L3  reusable learned executable structures
L4  offline/meta-level self-modification
L5  online causal reflection
L6  online modification of the mechanism that modifies execution
```

The project has experimental evidence around L1-L2, literature baselines around L3-L4, and has not yet implemented or falsified L5-L6.

## 8. What must not be assumed

This document does not assume:

- that reflection is required for intelligence;
- that self-reference requires homoiconicity;
- that an infinite tower is physically necessary;
- that online self-modification is preferable to offline self-modification;
- that causal reflection produces useful adaptation without an external evaluation condition;
- that reflective systems solve the limits of self-justification identified in formal logic.

## 9. Minimal experiment candidate

A useful next experiment is a tiny interpreter with an explicitly reifiable execution state:

```text
E(R, S, K) -> continuation
```

where `R` is executable representation, `S` is operational state, and `K` is the continuation/control state.

A reflective operation may produce:

```text
reify(R, S, K) -> description
modify(description) -> description'
install(description') -> updated execution context
```

The decisive test is not whether `description'` exists. It is whether the *same ongoing run* continues with an execution rule measurably changed by `description'`.

A fixed baseline must execute the same task without reflective modification under the same resource budget.

## 10. Current question

> What is the smallest fixed substrate that permits a running machine to modify the executable mechanism that determines its own subsequent transitions, with causal continuity and observable replay?

This question is narrower than machine intelligence and should be answered before adding learning or higher-order self-improvement mechanisms.
