# Representation Control v0 — Mechanism Frontier Follow-up

**Status:** EXPERIMENTALLY_SUPPORTED / LOCAL REPLAY / NOT YET CI-VERIFIED  
**Branch:** `research/evidence-disposition-v0`

## Purpose

Test whether part of the resource-bounded frontier shift attributed to direct predecessor access can be recovered without changing the transition topology, by moving computation into a target-oblivious representation while keeping the online executor successor-only.

This is a representation/allocation control, not a mechanism-change experiment.

## Contract

Across all configurations:

- same instance family and correctness criterion;
- 3 independent query seeds: 17, 23, 41;
- 80 queries per seed;
- 240 query observations per graph/cap aggregate;
- online cap `B_on ∈ {10,20,40,80,160,320,640}`;
- primary online tick: one successor-edge or precomputed-macro-edge examination;
- no target is seen while macro representations are built.

### Modes

1. **forward** — successor-only BFS + visited set, `B_off=0, R=0`.
2. **native_bidi** — direct predecessor access + bidirectional BFS. Available only where the graph family has an explicitly declared inverse relation.
3. **macro2/3/4** — unchanged forward successor executor using a frozen target-oblivious k-step successor representation. All construction work is charged to `B_off`; stored macro endpoints are charged to `R`.

The macro representation does not know the future target.

## Representative aggregate observations

### affine_mix, M=30

At `B_on=40`:

- forward: 83.33%
- native bidi: 100.00%
- macro2: 85.00%
- macro3: 82.08%
- macro4: 96.67%

At `B_on=80`:

- forward: 100.00%
- native bidi: 100.00%
- macro4: 99.58%

Macro4 therefore recovers most of the native frontier at this small M, but only after substantial offline representation cost:

- offline ticks = 2,568
- stored macro endpoints = 844.

### affine_mix, M=300

At `B_on=160`:

- forward: 35.00%
- native bidi: 97.50%
- macro2: 36.25%
- macro3: 33.33%
- macro4: 41.25%

At `B_on=640`:

- forward: 91.67%
- native bidi: 100.00%
- macro2: 77.92%
- macro3: 74.17%
- macro4: 79.58%

Offline cost for macro4:

- 29,298 successor evaluations
- 15,092 stored macro endpoints.

Here richer successor-only representation did **not** recover the native frontier under the same online cap.

### affine_mix, M=3000

At `B_on=640`:

- forward: 12.08%
- native bidi: 83.75%
- macro2: 10.42%
- macro3: 10.42%
- macro4: 10.83%

Macro4 requires:

- 296,598 offline successor evaluations
- 158,192 stored endpoints.

The tested fixed-substrate macro representation therefore leaves a very large frontier gap at this scale.

### perm_mix, M=31

At `B_on=40`:

- forward: 83.75%
- native bidi: 100.00%
- macro2: 76.25%
- macro3: 80.42%
- macro4: 90.83%.

At `B_on=80`:

- forward: 100.00%
- native bidi: 100.00%
- macro4: 100.00%.

Macro4 offline cost = 2,544 evaluations; stored endpoints = 820.

### opaque_mix, M=31

No native predecessor mechanism is declared for this family, so no native-bidirectional score is reported.

At `B_on=40`:

- forward: 82.92%
- macro2: 80.83%
- macro3: 87.50%
- macro4: 92.50%.

At `B_on=80`:

- forward: 100.00%
- macro4: 100.00%.

This is a pure representation-control result.

## Interpretation

The experiment materially changes the previous interpretation.

A richer target-oblivious representation can itself shift the online frontier without changing the successor-only transition topology. Therefore an observed frontier shift cannot be attributed to mechanism change unless representation/allocation alternatives are tested under matched resource accounting.

At the same time, the tested macro family does not close the native predecessor frontier at larger M. In particular, for affine M=3000 at `B_on=640`, native bidirectional solves 83.75% of the sampled queries while macro4 solves only 10.83%.

The correct current conclusion is therefore neither:

> predecessor access is definitely a new computational capability

nor:

> representation can always reproduce the same frontier.

The evidence currently says:

> representation can reproduce part of the frontier shift, sometimes almost all of it on small instances, but the tested representation family leaves a substantial residual gap at larger scales.

## Important resource distinction

Macro representations have nonzero offline cost and state size. For example, affine M=3000 macro4 costs 296,598 offline successor evaluations and stores 158,192 endpoints.

Therefore equal `B_on` does **not** imply equal total resource usage.

This experiment measures the representation-side ability to trade `B_off,R` for lower online work. A Pareto comparison must therefore retain all three quantities:

```text
(B_off, R, B_on)
```

not `B_on` alone.

## Current status of the mechanism claim

The strongest supported claim remains:

> Direct predecessor access produced a resource-bounded frontier shift under the zero-offline/zero-persistent-state contract.

The representation-control result weakens any attempt to interpret that shift as an unconditional capability difference.

The next decisive experiment is to search the representation family itself more systematically and compare the full Pareto frontier over:

```text
offline computation
state size
online computation
```

before assigning causal primacy to transition-mechanism change.

## Sample provenance

Full local run:

- script: `frontier_representation_control_v3.py`
- seeds: 17, 23, 41
- graphs: affine M=30/300/3000, permutation M=31, opaque M=31
- 80 queries per seed
- caps: 10,20,40,80,160,320,640

Repository preserves deterministic representative query-level samples in:

`experiments/mechanism-frontier-shift-v0/samples-v0/REPRESENTATIVE-SAMPLES-V0.csv`

The full local sample export is larger than the repository representative sample set and remains CONVERSATION/LOCAL artifact until separately packaged.
