# Reflection Frontier

Status: RESEARCH / OPEN

This document records the narrower architectural question that emerged after the executable-representation and online hot-swap experiments.

## 1. Scope

The project distinguishes:

```text
parameter mutation
    -> executable-structure mutation
    -> reusable executable structure
    -> offline/meta-level modification
    -> online causal reflection
```

The target of interest is the last transition: a running system modifies a representation or mechanism that participates causally in the execution that continues after the modification.

This is a research target, not an established requirement for intelligence.

## 2. Important correction: homoiconicity is sufficient, not necessary

A unified code/data representation plus `eval` is a convenient construction for self-reference in Lisp-like systems, but it is not a theorem-level prerequisite for computational self-reference.

Kleene's recursion theorem applies to acceptable programming systems more generally. A system can obtain fixed points without being homoiconic and without exposing a primitive named `eval`.

The stronger invariant is:

> the system has some effective representation/encoding through which computation can obtain or transform a description that can affect subsequent execution.

## 3. Offline versus online modification

### Offline structural modification

A system produces a new program/artifact and a later execution starts from that artifact or checkpoint.

### Online causal reflection

A running execution reifies or accesses execution state, control, program structure, interpreter behavior, or meta-level policy; modifies it; and then continues using the modified representation without requiring an external restart.

The causal criterion is:

```text
reified or exposed execution machinery
    -> modify
    -> modified representation participates in later transitions
    -> observable behavior changes
```

A side-channel description that is never consulted by future execution does not satisfy this criterion.

## 4. Reflective towers are a model, not necessarily the minimum implementation

3-Lisp provides a canonical reflective-tower model in which interpreters are themselves expressed in the reflective language. Semantics for reflective towers can also be given without requiring a literal infinite concrete tower.

Therefore:

```text
online reflection != infinite interpreter tower
```

The engineering question is the smallest operational mechanism that gives causal access to execution machinery while preserving a well-defined continuation.

## 5. Reflection and causal connection

The important property is not self-description alone but causal relevance.

The experiment must distinguish:

```text
inspect-only representation
```

from:

```text
causally connected representation
```

The latter changes a later transition under a minimal-pair test.

## 6. Relation to practical reflective systems

Metaobject protocols provide a concrete example in which meta-level execution policy is exposed as programmable structure and can affect ordinary execution.

They are useful precedent, not proof that an arbitrary evaluator can rewrite itself online.

## 7. Working capability frontier

The project should not treat reflection as an infinite ladder of increasingly remote meta-evaluators. Once the evaluator/transition mechanism is itself represented in the machine state, the same reify/modify/install semantics can in principle be applied again through the fixed substrate.

Therefore the main research axes after causal reflection are better expressed as independent dimensions:

```text
Dimension A — executable depth
  parameter -> structure -> reusable structure -> evaluator/transition mechanism

Dimension B — temporal continuity
  offline -> checkpointed -> same-process online

Dimension C — adaptation
  fixed proposal -> search -> history-dependent proposal -> contextual proposal

Dimension D — structural discovery
  fixed candidate palette -> recomposition -> reusable learned structures

Dimension E — meta-modification
  fixed proposer -> modified proposer/modifier
```

Current evidence:

- parameter/executable mutation: experimentally supported;
- reusable learned executable structures: literature baseline, not built here;
- online hot-swap: experimentally supported;
- history-dependent and explicit-context credit: experimentally supported;
- causal evaluator reflection: not yet demonstrated;
- context discovery: not yet demonstrated;
- modification of the proposer/modifier: not yet demonstrated.

## 8. What must not be assumed

This document does not assume:

- reflection is required for intelligence;
- self-reference requires homoiconicity;
- an infinite tower is physically necessary;
- online self-modification is preferable to offline modification;
- causal reflection automatically produces useful adaptation;
- formal self-reference results directly determine the engineering architecture.

## 9. Minimal experiment candidate

Use a tiny interpreter with an explicitly reifiable execution state:

```text
E(R, S, K) -> continuation
```

with an experimental reflective state:

```text
Q = <R, S, K, rho>
```

A candidate reflective operation may expose:

```text
reify(Q) -> description
modify(description) -> description'
install(description') -> Q'
```

`modify` need not be a primitive; it may be ordinary computation over reified data.

The decisive test is whether the same ongoing run continues with an execution rule measurably changed by `description'`.

## 10. Current question

> What is the smallest fixed substrate that permits a running machine to modify the executable mechanism that determines its own subsequent transitions, with causal continuity and observable replay?

This question is narrower than machine intelligence and should be answered before claiming higher-order self-improvement.


## 11. Current narrow substrate candidate

The first candidate reflective interpreter proposes a narrower target than whole-evaluator reflection:

```
rho_dispatch = compound-procedure dispatch semantics
```

The candidate uses an object-language `*applier*` closure as the dispatch rule for compound procedures.

The current research decision is to test this seam first rather than immediately reify the entire evaluator.

The required causal chain is:

```
reify dispatch-relevant state
  -> object-language modification
  -> install
  -> later compound call
  -> modified dispatch rule is actually consulted
  -> observable difference
```

The following are explicit controls rather than implementation details:

- ordinary `set!` rebinding;
- restart/external hot-swap;
- extra computation or budget;
- unrelated continuation modification;
- hidden host-language dispatch.

### Representation contract

A reified state component is not considered fully reflective merely because a host object is wrapped in an object-language list.

The experiment must define how the relevant environment/continuation information is represented, and how that representation is transformed back into live machine state.

### Continuation / meta-level semantics

The project does not require a literal single host-language loop.

The stronger invariant is causal continuity with explicit continuation and, where needed, meta-continuation semantics.

See:

- `docs/REFLECTION-SUBSTRATE-LITERATURE-ALIGNMENT_v0.1.md`
- `docs/REFLECTION-SUBSTRATE-REAUDIT_v0.2.md`

### Immediate decision

Do not broaden the reflective substrate until the narrow dispatch-only causal-reflection minimal pair passes with matched controls.

