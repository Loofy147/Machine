# Machine

Machine-native computation / adaptation research.

## Current phase

This repository is defining an **implementation-independent machine model** before committing to a language, runtime, model architecture, or anthropomorphic cognitive vocabulary.

The project does not assume that a machine should think, feel, attend, remember, or reason in human terms. Human concepts may describe observations later, but they are not accepted as architectural primitives without machine-level evidence.

## Current research question

> What is the smallest fixed substrate that permits executable state to change its own future operating regime, while consequences and retained history can affect subsequent changes?

The broader question of machine intelligence remains deliberately downstream of this operational question.

## Current claim frontier

### Experimentally supported in tested regimes

- Executable representations can be changed and subsequently produce different behavior.
- Mutable executable representation is a capability for adaptation, but does not itself provide a search advantage.
- Continuous same-process evaluator hot-swap works in the current prime-stream harness.
- Outcome history bound to operator identity can causally change proposal policy over a fixed candidate palette.
- Context-indexed history can preserve useful credit when a previously encountered context returns, provided the context is supplied explicitly.

### Not established

- context discovery;
- reusable learned executable structure;
- self-discovery of the adaptation mechanism;
- causal reflection of the evaluator/transition semantics;
- general-purpose machine intelligence.

## Core separation

```text
implementation language
    != operational representation
    != operational semantics
    != physical substrate
```

Python, Rust, C, a VM, an interpreter, native code, or another substrate may be used as research instruments. None is assumed to be the machine's native definition.

Likewise:

```text
reconfigurability
    != adaptation
    != learning
    != reusable learning
    != causal reflection
```

## Research gates

1. Stabilize the abstract transition semantics.
2. Test the same semantics on independent execution substrates.
3. Validate adaptive mechanisms with controlled ablations and matched budgets.
4. Test contextual credit without supplying context labels.
5. Test reusable executable structure on genuinely held-out task families.
6. Implement the smallest causal-reflection substrate only after the preceding semantics are sufficiently stable.

## Current documents

- `docs/ABSTRACT-MACHINE.md` — implementation-independent model
- `docs/FOUNDATION.md` — current principles and claim frontier
- `docs/EXPERIMENT-V0.md` — falsifiable experimental program
- `docs/EXPERIMENT-REVIEW-9-MECHANISMS.md` — nine-mechanism ablation review
- `docs/EXPERIMENT-B-CLEAN.md` — clean mutable-executable-representation experiment
- `docs/EXPERIMENT-ONLINE-REFLECTIVE-LEARNING.md` — online reflective-learning design and boundary
- `docs/EXPERIMENT-CONTEXTUAL-CREDIT.md` — context-indexed credit experiment
- `docs/REFLECTION-FRONTIER.md` — causal-reflection boundary
- `docs/INTERACTION-OPERATING-MODE.md` — project interaction/evidence discipline
- `docs/OPEN-QUESTIONS.md` — unresolved questions

The repository remains research-first. Implementation code should be introduced only as an explicitly named experimental substrate with reproducible evidence attached to its claims.
