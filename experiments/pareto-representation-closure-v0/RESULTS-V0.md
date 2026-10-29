# Pareto Representation Closure v0 — Results

**Status:** EXPERIMENTALLY_SUPPORTED / LOCAL REPLAY / NOT YET CI-VERIFIED
**Branch:** `research/evidence-disposition-v0`
**Code:** `experiments/pareto-representation-closure-v0/run.py`

## Question

Can the resource-bounded frontier produced by direct predecessor access be recovered by moving the same information into frozen target-oblivious state, while keeping the successor transition rule for execution?

This is the strongest representation-closure control attempted so far.

## Contract

For each graph:

- `B_on` is post-instance computation;
- `B_off` is preprocessing/representation construction work;
- `R` is stored representation entries;
- queries are unknown during offline construction;
- correctness criterion is exact reachability;
- 80 queries per seed;
- seeds = 17, 23, 41;
- `M ∈ {30,100,300}`.

Compared methods:

1. **forward** — successor-only BFS with visited set; `B_off=R=0`.
2. **native_bidi** — bidirectional BFS with direct predecessor access; `B_off=R=0`.
3. **reverse_index** — target-oblivious reverse adjacency stored offline and consumed by the same bidirectional search logic.
4. **policy** — target-oblivious all-pairs next-action table used by a fixed successor executor.

## Resource sizes

| M | Reverse-index B_off | Reverse-index R | All-pairs policy B_off | Policy R |
|---:|---:|---:|---:|---:|
| 30 | 90 | 90 | 2,700 | 870 |
| 100 | 300 | 300 | 30,000 | 9,900 |
| 300 | 900 | 900 | 270,000 | 89,700 |

The reverse index therefore stores exactly the 3M directed graph edges.

The all-pairs policy stores one action cell for essentially every ordered start/target pair.

## Frontier closure

Minimum online budget required to solve every sampled query:

| M | Method | B_off | R | B_on max |
|---:|---|---:|---:|---:|
| 30 | forward | 0 | 0 | 74 |
| 30 | native_bidi | 0 | 0 | 26 |
| 30 | reverse_index | 90 | 90 | 26 |
| 30 | policy | 2,700 | 870 | 9 |
| 100 | forward | 0 | 0 | 254 |
| 100 | native_bidi | 0 | 0 | 70 |
| 100 | reverse_index | 300 | 300 | 70 |
| 100 | policy | 30,000 | 9,900 | 13 |
| 300 | forward | 0 | 0 | 845 |
| 300 | native_bidi | 0 | 0 | 195 |
| 300 | reverse_index | 900 | 900 | 195 |
| 300 | policy | 270,000 | 89,700 | 17 |

Median and p90 online requirements were:

| M | Method | Median B_on | P90 B_on |
|---:|---|---:|---:|
| 30 | forward | 22.5 | 47 |
| 30 | native_bidi | 9 | 18 |
| 30 | reverse_index | 9 | 18 |
| 30 | policy | 5 | 7 |
| 100 | forward | 80.5 | 193 |
| 100 | native_bidi | 23 | 44 |
| 100 | reverse_index | 23 | 44 |
| 100 | policy | 7 | 11 |
| 300 | forward | 255.5 | 605 |
| 300 | native_bidi | 48.5 | 112 |
| 300 | reverse_index | 48.5 | 112 |
| 300 | policy | 11 | 15 |

## Main findings

### 1. The direct predecessor frontier is exactly reproducible as stored relation data

For all tested budgets and seeds:

```text
native_bidi == reverse_index
```

The online success patterns and minimum online budgets are identical.

Therefore:

> If the substrate permits a frozen state representation to contain and generically traverse an explicit transition relation, direct predecessor access does not create an unrepresentable capability. It changes where the relation is stored and when its construction cost is paid.

This is the strongest representation-closure result so far.

### 2. The closure is not free

The reverse-index representation pays:

```text
B_off = 3M
R = 3M
```

to recover the native online frontier.

So the mechanism and representation variants occupy different points in the multi-resource frontier.

The direct predecessor mechanism has:

```text
B_off = 0
R = 0
```

while the stored relation has:

```text
B_off = Θ(M)
R = Θ(M)
```

### 3. A much richer fixed-successor representation can reduce online computation even further

The target-oblivious all-pairs policy table reduces the maximum sampled online budget to:

```text
M=30   -> 9
M=100  -> 13
M=300  -> 17
```

but pays approximately:

```text
B_off = Θ(M²)
R = Θ(M²)
```

This directly demonstrates computation relocation:

```text
large offline computation/state
        ->
small online computation
```

without requiring direct predecessor access during execution.

## Correct interpretation

The previous statement:

> direct predecessor access creates a mechanism-specific capability frontier

is too strong if the substrate allows arbitrary target-oblivious transition relations to be stored and interpreted.

The more precise result is:

> direct predecessor access provides a favorable low-`B_off`, low-`R` point on the online-computation frontier.

A sufficiently rich frozen representation can reproduce the same online behavior, but pays additional preprocessing and state resources.

The all-pairs policy goes further: it can reduce online search below the direct predecessor frontier by paying substantially more offline/state resources.

Therefore no absolute capability hierarchy has been demonstrated.

## Critical boundary

The representation closure itself depends on the substrate contract.

If the substrate provides:

```text
generic state
+
generic indexed relation lookup/traversal
```

then predecessor access can be represented as data.

If the substrate provides only:

```text
successor operations A/B/C
```

and has no generic mechanism for interpreting a stored adjacency relation as executable transitions, then the reverse index is not merely data: the ability to interpret it is part of the transition mechanism.

Therefore the remaining question is not whether the relation can be stored. It can.

The remaining question is:

> What is the minimum fixed substrate required to make arbitrary executable relations stored in state operationally usable?

That is now a cleaner substrate question than "is mechanism change more powerful than state mutation?"

## Pareto consequence

There is no single scalar winner.

The tested points form a multi-resource tradeoff:

```text
forward:
    (B_off=0, R=0, high B_on)

direct predecessor:
    (0, 0, lower B_on)

reverse-index:
    (Θ(M), Θ(M), same B_on as predecessor)

all-pairs policy:
    (Θ(M²), Θ(M²), very low B_on)
```

A mechanism is interesting only if it contributes a Pareto point that cannot be reproduced by the fixed substrate plus admissible representation under the same resource accounting.

## Next discriminating experiment

The next test should target the substrate boundary directly:

1. Define the smallest generic state-indexed relation lookup permitted by the abstract machine contract.
2. Test whether reverse-index storage becomes operational without adding a new transition primitive.
3. Compare its cost against direct predecessor access.
4. Repeat on graphs where the relation is not algebraically invertible.
5. Search compact relation encodings between raw reverse index and full all-pairs policy.

The decisive question has become:

> Is direct transition access fundamentally additional computation, or merely an efficient primitive for interpreting information that could otherwise reside in state?

