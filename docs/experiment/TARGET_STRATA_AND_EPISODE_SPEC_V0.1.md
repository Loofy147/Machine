# Target Strata and Episode Specification v0.1

**Status:** DESIGN WORKSHEET — NUMERIC WEIGHTS OPEN  
**Branch:** `research/confirmatory-freeze-order-v0.1`  
**Parent:** `DECISION_USE_CASE_AND_MARGIN_DERIVATION_V0.2.md`

This document defines the target case strata and the minimum complete episode needed to derive operational utility and practical margins without using confirmatory outcomes.

---

## 1. Purpose

The primary target population is fresh `Zb = context-discrimination-fault` cases.

The target population cannot be treated as homogeneous merely because every case has the same hidden mechanism class. The operational value of a diagnosis can change with:

- severity of the failure;
- how informative probes are;
- how strongly contexts differ;
- how much historical information is available;
- how recoverable the case is under the fixed repair controller.

Therefore the case mix is represented explicitly before numerical margins are derived.

---

## 2. Target stratum axes

### S1 — failure severity

`low / medium / high`

Meaning: the operational consequence of leaving the failure unresolved for one additional decision cycle.

Important constraint: severity is defined from the operational contract, not from the eventual treatment result.

### S2 — context-change magnitude

`small / medium / large`

Meaning: magnitude of the change separating the contexts that should no longer share historical information.

The generator may use a normalized machine-native scale, but the mapping must be frozen before confirmatory execution.

### S3 — probe informativeness

`low / medium / high`

Meaning: expected ability of a permitted diagnostic probe to distinguish persistence/decay behavior from context-indexing behavior while respecting the fixed observation boundary.

This is a pre-study property of the probe design, not a label derived from observed success.

### S4 — history length

`short / medium / long`

Meaning: amount of retained historical operational information available at episode start.

This axis matters because context-blind accumulation was an identified exploratory failure mode.

### S5 — repair recoverability

`direct / indirect / difficult`

Meaning: expected accessibility of a sufficient repair to the unchanged repair controller under the declared search budget.

The repairability descriptor must be defined from the generator contract, not from which arm happens to succeed.

---

## 3. Minimum target strata

The first confirmatory candidate may use a reduced factorial design rather than all combinations, but the following distinctions must remain representable:

| Stratum | Severity | Context change | Probe informativeness | History | Repair recoverability | Weight |
|---|---|---|---|---|---|---|
| A | low | small | low | short | direct | OPEN |
| B | low | large | high | short | direct | OPEN |
| C | high | small | high | long | indirect | OPEN |
| D | high | large | low | long | difficult | OPEN |

These four rows are design placeholders, not final generator quotas.

A final design may add or remove strata only before confirmatory generation and with documented rationale independent of observed outcomes.

---

## 4. Why these axes matter to the margin

A diagnostic success probability change of the same numerical size can have different operational value across strata.

For stratum `s`:

\[
V_{D,s}
=
U_s(correct\ diagnosis + fixed\ downstream\ process)
-
U_s(incorrect\ diagnosis + fixed\ downstream\ process).
\]

The population-level operational consequence is therefore represented as:

\[
\Delta U_D
=
\sum_s w_s\Delta p_sV_{D,s}
-C_{transfer}
-\Delta Risk.
\]

The weights `w_s` and values `V_D,s` must be established before confirmatory outcomes.

If the experiment cannot justify stable `V_D,s`, it must not force a single scalar `delta_D` merely for statistical convenience.

---

## 5. Complete episode specification

Each target case follows the same logical episode.

### Phase 0 — initialization

The harness creates a fresh target case with:

```text
hidden mechanism: Zb
stratum: predeclared s
initial state: fresh
artifact: baseline = null / transfer = frozen Za artifact
repair controller: fixed
budget: fixed
```

The machine receives only the declared observation boundary.

### Phase 1 — failure observation

The system encounters the injected context-discrimination failure.

The machine records:

```text
initial observation
failure evidence
resource state
```

No hidden label is exposed.

### Phase 2 — diagnostic probing

Under S2, the machine may select sequential probes.

For each probe `j`, record:

```text
probe_id
pre_probe_state hash / identifier
probe action
observable consequence
resource cost
action reversibility
post_probe observation
```

The artifact can influence probe selection only in the transfer arm.

### Phase 3 — mechanism decision

The machine emits:

```text
Z_hat in {persistence/decay-fault, context-discrimination-fault, unresolved}
```

`unresolved` is permitted only if the protocol explicitly allows escalation at the diagnostic stage. It must never be scored as correct merely because the repair later succeeds.

### Phase 4 — fixed repair search

The repair controller is identical across baseline and transfer.

The controller receives the diagnosis output and the same repair vocabulary, search budget, and validation contract.

Record:

```text
repair candidate sequence
search cost
rollback events
first independently validated sufficient repair
```

### Phase 5 — independent validation

Validation is performed through an independently specified procedure that was not selected from the observed treatment result.

At minimum the validation set must be distinct from the diagnostic probes and must include replay/held-out checks appropriate to the generator.

Record:

```text
validation evidence
Y_V
stability/replay status
```

### Phase 6 — terminal decision

The case terminates in:

```text
VALIDATED_RECOVERY
VALIDATED_NO_RECOVERY
ESCALATE_TIMEOUT
ESCALATE_SAFETY
```

---

## 6. The critical counterfactual

The value of diagnosis is defined by comparing downstream consequences while keeping the repair machinery fixed.

For case `i`, conceptualize two downstream paths:

```text
correct diagnosis -> fixed repair controller
incorrect diagnosis -> same fixed repair controller
```

The experiment does not observe both paths for the same physical episode. The utility contract therefore has to define, before confirmatory execution, how the consequences of a diagnostic error are represented without peeking at post-hoc treatment outcomes.

This is the key requirement for turning `Y_D` into `V_D`.

---

## 7. Minimum episode invariants

Every confirmatory episode must satisfy:

1. hidden `Z` is unavailable to the machine;
2. target generator identity cannot reveal `Z` through a deterministic shortcut;
3. transfer artifact cannot contain target outcomes or target repair shortcuts;
4. baseline and transfer use identical repair machinery;
5. probes are budgeted and auditable;
6. repair cost begins at the same protocol boundary in both arms;
7. validation is independent of the diagnostic trace;
8. failed/timeout repair episodes follow a predeclared censoring rule;
9. safety violations are terminal/admissibility events, not utility discounts;
10. case membership and stratum are fixed before outcome observation.

---

## 8. Anti-confound mapping to earlier feedback

| Earlier lesson | Episode protection |
|---|---|
| Search algorithm can dominate substrate | identical repair controller and budget |
| Noisy evaluation can hurt | probe cost and consequence recorded separately |
| Context-free accumulation can mislead | artifact provenance and allowed information audited |
| Representation expansion can buy trivial solutions | explicit resource cost for probes/structural changes |
| Detection/localization/selection/generalization differ | separate `Y_D`, repair, and `Y_V` endpoints |
| Bundled mechanism roles cause confounding | Za/Zb causal definitions keep persistence and context-indexing distinct |
| Hidden fault labels can leak through fixtures | injector/generator identifiers audited for proxy leakage |

---

## 9. Required pre-freeze table

Before confirmatory generation, every row must be populated:

| Field | Required value |
|---|---|
| stratum definition | FROZEN |
| stratum weight `w_s` | FROZEN |
| `V_D,s` | FROZEN / explicitly labeled assumption |
| probe unit | FROZEN |
| repair unit | FROZEN |
| validation unit | FROZEN or intentionally unweighted |
| resource ceiling | FROZEN |
| safety invariants | FROZEN |
| timeout/censoring rule | FROZEN |
| sufficient-repair definition | FROZEN |
| independent-validation definition | FROZEN |
| artifact version | FROZEN |

---

## 10. Status

**ESTABLISHED AS DESIGN**

- The target is a fresh `Zb` population, not historical benchmark reuse.
- Heterogeneity is represented explicitly before margin derivation.
- A complete episode now has a fixed sequence from failure to independent validation.
- The first experimental lessons are attached to specific anti-confound controls.

**OPEN**

- final stratum set;
- weights;
- numerical utility values;
- resource conversions;
- safety bounds;
- timeout/censoring policy;
- final practical margins.

**NEXT DISCRIMINATING TEST**

Instantiate one fully specified episode for each candidate stratum and ask, before any confirmatory outcome is generated: **can the operational difference between correct and incorrect diagnosis be defined without referring to the treatment result?**
