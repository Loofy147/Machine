# Machine — Foundation

Status: RESEARCH / OPEN HYPOTHESES

## Core question

> What is the smallest composable set of machine-native operations that can produce reusable adaptive behavior without importing human cognitive mechanisms as architectural primitives?

The project deliberately studies machine-operational capabilities rather than starting from the category of "intelligence".

## Research origin

The current research grew from earlier questions about goals, feelings, identity, operational significance, adaptation, and the difference between human descriptions and machine mechanisms. Those questions are preserved in `docs/RESEARCH-ORIGIN.md`.

The origin layer is provenance, not evidence. Human concepts may motivate a machine-native question without prescribing the mechanism that answers it.

## Non-goals

This repository does not begin by implementing human-like thinking, emotion, attention, personality, memory, planning, or general intelligence as first-class concepts.

Human concepts may describe observed behavior after the fact, but they are not architectural primitives without machine-level evidence.

## Working principles

1. Machines should be machines, not human clones.
2. Abstract the function required, not the human mechanism associated with it.
3. Knowledge is not the same as the ability to use knowledge during operation.
4. A transition need not require a semantic task objective on every cycle.
5. State transition may be driven by operational conditions such as change, consequence, availability, conflict, uncertainty, failure, or resource pressure.
6. The machine should be able to change how it operates, not only what it stores.
7. A failed or surprising operation is evidence about the current operating regime.
8. Persistent state should preserve future utility and meaning, not merely bytes.
9. Remembering does not imply activation; activation does not imply influence.
10. Generality is an open hypothesis and may belong to capability acquisition/composition rather than one universal mechanism.
11. Experimental relevance does not imply architectural primitivity or universality.
12. Mechanisms should be separated by causal role before being named primitives.
13. Search/adaptation procedures must not be credited to mutable representation merely because the representation is mutable.
14. Learning claims require matched history-erased/shuffled controls.
15. Context-sensitive learning must distinguish supplied context labels from context discovered from machine-observable state.
16. Human descriptions such as feeling or motivation may be retained as functional questions, but must be translated into machine-operational variables before becoming architectural claims.

## Current architectural classification

The nine-mechanism experiment indicates that a flat primitive list is misleading. The current classification is provisional.

### Structural execution

- State
- Operation / Transformation
- Transition
- Control / scheduling

These are partly definitional: deleting them may delete executability rather than ablate a separable capability.

### Operation-space modulation

- Invocation constraints
- Variation / branching
- Composition

The causal role of each remains conditional on fair ablations and matched budgets.

### Regime adaptation

- Evaluation / testing
- Reformation
- Experience / accumulation

These alter how future operation is evaluated, generated, constrained, or scheduled.

## Operational significance

An original project question was why some events or conditions should alter future machine operation more strongly than others.

Human descriptions of such changes may use words such as:

```text
fear
urgency
curiosity
motivation
attention
```

The current machine-native formulation is narrower:

> What mechanism changes the operational significance of a state, consequence, or predicted consequence so that it alters subsequent transition policy?

Candidate variables include:

```text
state deviation
consequence estimate
cost / irreversibility
uncertainty
resource pressure
history
context
persistence / decay
```

This is an open research direction. None of these variables is being declared equivalent to a human emotion, and no emotion-like primitive has been added to the abstract model.

## Current experimental frontier

### Established within tested regimes

- Executable representations can be modified and produce different future behavior.
- Mutable executable representation is a substrate capability for adaptation; it does not itself provide an adaptive search advantage.
- Search dynamics can dominate performance in a small mutable instruction space.
- Continuous same-process evaluator hot-swap is experimentally supported in the current prime-stream harness.
- History bound to operator identity can causally change proposal policy over a fixed candidate palette.
- Context-indexed history preserves useful operator credit when the same context recurs after another context intervenes, when context labels are supplied.

### Important negative results / corrections

- The nine-mechanism result does not justify a flat nine-primitive architecture.
- Variation's measured effect is confounded by the poor single-path fallback selector.
- Invocation gating combined multiple functions and must be decomposed.
- No-testing outperforming full-testing shows that noisy evaluation can hurt in this regime; it does not show evaluation is intrinsically harmful.
- Scalar operation-only accumulation can become harmful when weighted strongly.
- Mutable executable state does not establish learning, reusable structure, or intelligence.
- The current online prime experiment does not establish causal reflection of the evaluator because its live source representation is external to the evaluator state.

## Contextual experience

The current best-supported experience hypothesis is no longer merely that "memory should be contextual". The narrower experimentally supported result is:

```text
(context, operation) -> outcome history
```

can preserve useful credit where:

```text
operation -> global outcome history
```

would mix incompatible regimes.

The latest controlled experiment used explicit `REPEAT` and `UNIQUE` labels and measured a real performance crossover between `memo_cache` and `math_isqrt`. Therefore the result establishes context-conditioned credit in the tested policy layer.

It does **not** establish context discovery. The next experiment must derive regime features from machine-observable state/event history rather than receiving the regime label from the harness.

## Reconsidering the earlier primitive vocabulary

The earlier candidate set (`State`, `Represent`, `Select`, `Operate`, `Observe`, `Recompose`) remains useful as vocabulary but not as an architectural commitment.

- `Represent` may be an executable transformation.
- `Select` may reduce to scheduling/control.
- `Operate` may be the general transition semantics.
- `Observe` may be a state/result relation rather than a perceptual faculty.
- `Recompose` may be a family containing variation, composition, and reformation.

## Current machine cycle

```text
S
 -> determine executable transition
 -> execute
 -> obtain consequence
 -> update state and/or operation structure
 -> S'
```

Optional mechanisms participate only when required by the regime.

## Reconfigurability vs adaptation vs learning

These claims remain explicitly separate:

```text
reconfigurability
  != adaptation procedure
  != learning
  != reusable learning
  != self-discovery of the adaptation mechanism
  != causal reflection
```

Evidence for one must not silently promote the status of another.

## Reflection frontier

The current target is a narrower machine capability:

> a single ongoing computational process reifies executable state or execution machinery, modifies a representation that actually participates in future transitions, safely commits the change, and continues execution without external restart.

The current hot-swap experiment reaches online executable replacement but not this stronger causal-reflection criterion.

## Goalless operation

A transition may be driven by machine-native conditions without a semantic task objective on every cycle. This remains an open experimental question rather than an established capability.

## Intelligence criterion

Do not define success as the presence of a component named `intelligence`.

The stronger operational target is:

> Can a small machine acquire reusable operational structure under conditions not explicitly encoded as fixed procedures, while the mechanism responsible for that adaptation remains auditable?

## Current unknowns

- Can the structural execution layer be reduced further?
- Which operation-space mechanisms are causally necessary under fair controls?
- Can context be discovered from machine state rather than supplied labels?
- Can contextual credit improve cumulative regret rather than only configuration persistence?
- Can reusable executable structure be learned across genuinely held-out tasks?
- Can an online machine causally modify the evaluator/transition mechanism while preserving the same continuation?
- Can the proposer/modifier itself be modified without introducing an unexamined fixed meta-layer?
- Does regime modification generalize rather than merely improve search?
- Can useful goalless operation exist without hidden objective injection?
- Which state should persist, decay, or be discarded for cumulative adaptation?
- Can changes in operational significance be induced by machine-observable consequence, cost, uncertainty, or regime shift without importing a human emotion primitive?
