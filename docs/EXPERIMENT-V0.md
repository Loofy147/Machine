# V0 — Abstract Machine Operation Experiment

Status: RESEARCH / SEMANTICS FIRST / NOT YET IMPLEMENTED

## Purpose

Test whether an implementation-independent transition model can produce reusable adaptive behavior when the machine can alter its operation structure.

No programming language or execution substrate is part of the hypothesis.

## Research claim

A machine may acquire reusable, non-fixed behavior from continuous operation if its abstract state can drive executable transformations, observations can affect later state, and the machine can alter the structure of future transformations.

## What this experiment must distinguish

1. fixed procedure execution;
2. adaptive next-operation selection;
3. adaptive recomposition of operation sequences and representations.

## Experimental groups

### A — Fixed

A fixed operation graph is supplied for each task family.

### B — Selective

The machine can select the next operation from an available operation set, but cannot change the representation or graph structure beyond the next step.

### C — Recomposition

The machine can change operation order, insert/remove operations, branch, retry under different conditions, and replace the current representation when evidence indicates that the current operating path is insufficient.

## Environment requirements

The environment should provide:

- bounded but nontrivial state;
- executable transformations with different costs and effects;
- consequences that are not fully visible before execution;
- repeatable experiments;
- task instances whose successful procedure is not fixed across the family;
- unseen combinations at evaluation time.

The first environment should be synthetic and deterministic enough to support exact replay.

## Semantic invariants

Before any implementation is accepted, the experiment must specify:

- what constitutes a state;
- what constitutes an operation;
- what constitutes a transition;
- what is observable;
- how a new operation structure is represented;
- what information is allowed to affect transition selection;
- what information is explicitly not part of the machine model.

These semantics must be implementable by more than one execution substrate without changing their meaning.

## Metrics

### Primary

- success on unseen task instances;
- transfer across unseen operation combinations;
- recovery after an invalid or unproductive path;
- quality of recomposed operation structures;
- reproducibility of the same abstract transition trace across independent substrates.

### Secondary

- operation count;
- computational/resource cost;
- repeated failed operations;
- unnecessary recompositions;
- state corruption;
- sensitivity to operation ordering.

## Falsification tests

The hypothesis is weakened or rejected if any of the following occurs:

1. recomposition does not outperform fixed procedures on unseen compositions;
2. gains disappear when superficial search budget is normalized;
3. the system only memorizes successful traces rather than learning reusable transition structure;
4. goalless operation produces no stable useful behavior without hidden objective injection;
5. state persistence does not improve cumulative adaptation beyond replaying the same computations;
6. changing representations does not improve recovery from mismatched or novel tasks;
7. two faithful implementations of the abstract model do not produce semantically equivalent traces where equivalence is expected.

## No hidden goal

The machine model must not receive a semantic task objective through an implementation detail disguised as a selector, reward, benchmark heuristic, operation registry, or harness condition.

An explicit objective may exist in an experimental environment. It must be represented as an environmental condition and kept separate from the machine model.

## Reproducibility

Every run should record, at minimum:

```text
run_id
initial_state
available_operations
operation_inputs
operation_outputs
observations
state_transitions
operation_structures
resource_usage
final_state
substrate_id
model_version
```

The run must be replayable from the recorded abstract inputs and deterministic environment state.

## Success is not intelligence

A successful run is evidence only that the machine produced the required behavior.

A stronger claim requires evidence of reusable operational structure on unseen compositions and evidence that the behavior changed through experience rather than through a hidden fixed procedure.
