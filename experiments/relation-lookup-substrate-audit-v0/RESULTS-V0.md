# Relation-Lookup Substrate Audit v0

**Status:** EXPERIMENTALLY_SUPPORTED / LOCAL REPLAY / CONCEPTUAL AUDIT  
**Branch:** `research/evidence-disposition-v0`  
**Code commit:** `1127fa60e60c001a2a755d7f1b35dc0730d5cc59`

## Question

Is `relation_lookup(state, key)` itself a new computational primitive, or can it be ordinary computation over state data under the existing fixed substrate?

## Three substrate contracts

### S0 — opaque state

The transition mechanism cannot inspect an arbitrary relation stored in state.

Under S0, adding relation lookup necessarily adds a new state-access/transition capability.

### S1 — generic readable state

The fixed substrate already provides:

- access to stored state entries;
- equality on keys;
- branching/control;
- repeated transition execution.

Under S1, a finite relation

```text
[(k1,v1), ..., (kn,vn)]
```

can be searched by ordinary computation:

```text
lookup(R,k):
    for (ki,vi) in R:
        if ki == k:
            return vi
    return miss
```

No new transition topology is required.

### S2 — direct indexed relation access

The fixed substrate additionally provides an indexed relation lookup primitive.

This is not semantically necessary for S1 derivability; it is an efficiency primitive.

## Local closure check

The executable audit compared:

- derived scan lookup over ordinary state pairs;
- direct indexed lookup.

For five entries:

```text
semantic_equivalence = True
derived ticks = 15
direct ticks  = 5
```

Thus the two implementations have the same observed semantics while having different costs.

This is intentionally a minimal demonstration, not evidence that the Machine repository's current concrete substrate already satisfies S1.

## Conceptual conclusion

The correct classification is conditional:

> `relation_lookup` is not intrinsically a new computational capability.

If generic state inspection, comparison, and control are already part of the fixed substrate, relation lookup can be represented as ordinary data-processing code. A direct lookup primitive can still be a major resource optimization and can create a better Pareto point, without changing the set of computable relations.

Conversely, if the fixed substrate does not expose generic state inspection, then adding relation lookup changes the substrate contract and must be counted as a new primitive.

Therefore the question cannot be decided from the name "lookup"; it must be decided from the exact primitive contract of the substrate.

## Reference-backed justification

The conceptual result is consistent with the universal-machine/program-as-data tradition:

1. Turing's universal machine can be given a finite description of another machine and simulate that machine using the same universal mechanism. The program description is therefore manipulable as data by the fixed machine. urlTuring, On Computable Numbers (Oxford Academic)https://academic.oup.com/plms/article-abstract/s2-42/1/230/1491926
2. The Stanford Encyclopedia of Philosophy describes the universal-machine construction as interpreting a program description and notes that program and machine behavior can be represented and manipulated on the same tape. urlStanford Encyclopedia: Turing Machineshttps://plato.stanford.edu/entries/turing-machine/
3. The stored-program tradition likewise makes it possible for instructions and ordinary data to occupy the same memory system, supporting the distinction between what is represented in state and what a fixed execution substrate can do with that representation. urlComputer History Museum: John von Neumannhttps://history.computer.org/pioneers/von-neumann.html
4. Universal-machine equivalence does not imply equal resource cost: the Stanford Encyclopedia explicitly notes that a universal simulator may execute many more transitions than the simulated machine. This directly supports separating capability/behavioral equivalence from the resource Pareto frontier. urlStanford Encyclopedia: Computability and Complexityhttps://plato.stanford.edu/archives/fall2020/entries/computability/

## Relation to the current Machine model

The current abstract model defines:

```text
State
Operation
Transition
Control / scheduling
```

and deliberately does not define a universal indexed-state lookup primitive.

Therefore the repository does **not** currently justify saying that generic `relation_lookup` is already part of the fixed substrate.

The correct repository disposition is:

```text
relation_lookup = UNDER-SPECIFIED
```

not:

```text
relation_lookup = definitely new primitive
```

and not:

```text
relation_lookup = definitely already available
```

## Decisive formal requirement

Before interpreting any future frontier shift as mechanism-specific, the substrate specification must state whether the following are fixed primitives:

```text
read_state(address/key)
compare(a,b)
branch(condition)
iterate(container)
construct/access relation entries
```

If all are fixed, then a generic finite relation interpreter is derivable.

If they are not, the missing operation must be charged explicitly as substrate capability.

## Research consequence

The next comparison should therefore fix one of two explicit contracts:

### Contract A — generic readable state

Give both systems the same generic state-reading substrate.

Then compare:

```text
derived relation traversal
vs
direct indexed relation primitive
```

The expected distinction is resource cost, not ultimate capability.

### Contract B — opaque state

Disallow generic relation access.

Then adding direct relation traversal is genuinely a new substrate capability and should be evaluated as such.

The previous mechanism-frontier experiments mixed these contracts implicitly. This audit removes that ambiguity.

