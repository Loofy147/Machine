# Current Frontier Reconciliation v0.1

**Recorded:** 2026-09-19
**Repository:** `Loofy147/Machine`
**Purpose:** durable research-state record for the current capability/allocation frontier and the results that must not be reconstructed from conversation context.

## 1. Current repository research state

Relevant branches remain:

- `main` = integration authority at `1626bac2f5c478294afa4b9463f694608c322117`
- `research/machine-native-primitives-v0` = broad machine-model research
- `research/target-oblivious-frontier-v0` = resource/placement frontier
- `research/confirmatory-freeze-order-v0.1` = confirmatory protocol/freeze
- `research/evidence-disposition-v0` = current evidence/provenance consolidation
- stale branches `research/definition`, `research/machine-native-primitives`, `research/machine-native-primitives-v0-docs`, `research/machine-native-primitives-v0-issue`, `research/test-write` remain ARCHIVE CANDIDATES.

The evidence branch's older commit-count statement in the canonicalization document is stale; current direct repository comparisons remain authoritative.

## 2. Existing scientific results

### Nine-mechanism line

The repository does not justify nine flat primitives. Variation, invocation gating, composition, and reformation have bounded empirical effects; representation, transformation, and control remain structural scaffolds rather than proven irreducible primitives.

### B-clean

Mutable executable representation is a substrate capability, not evidence by itself of adaptive advantage. Search dynamics dominated the tested bounded hypothesis family.

### Contextual credit

Context-indexed history can improve behavior when operator value crosses between supplied contexts. Context discovery remains OPEN.

### Online reflection

Continuous hot-swap and history-dependent proposals are demonstrated within their declared boundaries. Causal reification of the live transition/evaluator machinery remains OPEN.

### Target-oblivious frontier

Under a freeze-before-target-reveal protocol, partial target-specific state that cannot contain the realized target does not alter strict-heldout behavior. Full target-oblivious precomputation can move computation offline in the finite graph fixture.

Interpretation remains resource placement, not proof that reflection is necessary.

## 3. Insufficiency detector

The adversarial detector is packaged in:

`experiments/frontier-insufficiency-adversarial-v0/`

Its third verdict is:

`INCONCLUSIVE_AT_RESOLUTION(delta)`

Persistent nonzero residual is not treated as a proof of expressive insufficiency. Selected negative conclusions are accepted only when an independent regularity certificate supports them.

This package is locally replayed but not yet CI-integrated.

## 4. Mechanism frontier line

### 4.1 Native transition-access result

With:

```text
B_off = 0
R = 0
same instance family
same correctness criterion
same online tick accounting
```

forward BFS + visited set was compared with bidirectional BFS with direct predecessor access.

The result is a measured resource-bounded feasible-set/Pareto-frontier shift: direct predecessor access solves additional sampled instances at tight `B_on`.

### 4.2 Successor-only emulation control

The predecessor relation was then emulated with only the original successor operations by exhaustive online scanning, with every tested edge charged to `B_on`.

That emulation does not reproduce the native frontier at the tight budgets tested.

This supports a narrower interpretation:

> direct predecessor access is a distinct resource under this contract because obtaining equivalent information through the tested successor-only substrate costs substantially more online computation.

It does not prove different ultimate computational power.

## 5. New representation control

The next test kept the transition topology fixed and changed only the frozen representation.

A target-oblivious macro representation was built for 2, 3, or 4 successive successor steps. The online executor remained the same successor-only forward BFS; the macro construction cost was charged to `B_off`, and stored macro endpoints were counted as `R`.

Three independent query seeds were used:

```text
17, 23, 41
```

80 queries per seed and caps:

```text
10, 20, 40, 80, 160, 320, 640
```

Graph families:

```text
affine_mix: M = 30, 300, 3000
perm_mix:   M = 31
opaque_mix: M = 31
```

### Observations

For affine M=30 at `B_on=40`:

```text
forward  = 83.33%
native   = 100.00%
macro4   = 96.67%
```

For affine M=300 at `B_on=160`:

```text
forward  = 35.00%
native   = 97.50%
macro4   = 41.25%
```

For affine M=3000 at `B_on=640`:

```text
forward  = 12.08%
native   = 83.75%
macro4   = 10.83%
```

For perm M=31 at `B_on=40`:

```text
forward  = 83.75%
native   = 100.00%
macro4   = 90.83%
```

For opaque M=31 at `B_on=40` there is deliberately no native reverse score, because no inverse transition mechanism is supplied:

```text
forward  = 82.92%
macro4   = 92.50%
```

Thus the representation itself can shift the frontier without mechanism change, but the tested macro family does not generally close the native predecessor frontier at larger M.

### Resource cost

The macro4 representation costs:

- affine M=30: 2,568 offline successor evaluations / 844 stored endpoints;
- affine M=300: 29,298 / 15,092;
- affine M=3000: 296,598 / 158,192;
- perm M=31: 2,544 / 820;
- opaque M=31: 2,667 / 857.

Therefore equal `B_on` does not imply equal total resource usage.

The relevant state is now:

```text
(B_off, R, B_on)
```

not `B_on` alone.

## 6. Current interpretation after the representation control

The evidence now rules out two premature conclusions.

### Not established

> "The native bidirectional frontier shift proves mechanism change creates a new absolute computational capability."

We do not have that.

### Also not established

> "Any mechanism-induced frontier shift can be reproduced by state representation."

The tested macro family does not reproduce the native frontier at larger M.

### What is established within scope

1. Direct predecessor access causes a measurable resource-bounded frontier shift in the declared graph family.
2. Successor-only exhaustive emulation cannot reproduce that shift at the tested tight budgets.
3. Fixed successor execution with richer target-oblivious representation can itself shift the frontier.
4. The amount recoverable by the tested representation depends strongly on graph scale and representation budget.
5. Therefore the causal question cannot be answered from `B_on` alone.

## 7. Current frontier

The frontier is now explicitly a multi-resource question:

> Under a fixed instance family and correctness requirement, what Pareto frontier is achievable over offline computation `B_off`, persistent representation size `R`, and post-instance computation `B_on`?

Then, and only then:

> Does changing transition access produce a Pareto frontier point that the best available fixed-substrate representation cannot reproduce under the same resource contract?

This is stronger than asking whether one mechanism "beats" another.

## 8. Immediate next discriminating experiment

The next experiment should not add another named algorithm.

It should search the representation family and produce explicit Pareto fronts:

```text
forward baseline:
    (B_off=0, R=0, B_on)

representation family:
    macro2
    macro3
    macro4
    compact abstractions
    target-oblivious distance summaries
    other reusable subplans

transition-access family:
    direct predecessor
    successor-only equivalents

compare:
    same correctness
    same information timing
    same total/individual resource accounting
```

The decisive result would be a frontier point where:

```text
transition-access variant is feasible
AND
all tested fixed-substrate representations are infeasible
under the same (B_off, R, B_on) contract.
```

That would be substantially stronger evidence for a mechanism-specific capability boundary.

## 9. Repository samples now recorded

Representative query-level samples are committed at:

`experiments/mechanism-frontier-shift-v0/samples-v0/REPRESENTATIVE-SAMPLES-V0.csv`

The deterministic rerun script is:

`experiments/mechanism-frontier-shift-v0/samples-v0/run.py`

Resource metadata:

`experiments/mechanism-frontier-shift-v0/samples-v0/REPRESENTATION-METADATA-V0.json`

Results:

`experiments/mechanism-frontier-shift-v0/samples-v0/RESULTS-REPRESENTATION-CONTROL-V0.md`

The larger local raw export is retained separately and is not yet treated as repository evidence in full.

## 10. Governing interpretation rules

Do not treat computation relocation as computation elimination.

Do not treat algorithm-name changes as capability changes.

Do not treat a plateau as proof of expressive insufficiency without the assumptions needed to exclude unseen solutions.

Do not treat a mechanism-induced shift at fixed `B_on` as proof of absolute computational-power separation.

Do not compare architectures without recording `B_off`, `R`, `B_on`, information timing, correctness, and what computation is embedded in the mechanism.

Do not promote conversation results to repository evidence without executable provenance and replay.
