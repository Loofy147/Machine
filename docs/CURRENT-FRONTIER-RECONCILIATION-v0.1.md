# Current Frontier Reconciliation v0.1

**Recorded:** 2026-09-19  
**Repository:** `Loofy147/Machine`  
**Purpose:** durable research-state record for the capability/allocation frontier.

## 1. Research state

- `main` = integration authority at `1626bac2f5c478294afa4b9463f694608c322117`.
- `research/machine-native-primitives-v0` = broad machine-model research.
- `research/target-oblivious-frontier-v0` = resource/placement frontier.
- `research/confirmatory-freeze-order-v0.1` = confirmatory protocol/freeze.
- `research/evidence-disposition-v0` = current evidence/provenance consolidation.
- `research/definition`, `research/machine-native-primitives`, `research/machine-native-primitives-v0-docs`, `research/machine-native-primitives-v0-issue`, `research/test-write` remain ARCHIVE CANDIDATES.

## 2. Existing evidence

The repository-backed lines remain:

- nine-mechanism review: no justification for nine flat primitives;
- B-clean: mutable executable representation is a substrate capability, not an adaptive advantage by itself;
- contextual credit: context-indexed history helps in the tested supplied-context regime;
- online reflection: hot-swap and history-dependent proposals supported, causal evaluator reflection still OPEN;
- target-oblivious frontier: offline state can relocate computation; strict-heldout controls pass.

The adversarial insufficiency detector establishes that persistent nonzero residual is not sufficient for a global insufficiency claim; `INCONCLUSIVE_AT_RESOLUTION(delta)` is required without independent regularity/certificates.

## 3. Mechanism frontier result

With:

```text
B_off = 0
R = 0
same graph
same queries
same correctness criterion
1 candidate-edge examination = 1 B_on tick
```

direct predecessor access plus bidirectional search shifts the online feasible frontier relative to successor-only forward BFS.

Successor-only exhaustive inverse emulation cannot recover the native frontier at the tight budgets tested.

This is a resource-bounded frontier result, not an ultimate computational-power separation.

## 4. Representation closure result

A stronger follow-up tested whether the predecessor frontier can be purchased as frozen state.

### Reverse-index representation

For M in {30,100,300}:

```text
B_off = 3M
R = 3M
```

The reverse-index representation reproduced the native bidirectional success pattern and minimum online budgets exactly in every tested summary row.

This means:

> if a substrate can generically interpret an indexed relation stored in state, predecessor access is representable as frozen data.

The remaining issue is whether generic stored-relation traversal belongs to the original fixed substrate or is itself a transition primitive.

### All-pairs policy representation

The fixed successor executor was given an exact target-oblivious `(start,target) -> next-action` table.

Maximum post-instance budget needed to solve every sampled query became:

```text
M=30  -> 9
M=100 -> 13
M=300 -> 17
```

while the forward baseline required:

```text
M=30  -> 74
M=100 -> 254
M=300 -> 845
```

The policy table paid approximately:

```text
B_off = Θ(M^2)
R     = Θ(M^2)
```

Thus the fixed successor executor can trade large offline/state resources for very small online computation.

## 5. Current interpretation

Two premature conclusions are now explicitly rejected.

### Rejected interpretation A

> direct predecessor access proves an absolute new computational capability.

Not supported.

### Rejected interpretation B

> every mechanism-induced frontier shift can be reproduced by ordinary state representation at negligible cost.

Also not supported.

### Current supported interpretation

The experiments establish a multi-resource tradeoff among:

```text
offline computation B_off
persistent representation R
post-instance computation B_on
```

Direct predecessor access provides a low-`B_off`, low-`R` point on that frontier.

A reverse-index can reproduce its online behavior by paying `Θ(M)` offline/state resources.

An all-pairs policy can reduce online computation further by paying `Θ(M^2)` resources.

Therefore the remaining mechanistic question is narrower:

> Does a fixed substrate contain a generic state-indexed relation interpreter, or does adding that interpreter constitute a genuine transition primitive?

That boundary determines whether predecessor access is best described as representation or mechanism under the chosen substrate.

## 6. Current frontier

The active research object is now the Pareto frontier:

```text
(B_off, R, B_on)
```

for a fixed information-timing contract and correctness requirement.

A mechanism is causally interesting only if it supplies a Pareto point that the admissible fixed-substrate representation family cannot reproduce under the same resource contract.

## 7. Immediate next test

Define and isolate the smallest generic operation:

```text
relation_lookup(state, key) -> stored executable relation
```

Then test:

1. whether it already follows from the abstract machine contract;
2. whether it must be added as a new substrate primitive;
3. whether direct predecessor access offers any Pareto advantage after that primitive is admitted;
4. whether a compact relation encoding can approach the reverse-index frontier with sub-`Θ(M)` storage.

## 8. Provenance status

Repository-backed now:

- adversarial insufficiency detector;
- mechanism frontier baseline/emulation;
- macro representation controls;
- Pareto representation closure;
- representative query-level samples;
- resource metadata;
- current claim registry.

Still CONVERSATION-ONLY:

- earlier policy-table/BFS numerical run;
- h-allocation sweep;
- memoized-lookahead ~19.3% reduction;
- workload crossover near N=40/62.

Those remain excluded from scientific evidence until their original harnesses and raw outputs are packaged.

## 9. Sample locations

`experiments/pareto-representation-closure-v0/REPRESENTATIVE-SAMPLES-V0.csv`

`experiments/pareto-representation-closure-v0/SUMMARY-V0.csv`

`experiments/pareto-representation-closure-v0/PARETO-FRONTIER-V0.csv`

`experiments/pareto-representation-closure-v0/RESOURCE-METADATA-V0.json`

`experiments/pareto-representation-closure-v0/RESULTS-V0.md`

`experiments/pareto-representation-closure-v0/run.py`

## 10. Governing rule

Do not ask which named category wins.

Measure the Pareto frontier first.

Then identify which substrate/resource distinction caused the frontier shift.

