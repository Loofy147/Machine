# Margin Justification v0.1 — Reviewed

**Status:** DESIGN CONTRACT — NUMERICAL VALUES OPEN  
**Parent:** `PRIMARY_COMPARISON_FREEZE_V0.1.md`  
**Statistical plan:** `STATISTICAL_COMPARISON_PLAN_v0.1.md`  
**Semantics:** `DECISION_UTILITY_SEMANTICS_V0.1.md`

## 1. Purpose

The confirmatory margins must represent differences that are practically meaningful or practically negligible for the intended operational use of the machine. They must therefore come from an explicit utility/cost/safety contract rather than from observed benchmark performance.

This document records the reviewed derivation procedure before confirmatory observations. It intentionally does not invent numerical margins where the repository has no independent operational basis for them.

The general statistical principle is consistent with ICH E9/FDA guidance: equivalence or non-inferiority margins are design features that require substantive pre-specification and justification; equivalence is assessed against the pre-specified interval, not inferred from a non-significant superiority test. These sources are methodological references, not sources of numerical values for this experiment.

## 2. Primary margins

The primary diagnostic margin is:

\[
\delta_D>0
\]

for superiority of diagnostic-transfer success probability.

For repair cost, the general equivalence region is:

\[
-\delta_R^- < \theta_R < \delta_R^+.
\]

The previous symmetric form `|theta_R| < delta_R` is retained only as a special case requiring an explicit symmetry justification.

`delta_P` and `delta_V` remain secondary unless separately promoted through a pre-specified multiplicity-controlled family.

## 3. Diagnostic margin semantics

The primary diagnostic estimand is:

\[
\theta_D=P(Y_D=1\mid T_b^{transfer})-P(Y_D=1\mid T_b^{baseline}).
\]

`delta_D` is the smallest positive change on this probability scale that is practically important under the pre-declared target case mix and operational decision rule.

### 3.1 Case-level diagnostic value

Define, for case `i`, the downstream utility difference attributable to correct rather than incorrect diagnosis:

\[
V_{D,i}=
U_i(\text{correct diagnosis + downstream process})
-
U_i(\text{incorrect diagnosis + downstream process}).
\]

A scalar `V_D` may be used only when case-mix variation is negligible or a pre-specified weighting rule gives it a defensible interpretation.

The benchmark must not assume that every correct diagnosis has the same operational value.

### 3.2 Diagnostic failure loss

`L_D` is **not automatically independent** of `V_D`.

If the loss from incorrect diagnosis is already included in the utility contrast `V_{D,i}`, adding the same loss again as a separate penalty double-counts it.

A separate diagnostic-failure loss is permitted only for an additional consequence not already represented in `V_{D,i}`, such as an independently modeled safety event, irreversible side effect, or external delay cost.

### 3.3 Deployment threshold

`B_D,min` is the minimum incremental expected decision benefit required before deploying the transferred diagnostic capability under the declared use case.

It is not a statistical significance threshold, desired p-value, arbitrary effect size, or sample-size convenience parameter.

### 3.4 Probability-to-utility mapping

Let `C_deploy,incremental` denote the pre-declared incremental operational cost of making the transfer capability available.

In a homogeneous linear special case:

\[
\Delta U_D(\theta_D)=\theta_D V_D-C_{deploy,incremental}.
\]

The operational margin is then the smallest positive `theta_D` satisfying:

\[
\Delta U_D(\theta_D)\ge B_{D,min}.
\]

Equivalently, under those assumptions:

\[
\delta_D
\ge
\frac{B_{D,min}+C_{deploy,incremental}}{V_D}.
\]

This is a derivation template only. Where utility differs by case, where diagnosis changes downstream repair behavior, or where the mapping is nonlinear, the project must use the declared case-mix-weighted utility function instead of this scalar formula.

A numerical `delta_D` therefore cannot be frozen until the probability-to-decision mapping itself is frozen.

## 4. Repair-cost semantics

Define:

\[
C_R\ge0
\]

as total repair-search resource cost from the start of repair search until the first repair that passes the independent validation contract.

The cost unit must be fixed before confirmatory execution. Possible units include candidate evaluations, normalized compute units, wall-clock time, energy/resource units, or a pre-specified composite.

If multiple resource components are combined, conversion weights are fixed in advance.

A run that never obtains an independently validated repair must not receive an arbitrary finite cost. A timeout/censoring rule or explicit failure category must be fixed before data collection.

## 5. Repair equivalence semantics

The current estimand is:

\[
\theta_R=E[C_R\mid T_b^{transfer}]-E[C_R\mid T_b^{baseline}].
\]

The general equivalence region is:

\[
-\delta_R^-<\theta_R<\delta_R^+.
\]

Interpretation:

- `delta_R+` = largest practically negligible **increase** in repair cost;
- `delta_R-` = largest practically negligible **decrease** treated as equivalent for the stated dissociation claim.

The symmetric condition `|theta_R| < delta_R` is allowed only if the operational argument establishes genuine symmetry around zero.

For the WHAT/HOW dissociation, `delta_R+` is the critical protection against materially worsening repair behavior. An apparently beneficial reduction in repair cost does not justify widening the acceptable-worsening margin.

## 6. Safety semantics

Safety is a constraint, not a generic utility weight by default.

Define a pre-declared admissible safety set:

\[
\mathcal S_{safe}.
\]

The equivalence region is admissible only if values within it satisfy the applicable safety invariants, or if safety is represented by a separate pre-specified endpoint and decision rule.

A statistically small effect is not practically negligible when it violates a safety boundary.

## 7. Required pre-confirmatory inputs

| Input | Required for | Status |
|---|---|---|
| target case-mix / weighting rule | `delta_D` | OPEN |
| case-level `V_D,i`, or defensible scalar reduction | `delta_D` | OPEN |
| any additional diagnostic-failure loss not already in `V_D` | `delta_D` | OPEN |
| incremental deployment cost | `delta_D` | OPEN |
| minimum deployment benefit `B_D,min` | `delta_D` | OPEN |
| repair-cost unit and conversion weights | `delta_R` | OPEN |
| upper practical tolerance `delta_R+` | `delta_R` | OPEN |
| lower practical tolerance `delta_R-`, if symmetric equivalence is retained | `delta_R` | OPEN |
| safety admissible set/bound | both | OPEN |
| repair timeout/censoring/failure rule | `delta_R` and analysis | OPEN |

These inputs must be frozen from the intended machine operating contract, not inferred from benchmark outcomes.

## 8. Prohibited derivations

The following are invalid:

- choosing a margin because it yields a convenient sample size;
- selecting it from exploratory effect sizes;
- selecting it from confirmatory calibration outcomes;
- inspecting candidate-generator performance before choosing it;
- using a conventional percentage without an operational justification;
- widening the margin after seeing low power;
- double-counting the same downstream loss in both `V_D` and `L_D`.

## 9. Sample-size consequence

Until the primary margins are numerically frozen and their scales are explicit, confirmatory sample size `N` remains `OPEN`.

External calibration may estimate nuisance quantities such as baseline rates, variance/dispersion, and clustering/design effects after the question and margin definitions are fixed. Calibration may not optimize the margins.

## 10. Freeze rule

Margin freeze is complete only when:

1. each primary margin has a numeric value or explicit interval;
2. its unit/scale is explicit;
3. the operational rationale is recorded;
4. case-mix weighting is recorded where applicable;
5. repair censoring/failure handling is fixed;
6. applicable safety constraints are explicit;
7. the rationale predates confirmatory outcome observation;
8. no value was selected to obtain a preferred sample size or result;
9. the resulting margin(s) are copied unchanged into the Statistical Comparison Plan.

## 11. Current conclusion

**Status: OPEN / BLOCKER.**

The project should now define the operational utility/cost/safety contract rather than guess numerical margins.

The intended chain remains:

```text
scientific estimand
    -> operational decision rule
    -> practical-effect margin
    -> sample-size calculation
```

not:

```text
preferred sample size
    -> convenient margin
    -> post-hoc utility story
```

## References

1. ICH E9, *Statistical Principles for Clinical Trials*.
2. ICH E9(R1), *Estimands and Sensitivity Analysis in Clinical Trials*.
3. FDA, *Non-Inferiority Clinical Trials* (2016).

These references establish general principles for pre-specified substantive margin justification; they do not determine the numerical values for this experiment.
