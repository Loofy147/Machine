# Machine

Machine-native intelligence research.

This repository tests a narrow question:

> What is the smallest composable set of machine-native operations that can produce reusable, adaptive behavior without encoding human cognitive primitives as the architecture?

## Current stance

The project does **not** assume that a machine should think like a human.

It starts from executable machinery:

```text
State
  -> Represent
  -> Select
  -> Operate
  -> Observe
  -> Recompose
  -> State'
```

These are research candidates, not established facts.

The first experiment is intentionally small and synthetic. It will test whether adaptive operation and recomposition produce transfer to unseen task compositions beyond fixed procedures.

See:

- `docs/FOUNDATION.md` — principles and primitive candidates
- `docs/EXPERIMENT-V0.md` — falsifiable V0 experiment
- `docs/OPEN-QUESTIONS.md` — unresolved questions
