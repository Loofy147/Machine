# Margin Justification v0.1

**Status:** DESIGN CONTRACT — NUMERICAL VALUES OPEN
**Parent:** `PRIMARY_COMPARISON_FREEZE_V0.1.md`
**Statistical plan:** `STATISTICAL_COMPARISON_PLAN_v0.1.md`
**External methodological basis:** ICH E9 / E9(R1); EMA draft guideline on non-inferiority and equivalence comparisons (2025). See repository research notes or the official sources listed below.

## 1. Purpose

The confirmatory margins must represent differences that are practically meaningful or practically negligible for the machine's intended operational use. They must therefore come from an explicit utility/cost/safety contract rather than from observed benchmark performance.

This document freezes the derivation procedure before confirmatory data. It does **not** invent numerical margins where the repository has no independent operational basis for them.

The methodological principle is that equivalence/non-inferiority margins are design features that should be pre-specified and justified independently of observed study results.

## 2. Decision variables

The primary confirmatory margins are:

\[
\delta_D>0
\]

for diagnostic-transfer superiority, and

\[
\delta_R>0
\]

for repair-search-cost equivalence.

`δP` and `δV` remain secondary unless explicitly promoted through a pre-specified multiplicity-controlled family.

## 3. Diagnostic margin

The primary diagnostic estimand is an absolute success-probability difference:

\[
\theta_D=P(Y_D=1|T_b^{transfer})-P(Y_D=1|T_b^{baseline}).
\]

The diagnostic SPIE `δD` must be the smallest improvement that would change an operational decision about deploying the transferred diagnostic capability.

It is determined before confirmatory observations by the following contract:

1. Define the operational cost of a diagnostic failure, `L_D`.
2. Define the operational value of one successful diagnostic identification, `V_D`, on the same decision scale.
3. Define the minimum deployment-level net benefit that justifies adoption, `B_D,min`.
4. Convert that threshold to a probability improvement under the declared case mix and downstream repair process.
5. Freeze the resulting probability difference as `δD`.

The conversion must use only pre-study utility/cost assumptions and declared downstream consequences. It must not use observed confirmatory success rates to choose the margin.

A simple special case is permitted when the downstream value/cost is linear and homogeneous:

\[
\delta_D = \frac{B_{D,min}}{N_{decision}(V_D+L_D)}
\]

where `N_decision` is a pre-declared operational decision batch size. The special case may be used only if its assumptions are documented and fixed before data collection.

## 4. Repair margin

The primary repair estimand is:

\[
\theta_R=E[C_R|T_b^{transfer}]-E[C_R|T_b^{baseline}].
\]

The equivalence margin `δR` is the largest repair-cost difference judged operationally negligible.

It is derived before confirmatory observations by:

1. defining the unit of repair cost (`candidate evaluations`, normalized compute, wall-clock budget, or another fixed unit);
2. defining the maximum additional repair expenditure that does not change the operational decision to deploy the diagnostic transfer;
3. freezing that tolerance as `δR` on the chosen cost scale;
4. fixing any transformation/ratio scale if the raw cost distribution is strongly skewed.

The tolerance must be expressed in operational cost units, not as a fraction selected from observed variance or observed treatment differences.

## 5. Safety constraint

A margin may not permit a change that crosses a pre-declared safety boundary.

If an intervention changes a safety-relevant quantity, the acceptable equivalence region must be bounded by the stricter of:

\[
\text{utility tolerance}
\]

and

\[
\text{safety tolerance}.
\]

A statistically small effect is not practically negligible when it violates a declared safety invariant.

## 6. Prohibited derivations

The following are not valid ways to select `δ`:

- choosing a margin because it produces a convenient sample size;
- choosing a margin from the observed exploratory effect;
- choosing a margin from confirmatory calibration outcomes;
- choosing a margin after inspecting candidate-generator performance;
- choosing a margin as an arbitrary percentage solely because it is conventional;
- widening the margin after observing low power.

Margin choice must remain independent of study outcomes.

## 7. Required pre-confirmatory inputs

The repository currently lacks independently frozen values for:

| Input | Required for | Current status |
|---|---|---|
| diagnostic failure cost `L_D` | `δD` | OPEN |
| successful-identification operational value `V_D` | `δD` | OPEN |
| minimum deployment benefit `B_D,min` | `δD` | OPEN |
| operational decision batch `N_decision` | `δD` special case | OPEN |
| repair-cost unit | `δR` | OPEN |
| maximum operationally negligible repair-cost increase | `δR` | OPEN |
| safety tolerance, if applicable | both | OPEN |

These inputs must be frozen from the intended machine operating contract, not inferred from benchmark results.

## 8. Consequence for sample size

Until `δD` and `δR` are numerically frozen, the confirmatory sample size `N` remains OPEN.

Calibration may estimate nuisance quantities such as variance, baseline rates, or cluster effects after the primary question and margins are conceptually frozen. It may not select or optimize the margins.

## 9. Freeze rule

The margin freeze is complete only when:

- each primary margin has a numeric value;
- the unit/scale is explicit;
- the operational utility/cost/safety rationale is recorded;
- the rationale predates confirmatory outcome observation;
- no value was chosen to obtain a preferred sample size or result;
- the resulting margins are entered unchanged in the Statistical Comparison Plan.

## 10. Current conclusion

**Status: OPEN / BLOCKER.**

The correct action is not to guess numerical margins. The project must first declare the operational utility/cost/safety contract from which `δD` and `δR` can be calculated.

This preserves the distinction between:

```text
scientific estimand
    -> practical decision threshold
    -> statistical margin
    -> sample size
```

rather than reversing the chain from observed data or desired statistical convenience.

## References

1. ICH E9, *Statistical Principles for Clinical Trials*.
2. ICH E9(R1), *Estimands and Sensitivity Analysis in Clinical Trials*.
3. EMA, *Draft guideline on non-inferiority and equivalence comparisons in clinical trials* (first published 13 November 2025; consultation closed 31 May 2026).

Official sources:
- https://www.ema.europa.eu/en/non-inferiority-equivalence-comparisons-clinical-trials-scientific-guideline
- https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e9r1-statistical-principles-clinical-trials-addendum-estimands-and-sensitivity-analysis-clinical
