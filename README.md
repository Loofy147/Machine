# Machine

Machine-native intelligence research.

## Current phase

This repository is defining an **implementation-independent machine model** before selecting a language, runtime, or model architecture.

The project does **not** assume that a machine should think, feel, attend, remember, or reason in human terms. Human concepts may later describe observed behavior, but they are not accepted as architectural primitives without evidence that the machine needs them.

### Current research question

> What is the smallest set of machine-native state transitions and executable operations that can produce reusable, adaptive behavior?

### Baseline hypothesis

```text
State
  -> represent change
  -> choose an available operation
  -> execute
  -> observe consequence
  -> alter operation structure when needed
  -> State'
```

This is a hypothesis, not a final architecture.

## Important separation

`Machine model != implementation language`

Python, Rust, C, a VM, a graph executor, or another substrate may be used later as research instruments. None is assumed to be the machine's native substrate.

## Research gates

1. Define the abstract state-transition semantics.
2. Prove that the semantics are independent of any specific implementation language.
3. Build at least two different execution substrates for the same semantics.
4. Compare whether the semantics produce the same observable behavior across substrates.
5. Only then investigate learning, persistent operation, recomposition, and transfer.

## Current documents

- `docs/ABSTRACT-MACHINE.md` — implementation-independent model
- `docs/FOUNDATION.md` — principles, boundaries, and current hypotheses
- `docs/EXPERIMENT-V0.md` — falsifiable experimental program
- `docs/OPEN-QUESTIONS.md` — unresolved questions

The Python implementation previously used for the initial scaffold is intentionally not part of the current baseline. A future implementation belongs under an explicitly named research-harness boundary.
