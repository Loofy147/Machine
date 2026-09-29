# Decision Utility Semantics v0.1

**Status:** DESIGN CONTRACT — NUMERIC INPUTS OPEN  
**Parents:** `PRIMARY_COMPARISON_FREEZE_V0.1.md`, `MARGIN_JUSTIFICATION_V0.1.md`  
**Purpose:** define the semantics of the operational quantities from which confirmatory practical-effect margins may be derived.

## 1. Scope

This document defines meanings and units. It does **not** assign numerical values.

The confirmatory study uses two primary margins:

- `delta_D`: superiority margin for diagnostic identification success;
- `delta_R`: equivalence margin for repair-search cost.

`delta_P` and `delta_V` remain secondary unless separately promoted by a pre-specified multiplicity-controlled family.

## 2. Unit discipline

Every operational quantity must have an explicit unit before a numerical value is frozen.

A utility quantity and a resource-cost quantity must not be added or compared directly unless a declared conversion function maps them to a common decision scale.

Permitted examples include:

```text
compute units -> monetary proxy -> decision utility
candidate evaluations -> normalized resource units
wall-clock time -> declared operational-cost units
risk probability -> expected loss units
```

No conversion factor may be estimated from confirmatory treatment outcomes.

## 3. Diagnostic outcome value

The primary diagnostic outcome is:

\[
Y_D = 1\{\hat Z = Z\}.
\]

A correct diagnosis is not assigned an intrinsic universal value.

Instead define a case-level downstream utility difference:

\[
V_{D,i}=U_i(\text{correct diagnosis and downstream process})
       -U_i(\text{incorrect diagnosis and downstream process}).
\]

`V_D` is therefore not an arbitrary reward for being correct. It is the pre-declared downstream decision value of correctness for the specified target population.

If all eligible cases have the same downstream utility difference, a scalar `V_D` may be used. Otherwise the case-mix distribution and weighting rule must be declared.

## 4. Diagnostic failure cost

`L_D` is **not automatically an independent quantity** from `V_D`.

If an incorrect diagnosis incurs a downstream loss relative to a correct diagnosis, that loss is already represented by `V_D` under the definition above.

Use a separate `L_D` only when there is an additional loss component not already included in `V_D`, for example:

- safety-relevant misclassification loss;
- irreversible intervention exposure;
- external side-effect cost;
- delay cost that is not captured in the repair utility.

Then:

\[
V_D = V_{downstream\ benefit}-L_{additional\ diagnostic\ failure}
\]

must be made explicit instead of double-counting the same consequence.

## 5. Deployment threshold

`B_D,min` is the minimum **incremental expected decision benefit** required before deploying the transferred diagnostic capability under the declared use case.

It is not:

- a statistical significance threshold;
- an arbitrary desired effect size;
- a value selected to obtain a convenient sample size.

It may incorporate pre-declared operational costs of deployment, maintenance, latency, complexity, and safety constraints, but each component must be separately specified.

## 6. Mapping diagnostic probability to utility

The study's primary diagnostic estimand is an average probability difference:

\[
\theta_D=P(Y_D=1|T_b^{transfer})-P(Y_D=1|T_b^{baseline}).
\]

A scalar `delta_D` can represent an operational SPIE only if a declared utility mapping makes the probability scale meaningful for the target population.

Under a homogeneous linear special case:

\[
\Delta U_D = \theta_D\,V_D - C_{deploy,incremental},
\]

and `delta_D` is the smallest positive `theta_D` satisfying:

\[
\Delta U_D \ge B_{D,min}.
\]

Thus:

\[
\delta_D \ge
\frac{B_{D,min}+C_{deploy,incremental}}{V_D}.
\]

This is only a derivation template, not the default formula. When `V_D` varies materially by case, use the declared case-mix-weighted utility mapping instead of inserting a single scalar.

## 7. Repair-search cost

Let:

\[
C_R \ge 0
\]

be the total resource cost from the start of repair search until the first repair that passes the **independent validation contract**.

The unit must be fixed before confirmatory execution. A valid cost definition may include:

- candidate evaluations;
- normalized compute units;
- wall-clock time;
- energy/resource units;
- a declared composite cost.

If multiple components are combined, the conversion weights are pre-specified.

A run that never obtains an independently validated repair is not assigned an arbitrary finite cost. The protocol must define a censoring/timeout rule or a failure category before data collection.

## 8. Repair equivalence margin

The current protocol uses:

\[
|\theta_R| < \delta_R.
\]

This assumes symmetric practical tolerance around zero. That symmetry is not automatic.

The preferred general form is:

\[
-\delta_R^- < \theta_R < \delta_R^+.
\]

where:

- `delta_R+` = largest practically negligible **increase** in repair cost;
- `delta_R-` = largest practically negligible **decrease** treated as equivalent for the dissociation claim.

Use the symmetric form only if the operational argument establishes that gain and loss are genuinely interchangeable around zero for the intended claim.

For the WHAT/HOW dissociation, the practically important boundary is usually the **increase** side. Therefore `delta_R+` is the safety-critical quantity unless the protocol explicitly requires symmetric equivalence.

## 9. Safety is a constraint, not a utility weight by default

A safety invariant can invalidate an otherwise small numerical difference.

Define a pre-declared admissible set:

\[
\mathcal S_{safe}.
\]

An equivalence margin is valid only when every value inside the declared equivalence region also satisfies the applicable safety constraints, or when violations are explicitly handled by a separate safety endpoint.

Do not compensate a safety violation by assigning it a monetary or utility weight unless the experiment explicitly declares that decision model.

## 10. Decision-level derivation chain

The intended chain is:

```text
operational use case
    -> downstream consequences
    -> utility / resource units
    -> deployment threshold
    -> smallest practically important effect
    -> statistical margin
    -> sample-size calculation
```

The chain must never be reversed:

```text
preferred sample size
    -> convenient margin
    -> post-hoc utility story
```

## 11. Missing inputs are first-class states

Until the operational contract supplies the necessary values, the status is `OPEN` rather than `UNKNOWN`:

- `OPEN` means the project has identified exactly what must be specified but has not yet frozen it.
- `UNKNOWN` is reserved for empirical or epistemic uncertainty about a property that has been investigated under the declared audit contract.

This distinction prevents an absent design choice from being mistaken for an empirical finding.

## 12. External methodological basis

The margin discipline is consistent with established statistical guidance: equivalence/non-inferiority margins should be explicitly specified and justified on substantive grounds, and equivalence is assessed against the pre-specified interval using confidence intervals rather than a non-significant superiority test. See FDA/ICH E9 materials in the research record.

The present experiment is not a clinical trial; these sources are used only for the general statistical design principle concerning pre-specified, substantively justified margins.

## 13. Freeze condition

The decision-utility layer is ready for numerical freezing only when all applicable items have:

1. a definition;
2. an explicit unit;
3. an operational owner/source;
4. a pre-study value or declared derivation rule;
5. a statement of why the value is decision-relevant;
6. no dependence on confirmatory outcomes.

Until then, `delta_D`, `delta_R`, and the confirmatory sample size remain open.
