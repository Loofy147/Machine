# Statistical Comparison Plan v0.1

**Status:** PRE-REGISTRATION CANDIDATE  
**Parent:** `docs/experiment/EXPERIMENT_PROTOCOL_v0.1_INITIAL_FREEZE_CANDIDATE.md`  
**Primary-comparison freeze:** `docs/experiment/PRIMARY_COMPARISON_FREEZE_V0.1.md`  
**Scope:** confirmatory comparison hierarchy, estimands, transfer arms, thresholds, multiplicity, decision rules, and sample-size determination.

## 1. Confirmatory scope

Exactly one confirmatory transfer direction is frozen before confirmatory data collection and before any calibration capable of revealing pair-specific empirical outcomes:

\[
\boxed{\texttt{persistence/decay-fault}\rightarrow\texttt{context-discrimination-fault}}
\]

The pair and direction are selected from frozen operator semantics/mechanism theory, not prior empirical performance. The exact definitions and transfer-arm contract are recorded in `PRIMARY_COMPARISON_FREEZE_V0.1.md`.

Previously explored classes/cases are excluded from confirmatory data whenever prior exposure could reveal the selected contrast or its expected outcome. They remain exploratory.

No post-outcome search over pairs is permitted for the primary claim.

## 2. Mechanism-class construction

Mechanism classes are defined extensionally by operator semantics. Observed performance, previous success, or benchmark convenience cannot define class membership.

For the primary pair:

- `persistence/decay-fault` = historical influence persists beyond the declared validity regime while context indexing remains fixed;
- `context-discrimination-fault` = historical information is merged or addressed across distinct operating contexts despite the persistence rule remaining fixed.

Functionally equivalent implementations belong to the same class. The taxonomy and causal intervention contracts are frozen before confirmatory generation.

The hidden fault label is never available to the system under test, and injector identity must not serve as a deterministic proxy for class identity within the observation boundary.

## 3. Diagnostic-policy arms

Three policies are distinct:

- **S0:** no probe before classification;
- **S1:** exactly one probe selected before observing its result;
- **S2:** sequential/adaptive probe selection conditioned on prior observations.

**Primary policy:**

\[
\boxed{S2}
\]

S0 and S1 remain exploratory unless a separate multiplicity-controlled confirmatory family is frozen before collection.

Resource budgets and permitted action spaces are frozen before execution.

## 4. Transfer arms

The target population contains fresh `context-discrimination-fault` cases only.

### `T_b^baseline`

The baseline arm receives:

- fresh target cases;
- identical initial state and observation boundary;
- the same S2 policy interface and probe budget;
- no diagnostic artifact transferred from source-class training;
- the same repair controller, action vocabulary, validation procedure, and repair budget used by the transfer arm.

### `T_b^transfer`

The transfer arm is identical except that it receives a frozen diagnostic artifact learned from designated source-class (`persistence/decay-fault`) training episodes.

The transfer artifact is restricted to diagnostic identification and/or probe-selection capability. It must not encode:

- target labels;
- target-case outcomes;
- target-specific repair candidates;
- target-specific repair shortcuts;
- hidden fault labels;
- generator identifiers that deterministically reveal the target class.

The repair controller and repair-search budget remain identical between arms.

Therefore the primary comparison isolates transfer of **diagnostic WHAT/HOW-of-probing capability**, not direct transfer of a repair procedure.

## 5. Diagnostic-transfer estimand

Let:

\[
Y_D=\mathbf 1\{\hat Z=Z\}
\]

under the primary S2 policy and the declared analysis population.

For the frozen target class:

\[
\theta_D = P(Y_D=1\mid T_b^{transfer}) - P(Y_D=1\mid T_b^{baseline}).
\]

Both arms use the same fresh target population, design strata, budget, observation boundary, and evaluation conditions. The only intended treatment difference is availability of the frozen transferred diagnostic artifact.

Primary superiority criterion:

\[
\theta_D > \delta_D.
\]

## 6. Probe-policy transfer estimand

Let \(C_P\) be a pre-declared probe-cost measure.

\[
\theta_P = E[C_P\mid T_b^{transfer,S2}] - E[C_P\mid T_b^{baseline,S2}].
\]

A negative value denotes lower probe cost under transfer.

This is a policy-efficiency estimand, not a correctness estimand. It is secondary unless explicitly promoted through a pre-specified multiplicity-controlled family.

## 7. Repair-transfer estimand

Let \(C_R\) be the pre-declared repair-search cost, such as candidate evaluations until the first independently validated sufficient repair.

\[
\theta_R = E[C_R\mid T_b^{transfer}] - E[C_R\mid T_b^{baseline}].
\]

Primary dissociation condition:

\[
|\theta_R| < \delta_R.
\]

The repair search mechanism, action vocabulary, validation procedure, and budget are identical across arms. The transfer artifact cannot modify these components.

If the cost distribution requires a transformed, ratio, quantile, or other robust estimand, that choice must be frozen before confirmatory collection.

## 8. Validation-transfer estimand

Let:

\[
Y_V=\mathbf 1\{\text{held-out generalization and preservation criteria pass}\}.
\]

Define:

\[
\theta_V=P(Y_V=1\mid T_b^{transfer})-P(Y_V=1\mid T_b^{baseline}).
\]

This remains secondary unless promoted under a pre-specified confirmatory family.

## 9. Primary dissociation criterion

The confirmatory WHAT/HOW claim can be confirmed only when both are satisfied:

\[
\boxed{\theta_D>\delta_D}
\]

and:

\[
\boxed{|\theta_R|<\delta_R}.
\]

Neither criterion may be satisfied by substituting another mechanism pair, difficulty stratum, generator family, or exploratory result.

## 10. Thresholds

No numerical \(\delta\) is inherited from previous exploratory results.

Each margin must be defined as a smallest practically important effect (SPIE) on its native scale:

- \(\delta_D\): minimum useful absolute change in diagnostic success probability;
- \(\delta_P\): maximum practically negligible change in probe cost if policy equivalence is tested;
- \(\delta_R\): maximum practically negligible change in repair-search cost;
- \(\delta_V\): minimum useful validation-transfer effect if used confirmatorily.

The repository currently lacks an independent utility/cost/safety specification sufficient to justify numerical SPIE values. Therefore the numerical margins are intentionally **OPEN** and constitute a pre-confirmatory blocker. They must not be chosen from calibration or exploratory outcomes.

## 11. Primary analysis and inference convention

For the primary diagnostic superiority test:

- two-sided confidence intervals are reported for estimation;
- the superiority decision uses the pre-specified one-sided lower confidence bound at \(\alpha=0.05\);
- target power for sample-size planning is **0.90**, unless a new preregistration version explicitly changes it before confirmatory data collection.

For the repair-equivalence criterion, use a pre-specified TOST-equivalent inference at \(\alpha=0.05\), corresponding to a 90% confidence interval for the equivalence decision once \(\delta_R\) is numerically frozen.

The point-estimator/model family must be fixed before confirmatory data collection; if clustering or repeated measures are present, the analysis must model that structure rather than assume independent observations.

## 12. Sample-size determination

Sample size is determined only after estimands, margins, and the primary analysis are frozen.

For binary outcomes, use a declared two-arm design sized for the frozen \(\delta_D\), type-I error, 0.90 target power, baseline event-rate assumptions, and design effect.

For repair-cost equivalence, use the frozen cost estimand, equivalence margin, and declared matched/hierarchical model with conservative nuisance assumptions.

No numerical \(N\) is frozen while the primary margins remain OPEN.

## 13. Calibration / confirmatory separation

A separate calibration set may estimate only pre-specified nuisance/design quantities, such as:

- baseline event rates;
- variance/dispersion;
- cluster/design effects;
- feasible difficulty/risk strata;
- execution/resource feasibility of the already frozen design.

Calibration observations cannot be reused as confirmatory observations.

Calibration cannot choose or replace the primary pair, redefine the target population, alter estimand formulas, change the primary analysis, or select practical-effect margins from observed outcomes.

If the frozen design proves infeasible during calibration, that result is recorded as a design-feasibility finding. It does not authorize silent replacement of the confirmatory question; any design change creates a new pre-registered version before confirmatory collection.

## 14. Multiple comparisons

Exactly one transfer direction is primary.

All other class pairs, the reverse direction, generator contrasts, difficulty strata, secondary metrics, and S0/S1 policy contrasts are exploratory unless a multiplicity-controlled confirmatory family is frozen in advance.

No post-outcome scan is permitted to promote a successful pair to primary.

## 15. Decision rule

**CONFIRM** only when both primary criteria pass under the frozen analysis.

Otherwise:

**NOT CONFIRMED.**

Failure to confirm is not interpreted as proof of the opposite hypothesis.

Exploratory findings remain explicitly exploratory.

## 16. Reporting

For each estimand report:

- point estimate;
- confidence interval;
- pre-declared margin;
- analysis population;
- generator/design strata;
- clustering structure;
- exclusions with their pre-specified reasons;
- confirmatory/exploratory status;
- calibration versus confirmatory data origin;
- transfer-artifact provenance and version.

`Unknown` twin-audit cases remain represented in overall \(P_0\) accounting but do not enter twin-specific estimands requiring established identifiability.

## 17. Freeze checklist

Already frozen at design level:

1. primary direction and pair;
2. mechanism taxonomy and causal intervention definitions;
3. exact estimand formulas and scales;
4. primary policy arm `S2`;
5. transfer-arm isolation and repair-controller equality;
6. \(\alpha=0.05\) and 0.90 target power;
7. calibration/confirmatory separation;
8. multiplicity rule;
9. decision/reporting rules.

Still OPEN and blocking final confirmatory freeze:

10. numerical \(\delta_D,\delta_P,\delta_R,\delta_V\) where applicable;
11. nuisance assumptions and numerical sample size derived from the frozen margins;
12. exact model/estimator family if not fully determined by the final data structure.

**Status:** Primary comparison and arm structure are frozen at design level. Final statistical freeze is blocked only by the explicitly identified margin/nuisance specifications, not by the mechanism-pair choice.
