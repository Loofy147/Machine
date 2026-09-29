# Decision Use Case and Margin Derivation v0.1

**Status:** DESIGN PATH — NUMERIC INPUTS OPEN  
**Branch:** `research/confirmatory-freeze-order-v0.1`

This document records the decision-engineering path for resolving the remaining practical-margin blockers. It is a design artifact, not empirical evidence and not a source of numeric margin values.

## 1. Starting point: an operational decision

The confirmatory experiment must not begin by asking only whether a statistical endpoint moves. It must first specify the operational decision in which the capability would be used.

The working decision loop is:

```text
observe failure
    -> identify mechanism
    -> choose probe/search regime
    -> repair
    -> independently validate
    -> accept / reject / escalate
```

The primary scientific contrast remains:

```text
Za = persistence/decay fault
Zb = context-discrimination fault
```

The question is whether a diagnostic capability acquired from Za cases transfers to fresh Zb cases without changing the repair machinery.

## 2. Operational decomposition

The experiment separates three quantities that must not be collapsed:

1. **Diagnostic capability** — whether the mechanism is identified correctly.
2. **Decision consequence** — what correct versus incorrect identification changes downstream.
3. **Resource/safety consequence** — additional compute, delay, irreversibility, or other operational cost imposed by the capability.

The statistical endpoint `theta_D` measures only the first quantity. A practical margin must connect the first quantity to the second and third under a pre-declared use case.

## 3. Case-level diagnostic value

For case `i`, define:

\[
V_{D,i} = U_i(\text{correct diagnosis + downstream process})
       - U_i(\text{incorrect diagnosis + downstream process}).
\]

`V_D,i` is therefore contextual. It is not an intrinsic reward assigned to the label “correct diagnosis”.

If a separate diagnostic loss term `L_D` is used, it must represent only an additional consequence not already included in `V_D,i`. Otherwise the same downstream harm is counted twice.

## 4. From diagnostic probability to operational value

Let `Delta p_i` be the change in diagnostic-success probability for case class `i` attributable to transfer. With case-mix weights `w_i`, a generic expected incremental utility representation is:

\[
\Delta U_D
= \sum_i w_i\,\Delta p_i\,V_{D,i}
  - C_{transfer}
  - \Delta Risk.
\]

This is a decision model, not a statistical identity. Its terms must be independently specified and measured or justified before confirmatory outcomes are observed.

### Homogeneous special case

If the decision contract establishes a common `V_D`, a common probability effect is meaningful, and incremental transfer cost/risk can be treated as a fixed quantity, then:

\[
\Delta U_D = \theta_D V_D - C_{deploy,incremental}.
\]

For a minimum required deployment benefit `B_D,min`, the corresponding threshold is:

\[
\theta_D V_D - C_{deploy,incremental} \ge B_{D,min}.
\]

Therefore the smallest qualifying probability effect is:

\[
\delta_D =
\frac{B_{D,min}+C_{deploy,incremental}}{V_D}.
\]

This equation is valid only under the stated special-case assumptions. It must not be treated as the default derivation for heterogeneous case mixes.

## 5. Machine-native operational units

The preferred unit system is machine-operational rather than monetary unless an external deployment decision actually requires monetary conversion.

Candidate quantities include:

- normalized compute/resource units;
- probe units;
- wall-clock delay, when operationally relevant;
- bounded irreversibility or safety-risk units;
- independently validated recovery/preservation outcomes.

Monetary value may be added as an external mapping layer. It should not be introduced merely because it makes the margin formula easier to write.

## 6. Repair-search equivalence

Define repair cost `C_R >= 0` from repair-search start to the first independently validated sufficient repair.

The contract should use an asymmetric equivalence region unless there is a substantive reason for symmetry:

\[
-\delta_R^- < \theta_R < \delta_R^+.
\]

where:

\[
\theta_R = E[C_R|transfer]-E[C_R|baseline].
\]

Interpretation:

- `delta_R+` is the largest increase in repair cost considered practically negligible;
- `delta_R-` is the largest decrease represented as still equivalent for the stated dissociation claim.

Safety constraints are separate admissibility conditions. A safety violation is not made acceptable by assigning it a convenient numeric cost.

## 7. Valid sources for the missing operational inputs

Use the following evidence hierarchy when populating the numeric contract:

1. **Operational contract** — explicit SLO, resource budget, safety bound, or deployment requirement.
2. **Engineering constraint** — measured system limit or independently imposed resource ceiling.
3. **External empirical evidence** — directly relevant published or operational observations with clear population/context limits.
4. **Explicit design judgment** — allowed only when the first three sources are unavailable; label it as a design assumption and preserve the rationale.

The following are invalid derivation sources for the primary margins:

- observed pilot effect size;
- desired statistical power or sample size;
- whichever margin produces a convenient confirmatory result;
- post-generation case composition;
- retrospective threshold tuning.

## 8. Required decision worksheet

Before confirmatory freeze, fill one operational worksheet containing:

| Input | Required meaning | Allowed source | Status |
|---|---|---|---|
| Target case mix | Which target failures the decision contract covers | pre-study generator/operational specification | OPEN |
| `w_i` | Predeclared case-mix weights | operational population definition | OPEN |
| `V_D,i` | Downstream value difference from correct vs incorrect diagnosis | operational/evidence/design assumption | OPEN |
| `C_transfer` | Incremental resource cost of the transfer capability | engineering constraint/measurement | OPEN |
| `Delta Risk` | Incremental non-utility risk | safety/engineering constraint | OPEN |
| `B_D,min` | Minimum incremental deployment benefit | deployment/operational contract | OPEN |
| `C_R` unit | Repair-search cost unit | engineering measurement | OPEN |
| `delta_R+` | Acceptable practical increase | operational constraint | OPEN |
| `delta_R-` | Acceptable practical decrease, if needed | operational constraint | OPEN |
| Timeout/failure rule | Treatment of uncensored repair search | protocol contract | OPEN |
| Safety admissibility | Conditions that invalidate a repair/process | safety/engineering contract | OPEN |

## 9. Decision gate before confirmatory generation

The experiment remains a **candidate confirmatory design** until the worksheet is resolved sufficiently to derive the margins without reference to confirmatory outcomes.

The gate is satisfied only when:

- the operational use case is explicit;
- the target case mix and weighting are fixed;
- utility/cost/risk units are explicit;
- `delta_D` has a pre-study derivation or explicitly labeled design assumption;
- repair-cost units, timeout/censoring rules, and `delta_R+/-` are fixed where required;
- safety admissibility is fixed where applicable;
- the resulting thresholds do not depend on the eventual data.

## 10. What this document does not establish

This document does **not** establish:

- that the proposed transfer capability is useful;
- that Za-to-Zb transfer exists empirically;
- that the current toy pilot has practical significance;
- that a particular numeric margin is correct;
- that the confirmatory design is ready to run.

Those are separate empirical or design questions.

## 11. Next discriminating step

The next task is to instantiate exactly one concrete operational use case from:

```text
failure observation -> diagnosis -> repair/search choice -> repair -> independent validation
```

and populate the worksheet with evidence-backed or explicitly labeled design inputs. Only after that derivation should `delta_D`, `delta_R+/-`, nuisance assumptions, and sample size be finalized.
