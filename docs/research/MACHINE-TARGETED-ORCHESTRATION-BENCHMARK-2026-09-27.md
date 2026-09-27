# Machine-Targeted Orchestration Benchmark — 2026-09-27

Run ID: `MACHINE-ORCH-2026-09-27-001`

## Target identity

Repository: `Loofy147/Machine`
Default branch: `main@1626bac2f5c478294afa4b9463f694608c322117`
Primary integrated research branch: `research/evidence-disposition-v0@137f76bc7fb56138a40b3bc98ed2a3291fe7acf5`
Experimental CEK branch: `research/substrate-interpreter-v0@d935495355ac6b827a17d6147d7f38fbcaaeb15f`
Concrete Machine Substrate branch discovered during continuation: `research/bidirectional-substrate-v3@59fab62704875193801db77c7cb8361475297f48`

## Purpose

Test whether orchestration can correctly select, reconcile, and verify the next discriminating Machine research action without collapsing branch identity, specification, implementation, execution, or evidence status.

## Executed orchestration trace

DISCOVER → BRANCH-RECONCILE → EVIDENCE-SELECT → OPEN-GAP-DETECT → CI-VERIFY → SUBSTRATE-SEARCH → CONTRACT-CROSSWALK → CORRECTION → NEXT-ACTION

## Initial finding

The first pass correctly detected that `research/substrate-interpreter-v0` contains an explicit CEK-style experimental S1/S2 interpreter and that this result must not automatically become the canonical Machine interpreter.

However, that was initially stated too broadly as absence of a concrete Machine substrate.

## Correction discovered during continued orchestration

A complete branch/source inventory found:

`research/bidirectional-substrate-v3@59fab62704875193801db77c7cb8361475297f48`

with:

- `docs/research/MACHINE-SUBSTRATE-SPEC-REV2.1.md`
- `experiments/bidirectional-substrate-v3/substrate_lib.py`
- `experiments/bidirectional-substrate-v3/substrate_bench.c`
- `experiments/bidirectional-substrate-v3/test_correctness.py`
- `.github/workflows/bidirectional-substrate-v3-conformance.yml`

The Rev 2.1 specification explicitly defines:

`M = (S, Sigma, delta, R, C)`

with persistent inverse relation representation `R^-1`, including the labeled predecessor fiber `F(u)`.

It specifies:

- P-04: build `R^-1` in `Theta(n+E)` offline work;
- P-05: fiber lookup in `O(1)` entry time plus `O(deg^-(u))` iteration;
- P-06: forward `delta(s,a)` evaluation in `O(1)`;
- P-08: optional per-action fibers.

The source implementation describes itself as the reference implementation of the Machine Substrate contract.

Therefore the earlier statement:

> "no concrete Machine substrate exists"

was too broad and has been retired.

The defensible statement is narrower:

> No canonical CEK/object-language interpreter corresponding to the experimental S1/S2 interpreter was identified. A separate concrete Machine Substrate Rev 2.1 reference implementation does exist on `research/bidirectional-substrate-v3`, but its canonical architectural status relative to the abstract Machine model remains to be reconciled.

## CI verification

The Rev 2.1 branch exposes a dedicated conformance workflow:

`.github/workflows/bidirectional-substrate-v3-conformance.yml`

The latest observed successful run:

- run ID: `35585026821`
- run number: 10
- head: `59fab62704875193801db77c7cb8361475297f48`
- conclusion: success

The workflow performs syntax/smoke validation, artifact validation, deterministic generation of regression inputs, and the full v3 regression verifier.

## Contract crosswalk

The important result is that the CEK S1/S2 experiment and Machine Substrate Rev 2.1 are not the same contract.

### Experimental CEK line

S1:
generic readable state + comparison + branching + iteration.

S2:
S1 + direct relation lookup.

Measured finite resource comparison:
- S1: `(B_off,R,B_on,C_access)=(5,5,676,291)`
- S2: `(5,5,20,10)`

### Machine Substrate Rev 2.1

The substrate itself stores:

`delta-table + R^-1`

with an explicit offline build cost and online fiber-access contract.

This means predecessor access is already represented as an explicit substrate/resource contract in Rev 2.1. It should not be compared to the CEK S2 primitive without first aligning:

- information availability;
- persistent representation;
- preprocessing timing;
- access semantics;
- access cost;
- update semantics;
- correctness domain.

## Current research disposition

| Question | Status |
|---|---|
| Experimental CEK S1 derivability | EXPERIMENTALLY_SUPPORTED |
| Experimental CEK S2 finite resource advantage | EXPERIMENTALLY_SUPPORTED |
| Concrete Machine Substrate Rev 2.1 exists | ESTABLISHED BY SOURCE INSPECTION |
| Rev 2.1 substrate correctness/regression workflow passes | EXPERIMENTALLY_SUPPORTED / CI |
| Rev 2.1 = canonical architecture of Machine | OPEN |
| CEK S1/S2 result directly classifies Rev 2.1 | CONTRADICTED BY CONTRACT MISMATCH |
| Predecessor access can be treated as a resource/representation choice under Rev 2.1 | INFERENCE, strongly supported by the explicit `R^-1` contract |
| General computational-power separation | OPEN / NOT SUPPORTED |

## Orchestrator finding

The most important benchmark result is the correction itself.

The orchestrator did not stop at the first apparently coherent answer. A broader branch/source search invalidated an over-broad intermediate conclusion and replaced it with a more precise branch-specific statement.

This is the desired failure mode:

`candidate absence -> broader search -> contradictory evidence -> claim narrowing`

rather than:

`candidate absence -> premature closure`.

## Next discriminating action

Do not build another generic CEK interpreter yet.

Instead reconcile:

1. abstract Machine model;
2. Machine Substrate Rev 2.1;
3. bidirectional frontier experiments;
4. the later S1/S2 relation-lookup experiments.

Construct a contract matrix covering:

`Information, Representation, Timing, Access, Cost, Mutation, Correctness`

Then determine whether the existing Rev 2.1 `R^-1` substrate already subsumes the measured predecessor-frontier effect as a representation/resource choice.

Only after this crosswalk should a new substrate primitive be proposed.

## Epistemic disposition

The benchmark yields no new universal Machine capability claim.

It yields a stronger procedural result:

> Machine research orchestration can detect and repair a provenance-level false generalization when additional branch evidence contradicts the first framing, while preserving exact branch/commit identity and evidence status.

Report artifact SHA-256 from the initial generated artifact:
`2e146ea7d4f32a35b9e690b3530288ed552e70f9a19757e1096dce1b58650b27`
