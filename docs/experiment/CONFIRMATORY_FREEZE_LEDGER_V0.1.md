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

## 5. Decision-first operational use case

The working bounded-laboratory decision loop is now explicit:

```text
observe failure
  -> diagnostic probing
  -> mechanism decision
  -> fixed repair/search regime
  -> independent validation
  -> VALIDATED_RECOVERY / VALIDATED_NO_RECOVERY / ESCALATE_TIMEOUT / ESCALATE_SAFETY
```

Diagnostic correctness is separated from downstream repair success. A repair that happens to work does not retroactively make the diagnosis correct.

The operational utility is represented as a vector before any scalar projection:

```text
recovery outcome
validation outcome
probe units
repair-search units
delay/decision units
safety/admissibility status
```

Any scalar utility or practical margin must be derived from a pre-study contract, not from confirmatory outcomes.

## 6. Lessons carried forward from first experiments

The following exploratory observations are now explicit design constraints:

1. mutable executable representation is a substrate capability, not by itself evidence of an adaptive algorithm;
2. search dynamics can dominate substrate effects, so the repair/search controller must remain identical across primary arms;
3. noisy evaluation can hurt, so probe actions are resource-bearing decisions rather than free information;
4. context-free accumulation can misapply historical experience, so the transfer artifact is bounded, versioned, and auditable;
5. failure detection, fault localization, intervention selection, and post-intervention generalization are separate capabilities and endpoints;
6. structural/representation expansion must incur explicit resource cost;
7. bundled mechanism roles must not be mistaken for single primitives.

These are constraints derived from exploratory evidence, not confirmatory effects.

## 7. Canonical target case

One concrete fresh-target fixture is now specified for decision derivation:

`docs/experiment/CANONICAL_OPERATIONAL_CASE_ZB_CONTEXT_MERGE_V0.1.md`

The case models a `Zb` context-discrimination fault where history remains valid but is addressed through an insufficient context key. The diagnostic boundary, probe family, repair boundary, validation boundary, terminal decisions, measurement record, and falsifiers are explicitly defined there.

This case is a design fixture, not confirmatory data and not evidence that all `Zb` cases behave this way.

## 8. Target-strata operationalization

The primary target remains fresh `Zb` cases. Candidate predeclared strata are:

- failure severity;
- context-change magnitude;
- probe informativeness;
- history length;
- repair recoverability.

The canonical case is one fixture within that larger population. Stratum weights and numerical utility values remain open.

## 9. Decision-first derivation path

For stratum `s`:

\[
V_{D,s}=U_s(\text{correct diagnosis + fixed downstream process})-U_s(\text{incorrect diagnosis + fixed downstream process}).
\]

Population-level decision consequence is represented generically as:

\[
\Delta U_D=\sum_s w_s\,\Delta p_s\,V_{D,s}-C_{transfer}-\Delta Risk.
\]

Only where the case mix and utility model justify a stable scalar mapping should a single `delta_D` be derived. The homogeneous formula remains a special case.

For repair, the preferred equivalence region remains:

\[
-\delta_R^-<\theta_R<\delta_R^+.
\]

## 10. Remaining blockers

1. final target-stratum set;
2. stratum weights `w_s`;
3. case/stratum diagnostic utility `V_D,s`;
4. `C_P`, `C_R`, and optional `C_V` unit definitions;
5. aggregate resource conversion, if required;
6. minimum operational benefit `B_D,min`;
7. transfer overhead/risk treatment;
8. admissibility/safety bounds;
9. repair timeout/censoring/failure rule;
10. numerical `delta_D` if justified;
11. numerical `delta_R+/-`;
12. nuisance assumptions, estimator/model family where required, and `N`.

No number is authorized merely because it makes the pilot or desired power convenient.

## 11. Freeze order

```text
G_spec
  -> M^(v)
  -> P0
  -> primary mechanism pair/direction
  -> estimands
  -> operational decision use case
  -> target strata / pre-generation case mix
  -> practical margins
  -> primary analysis
  -> external nuisance calibration
  -> confirmatory freeze
  -> instantiate E
  -> generate/run confirmatory data
  -> locked analysis
```

The realized `E` must never be allowed to retroactively select the primary pair, estimands, margins, case mix, or analysis.

## 12. Documentation lineage

| Document | Role | Status |
|---|---|---|
| `EXPERIMENT_PROTOCOL_v0.1_INITIAL_FREEZE_CANDIDATE.md` | parent experimental protocol | candidate |
| `PRIMARY_COMPARISON_FREEZE_V0.1.md` | primary pair and transfer-arm contract | design frozen except numerical margins |
| `STATISTICAL_COMPARISON_PLAN_v0.1.md` | estimands, inference, multiplicity, N rules | candidate; blocked by margins/nuisance inputs |
| `DECISION_UTILITY_SEMANTICS_V0.1.md` | operational meaning and units of utility/cost inputs | design contract |
| `DECISION_USE_CASE_AND_MARGIN_DERIVATION_V0.1.md` | decision-first worksheet | current general framework |
| `DECISION_USE_CASE_GAP_AUDIT_V0.1.md` | audit of initial operational-input gap | historical blocker; retained for lineage |
| `CANONICAL_OPERATIONAL_CASE_ZB_CONTEXT_MERGE_V0.1.md` | concrete bounded-lab Zb case | current design fixture |
| `MARGIN_JUSTIFICATION_V0.1.md` | initial margin derivation contract | superseded by reviewed semantics |
| `MARGIN_JUSTIFICATION_V0.1_REVIEWED.md` | reviewed margin derivation and blockers | current margin contract |
| this file | durable cross-document control ledger | current |

## 13. Status

**CURRENT STATE:** primary question, transfer structure, bounded-laboratory operational use case, and one canonical `Zb` case are documented; practical numerical margins, case-mix weights, and sample-size inputs remain open.

The repository must not enter confirmatory generation/run until the remaining blockers are either populated and frozen or explicitly moved to a new preregistered version with documented rationale.
