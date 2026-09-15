# Experiment B-clean: Executable Representation Adaptation

Status: EXPERIMENTALLY_SUPPORTED / LIMITED

This experiment tests whether an explicitly mutable executable representation provides an adaptive advantage beyond the search/adaptation algorithm operating over it.

## 1. Setup

A fixed x86-64 substrate executes one mutable instruction sequence:

```text
mov eax, edi
<ALU operation> eax, imm8
ret
```

The candidate space was restricted to five stateless operations:

```text
ADD, OR, AND, SUB, XOR
```

The hidden target was:

```text
x XOR 15
```

Each candidate is represented by an operation selector plus an 8-bit immediate. The substrate is fixed; the executable representation is modified between evaluations.

A 16-point training set was used for search and a separate 64-point held-out test set measured generalization. Fifteen independent seeds were run for each search method at two equal candidate-evaluation budgets: 300 and 3000.

Methods:

- hill climbing
- simulated annealing
- uniform random search

## 2. Results

| Budget | Method | Train solved | Mean train error | Mean held-out test error |
|---:|---|---:|---:|---:|
| 300 | hill climb | 3/15 | 392.87 | 1937.07 |
| 300 | annealing | 11/15 | 49.47 | 229.73 |
| 300 | random | 4/15 | 34.53 | 136.53 |
| 3000 | hill climb | 3/15 | 392.87 | 1937.07 |
| 3000 | annealing | 14/15 | 30.00 | 146.80 |
| 3000 | random | 12/15 | 3.20 | 12.80 |

No run with zero training error had non-zero test error under this candidate family and split protocol.

## 3. Interpretation

### 3.1 Reconfigurability

**Status: EXPERIMENTALLY_SUPPORTED**

The substrate can modify its executable representation and subsequently execute different behavior. This was already established by direct instruction mutation.

### 3.2 Adaptation

**Status: EXPERIMENTALLY_SUPPORTED, but not substrate-specific**

The search procedures can use observed fitness to modify the executable representation and reach the target function. The experiment therefore demonstrates adaptive modification of executable representation.

It does **not** show that mutable executable representation itself supplies the adaptive algorithm. The adaptation policy was supplied externally by the experimenter.

### 3.3 Search algorithm dominates the result

The clean comparison shows no evidence that executable representation mutation, by itself, outperforms ordinary search over the same finite hypothesis space.

At budget 3000, random search substantially outperformed hill climbing and simulated annealing on both mean train error and held-out test error. This is consistent with the hypothesis that, for this small search space, search dynamics are the dominant factor.

Therefore the previous claim must be weakened:

> Mutable executable representation is a substrate capability for adaptation, not evidence of an adaptive advantage by itself.

### 3.4 Held-out generalization

The absence of train-perfect/test-imperfect cases is expected to be interpreted cautiously. The candidate family is extremely small and the target function is exactly representable as `XOR 15`. Zero train error strongly identifies that candidate under the sampled inputs; it does not establish reusable learning.

The experiment therefore demonstrates **generalization within a known hypothesis family**, not reusable learned structure.

### 3.5 Hill-climbing result

Hill climbing was unchanged between 300 and 3000 evaluations in the reported aggregate results. This indicates strong local trapping under the chosen mutation neighborhood. It is evidence about the search procedure, not evidence against mutable representations.

## 4. Important correction from the previous adaptive experiment

The earlier experiment included `ADC`, `SBB`, and `CMP`. Those instructions depend on or modify arithmetic flags, creating hidden machine state that was not represented in the candidate tuple `(operation, immediate, input)`.

This clean experiment removes those stateful operations and leaves:

```text
ADD, OR, AND, SUB, XOR
```

so candidate evaluation is deterministic with respect to the represented input and parameters.

## 5. What remains open

The experiment does not test structural adaptation such as changing the number, ordering, branching, or composition of instructions.

It also does not test reusable learning across a family of tasks.

The next discriminating experiment should therefore test whether the machine can discover and preserve a reusable executable substructure across related tasks, with genuinely held-out tasks and an explicit fresh-search baseline.

A further requirement is to separate:

```text
reconfigurability
adaptation
learning
reusable learning
self-discovery of the adaptation mechanism
```

These are not interchangeable claims.
