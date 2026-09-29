# Frontier Insufficiency Adversarial Detector v0 — Results

**Status:** EXPERIMENTALLY_SUPPORTED / LOCAL RUN / NOT YET CI-REPLAYED  
**Branch:** `research/evidence-disposition-v0`  
**Code commit:** `72dce24466a86d395174a6e4995d20f9fecdd523`

## Question

Can a black-box detector distinguish persistent search failure from expressive insufficiency of the current solution space without being given the concept of structural insufficiency?

The detector receives only:

- residual(x);
- the search interval [lo, hi];
- finite search budgets.

It is not given fixture identity, structural labels, or ground truth.

The search uses two genuinely different families:

1. uniform-density sampling;
2. stratified coverage with a geometric coverage bound, followed by local zoom refinement around the best separated points.

The detector has three honest outcomes:

- `SUFFICIENT_FOUND`
- `INSUFFICIENT_CERTIFIED_AT_RESOLUTION`
- `INCONCLUSIVE_AT_RESOLUTION`

The second verdict is permitted only with an independently supplied Lipschitz bound.

## Adversarial fixtures

| Fixture | Ground truth | Purpose |
|---|---|---|
| A | sufficient | narrow funnel; local refinement can reach zero |
| A2 | sufficient | zero exists in a needle; no gradient information |
| B | insufficient | wide positive floor |
| D | insufficient | dense periodic near-misses, never zero |
| E | insufficient | multiscale positive basins approaching zero without attaining it |

Ground truth is used only for evaluation, never by the detector.

## Executed blind results

```text
A_sufficient_hard_funnel:
  verdict=SUFFICIENT_FOUND
  delta=20
  best=0
  stable=True
  cross=False

A2_sufficient_hard_NO_GRADIENT:
  verdict=INCONCLUSIVE_AT_RESOLUTION
  delta=5
  best=1
  stable=True
  cross=True

B_insufficient_easy:
  verdict=INCONCLUSIVE_AT_RESOLUTION
  delta=5
  best=1
  stable=True
  cross=True

D_insufficient_dense_near_misses:
  verdict=INCONCLUSIVE_AT_RESOLUTION
  delta=5
  best=1.00048
  stable=False
  cross=False

E_pathological_multiscale:
  verdict=INCONCLUSIVE_AT_RESOLUTION
  delta=5
  best=0.00416667
  stable=False
  cross=False
```

## Certified results

With independent fixture-specific Lipschitz bounds:

```text
B_insufficient_easy:
  L=0.00333333
  verdict=INSUFFICIENT_CERTIFIED_AT_RESOLUTION
  delta=5
  best=1
  certified global lower bound >= 0.99166667

D_insufficient_dense_near_misses:
  L=0.349066
  verdict=INSUFFICIENT_CERTIFIED_AT_RESOLUTION
  delta=5
  best=1.00048
  certified global lower bound >= 0.12781126
```

## Established interpretation

1. A single plateau is not sufficient evidence of expressive insufficiency.
2. Agreement between two search families is evidence of persistent failure, but is not by itself a proof that no solution exists.
3. A finite black-box detector cannot, in general, distinguish a positive floor from an arbitrarily narrow unseen zero without additional regularity assumptions or a certificate.
4. An explicit third verdict, `INCONCLUSIVE_AT_RESOLUTION(δ)`, is therefore logically necessary.
5. A negative conclusion can become defensible when an independently justified regularity certificate yields a positive global lower bound.

## Important scope boundary

This experiment does **not** establish a general detector for structural insufficiency.

It establishes a stricter methodological rule:

> Under finite black-box observation, the detector must not convert persistent nonzero residual into an unconditional claim that the solution space is insufficient.

The correct negative claim is relative to explicit constraints, resolution, and any independently justified regularity certificate.

## Next discriminating test

Extend the detector to additional independently generated sufficient/insufficient pairs where:

- the sufficient case is difficult but searchable;
- the sufficient case has a sparse solution;
- the insufficient case has many near-misses;
- search difficulty and expressive insufficiency are independently varied.

Then measure false-insufficiency and false-sufficiency rates under fixed query budgets and resolution schedules.

