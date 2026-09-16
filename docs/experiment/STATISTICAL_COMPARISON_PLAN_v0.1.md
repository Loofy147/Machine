# Statistical Comparison Plan v0.1

**Status:** PRE-REGISTRATION CANDIDATE  
**Parent:** `docs/experiment/EXPERIMENT_PROTOCOL_v0.1_INITIAL_FREEZE_CANDIDATE.md`  
**Scope:** confirmatory comparison hierarchy, estimands, transfer arms, thresholds, multiplicity, decision rules, and sample-size determination.

## 1. Confirmatory scope

Exactly one confirmatory transfer direction will be frozen before confirmatory data collection and before any calibration capable of revealing pair-specific empirical outcomes:

\[
(Z_a^* \rightarrow Z_b^*)
\]

The pair must be selected from mechanism classes using frozen operator semantics/mechanism theory, not prior empirical performance.

Previously explored classes/cases are excluded from confirmatory data whenever prior exposure could reveal the selected contrast or its expected outcome. They remain exploratory.

No post-outcome search over pairs is permitted for the primary claim.

## 2. Mechanism-class construction

Mechanism classes are defined extensionally by operator semantics. Observed performance, previous success, or benchmark convenience cannot define class membership.

Algebraically/extensionally equivalent operators within the declared domain are assigned to the same functional-equivalence class before sampling. The class taxonomy is frozen before confirmatory generation.

Any proposed arithmetic-versus-bitwise contrast must document the semantic distinction under the declared domain rather than merely rely on operator names.

## 3. Diagnostic-policy arms

Three policies are distinct:

- **S0:** no probe before classification;
- **S1:** exactly one probe selected before observing its result;
- **S2:** sequential/adaptive probe selection conditioned on prior observations.

Resource budgets and permitted action spaces are frozen before execution.

S0, S1, and S2 answer different questions and are not interchangeable.

## 4. Diagnostic-transfer estimand

Let:

\[
Y_D=\mathbf 1\{\hat Z=Z\}
\]

under a specified policy and evaluation population.

For the primary transfer direction, the confirmatory diagnostic-transfer estimand is defined as a **transfer-increment against the corresponding frozen-policy baseline on matched fresh target cases**:

\[
\theta_D = P(Y_D=1\mid T_{b}^{transfer}) - P(Y_D=1\mid T_{b}^{baseline}).
\]

`baseline` and `transfer` must be defined operationally before data collection; they must share the same target mechanism population, design strata, budget, and evaluation conditions. The only intended difference is the availability of the transferred diagnostic knowledge/policy component under study.

Primary superiority criterion:

\[
\theta_D > \delta_D.
\]

## 5. Probe-policy transfer estimand

Let \(C_P\) be a pre-declared probe-cost measure (for example probe count or normalized probe cost).

For the specified policy-transfer comparison:

\[
\theta_P = E[C_P\mid T_b^{transfer,S2}] - E[C_P\mid T_b^{baseline,S2}].
\]

The sign convention is fixed so that a negative value indicates lower cost under transfer.

This measures **policy efficiency**, not diagnostic correctness. It does not by itself establish WHAT-learning.

If policy equivalence is made confirmatory, the margin \(\delta_P\) and equivalence procedure must be frozen before collection.

## 6. Repair-transfer estimand

Let \(C_R\) be a pre-declared repair-search cost, such as candidate evaluations until the first independently validated sufficient repair.

\[
\theta_R = E[C_R\mid T_b^{transfer}] - E[C_R\mid T_b^{baseline}].
\]

Primary dissociation condition:

\[
|\theta_R| < \delta_R.
\]

If the chosen cost distribution is strongly skewed or heavy-tailed, a ratio, transformed, quantile, or other robust estimand may replace the raw mean difference; that choice must be frozen before confirmatory collection.

## 7. Validation-transfer estimand

Let:

\[
Y_V=\mathbf 1\{\text{held-out generalization and preservation criteria pass}\}.
\]

Define:

\[
\theta_V=P(Y_V=1\mid T_b^{transfer})-P(Y_V=1\mid T_b^{baseline}).
\]

This is a validation-transfer effect and is distinct from replay/plausibility success.

## 8. Primary dissociation criterion

The confirmatory WHAT/HOW claim can be confirmed only when both are satisfied:

\[
\boxed{\theta_D>\delta_D}
\]

and:

\[
\boxed{|\theta_R|<\delta_R}.
\]

Neither criterion may be satisfied by substituting the best exploratory pair or stratum.

## 9. Thresholds

No numerical \(\delta\) is inherited from previous exploratory results.

Each margin must be defined as a smallest practically important effect (SPIE) on its native scale:

- \(\delta_D\): minimum useful absolute change in diagnostic success probability;
- \(\delta_P\): maximum practically negligible change in probe cost if policy equivalence is tested;
- \(\delta_R\): maximum practically negligible change in repair-search cost;
- \(\delta_V\): minimum useful validation-transfer effect if used confirmatorily.

The justification must come from system-level utility, cost, or safety constraints, not from observed confirmatory outcomes and not from calibration outcomes.

## 10. Sample-size determination

Sample size is determined only after estimands, margins, and the primary analysis are frozen.

For binary outcomes, use a declared two-arm design sized for the target \(\delta\), type-I error, power, baseline event rate assumptions, and design effect.

For equivalence on cost/count outcomes, use the planned matched/hierarchical model and equivalence margin with conservative variance assumptions.

If observations are clustered by mechanism class, generator family, case, or repeated run, the analysis and sample-size calculation must reflect the declared clustering rather than assume independent observations.

No numerical \(N\) is frozen until external calibration supplies defensible nuisance estimates from data excluded from confirmatory observations. Such calibration may inform variance, baseline rates, clustering/design effects, or feasible predeclared design strata; it may not select the primary pair, alter the estimands, or choose \(\delta\).

## 11. Calibration / confirmatory separation

A separate calibration set may estimate only pre-specified nuisance/design quantities, such as:

- baseline event rates;
- variance/dispersion;
- cluster/design effects;
- feasible difficulty/risk strata;
- execution/resource feasibility of an already frozen design.

Calibration observations cannot be reused as confirmatory observations.

Calibration cannot be used to choose or replace the primary pair, redefine the target population, alter estimand formulas, change the primary analysis, or select practical-effect margins from observed outcomes.

If a proposed design proves infeasible during calibration, the result is recorded as a design-feasibility finding. It does not authorize silent replacement of the confirmatory question; any design change creates a new pre-registered version before confirmatory collection.

## 12. Multiple comparisons

Exactly one transfer direction is primary.

All other class pairs, generator contrasts, difficulty strata, secondary metrics, and diagnostic-policy contrasts are exploratory unless a multiplicity-controlled confirmatory family is frozen in advance.

No post-outcome scan is permitted to promote a successful pair to primary.

If later work requires multiple confirmatory pairs, use a pre-specified gatekeeping/closed-testing plan or another appropriate multiplicity-control method fixed before data collection.

## 13. Decision rule

**CONFIRM** only when the primary superiority and equivalence criteria both pass under the pre-specified analysis.

Otherwise:

**NOT CONFIRMED.**

Failure to confirm is not interpreted as proof of the opposite hypothesis.

Exploratory findings remain explicitly exploratory.

## 14. Reporting

For each estimand report:

- point estimate;
- confidence interval;
- pre-declared margin;
- analysis population;
- generator/design strata;
- clustering structure;
- exclusions with their pre-specified reasons;
- confirmatory/exploratory status;
- calibration versus confirmatory data origin.

`Unknown` twin-audit cases remain represented in overall \(P_0\) accounting but do not enter twin-specific estimands requiring established identifiability.

## 15. Freeze checklist

Before confirmatory execution, freeze:

1. \((Z_a^*,Z_b^*)\) and selection rationale;
2. mechanism taxonomy and operator semantics;
3. exact estimand formulas and scales;
4. applicable \(\delta_D,\delta_P,\delta_R,\delta_V\);
5. analysis confidence level and power target;
6. nuisance assumptions used for sample size;
7. primary policy arm;
8. calibration/confirmatory separation;
9. multiplicity/gatekeeping rule;
10. decision/reporting rules.

**Status:** Candidate for joint review with the parent experiment protocol. Final confirmatory freeze occurs only after all ten items are populated and independently checked.
