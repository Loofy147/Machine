# Decision Use Case and Margin Derivation v0.2

**Status:** BOUNDED LABORATORY CONTRACT — DESIGN INPUTS UNDER REVIEW  
**Branch:** `research/confirmatory-freeze-order-v0.1`  
**Supersedes:** `DECISION_USE_CASE_AND_MARGIN_DERIVATION_V0.1.md` as the working operational worksheet; v0.1 remains historical lineage.

This document turns the confirmatory question into one concrete machine-operational use case. It deliberately incorporates lessons from the first exploratory experiments without promoting those experiments to confirmatory evidence.

---

## 1. Operational use case

### 1.1 Situation

A machine is executing a reusable operational process over inputs arriving under changing conditions. The process has:

- retained historical operational information;
- a context/indexing mechanism;
- a diagnostic probe interface;
- a repair/search procedure;
- an independent validation procedure.

A persistent performance failure is observed.

The machine must decide whether to:

1. continue operating/searching locally;
2. probe for a mechanism-level explanation;
3. change the historical persistence/decay rule;
4. change the context/indexing relation;
5. proceed to the existing repair controller;
6. reject or escalate after an unsuccessful repair/validation attempt.

The confirmatory comparison asks whether diagnostic capability learned from **persistence/decay failures (`Za`)** transfers to fresh **context-discrimination failures (`Zb`)**.

The repair controller is held fixed. The transferred artifact may modify diagnosis/probe selection only.

### 1.2 Why this is an operational decision rather than a benchmark score

The relevant machine event is not merely:

```text
label = Za or Zb
```

The relevant event is:

```text
failure observed
  -> diagnostic action selected
  -> evidence accumulated
  -> mechanism identified
  -> existing repair regime entered
  -> repair independently validated
  -> accept / reject / escalate
```

A diagnosis has practical value only if changing the diagnosis changes this downstream path in a useful way.

---

## 2. Design lessons carried forward from the first experiments

The following are durable design constraints derived from the exploratory corpus.

### L1 — Reconfiguration is not adaptation

The earlier executable-representation experiment showed that mutable representation can support adaptive modification when an external search algorithm supplies the adaptation procedure. It did not establish that representation mutation itself supplies adaptive intelligence.

**Operational consequence:** success must be attributed to the diagnostic/decision process actually under test, not to the mere availability of a structural intervention.

Source: `docs/EXPERIMENT-B-CLEAN.md`.

### L2 — Search dynamics can dominate substrate effects

The same exploratory experiment showed large differences between search procedures inside a small hypothesis space.

**Operational consequence:** diagnostic transfer must not be confounded with a better or different repair/search algorithm. The repair controller, action vocabulary, validation, and budget are identical across baseline and transfer arms.

### L3 — Evaluation quality can hurt

The nine-mechanism review found that a noisy evaluation mechanism could reduce performance relative to a strong immediate heuristic.

**Operational consequence:** probes are resources, not free information. A probe is useful only through the decision-relevant information it produces relative to its cost and risk.

### L4 — Context-free accumulation is unsafe as a default abstraction

The nine-mechanism review found that scalar operation-level accumulation can become harmful when experience is not indexed by the conditions under which the consequence occurred.

**Operational consequence:** the transferred diagnostic artifact must be inspected as an auditable object and its allowed content must exclude target labels, target outcomes, generator IDs, and direct repair shortcuts. Historical evidence may guide probe selection, but it may not become an unbounded target-specific shortcut.

### L5 — Failure detection, localization, intervention selection, and generalization are separate

The error-source-localization work explicitly separates:

```text
failure detection
fault localization
intervention selection
post-intervention generalization
```

**Operational consequence:** the primary endpoint is mechanism identification; repair/search cost and validation are separate endpoints. A system that detects failure but chooses the wrong mechanism is not credited as correctly diagnosing.

### L6 — Structural change requires an explicit cost

The representation-localization work warns that unrestricted representational expansion can always purchase a solution by adding distinctions.

**Operational consequence:** every probe and repair-search action consumes a declared resource unit, and representation/context changes cannot be treated as free capability.

### L7 — Causal distinctions must survive matched controls

Earlier work exposed confounding when a mechanism bundled multiple roles, such as domain validity, resource limits, and capability availability.

**Operational consequence:** the Za/Zb distinction must be implemented as a causal difference while holding unrelated control surfaces fixed.

### L8 — Historical experiments remain exploratory

None of the above observations are being imported as confirmatory effect estimates or as numerical margin values.

---

## 3. Minimal operational contract

The laboratory contract is intentionally bounded. It is not a claim about deployment in the physical world.

### 3.1 Observation boundary

The machine receives only the normal operational observation stream:

```text
state/inputs
observed outcomes
probe consequences
resource consumption
validation outcomes
```

The machine does not receive:

```text
hidden fault label
injector identity
expected repair class
target generator ID
post-hoc explanation from the harness
```

### 3.2 Actions

The primary diagnostic controller may select only actions in a predeclared probe/action vocabulary.

A probe returns an observable consequence and consumes one or more resource units.

After diagnosis, the same repair controller and repair budget are used in both arms.

### 3.3 Terminal decisions

Every case terminates in exactly one of:

```text
VALIDATED_RECOVERY
VALIDATED_NO_RECOVERY
ESCALATE_TIMEOUT
ESCALATE_SAFETY
```

No successful-looking result is accepted without independent validation.

---

## 4. What counts as a correct diagnosis

For target case `i`:

\[
Y_{D,i}=1\{\hat Z_i=Z_i\}.
\]

Correct diagnosis requires that the inferred mechanism match the mechanism actually injected by the generator specification.

A repair that happens to succeed does **not** retroactively make the diagnosis correct.

A diagnosis that is correct but followed by an independently invalid repair is still a correct diagnosis, but it is not a successful operational episode.

This separation is mandatory because otherwise the experiment collapses:

```text
what was inferred
```

into:

```text
what eventually worked
```

---

## 5. Decision utility: machine-native representation

The base operational utility is a vector first, scalar second.

For each case record:

```text
recovery outcome
validation outcome
probe units consumed
repair-search units consumed
elapsed decision units
safety/admissibility violations
```

The primary design principle is:

> Preserve operationally distinct consequences as separate dimensions before any scalar utility mapping is introduced.

A generic case utility can therefore be represented as:

\[
U_i =
(U_{recovery},
 U_{validation},
 -C_{probe},
 -C_{repair},
 -C_{delay},
 -R_{safety}).
\]

A scalar projection is permitted only after the unit, weights, admissibility constraints, and decision owner are declared.

This avoids inventing a monetary value merely to force unrelated quantities into one equation.

---

## 6. Operational consequence of diagnostic correctness

For each target case class or stratum `i`, define:

\[
V_{D,i}=
U_i(\text{correct diagnosis followed by the fixed downstream process})
-
U_i(\text{incorrect diagnosis followed by the fixed downstream process}).
\]

Importantly, the downstream process must be held to the frozen repair controller and validation contract when computing this contrast.

`V_D,i` is therefore a property of the decision contract and case mix, not of the observed confirmatory treatment effect.

If a separate `L_D` is introduced, it must capture only harm not already present in `V_D,i`.

---

## 7. Practical diagnostic margin

The primary statistical effect remains:

\[
\theta_D=P(Y_D=1|T_b^{transfer})-P(Y_D=1|T_b^{baseline}).
\]

For heterogeneous cases, the operational threshold is not necessarily a single naive probability number. The preferred decision rule is:

\[
\Delta U_D(\theta_D, w, V_D, C, R) \ge B_{D,min}
\]

subject to all admissibility constraints.

A scalar `delta_D` may be derived only when the case-mix and utility model establish a stable mapping from diagnostic-probability improvement to expected operational benefit.

In the homogeneous special case:

\[
\delta_D=
\frac{B_{D,min}+C_{transfer}+\Delta Risk}{V_D}.
\]

This is a special-case derivation, not a default law.

If the derived value is outside the valid probability domain, the decision contract is internally inconsistent for this endpoint and must be repaired rather than truncated to `[0,1]`.

---

## 8. Repair-search cost and the WHAT/HOW dissociation

Repair cost is measured from the first repair-search action after diagnosis until the first independently validated sufficient repair.

\[
\theta_R=E[C_R|transfer]-E[C_R|baseline].
\]

The preferred equivalence region is:

\[
-\delta_R^- < \theta_R < \delta_R^+.
\]

The purpose is not to claim that repair costs are literally identical. It is to test whether diagnostic transfer changes **what is recognized** without materially changing **how the fixed repair system behaves**.

If safety or irreversible side effects differ, practical equivalence cannot override those constraints.

---

## 9. Probe economics

Probe count is a secondary endpoint:

\[
\theta_P=E[C_P|transfer,S2]-E[C_P|baseline,S2].
\]

A lower probe count is not automatically better.

A probe may be worth its cost if it materially increases diagnostic correctness or reduces an otherwise larger downstream loss.

Therefore the first experiment records:

```text
probe cost
probe consequence
change in diagnostic belief/output
subsequent decision
```

rather than optimizing raw probe count alone.

---

## 10. Safety/admissibility contract

Safety is represented as an admissibility condition rather than an arbitrary compensatory scalar.

A case is invalid for the intended operational claim if an intervention violates a predeclared invariant such as:

```text
forbidden transition
irreversible modification outside declared sandbox
validation bypass
resource ceiling violation
```

A safety-violating episode cannot be converted into an acceptable one by assigning a sufficiently negative numerical utility after the fact.

---

## 11. Case-mix definition

The primary target population is fresh `Zb = context-discrimination-fault` cases.

At minimum, target strata must vary along the dimensions that can alter diagnostic utility without revealing the hidden mechanism, for example:

```text
failure severity
probe informativeness
context-change magnitude
history length
baseline recoverability
```

Strata are generated before outcome observation and frozen before confirmatory execution.

No stratum may be added, removed, or reweighted after observing the transfer effect.

---

## 12. Resource accounting

Every arm must use the same accounting vocabulary:

```text
C_P = diagnostic probe units
C_R = repair-search units
C_V = validation units
C_total = declared aggregate resource measure, if a scalar total is required
```

The conversion between units is not assumed.

If the experiment needs a scalar budget, the conversion coefficients must be declared independently before confirmatory data.

This directly prevents the earlier failure mode in which one bundled resource notion could masquerade as several distinct mechanisms.

---

## 13. Minimum complete episode ledger

Each case should record at least:

| Field | Meaning |
|---|---|
| `case_id` | immutable case identifier |
| `target_stratum` | predeclared target stratum |
| `hidden_Z` | harness-only ground truth |
| `initial_observation` | observation boundary at episode start |
| `diagnostic_trace` | ordered probes and observed consequences |
| `diagnosis` | mechanism selected by machine |
| `Y_D` | diagnostic correctness |
| `repair_trace` | fixed-controller repair actions |
| `C_R` | repair-search cost |
| `validation_trace` | independent validation evidence |
| `Y_V` | validation result |
| `terminal_state` | recovery / no recovery / timeout / safety escalation |
| `C_P` | probe cost |
| `safety_flags` | admissibility violations |
| `artifact_version` | exact transfer-artifact identity or null |

The transfer artifact itself must have independent provenance and content audit.

---

## 14. Primary decision rule

The scientific and operational decisions are kept separate.

### Scientific layer

Test whether the primary diagnostic effect exceeds the predeclared practical threshold:

\[
\theta_D > \delta_D.
\]

### Repair dissociation layer

Check whether:

\[
-\delta_R^- < \theta_R < \delta_R^+.
\]

### Operational layer

Only if the statistical conditions and all admissibility constraints are satisfied may the result be interpreted as operationally useful under this bounded laboratory contract.

Failure of the utility gate does not erase a statistically detectable effect; it means the effect is not sufficiently valuable under the declared decision contract.

---

## 15. What the first experiments explicitly prevent us from doing

We will **not**:

- claim that mutable representation is itself the adaptive mechanism;
- let a better repair/search algorithm masquerade as diagnostic transfer;
- treat raw probe reduction as sufficient evidence of usefulness;
- treat context-free accumulated scores as transferable knowledge without auditing context;
- infer mechanism identity from whichever repair happened to work;
- credit post-hoc structural expansion without charging its resource cost;
- collapse detection, localization, intervention selection, and validation into one score;
- use pilot outcomes to select `delta_D`, `delta_R`, or the confirmatory case mix;
- use the desired sample size to manufacture a practical margin.

---

## 16. Remaining design inputs

The operational use case is now concrete, but the following numerical/design inputs remain open:

1. target stratum definitions and frozen weights `w_i`;
2. unit definitions for `C_P`, `C_R`, and optionally `C_V`;
3. admissible resource ceiling;
4. definition of the minimum deployment/operational benefit `B_D,min`;
5. case-level or stratum-level `V_D` values;
6. treatment of incremental transfer overhead and risk;
7. numerical `delta_D` if a scalar threshold is still warranted;
8. numerical `delta_R+/-`;
9. repair timeout/censoring/failure rule;
10. final statistical estimator/model family where required by the data structure;
11. nuisance assumptions and sample size.

These inputs must be filled from operational constraints, engineering measurements, relevant external evidence, or explicitly labeled design judgment—not from confirmatory outcomes.

---

## 17. Current status

**ESTABLISHED WITHIN PROJECT DESIGN**

- The experiment now has one explicit operational episode: persistent failure -> diagnostic probing -> mechanism decision -> fixed repair -> independent validation.
- Diagnostic correctness is separated from repair success.
- Probe cost, repair cost, validation, and safety are separate observables.
- The transfer artifact is constrained to diagnosis/probe selection.
- The first-experiment confounders are converted into explicit design constraints.

**OPEN**

- The numerical operational contract is not yet frozen.
- The case mix and utility weights are not yet frozen.
- No practical margin is yet authorized for confirmatory use.

**NEXT TEST**

Construct a single target-stratum table and fill one complete episode specification for each stratum before choosing any numerical margin.
