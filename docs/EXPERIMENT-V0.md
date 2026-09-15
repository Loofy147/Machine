# V0 — Machine-Native Operation Experiment

Status: RESEARCH / NOT YET IMPLEMENTED

## Research claim

A machine may acquire reusable, non-fixed behavior from continuous operation if it can represent state, select executable operations, observe consequences, and recompose its operation path.

## What this experiment must distinguish

This is not a test of language quality, task completion alone, or human-like reasoning.

It must distinguish:

1. fixed procedure execution;
2. adaptive next-operation selection;
3. adaptive recomposition of operation sequences and representations.

## Experimental groups

### A — Fixed

A fixed operation graph is supplied for each task family.

### B — Selective

The machine can select the next operation from an available operation set, but cannot change the representation or graph structure beyond the next step.

### C — Recomposition

The machine can change operation order, insert/remove operations, branch, retry under different conditions, and replace the current representation when evidence indicates the current path is insufficient.

## Environment requirements

The environment should provide:

- bounded but nontrivial state;
- executable operations with different costs and effects;
- hidden or partially observed consequences;
- repeatable experiments;
- tasks whose optimal or successful procedure is not fixed across all instances;
- unseen combinations at evaluation time.

The first environment should be synthetic and deterministic enough to support exact replay.

## Metrics

### Primary

- success on unseen task instances;
- transfer across unseen operation combinations;
- ability to recover after an invalid or unproductive path;
- quality of recomposed operation graphs.

### Secondary

- operation count;
- computational/resource cost;
- repeated failed operations;
- unnecessary recompositions;
- state corruption;
- sensitivity to operation ordering.

## Falsification tests

The hypothesis should be considered weakened or rejected if any of the following occurs:

1. recomposition does not outperform fixed procedures on unseen compositions;
2. gains disappear when superficial search budget is normalized;
3. the system only memorizes successful traces rather than learning reusable transition structure;
4. goalless operation produces no stable useful behavior without hidden objective injection;
5. state persistence does not improve cumulative adaptation beyond replaying the same computations;
6. changing representations does not improve recovery from mismatched or novel tasks.

## Control against hidden goals

The runtime must not smuggle a semantic task objective into the machine through the selector, reward function, benchmark harness, or operation registry.

Any explicit objective used by an environment must be marked as an environment condition, not as an assumed machine primitive.

## Reproducibility

Every run should record:

```text
run_id
initial_state
available_operations
operation_inputs
operation_outputs
observations
state_transitions
operation_graphs
resource_usage
final_state
```

The run must be replayable from recorded inputs and deterministic environment state.

## Success is not intelligence

A successful run is evidence only that the machine produced the required behavior.

The stronger claim — that the machine has acquired a reusable operational regime — requires transfer to unseen task compositions and evidence that behavior changes because of experience rather than because of a hidden fixed procedure.
