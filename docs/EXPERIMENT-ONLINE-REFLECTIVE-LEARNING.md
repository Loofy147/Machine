# Online Reflective Learning Experiment

Status: EXPERIMENTALLY_SUPPORTED / LIMITED — reflection target still OPEN

## Purpose

Test the smallest continuously executing machine that can:

1. reify or access executable state;
2. produce a candidate change to the operation used by the live process;
3. validate the candidate without destroying the current execution state;
4. commit or reject the candidate;
5. retain outcome history as ordinary state;
6. use that history to alter future candidate proposals.

This experiment does not assume intelligence, thinking, planning, attention, memory, or an agent abstraction.

## Core target

The stronger target remains a causally reflective state such as:

```text
Q = <R, S, K, rho, H>
```

where:

- `R` = executable control / current expression;
- `S` = ordinary operational state;
- `K` = continuation;
- `rho` = evaluator/transition machinery represented in the state under test;
- `H` = retained candidate/probe/outcome history.

The fixed substrate supplies transition semantics `E`.

The critical question is whether `rho` is actually part of the causal state consulted by future transitions, rather than merely an external source artifact.

## Candidate transition

```text
execute(E, Q) -> Q' / result
reify(Q) -> d
propose(d, H) -> d'
probe(Q, d') -> result'
commit(Q, d') -> Q'
```

`propose` is not assumed to be a primitive. It may initially be an explicit fixed mutation procedure.

## What has now been experimentally demonstrated

### A — Continuous online executable replacement

A long-lived Python process used a trusted prime-counting reference, an external `CURRENT` source file, isolated subprocess validation, and hot reload into the same process.

The live stream continued across accepted evaluator replacements while accumulated process state was preserved.

**Status: EXPERIMENTALLY_SUPPORTED.**

This establishes online hot-swap of an executable operation within one process.

### B — History-dependent proposal policy

A fixed candidate palette was paired with outcome history. A controlled ablation compared history-enabled, history-erased, and history-shuffled policies.

Correctly binding outcome history to operator identity materially reduced bad proposals relative to matched history-free or shuffled controls.

**Status: EXPERIMENTALLY_SUPPORTED, fixed candidate palette.**

This is credit assignment / policy adaptation, not discovery of new executable structure.

### C — Context-indexed credit

A subsequent experiment compared:

```text
(context, operator) -> history
```

against:

```text
operator -> global history
```

The measured streams contained a real performance crossover: `memo_cache` was best in REPEAT, while `math_isqrt` was best in UNIQUE.

For 60 seeds and block sequence `REPEAT -> UNIQUE -> REPEAT -> UNIQUE`, the recurring REPEAT block showed:

| Policy | memo weight at block start | memo active fraction | reacquire generation |
|---|---:|---:|---:|
| context-aware | 0.667 ± 0.000 | 0.989 ± 0.017 | 0.55 ± 0.83 |
| context-blind | 0.102 ± 0.013 | 0.956 ± 0.048 | 2.22 ± 2.40 |

Welch-style normal approximation gave:

```text
weight:  t = +326.35, p ≈ 0
active:  t = +5.08,   p = 3.773e-07
```

**Status: EXPERIMENTALLY_SUPPORTED, TESTBED-SPECIFIC.**

This establishes context-conditioned credit when the context label is supplied.

## Critical limitations of the current online system

The current prime-stream implementation does **not** yet satisfy causal procedural reflection.

1. `reify_current_source()` reads external source text; it does not reify the live evaluator, continuation, and state as one causal description.
2. Python's evaluation semantics remain external and fixed.
3. Candidate operators are a fixed human-written palette; the system does not synthesize arbitrary new operators or executable structures.
4. Candidate validation occurs outside the live execution path, so the current result demonstrates safe hot-swap rather than destructive online trial and rollback.
5. History records candidate trials, but the current proposer can exclude the active operator, which can alter long-run credit behavior.
6. Context labels in the contextual experiment were supplied by the harness; context was not discovered from machine state.
7. Candidate performance profiles in the contextual experiment were precomputed; the policy experiment therefore isolates credit assignment rather than full online learning from live execution.

These limitations are part of the result, not cleanup items to hide.

## Target property: online causal reflection

A successful reflective implementation must satisfy all of these:

### Continuity

`commit` occurs inside one execution trace. The experiment must not create a fresh process and restart from an initial state.

### Evaluator change

A minimal-pair probe must show different transition behavior under `rho_pre` and `rho_post` with the same ordinary test input.

### Causal use

The installed evaluator representation must be the representation actually consulted by subsequent execution.

### Observable effect

Changing the reified representation must change a later transition or result in a controlled minimal pair.

### Reproducibility

The committed representation should be replayable under matched initial conditions where portability is part of the claim being tested.

## Safety / commitment

Because the process is continuous, failed evaluator changes cannot destroy the only live execution state.

The implementation may use checkpoint/rollback, copy-on-write, speculative execution, shadow state, or another mechanism.

The abstraction under test is:

```text
candidate
  -> isolated probe
  -> commit | reject
```

not a particular checkpoint implementation.

## Learning condition

Selection alone is:

```text
propose -> probe -> accept/reject
```

Learning requires historical observations to alter future proposals.

The minimum causal control is:

```text
history-aware proposer
vs
same proposer with erased or shuffled history
```

with matched candidate budgets and task streams.

## Context-discovery condition

The next contextual experiment must remove the supplied `REPEAT` / `UNIQUE` label.

Instead derive a context signature from machine-observable state or recent event history, for example:

```text
recent recurrence
value distribution
transition statistics
resource/load pattern
```

Then compare:

```text
history erased
history global
history indexed by supplied context
history indexed by machine-derived context
```

Primary metrics should include cumulative regret, accepted improvements, bad proposals, and recovery time after hidden regime changes.

## Candidate program family

Use a deliberately small deterministic evaluator language whose mutations are inspectable.

Prime counting remains a useful first substrate because it provides:

- a trusted reference;
- valid faster variants;
- intentionally incorrect variants;
- measurable cost differences;
- a live stream that can continue across accepted changes.

Correctness must be separated from performance. Timing is secondary evidence.

## Versioned transition record

Relevant adaptation transitions should emit compact evidence such as:

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

The record is evidence, not an internal explanation.

## Falsifiers

The stronger claim of online reflective learning is not established if:

1. evaluator replacement requires a restart;
2. changing `rho` does not change subsequent transition semantics;
3. the installed `rho` is never causally consulted;
4. history-aware proposal provides no improvement over a matched history-free control;
5. improvements occur only on probe inputs and fail on held-out inputs;
6. apparent improvement is fully explained by fixed candidate enumeration or extra compute;
7. the trusted reference cannot reliably reject intentionally incorrect candidates;
8. contextual gains disappear when the regime label is removed.

## Non-goals

This experiment does not attempt to establish consciousness, general intelligence, human-like reasoning, or unbounded self-improvement.

It isolates machine-native capabilities in increasing order:

```text
continuous execution
-> executable replacement
-> history-dependent proposal
-> context-conditioned credit
-> context discovery
-> causal evaluator reflection
-> modification of the modification mechanism
```
