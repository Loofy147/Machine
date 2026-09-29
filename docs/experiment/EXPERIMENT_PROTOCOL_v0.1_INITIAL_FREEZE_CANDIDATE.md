# Experiment Protocol v0.1 — Initial Freeze Candidate

**Status:** INITIAL-FREEZE CANDIDATE  
**Purpose:** Specify the experimental design for separating **Identifiability → Learning → Repair** before implementation or confirmatory execution.

> This document is a design candidate, not a result. No empirical result is frozen by this document.

## 1. Core architecture

The experiment is decomposed into exactly three layers:

\[
\boxed{\text{Identifiability}\rightarrow\text{Learning}\rightarrow\text{Repair}}
\]

No fourth architectural layer is introduced.

- **Identifiability:** what distinctions are observable or interventionally identifiable under the declared observation boundary and probe space.
- **Learning:** whether the system acquires and transfers diagnostic and probing capability.
- **Repair:** whether the selected intervention is replayable, generalizes, and preserves previously correct behavior.

## 2. Causal state and observation boundary

For each generated case:

\[
S=(Z,E,N,\ldots)
\]

where:

- `Z` = mechanism class used by the benchmark oracle;
- `E` = generator family;
- `N` = declared nuisance/design variables;
- `S` = full system state relevant to generation and execution.

The system's pre-probe observation is:

\[
X_0=Obs(S)
\]

`Obs` is an explicit interface boundary, not an informal description.

No assumption is made that:

\[
X_0\perp Z
\]

and no assumption is made that `Z` is uniquely identifiable from `X_0` alone.

## 3. Full target population

Define the full population first:

\[
P_0 = \text{all cases admitted by the declared generator specification}
\]

Derived subsets are explicitly labeled rather than silently replacing `P0`:

- `P_twin`: cases eligible for observational-twin identification experiments;
- `P_shift`: cases used for generator-family transport tests;
- `P_adaptive`: cases used for sequential probing tests;
- `P_natural`: external natural-fault population.

No post-generation success criterion is allowed to redefine `P0`.

## 4. Twin-constructibility audit

For each declared cell `(Zi, Zj, E, Obs)` the audit records:

\[
M^{(v)}\in\{\text{Constructible},\text{Provably Impossible},\text{Unknown}\}
\]

The audit version `v` is frozen and records at minimum:

- audit/build algorithm version;
- search/intervention space;
- search budget;
- random seed, where applicable;
- date/time of freeze;
- specification version used by the audit;
- declared state/observation domain;
- declared train/test or item-generation space.

### Interpretation

- **Constructible:** a legal construction/witness exists under the declared specification and budget.
- **Provably Impossible:** impossibility is established **relative to the complete declared audit contract**: the specified `(Zi, Zj, E, Obs)`, state/observation/probe domains, item-generation or train/test space, and any declared search/resource bound on which the proof depends. This is a local result, not a claim of general impossibility outside that contract.
- **Unknown:** the audit did not establish either of the above. A failed search under a finite budget is not, by itself, an impossibility proof.

`Unknown` is **not discarded silently**. It remains represented in `P0` and is excluded only from estimands that explicitly require established twin identifiability.

A future stronger audit may change `Unknown` to another status; therefore any comparison across experiments must record and compare `M-version` and its audit contract.

## 5. Observational-twin identification block

For cases with `M = Constructible`, a twin pair satisfies:

\[
Obs(S_i)=Obs(S_j)
\]

and:

\[
Z_i\neq Z_j.
\]

A legal witness must exist within the declared intervention space:

\[
A^*\in\mathcal A_B
\]

such that:

\[
D\big(Obs(do(A^*,S_i)),Obs(do(A^*,S_j))\big)\ge\delta_O.
\]

The witness establishes item eligibility; it is **not** supplied to the system under test.

The witness-search trace is not itself part of the case semantics. The final construction procedure is fixed before confirmatory generation.

### Important separation

Twin construction is primarily a **within-generator-family causal-identification test**. Cross-generator variation is a separate transport test. The protocol does **not** require every observational twin to cross generator families.

## 6. Generator-family transport

`E` is treated as a separate design factor.

- **Within-E:** used to isolate causal/mechanism discrimination while holding generator family fixed.
- **Across-E:** used to test transport/robustness to generator-family shift.

The benchmark must not encode `Z` deterministically through injector/generator identity.

Held-out generator families are required for transport claims.

For the confirmatory freeze, the **generator specification/contract** may be defined before the primary comparison, but the concrete family `E` need not be instantiated or built yet. Realized `E` families are constructed only after the confirmatory question, estimands, practical-effect bounds, and primary analysis have been frozen.

## 7. Witness-construction process audit

The audit result (`Constructible / Provably Impossible / Unknown`) is distinct from the construction path.

For confirmatory items, the final legal construction recipe is fixed before generation. Search effort, failed attempts, or incidental search traces must not become hidden item variables.

The resulting item-level process variables are recorded for audit and balance diagnostics. Their distributions are checked across relevant `Z/E` cells. They are not used post-hoc to select a favorable confirmatory sample.

This is a **design/process balance requirement**, not a claim that any such variable is mathematically ancillary.

## 8. Difficulty and risk design

Measured quantities such as:

\[
C^*_{info}=\min_A Cost_{info}(A)
\]

must not be used as post-hoc inclusion filters for confirmatory analysis.

Difficulty/risk strata are defined by pre-generation design variables. Any external calibration may estimate nuisance quantities or assess feasibility, but may not use observed confirmatory outcomes to redefine the primary pair, estimands, or practical-effect bounds.

The protocol distinguishes at least:

- information/probe difficulty;
- search-policy cost;
- execution cost;
- intervention/rollback risk.

A mismatch between intended stratum and measured difficulty is recorded rather than repaired by selective deletion.

## 9. Diagnostic policies

Three diagnostic policies are defined:

\[
\pi_0 = \text{no probe}
\]

\[
\pi_1 = \text{single-shot probe selected before observing probe results}
\]

\[
\pi_S = \text{sequential/adaptive probing}
\]

Their resource budgets must be declared and comparable before execution.

The primary confirmatory policy is:

\[
\boxed{\pi_S=S2}
\]

S0/S1 remain exploratory unless an additional multiplicity-controlled confirmatory family is frozen in advance.

Interpretation:

- `pi0 → pi1`: value of one diagnostic intervention;
- `pi1 → piS`: value of adaptive information acquisition.

Neither difference alone is sufficient to establish `WHAT-learning`.

## 10. Tier-3 diagnostic isolation

At tier-3:

\[
Probe_3 \equiv Intervention_3
\]

at the level of the system action (`install(ρ')`). There is no separate cheap observational probe at that layer.

Therefore diagnostic probing is disposable:

```text
B0 = pristine baseline
Dk = isolated diagnostic context from B0
install(ρ'_k) → observe → discard(Dk)
...
choose (d*, Δ*)
T = fresh treatment/measurement context from B0
install(Δ*) on T
measure durability/generalization/preservation
```

The final treatment measurement must not rely on accumulated state from the diagnostic trajectory.

## 11. Rollback contract

Rollback is a safety and efficiency mechanism, not the sole guarantee of a clean final measurement.

Define invariants sufficient to preserve all state relevant to subsequent observations:

\[
I_{rollback}
\]

Validate rollback compositionally within a declared finite stress bound:

\[
n\le N_{max}
\]

No unbounded compositionality claim is made without a separate proof.

## 12. Clone-fidelity contract

Clone fidelity is independently specified from rollback.

For the final measurement context:

\[
I_{clone}(Clone(B_0),B_0)=1
\]

for all declared state/invariants capable of affecting subsequent measurements within the experiment boundary.

Clone fidelity must pass bounded validation before confirmatory execution relying on fresh measurement contexts.

## 13. Confirmatory comparison hierarchy

Exactly one primary transfer direction is frozen **before confirmatory data collection and before any calibration capable of revealing pair-specific empirical outcomes that could influence pair selection**:

\[
\boxed{Z_a^*\rightarrow Z_b^*}
\]

with the frozen definitions:

\[
Z_a^*=\texttt{persistence/decay-fault}
\]

\[
Z_b^*=\texttt{context-discrimination-fault}.
\]

The definitions, contamination rule, transfer-arm contract, and rationale are specified in `PRIMARY_COMPARISON_FREEZE_V0.1.md`. Selection is based on frozen mechanism semantics, not prior outcomes.

All other pairwise contrasts and secondary metrics are exploratory unless a multiplicity-controlled confirmatory family is frozen in advance.

## 14. Estimand separation

The protocol distinguishes:

\[
\theta_D=\text{diagnostic-transfer effect}
\]

\[
\theta_P=\text{probe-policy transfer effect}
\]

\[
\theta_R=\text{repair-transfer effect}
\]

\[
\theta_V=\text{validation/generalization transfer effect}
\]

Their scales, populations, policies, confidence procedures, and practical-equivalence/superiority bounds are frozen in the Statistical Comparison Plan.

## 15. Primary dissociation

The confirmatory WHAT/HOW dissociation is successful only if:

\[
\boxed{\theta_D>\delta_D}
\]

and the pre-specified repair-cost equivalence region contains the confidence interval for `theta_R`:

\[
\boxed{-\delta_R^-<\theta_R<\delta_R^+}
\]

or, only if explicitly justified as symmetric,

\[
\boxed{|\theta_R|<\delta_R}.
\]

A favorable exploratory pair may never replace the frozen primary comparison.

## 16. Unknown and overall reporting

`Unknown` twin-audit cases remain in the `P0` accounting and are explicitly reported. They do not enter estimands requiring established twin identifiability.

Overall system curves on `P0` may be reported separately from twin-specific causal estimands.

## 17. Freeze order

The confirmatory sequence is:

\[
\boxed{
G_{spec}
\rightarrow M^{(v)}
\rightarrow P_0
\rightarrow (Z_a^*,Z_b^*)
\rightarrow estimands
\rightarrow \delta
\rightarrow primary\ analysis
\rightarrow pre-generation\ design\ strata
\rightarrow external\ calibration\ (nuisance\ only)
\rightarrow confirmatory\ freeze
\rightarrow instantiate\ E
\rightarrow confirmatory\ generation/run
\rightarrow analysis
}
\]

Here `G_spec` is the frozen generator specification/contract, not the realized generator-family set `E`. `E` is intentionally not instantiated until the primary question and statistical decision structure are frozen.

External calibration may estimate nuisance quantities such as baseline rates, variance/dispersion, clustering/design effects, or feasibility of predeclared design strata. It must not select or replace the primary pair, redefine the estimands, or choose practical-effect margins from observed outcomes.

After confirmatory freeze:

- no replacement of the primary pair;
- no post-hoc exclusion to improve the confirmatory result;
- no change to estimand definitions or practical-effect bounds;
- no redefinition of `Z`;
- no redefining of `P0` from observed outcomes;
- no use of realized `E` results to retroactively alter the frozen confirmatory question.

**Status:** Initial-freeze candidate. Primary comparison and transfer-arm structure are frozen at design level; numerical practical-effect margins and final nuisance/sample-size specifications remain open.
