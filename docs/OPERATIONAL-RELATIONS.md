# Operational Relations — Machine

Status: RESEARCH / OPEN

This document inventories candidate machine-native relations that may underlie multiple observable phenomena. It is not a primitive specification.

## 1. Qualification rule

A relation qualifies for architectural consideration only if experiments can distinguish it from a combination of simpler relations.

For every candidate relation, ask:

```text
Does it add a causal capability?
Can it be reconstructed from simpler relations?
Does it introduce hidden objective information?
Does it change state, policy, executable structure, or only rename a computation?
Does its influence persist, decay, or remain local to one transition?
```

## 2. Candidate relation inventory

| Relation | Input | Effect | Current status |
|---|---|---|---|
| State difference | prior/current state | exposes operational change | STRUCTURAL |
| Consequence observation | transition/result/successor | adds post-transition information | STRUCTURAL / broad |
| Consequence prediction | state + operation + conditions | estimates possible result | OPEN |
| Prediction comparison | expected + observed | produces mismatch signal | OPEN |
| Significance / valuation | state + consequence + conditions | changes relative transition value | OPEN |
| Context discrimination | state/event history | distinguishes operating regimes | OPEN |
| Credit assignment | operation + context + outcome | changes future proposal bias | EXPERIMENTALLY_SUPPORTED in limited forms |
| Persistence | event/history + utility | preserves influence | OPEN beyond fixed history tests |
| Decay / staleness | retained influence + time/conditions | reduces or invalidates influence | OPEN |
| Scheduling | state + available transitions + constraints | determines next transition distribution | STRUCTURAL |
| Suppression / irrelevance | signal/history + context + resource state | reduces computational influence | OPEN |
| Exploration allocation | uncertainty/novelty + resources | shifts computation toward unknowns | OPEN |
| Constraint/gating | state + operation + constraints | blocks or permits execution | EXPERIMENTALLY_SUPPORTED in limited forms |
| Regime modification | current regime + evidence | changes future operation space/policy | EXPERIMENTALLY_SUPPORTED in limited forms |
| Representation revision | mismatch + model state | changes problem/model encoding | OPEN |
| Hypothesis-space modification | evidence + current operation space | changes what operations/structures can be proposed | OPEN |
| Continuity / lineage | prior state + provenance | constrains later operation by process history | OPEN |
| Reification | live executable state | exposes execution description | OPEN for causal reflection |
| Causal consultation | modified description + later transition | makes representation affect actual execution | OPEN |

## 3. Human-facing phenomena are composite descriptions

The following are intentionally treated as phenomenon labels rather than primitive relations:

```text
attention
curiosity
fear
urgency
motivation
preference
surprise
frustration
confidence
doubt
boredom
attachment
identity
self-preservation
```

They may expose missing relations, but a named phenomenon is not evidence for a dedicated mechanism.

Examples of candidate decompositions:

```text
urgency-like behavior
≈ consequence cost + time pressure + reversibility + scheduling

surprise-like behavior
≈ prediction + observation + comparison + state update

frustration-like regime change
≈ repeated failure + persistence + threshold + regime modification

identity-like continuity
≈ lineage + persistent state + provenance + continuity constraints
```

These are hypotheses, not architectural definitions.

## 4. Critical distinction: state, relation, policy, phenomenon

Do not collapse these categories.

```text
state variable
    = condition carried by the machine

relation
    = transformation or dependency between conditions

policy effect
    = change in what the machine does next

phenomenon
    = externally observed pattern that may result from a composition
```

For example, `uncertainty` may be state; `prediction comparison` may be a relation; `exploration` may be a policy effect; `curiosity` may be an external description of the combined behavior.

## 5. Provisional dependency structure

A useful starting graph is:

```text
state / environment
        │
        ├── consequence observation
        │
        ├── constraints / resources
        │
        └── context evidence
                │
                ▼
        optional prediction
                │
                ▼
        prediction comparison
                │
                ├──────────────┐
                ▼              ▼
        significance      model/representation
                │              │
                ▼              ▼
          scheduling      hypothesis-space change
                │              │
                └──────┬───────┘
                       ▼
                    execution
                       │
                       ▼
                  consequence
                       │
              ┌────────┼─────────┐
              ▼        ▼         ▼
           credit   persistence  regime evidence
              │        │         │
              └────────┴────┬────┘
                            ▼
                    future operation
```

This graph is a research hypothesis, not an architecture.

## 6. Significance must not hide the objective

`significance / valuation` must not silently become a universal reward function.

Experiments must distinguish signals arising from:

- measured operational cost;
- externally specified task criteria;
- predicted consequence;
- resource pressure;
- learned consequence statistics;
- viability constraints;
- or combinations of these.

Otherwise a phenomenon experiment merely hides the desired answer in the benchmark.

## 7. When should a model change?

Prediction error alone is insufficient. The machine may need to distinguish:

```text
parameter error
state change
policy failure
model incompleteness
representation failure
model-class failure
```

The transition between these levels is itself an open research problem.

## 8. What may influence what?

Technical connectivity does not imply causal permission.

```text
possible connection
    !=
permitted influence
```

The machine may need explicit isolation boundaries for stale information, conflicting regimes, or experimental controls.

## 9. Preserving ambiguity

When multiple hypotheses remain compatible with evidence, early commitment may destroy useful information.

Candidate operation:

```text
retain alternatives
    -> seek discriminating evidence
    -> commit when justified
```

This must be compared against forced single-hypothesis commitment.

## 10. When does retention become harmful?

A correct historical record may become operationally wrong when its context expires.

Therefore persistence and decay should be treated separately:

```text
record correctness
    !=
current influence correctness
```

A persistence experiment must measure both adaptation benefit and stale-state cost.

## 11. Does continuity itself matter?

If two systems have identical current state summaries but differ in lineage and uninterrupted execution history, do they behave differently or acquire different capabilities?

This distinguishes genuine continuity effects from simple data retention.

## 12. What changes the reachable space?

A central distinction is:

```text
better selection within fixed operation space
```

versus:

```text
changing the operation / hypothesis space itself
```

The latter is the critical frontier for reusable executable structure.

## 13. Current experimental priority

1. reproduce existing evidence artifacts;
2. test operational significance under controlled consequence-cost shifts;
3. test prediction error against raw history;
4. test persistence/decay under regime switches;
5. remove supplied context labels and test context discovery;
6. test suppression/irrelevance under matched information load;
7. test ambiguity retention versus forced commitment;
8. test representation/model revision versus policy-only revision;
9. test exploration under matched compute;
10. test continuity effects;
11. only then implement causal reflection.

## 14. Frontier rule

The purpose of this inventory is to expand the question space while keeping the executable primitive set small and evidence-driven.

A candidate relation must earn architectural status through a discriminating experiment; it must not enter merely because a human phenomenon has a familiar name.
