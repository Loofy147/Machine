# Canonical Operational Case — Zb Context-Merge Fault v0.1

**Status:** DESIGN FIXTURE — NOT CONFIRMATORY EVIDENCE  
**Branch:** `research/confirmatory-freeze-order-v0.1`

This document instantiates one concrete bounded-laboratory operational case for the decision-first derivation path. It is not a claim that this case represents all `Zb` failures.

## 1. Purpose

Instantiate exactly one fresh target-class (`Zb`) failure so that the project can inspect the complete operational chain before assigning practical margins:

```text
failure observation
  -> diagnosis
  -> probe/search choice
  -> repair
  -> independent validation
  -> terminal decision
```

The case is deliberately machine-native. It does not require a human-like concept such as intuition, emotion, or introspection.

## 2. Fault class

Primary target class:

```text
Zb = context-discrimination-fault
```

Mechanism:

- historical information remains valid for the context in which it was produced;
- the persistence/retention rule is correct;
- the context/indexing key is insufficient;
- records from distinct operating contexts are therefore merged or addressed together;
- the resulting historical influence is applied to the wrong context.

This is distinct from `Za`, where the historical influence persists beyond its declared validity regime.

## 3. Minimal fixture

Use two contexts:

```text
C_A
C_B
```

and two historical records:

```text
h_A = (context=C_A, state=s, observed transition=t_A, consequence=q_A)
h_B = (context=C_B, state=s, observed transition=t_B, consequence=q_B)
```

The local state component `s` is intentionally identical so that the context relation is causally necessary.

The correct context-conditioned consequences differ:

```text
q_A != q_B
```

The healthy addressing relation is:

```text
lookup(context, state)
```

The injected fault collapses it to an insufficient key such as:

```text
lookup(state)
```

The history itself is not stale. No persistence violation is injected.

## 4. Observable failure

The machine receives a fresh target case from `C_B` with state `s` and obtains a result consistent with the historical consequence associated with `C_A`.

At the observation boundary the machine may see:

- current input/state;
- observed output or consequence;
- accessible historical records through the declared interface;
- probe outcomes;
- resource cost and reversibility of probes;
- independent validation outcomes.

It does **not** receive:

- the hidden label `Zb`;
- the injector identity;
- the statement that the context key is wrong;
- the correct repair;
- a target-specific shortcut.

## 5. What must remain true

The fixture is eligible only if all of the following hold:

| Invariant | Required condition |
|---|---|
| Persistence | historical record remains within its intended validity lifetime |
| Context necessity | identical local state can require different consequences across contexts |
| Fault isolation | injected causal defect is the context/indexing relation |
| Hidden mechanism | `Zb` is absent from system-visible state |
| Repair separation | the repair controller is identical across baseline and transfer arms |
| Validation independence | success is checked on fresh observations not used for diagnosis |

## 6. Diagnostic probe vocabulary

The primary S2 diagnostic policy may choose from a predeclared probe family.

### P1 — context split probe

Hold the local state fixed and vary the context while querying historical influence.

Expected informative signature under `Zb`:

```text
same state
+ different context
-> materially different required consequence
```

but the retrieved historical influence remains effectively shared.

### P2 — persistence/age probe

Hold context fixed while varying history age or retention eligibility.

Expected informative signature under healthy persistence behavior:

```text
within validity regime
-> history remains applicable
```

A `Za` signature would instead appear only when validity is exceeded.

### P3 — replay/control probe

Replay a matched case inside the same context to test whether the observed failure is stable and attributable to context rather than transient execution noise.

The exact probe cost must be defined before confirmatory generation.

## 7. Diagnostic decision

A diagnosis is correct only when the machine identifies:

```text
context-discrimination-fault
```

rather than merely reporting:

```text
failure observed
```

or:

```text
historical information is wrong
```

The diagnostic endpoint therefore remains:

```text
Y_D = 1{Zhat = Z}
```

A diagnosis must be produced before the repair controller receives the diagnostic result.

## 8. Repair boundary

The same repair controller is used in baseline and transfer arms.

The controller receives:

- the original case state;
- the diagnostic output;
- the same repair-action vocabulary;
- the same search budget;
- the same validation procedure.

For this `Zb` fixture, a sufficient repair changes the context addressing relation so that history is indexed by the required context distinction.

A repair is successful only after independent validation on fresh cases.

The experiment does **not** credit the diagnostic system merely because it proposes a repair. The repair controller must establish sufficiency independently.

## 9. Why diagnosis has operational value here

The primary WHAT/HOW separation requires that diagnostic transfer can matter without giving the transfer arm a different repair algorithm.

Therefore the immediate operational consequence of a correct `Zb` diagnosis is defined at the **pre-repair diagnostic stage**:

```text
correct mechanism identification
-> selection of an informative probe/search regime
-> fewer irrelevant or misleading probes
-> lower diagnostic resource cost / delay
-> same repair controller
```

The repair mechanism itself is not credited to the transfer artifact.

This makes `theta_P` and the resource component of diagnostic utility observable without conflating them with `theta_R`.

## 10. Terminal decisions

After repair and independent validation, the case terminates in one of:

```text
ACCEPT_RECOVERED
REJECT_UNRECOVERED
ESCALATE_BUDGET
```

The terminal decision rule is fixed before confirmatory data collection.

`ESCALATE_BUDGET` is not coded as successful repair and is not assigned an arbitrary finite repair cost. The censoring/failure policy belongs in the statistical protocol.

## 11. Case-level utility decomposition

For this bounded laboratory case, define utility components without monetary conversion:

```text
U_case = recovery_value
         - diagnostic_resource_cost
         - delay_cost
         - safety_or_irreversibility_penalty
```

The terms are conceptual until operational units are fixed.

For a single case, the diagnostic-value contrast is:

```text
V_D = U(correct diagnosis + downstream process)
      - U(incorrect diagnosis + downstream process)
```

The expected value should only be populated after the laboratory contract specifies the units and weights.

## 12. Required measurement record

Every case should record at minimum:

```text
case_id
hidden_fault_class
initial_observation
probe_sequence
probe_outcomes
probe_cost
final_diagnosis
repair_controller_version
repair_action_sequence
repair_cost
validation_inputs
validation_outcome
terminal_decision
safety_admissible
```

The hidden fault class is harness-only and must never cross the system observation boundary.

## 13. First-pass strata

The single case is a canonical fixture, not the whole target population. Before confirmatory generation, fresh `Zb` cases should be stratified by predeclared dimensions that can change diagnostic value or risk, such as:

| Stratum dimension | Example levels | Why it matters |
|---|---|---|
| Context contrast | low / medium / high | changes how detectable the context error is |
| History density | sparse / moderate / dense | changes collision opportunity |
| Consequence separation | small / medium / large | changes downstream impact of wrong reuse |
| Probe ambiguity | low / medium / high | changes diagnostic resource requirement |
| Repair risk | low / medium / high | changes safety relevance of misdiagnosis |

The actual number and cut points of strata remain OPEN until `G_spec` is frozen.

## 14. Required controls from earlier experiments

The fixture inherits the following safeguards from earlier work:

1. **Context-conditioned experience:** experience must not collapse to a single operation-level score. Any diagnostic artifact must preserve the conditions under which consequences were observed.
2. **Search fairness:** informative probes must be compared under declared resource budgets; an intervention cannot appear superior merely because it receives hidden extra compute.
3. **Representation cost:** the context distinction must have an explicit representation/resource cost; maximal repartition is not a free solution.
4. **Failure-source separation:** the same observed failure must remain compatible with competing causal explanations during diagnosis.
5. **Hidden mechanism:** the injector must not be a deterministic proxy for the hidden class.
6. **Repair separation:** transferred history affects diagnosis/probe selection only, not the repair algorithm or repair budget.
7. **Independent validation:** recovery is established on fresh observations, not on the diagnostic trajectory alone.

## 15. Falsifiers for this operationalization

This case design is inadequate if any of the following becomes true:

- `P1` directly exposes the hidden class through an unmodeled oracle variable;
- a healthy `Za`-style persistence change produces the same observable signature under the declared probe set;
- the repair controller behaves differently between baseline and transfer because the artifact leaks repair information;
- diagnostic advantage disappears after matching probe budget and information availability;
- a context split always solves the case without any diagnostic inference, making the diagnosis endpoint vacuous;
- independent validation does not distinguish stable recovery from overfitting the diagnostic fixture;
- the case has no plausible operational consequence beyond the binary diagnostic label.

## 16. Current status

**DESIGN-READY AS A CANONICAL CASE, NOT CONFIRMATORY DATA.**

What is now concrete:

```text
Zb mechanism
-> observable failure
-> candidate probes
-> diagnostic endpoint
-> fixed repair boundary
-> independent validation
-> terminal decisions
-> measurable resource/risk consequences
```

What remains open:

```text
operational units
case-mix weights
V_D values
delta_D
delta_R+/delta_R-
timeout/censoring policy
sample-size nuisance assumptions
```
