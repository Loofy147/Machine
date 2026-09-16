# Primary Comparison Freeze v0.1

**Status:** FREEZE CANDIDATE — DESIGN LEVEL  
**Parent:** `EXPERIMENT_PROTOCOL_v0.1_INITIAL_FREEZE_CANDIDATE.md`  
**Statistical plan:** `STATISTICAL_COMPARISON_PLAN_v0.1.md`

## 1. Primary direction

The single primary transfer direction is:

\[
\boxed{Z_a^* \rightarrow Z_b^*}
\]

with:

\[
Z_a^* = \texttt{persistence/decay-fault}
\]

and:

\[
Z_b^* = \texttt{context-discrimination-fault}.
\]

The direction is fixed by mechanism theory before confirmatory item generation. It is not selected from prior performance.

## 2. Why these classes

The two classes are intentionally defined as distinct causal mechanisms that can produce a similar observable failure: inappropriate reuse of historical operational information after conditions change.

### `Z_a*` — persistence/decay fault

The machine retains an otherwise valid historical influence beyond its declared validity regime. The causal defect is persistence/decay: the historical record or its influence does not attenuate or expire when the relevant regime changes.

The defining intervention changes retention/decay behavior while keeping the context partitioning rule fixed.

### `Z_b*` — context-discrimination fault

The machine applies historical information across distinct operating contexts that should be separated. The causal defect is context discrimination/indexing: observations from different regimes are merged or addressed through an insufficient context key despite the history itself being otherwise retained within its intended lifetime.

The defining intervention changes the context/indexing relation while keeping the persistence rule fixed.

These definitions are extensionally different. An item belongs to one class according to the mechanism actually injected by the benchmark specification, not according to which repair happened to succeed.

## 3. Why the primary pair is not the historical nine-mechanism taxonomy

The earlier nine-mechanism work is exploratory evidence and already exposed representation, variation, composition, reformation, evaluation, accumulation, gating, and related operational mechanisms to empirical outcomes.

Those earlier experiments therefore cannot be reused as untouched confirmatory instances merely by selecting a favorable pair from the existing result table.

The present pair introduces two new fault classes defined around the still-open relation families of **persistence/decay** and **context discrimination**. Prior contextual-credit work motivates these relations but did not instantiate this pair as a hidden causal fault taxonomy with the present transfer question.

This is a repository-level contamination claim only: external experiments not recorded here are outside this audit.

## 4. Required separation of causal roles

The benchmark must ensure:

- `Z_a*` changes persistence/decay while holding context indexing fixed;
- `Z_b*` changes context discrimination/indexing while holding persistence/decay fixed;
- repair mechanisms for the two classes are not identical aliases;
- the hidden class label is never exposed to the system;
- injector identity is not a deterministic proxy for `Z` in the confirmatory observation boundary.

## 5. Primary transfer arms

The target population is fresh cases from `Z_b*` only.

### Baseline

`T_b^baseline` receives:

- the same fresh target-case distribution;
- the same initial state;
- the same S2 diagnostic policy interface and budget;
- no transferred diagnostic artifact from `Z_a*` episodes;
- the same repair controller available after diagnosis.

### Transfer

`T_b^transfer` receives exactly the same conditions, except that it also receives a frozen diagnostic artifact produced from designated source-class (`Z_a*`) training episodes.

The transferred artifact may alter **diagnostic identification/probe selection only**. It must not contain:

- target-class labels;
- target-case outcomes;
- target-specific repair candidates;
- target-specific repair search shortcuts;
- generator identifiers that reveal the target mechanism;
- hidden fault identifiers.

The repair search procedure, action vocabulary, validation procedure, and repair budget are identical between arms.

This separation is required for the primary WHAT/HOW dissociation: transfer may change **what mechanism the machine recognizes or how it probes**, but not directly change **how it repairs**.

## 6. Primary policy arm

The primary diagnostic policy is:

\[
\boxed{S2 = \text{sequential/adaptive probing}}
\]

S0 and S1 remain secondary/exploratory comparisons unless a separate multiplicity-controlled family is frozen before data collection.

## 7. Eligibility and twin requirement

The primary twin-specific estimands require an audit result:

\[
M^{(v)}=\text{Constructible}
\]

for the declared `(Za*, Zb*, E, Obs, domains, budget/specification)` contract.

`Provably Impossible` is interpreted only within that complete declared contract. `Unknown` remains in `P0` accounting but is not silently converted to failure or exclusion from the overall target population.

No confirmatory case is included solely because a post-hoc search happened to make it easier or more favorable.

## 8. Directional rationale

The source class is the narrower persistence/decay relation. The target class introduces context discrimination as the additional causal distinction. The frozen transfer question is therefore:

> Can diagnostic capability acquired from recognizing persistence/decay failure transfer to a fresh failure whose causal mechanism is instead context discrimination, while the target repair-search procedure remains unchanged?

The reverse direction is not primary. It remains exploratory.

## 9. Contamination rule

If later audit reveals that prior exposure included the present exact class definitions, transfer artifact, target fixture family, or outcome-bearing benchmark cases in a way that could reveal the primary contrast or its expected result, the confirmatory population is contaminated.

Contaminated cases remain historical/exploratory and cannot be silently relabeled as confirmatory.

## 10. Freeze state

At this stage the following are frozen at the design level:

- primary direction: `persistence/decay-fault -> context-discrimination-fault`;
- primary policy: `S2`;
- target population: fresh `Z_b*` cases;
- transfer artifact scope: diagnostic identification/probe selection only;
- repair controller and repair budget: held constant across arms;
- reverse direction: exploratory;
- prior historical experiments: exploratory, not confirmatory.

The numerical practical-effect margins \(\delta_D,\delta_R\) are **not yet numerically frozen** because the repository currently contains no independent utility/cost/safety specification from which defensible SPIE values can be derived. Inventing those values from exploratory outcomes would violate the freeze rule.

**Status:** primary-comparison and arm structure frozen at design level; numerical margins remain an explicit pre-confirmatory blocker.
