# Online Reflective Learning Experiment

Status: EXPERIMENT DESIGN / OPEN

## Purpose

Test the smallest continuously executing machine that can:

1. reify its live execution state;
2. produce a candidate change to the evaluator represented in that state;
3. probe the candidate without destroying the current execution state;
4. commit or reject the candidate;
5. retain probe history as ordinary state;
6. use that history to change the distribution of future candidate changes.

This experiment does not assume intelligence, thinking, planning, attention, memory, or an agent abstraction.

## Core state

Use a CEK-like state extended with an evaluator value:

```text
Q = <R, S, K, rho, H>
```

where:

- `R` = current expression / executable control;
- `S` = ordinary environment/state;
- `K` = continuation;
- `rho` = current evaluator representation;
- `H` = retained history of candidate/probe/outcome records.

The fixed substrate supplies the base transition relation `E` that interprets the current state and, in the experimental construction, consults `rho` for ordinary redex dispatch.

## Candidate transition

```text
execute(E, Q) -> Q' / result
reify(Q) -> d
propose(d, H) -> d'
probe(Q, d') -> result'
commit(Q, d') -> Q'
rollback(snapshot) -> Q
```

`propose` is not a primitive assumption. It is the mechanism under test and may initially be a fixed mutation procedure.

## Target property: online causal reflection

A successful run must satisfy all of these:

### Continuity

`install/commit` occurs inside one execution trace. The experiment must not serialize a new program to a fresh process and restart from an initial state.

### Evaluator change

A minimal-pair probe must show that the same test expression has different transition behavior under `rho_pre` and `rho_post` while ordinary test inputs are held constant.

### Causal use

The evaluator representation installed after commitment must be the representation actually consulted by subsequent execution. A descriptive copy that is never consulted fails the experiment.

### Reproducibility

The committed evaluator description must be closed over its intended state and portable into a fresh equivalent machine state. Replaying the same description under matched initial conditions must reproduce its transition behavior.

## Safety / commitment

Because the process is continuous, failed evaluator changes cannot be allowed to destroy the only live process.

The experiment therefore requires a non-destructive commitment mechanism. The implementation may use checkpoint/rollback, copy-on-write state, speculative execution, or an equivalent mechanism.

The abstraction being tested is:

```text
candidate
  -> isolated probe
  -> commit | reject
```

Not a specific checkpoint implementation.

## Learning condition

Selection alone is:

```text
propose -> probe -> accept/reject
```

Learning requires historical observations to change future proposals.

Primary test:

```text
P(success_{t+1} | H_t)
```

must improve relative to a matched history-independent control, after controlling for candidate-space exhaustion and changing task difficulty.

A stronger causal comparison is:

```text
history-aware proposer
vs
same proposer with matched/shuffled/erased history
```

under the same candidate budget.

## Experimental conditions

### C0 — Fixed evaluator

No modification of `rho`.

### C1 — Online evaluator mutation, no history use

`rho` can change, but candidate generation is history-independent.

This isolates reflection + selection from learning.

### C2 — Online evaluator mutation with history

`rho` can change and the proposer reads prior `(candidate, probe, outcome)` records.

This tests cumulative adaptation.

### C3 — Offline control

The same candidate-generation and evaluation logic operates in separate processes/episodes.

This separates online continuity from ordinary evolutionary iteration.

## Candidate program family

Use a deliberately small evaluator language whose semantics are deterministic and whose mutations are inspectable.

A suitable first task is prime counting or another bounded integer stream where:

- one implementation is trusted;
- at least one candidate mutation is measurably faster;
- at least one candidate mutation is intentionally incorrect;
- failures are detectable by a trusted reference;
- the live workload can continue across accepted changes.

Do not use timing as the only correctness signal.

Correctness must be checked against trusted reference outputs; timing is secondary evidence about performance.

## Live continuity test

Run a long-lived event stream:

```text
input_1 -> evaluator_0
input_2 -> evaluator_0
...
probe candidate
commit rho_1
input_n -> evaluator_1
...
```

The process must remain alive across the evaluator change.

The event log must prove which evaluator was active for each event.

## Versioned transition record

Every state transition relevant to adaptation should emit a compact record:

```text
{
  generation,
  parent_rho_hash,
  candidate_rho_hash,
  probe_id,
  reference_result_digest,
  candidate_result_digest,
  correctness,
  cost,
  committed,
  history_size
}
```

The record is evidence, not the machine's internal explanation.

## Mutation operators

Start with a tiny explicit set:

- replace operator body with a known valid variant;
- replace with an intentionally buggy variant;
- change a bounded parameter;
- compose two existing evaluator fragments.

Do not introduce open-ended code generation in the first experiment.

## Reference / validation separation

Use two sets:

```text
validation inputs
    used for candidate probes

held-out inputs
    never used to choose a candidate
```

A candidate is only considered an improvement if it passes correctness on validation and its held-out behavior remains correct.

## Measurements

Primary:

- continuous execution preserved: yes/no;
- causal evaluator change: yes/no;
- correctness after commitment;
- proposal success rate over time;
- held-out correctness;
- performance change after commitment.

Secondary:

- proposal entropy;
- rejected/accepted ratio;
- rollback rate;
- lineage diversity;
- history contribution above matched history-free control.

## Falsifiers

The experiment fails to establish online reflective learning if any of the following remains true:

1. the process must restart after evaluator replacement;
2. changing `rho` does not change subsequent transition semantics;
3. the installed `rho` is not causally consulted;
4. history-aware proposal is not better than a matched history-free control;
5. improvement exists only on probe inputs and fails on held-out inputs;
6. performance gains are explained entirely by candidate-space enumeration or increasing compute;
7. the trusted reference cannot reliably distinguish the intentionally buggy candidate.

## Non-goals

This experiment does not attempt to establish intelligence, consciousness, generality, human-like reasoning, or unbounded self-improvement.

It tests one machine-native capability:

> Can a single ongoing executable process change the rule that determines its future execution, safely commit that change, and learn from the consequences of doing so?
