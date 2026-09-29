# Canonical Machine Substrate Gate v0.2

Recorded: 2026-09-27
Repository: `Loofy147/Machine`
Branch: `research/orchestration-benchmark-2026-09-27`
Parent research state: `research/evidence-disposition-v0@137f76bc7fb56138a40b3bc98ed2a3291fe7acf5`

## Purpose

Close the provenance and contract gap around the phrase "canonical Machine substrate".

The benchmark initially found no canonical CEK interpreter. Continued branch/source inspection then found a separate concrete Machine Substrate Rev 2.1 reference implementation. This revision records that correction and narrows the remaining question.

## Repository state

### Abstract Machine model

`research/machine-native-primitives-v0@f752aac015d9f837bc6a89d44eed50e0325b60a6`

`docs/ABSTRACT-MACHINE.md` defines:

`S` = operational state,
`O` = executable operation,
`T(S,O,input) -> (S',result)`,
and a control/scheduling relation.

The document deliberately leaves the concrete storage and interpreter substrate open.

### Concrete Machine Substrate Rev 2.1

`research/bidirectional-substrate-v3@59fab62704875193801db77c7cb8361475297f48`

Relevant authoritative branch-local artifacts:

- `docs/research/MACHINE-SUBSTRATE-SPEC-REV2.1.md`
- `experiments/bidirectional-substrate-v3/substrate_lib.py`
- `experiments/bidirectional-substrate-v3/substrate_bench.c`
- `experiments/bidirectional-substrate-v3/test_correctness.py`
- `.github/workflows/bidirectional-substrate-v3-conformance.yml`

The specification explicitly defines:

`M = (S, Sigma, delta, R, C)`

with:

- dense finite states;
- partial deterministic transition function `delta`;
- stored forward transition table;
- stored inverse relation `R^-1`;
- labeled predecessor fibers `F(u)`;
- explicit resource contracts P-01..P-09.

The inverse index is constructed offline and then queried online. P-04 charges `Theta(n+E)` construction; P-05 exposes fiber lookup at `O(1)` entry plus output-sensitive iteration.

### CI evidence

Latest observed successful Rev 2.1 branch workflow:

- workflow: `Bidirectional Substrate v3 Conformance`
- run ID: `35585026821`
- run number: 10
- head: `59fab62704875193801db77c7cb8361475297f48`
- conclusion: success

The workflow performs source syntax/smoke validation, committed artifact validation, deterministic regression-input generation, and full regression verification.

### Experimental CEK interpreter

`research/substrate-interpreter-v0@d935495355ac6b827a17d6147d7f38fbcaaeb15f`

Contains:

`experiments/substrate-interpreter-v0/machine.py`

This is a CEK-style experimental interpreter used for the S1/S2 relation-lookup target. Its results remain valid evidence about that implementation and contract.

## Corrected classification

| Question | Status |
|---|---|
| Abstract Machine execution semantics defined | ESTABLISHED |
| Concrete Machine Substrate Rev 2.1 exists | ESTABLISHED BY SOURCE INSPECTION |
| Rev 2.1 implementation has CI conformance evidence | EXPERIMENTALLY_SUPPORTED |
| Rev 2.1 is explicitly called a reference implementation of the substrate contract | ESTABLISHED BY SOURCE INSPECTION |
| Rev 2.1 is merged/canonical on `main` | OPEN / NOT ESTABLISHED |
| A canonical CEK/object-language interpreter exists on `main` | OPEN / NOT ESTABLISHED |
| CEK S1/S2 experiment directly classifies Rev 2.1 | CONTRADICTED BY CONTRACT MISMATCH |
| Rev 2.1 predecessor access is part of its explicit resource/substrate contract | ESTABLISHED BY SOURCE INSPECTION |
| Whether Rev 2.1's `R^-1` is better described as representation, native substrate capability, or both under the abstract Machine model | OPEN / CONTRACT-CROSSWALK |
| General computational-power separation | OPEN / NOT SUPPORTED |

## Contract mismatch

The CEK S1/S2 experiment and Rev 2.1 are not interchangeable.

CEK experiment:

`S1 = generic readable state`
versus
`S2 = S1 + direct indexed relation lookup`

Rev 2.1:

`M = (S,Sigma,delta,R,C)`
with `R^-1` itself included in the substrate's declared representation/resource contract.

Therefore the measured CEK S1/S2 delta cannot be imported as a classification of Rev 2.1 without first equalizing:

- information source;
- representation;
- timing;
- access semantics;
- construction cost;
- query cost;
- dynamic update model;
- correctness contract.

## Decisive crosswalk

The next artifact should map both systems into:

`Information | Representation | Timing | Access | Cost | Mutation | Correctness`

Then evaluate:

### Case A

The inverse relation is merely a representation derivable under the fixed Machine substrate.

Disposition:
resource placement / optimization.

### Case B

The abstract Machine substrate excludes the access needed to exploit the stored inverse relation.

Disposition:
substrate capability expansion.

### Case C

The inverse relation is admissible, but its construction/storage/access cost creates a distinct Pareto point.

Disposition:
resource-bounded frontier shift.

### Case D

Different contracts are being compared.

Disposition:
INCONCLUSIVE / CONTRACT MISMATCH until normalized.

## Gate

No new primitive or computational-power claim should be promoted until the crosswalk is complete.

The immediate target is contract reconciliation, not further substrate expansion.
