# Current Frontier Reconciliation v0.1

**Recorded:** 2026-09-19
**Repository:** `Loofy147/Machine`
**Purpose:** durable research-state record for the capability/allocation frontier.

## 1. Current research state

- `main` = integration authority.
- `research/machine-native-primitives-v0` = broad machine-model research.
- `research/target-oblivious-frontier-v0` = resource/placement frontier.
- `research/confirmatory-freeze-order-v0.1` = confirmatory protocol/freeze.
- `research/evidence-disposition-v0` = current evidence/provenance consolidation.
- stale historical branches remain ARCHIVE CANDIDATES.

## 2. Established lines

The repository-backed research still supports the following bounded findings:

- the nine-mechanism result does not justify nine flat primitives;
- mutable executable representation is a substrate capability, not adaptive advantage by itself;
- contextual credit helps under supplied context labels;
- online executable hot-swap is supported, but causal evaluator reflection remains OPEN;
- target-oblivious precomputation relocates computation under a strict freeze-before-target-reveal protocol;
- finite black-box plateau is insufficient for a global expressive-insufficiency claim without additional assumptions.

## 3. Mechanism frontier result

Under:

```text
B_off = 0
R = 0
same instance family
same correctness criterion
same online tick accounting
```

direct predecessor access + bidirectional search shifts the sampled online feasible frontier relative to successor-only forward BFS.

Successor-only exhaustive inverse emulation does not reproduce that frontier at the tight budgets tested.

This is a resource-bounded frontier result, not an ultimate computability separation.

## 4. Representation closure result

A target-oblivious reverse adjacency index reproduces the native bidirectional online success pattern and minimum online budgets exactly in the tested finite arithmetic graph.

Its price is:

```text
B_off = 3M
R = 3M
```

An all-pairs target-oblivious policy table reduces maximum sampled `B_on` further, but costs approximately:

```text
B_off = Θ(M^2)
R = Θ(M^2)
```

This demonstrates a real three-resource frontier:

```text
(B_off, R, B_on)
```

## 5. Relation-lookup substrate audit

A separate conceptual and executable audit now isolates the remaining boundary.

### S0 — opaque state

If the substrate cannot generically inspect arbitrary stored relations, then adding relation traversal changes the substrate contract and is a new capability.

### S1 — generic readable state

If the substrate already provides:

```text
state read
key comparison
branching
iteration
```

then finite relation lookup is ordinary computation over state data.

### S2 — direct indexed access

An indexed lookup primitive can reduce cost even when S1 already permits the same lookup semantically.

The local audit demonstrated:

```text
derived scan:
  same semantics
  15 abstract ticks for five keys

direct indexed lookup:
  same semantics
  5 abstract ticks
```

Thus direct lookup can be a resource primitive without being a new computability primitive.

## 6. Reference-backed conceptual conclusion

The distinction is consistent with the program-as-data / universal-machine tradition.

Turing's universal-machine construction represents the description of another machine as data and uses a fixed machine to interpret that description. The Stanford Encyclopedia explicitly describes the program and behavior of a machine as being represented and manipulated on the same tape. urlTuring, On Computable Numbershttps://academic.oup.com/plms/article-abstract/s2-42/1/230/1491926 urlStanford Encyclopedia: Turing Machineshttps://plato.stanford.edu/entries/turing-machine/

Stored-program architecture likewise places program instructions and data in the same memory system, making the distinction a matter of representation and interpretation rather than a universal boundary between two physical kinds of memory. urlComputer History Museum: John von Neumannhttps://history.computer.org/pioneers/von-neumann.html

Critically, semantic/computational equivalence does not imply equal resource cost. The computability literature explicitly notes that a universal simulator can require many more transitions than the simulated machine. urlStanford Encyclopedia: Computability and Complexityhttps://plato.stanford.edu/archives/fall2020/entries/computability/

## 7. Final conceptual disposition

The correct statement is now:

> `relation_lookup` is not intrinsically a new computational capability. Its status depends on the fixed substrate contract.

If generic state-readable computation is already part of the substrate, direct relation lookup is primarily an optimization/resource primitive.

If generic relation access is absent, adding it changes the substrate.

Therefore the unresolved question is no longer:

> Is mechanism change more powerful than state mutation?

It is:

> Which state-access and relation-interpretation operations are already included in the fixed substrate, and which would constitute an actual addition to it?

## 8. Specification debt identified

The current abstract Machine model defines State, Operation, Transition, and Control, but it deliberately does not specify a concrete generic state-access algebra.

Therefore:

```text
relation_lookup = UNDER-SPECIFIED
```

not proven primitive, and not proven already available.

This is now explicit specification debt.

## 9. Next decisive action

Specify the minimal concrete state-access contract of the current interpreter core:

```text
read_state(key)
compare(a,b)
branch(c)
iterate(container)
construct/read relation entry
```

Then implement two versions:

1. relation traversal derived entirely from the fixed substrate;
2. direct relation lookup as an added primitive.

Measure both semantics and the complete:

```text
(B_off, R, B_on)
```

frontier.

Only after that comparison should a relation-access mechanism be classified as a genuine substrate extension.

## 10. Provenance status

Repository-backed:

- adversarial insufficiency detector;
- mechanism frontier baseline/emulation;
- macro representation controls;
- reverse-index representation closure;
- all-pairs policy closure;
- query-level samples and resource metadata;
- relation-lookup substrate audit;
- current claim registries.

Still CONVERSATION-ONLY:

- earlier h-allocation sweep;
- memoized-lookahead ~19.3% reduction;
- workload crossover near N=40/62;
- original policy-table numerical run before repository packaging.

Those remain excluded from scientific evidence until separately packaged.

## 11. Governing rule

Measure the Pareto frontier first.

Then identify which information-access or substrate boundary caused the shift.

Do not infer capability hierarchy from mechanism names.
