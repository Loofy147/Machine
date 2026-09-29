# Utility → Margin Numerical Walkthrough v0.1

**Status:** DESIGN EXAMPLE — NOT FROZEN
**Parent:** `DECISION_UTILITY_SEMANTICS_V0.1.md`
**Purpose:** demonstrate the mechanical derivation of practical-effect margins using only hypothetical pre-study assumptions.

> This file is a worked example. None of the numerical values below are approved confirmatory inputs.

## 1. Rules

The example must satisfy four constraints:

1. values are declared before any confirmatory outcome is observed;
2. units are explicit;
3. the margin is derived from operational assumptions rather than desired power/sample size;
4. the example is not reused as empirical evidence.

## 2. Diagnostic example

Assume a hypothetical deployment contract with one common decision unit:

| Quantity | Hypothetical value | Unit | Meaning |
|---|---:|---|---|
| `V_D` | 1000 | decision-utility units / correct diagnosis | downstream utility difference between correct and incorrect diagnosis |
| `C_deploy,incremental` | 50 | decision-utility units / decision unit | additional deployment/maintenance cost attributable to transferred diagnostic capability |
| `B_D,min` | 50 | decision-utility units / decision unit | minimum additional net benefit required for deployment |

Under the homogeneous linear special case:

\[
\Delta U_D = \theta_D V_D - C_{deploy,incremental}.
\]

Require:

\[
\Delta U_D \ge B_{D,min}.
\]

Therefore:

\[
\theta_D V_D - C_{deploy,incremental} \ge B_{D,min}
\]

and:

\[
\delta_D
=
\frac{B_{D,min}+C_{deploy,incremental}}{V_D}
=
\frac{50+50}{1000}
=
0.10.
\]

### Interpretation

Under these hypothetical assumptions, the smallest operationally important absolute improvement is:

\[
\boxed{\delta_D=0.10}
\]

meaning a ten-percentage-point improvement in diagnostic success probability.

This number is **not** justified by any experiment result. It is justified only by the stated hypothetical utility contract.

## 3. Feasibility check

A derived probability margin must satisfy:

\[
0<\delta_D\le1.
\]

If the derivation produces `δD > 1`, the operational contract cannot be met by the binary diagnostic outcome alone. The correct response is to revise the use-case economics/utility definition or conclude that this endpoint cannot support the desired deployment decision; do not clip the margin to 1.

## 4. Case-mix extension

The homogeneous example is valid only if `V_D` is sufficiently stable across the confirmatory population.

For heterogeneous cases, define:

\[
V_{D,i}
=
U_i(\text{correct diagnosis + downstream})
-
U_i(\text{incorrect diagnosis + downstream}).
\]

Then the probability-scale effect must be mapped through the declared target-population weighting distribution rather than by inserting an unweighted scalar `V_D`.

A confirmatory margin must therefore record:

- target case-mix distribution;
- weighting rule;
- utility scale;
- deployment cost;
- minimum deployment benefit;
- whether case-level utility varies by mechanism/difficulty stratum.

## 5. Repair-cost example

Assume the repair-search cost is measured in **normalized candidate-evaluation units**.

Hypothetically, the deployment contract states that an additional repair-search expenditure of up to 10 units has no operational consequence for the intended dissociation claim.

Then the positive-side margin is:

\[
\boxed{\delta_R^+=10\text{ candidate-evaluation units}}
\]

This is not derived from observed variance or observed treatment differences.

For the present WHAT/HOW claim, a decrease in repair cost does not undermine the dissociation. Therefore the scientifically relevant condition may be one-sided on the increase side:

\[
\theta_R < \delta_R^+.
\]

If symmetric equivalence is explicitly desired instead, a separate operational rationale must define `δR−` and justify:

\[
-\delta_R^-<\theta_R<\delta_R^+.
\]

Do not assume `δR− = δR+` merely for mathematical convenience.

## 6. Timeout and failed repair

Suppose a repair run that does not produce an independently validated repair within the fixed search budget is classified as:

```text
REPAIR_TIMEOUT
```

and is not assigned an arbitrary finite cost.

The statistical plan must then pre-specify how `REPAIR_TIMEOUT` enters the estimator/model. Candidate evaluation cost alone cannot silently transform a failed run into an ordinary finite observation.

## 7. Safety gate

The hypothetical margins are valid only if every accepted equivalence case remains inside the declared safety set:

\[
\mathcal S_{safe}.
\]

If a repair-cost difference of 10 units crosses a safety invariant, the utility-based margin is invalid and the safety bound becomes the controlling constraint.

## 8. What this example proves

It demonstrates only that the contract is mechanically usable:

```text
operational assumptions
    -> utility equation
    -> SPIE
    -> margin
```

It does **not** establish that the hypothetical numbers are appropriate for the Machine project.

## 9. Freeze consequence

The project may freeze numeric `δD`/`δR` only after replacing the hypothetical inputs here with independently justified operational values and recording their provenance.

Until then:

\[
\boxed{\delta_D,\delta_R,N = OPEN}
\]
