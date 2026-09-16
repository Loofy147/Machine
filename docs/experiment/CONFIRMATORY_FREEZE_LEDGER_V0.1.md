# Confirmatory Freeze Ledger v0.1

**Status:** RESEARCH CONTROL DOCUMENT — FINAL FREEZE NOT YET REACHED  
**Branch:** `research/confirmatory-freeze-order-v0.1`

This ledger records the durable state of the confirmatory-design work. It is a control document, not empirical evidence.

## 1. Current evidence/status boundary

Historical experiments in the repository remain **EXPLORATORY** for the present confirmatory question. They are not silently promoted to confirmatory evidence.

The present design is a new causal-fault taxonomy and transfer test. Its claims remain prospective until execution and analysis are complete.

## 2. Frozen design-level decisions

### Primary comparison

\[
Z_a^* = \texttt{persistence/decay-fault}
\]

\[
Z_b^* = \texttt{context-discrimination-fault}
\]

Primary direction:

\[
\boxed{Z_a^*\rightarrow Z_b^*}
\]

The selection is based on frozen mechanism semantics rather than prior empirical performance.

### Primary diagnostic policy

\[
\boxed{S2=\text{sequential/adaptive probing}}
\]

S0/S1 remain exploratory unless separately frozen under multiplicity control.

### Transfer architecture

`T_b^baseline` and `T_b^transfer` use fresh target-class cases and identical repair machinery. The transfer arm differs only by the frozen diagnostic artifact learned from designated source-class episodes. The artifact may affect identification/probe selection but may not directly encode target outcomes, target repair candidates, target labels, hidden mechanism labels, or deterministic generator identity.

### Population discipline

`P0` is defined from the generator specification before outcome-based filtering. Twin-specific subsets do not replace `P0`.

### Twin audit

The audit state is one of:

- `Constructible`;
- `Provably Impossible` relative to the complete declared audit contract;
- `Unknown`.

`Unknown` is not silently dropped. A failed finite search is not itself an impossibility proof.

### Generator discipline

`G_spec` is frozen before the primary question; realized generator families `E` are instantiated only after the primary comparison, estimands, practical-effect bounds, and primary analysis are frozen.

## 3. Statistical definitions

### Primary diagnostic effect

\[
\theta_D=P(Y_D=1\mid T_b^{transfer})-P(Y_D=1\mid T_b^{baseline}).
\]

where:

\[
Y_D=1\{\hat Z=Z\}.
\]

### Probe-policy effect

\[
\theta_P=E[C_P\mid T_b^{transfer,S2}]-E[C_P\mid T_b^{baseline,S2}].
\]

Secondary unless separately promoted.

### Repair-search effect

\[
\theta_R=E[C_R\mid T_b^{transfer}]-E[C_R\mid T_b^{baseline}].
\]

The preferred general practical-equivalence region is:

\[
-\delta_R^-<\theta_R<\delta_R^+.
\]

Symmetric `|theta_R| < delta_R` is a special case, not an assumption.

### Validation effect

\[
\theta_V=P(Y_V=1\mid T_b^{transfer})-P(Y_V=1\mid T_b^{baseline}).
\]

Secondary unless separately promoted.

## 4. Margin semantics

### `delta_D`

Smallest positive absolute change in diagnostic success probability that is operationally important under the frozen target case mix and decision-utility contract.

It must be derived from downstream utility/cost/safety consequences rather than from observed outcomes.

Case-level utility is preferred:

\[
V_{D,i}=U_i(\text{correct diagnosis + downstream process})-U_i(\text{incorrect diagnosis + downstream process}).
\]

A separate `L_D` is allowed only for additional loss not already represented in `V_D`, to avoid double-counting.

### `delta_R+`

Largest practically negligible **increase** in repair-search cost.

### `delta_R-`

Largest practically negligible **decrease** treated as equivalent for the stated dissociation claim. It is needed only if symmetric/two-sided equivalence is retained.

### `B_D,min`

Minimum incremental expected decision benefit required before deployment. It is not a significance threshold or sample-size parameter.

### `C_R`

Pre-declared repair-search resource cost from search start to the first independently validated sufficient repair. Unit and censoring/timeout rules must be fixed before collection.

### Safety

Safety constraints are modeled as an admissible set/invariant, not as an arbitrary monetary value by default.

## 5. Decision-first derivation path

The remaining numerical margins are now governed by an explicit operational-decision path rather than by statistical convenience.

The working operational loop is:

```text
observe failure
  -> identify mechanism
  -> choose probe/search regime
  -> repair
  -> independently validate
  -> accept / reject / escalate
```

The derivation separates:

1. diagnostic capability;
2. downstream decision consequence;
3. resource, delay, and safety consequence.

For target case class `i`:

\[
V_{D,i}=U_i(\text{correct diagnosis + downstream process})-U_i(\text{incorrect diagnosis + downstream process}).
\]

A generic decision-value representation is:

\[
\Delta U_D=\sum_i w_i\,\Delta p_i\,V_{D,i}-C_{transfer}-\Delta Risk.
\]

This is a pre-study decision model, not a statistical identity. The terms must be fixed or justified independently of confirmatory outcomes.

Under the explicitly declared homogeneous special case:

\[
\Delta U_D=\theta_DV_D-C_{deploy,incremental}
\]

and the minimum qualifying probability effect is:

\[
\delta_D=\frac{B_{D,min}+C_{deploy,incremental}}{V_D}.
\]

This formula is not the default for heterogeneous case mixes.

For repair, the preferred operational equivalence region remains:

\[
-\delta_R^-<\theta_R<\delta_R^+.
\]

The new durable decision worksheet is recorded in:

`docs/experiment/DECISION_USE_CASE_AND_MARGIN_DERIVATION_V0.1.md`

## 6. Confirmed blocker: operational contract

The repository audit now explicitly records that it does **not** contain an external operational contract sufficient to assign numerical practical margins.

Specifically, it currently lacks a pre-study specification of:

- the real or declared decision context in which diagnosis is used;
- target case-mix weights;
- downstream value difference between correct and incorrect diagnosis;
- acceptable incremental resource/delay cost;
- safety or irreversibility bounds;
- repair-cost unit and practical-equivalence thresholds.

This is a **design-input gap**, not an empirical finding about the machine.

Canonical audit:

`docs/experiment/DECISION_USE_CASE_GAP_AUDIT_V0.1.md`

The project must not fabricate these values from exploratory results or from desired statistical power.

## 7. What is not frozen yet

The following remain explicit blockers:

1. operational contract: deployment-linked, bounded laboratory contract, or methodological-only claim;
2. target case-mix/utility weighting for `delta_D`;
3. numerical operational values needed to derive `delta_D`;
4. repair-cost unit/conversion rule;
5. numerical `delta_R+` and, if required, `delta_R-`;
6. repair timeout/censoring/failure rule;
7. any applicable safety bounds;
8. nuisance assumptions for sample size;
9. numerical sample size `N`;
10. final estimator/model family where data structure does not determine it automatically.

## 8. Freeze order

```text
G_spec
  -> M^(v)
  -> P0
  -> primary mechanism pair/direction
  -> estimands
  -> operational decision use case
  -> practical margins
  -> primary analysis
  -> pre-generation strata
  -> external nuisance calibration
  -> confirmatory freeze
  -> instantiate E
  -> generate/run confirmatory data
  -> locked analysis
```

The realized `E` must never be allowed to retroactively select the primary pair, estimands, margins, or analysis.

## 9. Documentation lineage

| Document | Role | Status |
|---|---|---|
| `EXPERIMENT_PROTOCOL_v0.1_INITIAL_FREEZE_CANDIDATE.md` | parent experimental protocol | candidate |
| `PRIMARY_COMPARISON_FREEZE_V0.1.md` | primary pair and transfer-arm contract | design frozen except numerical margins |
| `STATISTICAL_COMPARISON_PLAN_v0.1.md` | estimands, inference, multiplicity, N rules | candidate; blocked by margins/nuisance inputs |
| `DECISION_UTILITY_SEMANTICS_V0.1.md` | operational meaning and units of utility/cost inputs | design contract |
| `DECISION_USE_CASE_AND_MARGIN_DERIVATION_V0.1.md` | decision-first operational path and margin worksheet | current; numeric inputs open |
| `DECISION_USE_CASE_GAP_AUDIT_V0.1.md` | audit proving the current operational-input gap | current blocker |
| `MARGIN_JUSTIFICATION_V0.1.md` | initial margin derivation contract | superseded by reviewed semantics |
| `MARGIN_JUSTIFICATION_V0.1_REVIEWED.md` | reviewed margin derivation and blockers | current margin contract |
| this file | durable cross-document control ledger | current |

## 10. Methodological references

The margin discipline follows the general principle that equivalence/non-inferiority margins should be pre-specified and substantively justified, with equivalence assessed against the declared interval using confidence intervals.

References:

1. ICH E9, *Statistical Principles for Clinical Trials*.
2. ICH E9(R1), *Estimands and Sensitivity Analysis in Clinical Trials*.
3. FDA, *Non-Inferiority Clinical Trials* (2016).

These references justify the design principle; they do not supply numerical values for this machine experiment.

## 11. Status

**CURRENT STATE:** primary question and transfer structure are frozen at design level; the decision-first operational path is documented; an explicit operational-contract gap has been confirmed; statistical margin semantics have been audited and tightened; numerical margins and sample size remain open.

The repository must not enter confirmatory generation/run until the blockers in §7 are either populated and frozen or explicitly moved to a new preregistered version with documented rationale.
