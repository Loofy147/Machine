# Machine Substrate Contract Crosswalk v0.1

Recorded: 2026-09-27
Repository: `Loofy147/Machine`
Branch: `research/orchestration-benchmark-2026-09-27`

## Objective

Reconcile the experimental CEK S1/S2 relation-lookup line with the concrete Machine Substrate Rev 2.1 line before making any primitive/frontier classification.

Sources under comparison:

| Surface | Provenance |
|---|---|
| Abstract Machine model | `research/machine-native-primitives-v0@f752aac015d9f837bc6a89d44eed50e0325b60a6` |
| Concrete Machine Substrate Rev 2.1 | `research/bidirectional-substrate-v3@59fab62704875193801db77c7cb8361475297f48` |
| Experimental CEK S1/S2 | `research/substrate-interpreter-v0@d935495355ac6b827a17d6147d7f38fbcaaeb15f` |
| Integrated frontier disposition | `research/evidence-disposition-v0@137f76bc7fb56138a40b3bc98ed2a3291fe7acf5` |

## Seven-axis contract matrix

| Axis | Experimental CEK S1/S2 | Machine Substrate Rev 2.1 | Reconciliation |
|---|---|---|---|
| Information | relation entries supplied as persistent state | `delta` table is the source transition relation | same underlying information can be represented, but the declared information boundary differs |
| Representation | same host Mapping supplied to S1/S2 | `delta` + explicit inverse CSR fibers `R^-1` | not representation-equivalent yet |
| Timing | S2 receives pre-indexed relation; CEK experiment charges construction separately | inverse index is explicitly built offline under P-04 | both permit preprocessing, but the accounting contract must be normalized |
| Access | S1 scans object-language relation; S2 performs direct lookup | P-05 fiber slice access is native to the declared substrate | direct access is already a declared substrate operation in Rev 2.1 |
| Cost | abstract transition/access ticks | word-RAM plus measured Python/C timings; explicit `Theta(n+E)` build | cost models are not directly interchangeable |
| Mutation | experimental relation fixture is effectively static | static CSR with P-07 dynamic-update alternatives | dynamic closure requires its own matched contract |
| Correctness | semantic equality of lookup results | C1–C7 substrate invariants/algorithmic checks | both are semantically audited, but at different abstraction levels |

## Key reconciliation

The Rev 2.1 contract already exposes predecessor information through:

```text
delta
  -> offline inverse construction R^-1
  -> fiber lookup F(u)
  -> online predecessor iteration
```

and explicitly charges construction and storage.

Therefore the earlier CEK S2 experiment should not be interpreted as evidence that Machine "discovers" an entirely new relation capability merely by adding a direct lookup primitive.

The stronger and more precise interpretation is:

> Under a contract that permits target-oblivious inverse representation, predecessor access can be supplied by representation plus a native access contract, relocating work from repeated online discovery to offline construction and persistent storage.

That is already encoded operationally in Rev 2.1 as P-04/P-05.

## What remains genuinely open

The crosswalk does **not** prove that the Rev 2.1 substrate is merely an optimization of the abstract Machine model.

Three boundaries remain:

### Boundary A — substrate semantics

Does the abstract Machine model permit persistent derived relations such as `R^-1` as ordinary machine state without adding a new primitive?

### Boundary B — access semantics

If `R^-1` is present as stored data, what fixed operation allows the machine to retrieve a fiber slice? In Rev 2.1 this is P-05. The abstract model currently does not prescribe the equivalent primitive set.

### Boundary C — resource frontier

Even when `R^-1` is derivable from `delta`, its construction and storage can create a materially better Pareto point under a fixed online budget.

Thus "derivable" and "free" must remain separate.

## Evidence already sufficient for a bounded statement

The Rev 2.1 source and CI establish, for that branch-specific contract:

- inverse-fiber construction is executable and tested;
- fibers match brute-force predecessor enumeration on randomized systems;
- backward reachability using fibers matches reference fixpoints;
- the implementation provides a substantial measured online work advantage over repeated predecessor scans on the tested workloads.

The latest observed conformance workflow run was:

`35585026821` at `59fab62704875193801db77c7cb8361475297f48`, conclusion `success`.

These statements remain branch-scoped. They do not imply that the Rev 2.1 implementation is merged into `main`.

## Decision

Current classification of predecessor access in Machine:

```
NOT:
"new computational power"                  [unsupported]

NOT:
"merely free ordinary computation"         [unsupported]

YES:
"explicit substrate/resource contract with
 target-oblivious inverse representation"  [established for Rev 2.1]

OPEN:
whether the same contract is derivable from
 the abstract Machine substrate primitives
without changing the admissible task/resource set
```

## Decisive next experiment

A clean test should compare two implementations under a single frozen Machine contract:

### Control

Only the abstractly admitted state/transition primitives.

If inverse fibers are allowed to be stored as ordinary state, derive predecessor enumeration from that state using only the admitted access operations.

### Treatment

Use the Rev 2.1 P-05 fiber access path.

### Hold fixed

- exact `delta`;
- exact target queries;
- target-reveal timing;
- persistent information budget;
- offline construction budget;
- representation bytes;
- correctness semantics.

### Measure

`(B_off,R,B_on,C_access)`

and the full feasible-set frontier.

### Decision rule

- same admissible information/representation + lower cost → resource primitive/optimization;
- additional access capability required → substrate extension;
- same semantics but different feasible set under fixed resource limits → resource-bounded frontier shift;
- unmatched contracts → INCONCLUSIVE / CONTRACT MISMATCH.

## Important consequence for the reflective line

This crosswalk strengthens the existing decision not to broaden reflection yet.

The immediate Machine frontier is not "add another primitive".

It is:

```
abstract model
   -> concrete substrate contract
   -> representation/access normalization
   -> frontier comparison
   -> only then primitive/reflection expansion
```

The reflective research line remains separately gated by the narrow `rho_dispatch` causal-reflection minimal pair.
