# Operational Relations — Machine

Status: RESEARCH / OPEN

This document is a compact inventory of candidate machine-native relations that may underlie multiple observable phenomena. It is not a primitive specification.

## Rule

A relation qualifies for architectural consideration only if experiments can distinguish it from a combination of simpler existing relations.

## Candidate relation inventory

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
| Decay | retained influence + time/conditions | reduces influence | OPEN |
| Scheduling | state + available transitions + constraints | determines next transition distribution | STRUCTURAL |
| Exploration allocation | uncertainty/novelty + resources | shifts computation toward unknowns | OPEN |
| Constraint/gating | state + operation + constraints | blocks or permits execution | EXPERIMENTALLY_SUPPORTED in limited forms |
| Regime modification | current regime + evidence | changes future operation space/policy | EXPERIMENTALLY_SUPPORTED in limited forms |
| Continuity / lineage | prior state + provenance | constrains later operation by process history | OPEN |
| Reification | live executable state | exposes execution description | OPEN for causal reflection |
| Causal consultation | modified description + later transition | makes representation affect actual execution | OPEN |

## Non-relations

The following are deliberately treated as phenomenon labels or composite effects rather than primitive relations:

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

A phenomenon may nevertheless expose a relation that is missing from the inventory. The inventory is therefore falsifiable.

## Dependency questions

For every candidate relation, test:

```text
Can it be removed without changing the capability?
Can it be reconstructed from other relations?
Does it require an externally supplied objective?
Does it add information or only rename an existing computation?
Does it operate on state, policy, or executable structure?
Does its effect persist, decay, or remain instantaneous?
```

## Current likely dependency structure

A provisional dependency graph is:

```text
state
  ├── consequence observation
  ├── constraints
  └── context
        ↓
   prediction (optional)
        ↓
   prediction comparison (optional)
        ↓
 significance / valuation (candidate)
        ↓
 scheduling / proposal
        ↓
 execution
        ↓
 consequence
        ↓
 credit / persistence / decay
        ↓
 regime modification
```

This graph is a research hypothesis, not an architecture.

## Critical distinction

`significance / valuation` must not secretly become a universal reward function.

Experiments must identify whether its signal comes from:

- measured operational cost;
- externally specified task criteria;
- predicted consequence;
- resource pressure;
- learned consequence statistics;
- viability constraints;
- or some combination.

Otherwise the phenomenon experiment merely hides the answer in the benchmark.

## Current experimental priority

1. reproduce existing evidence artifacts;
2. test operational significance under controlled consequence-cost shifts;
3. test prediction error against raw history;
4. test persistence/decay under regime switches;
5. discover context from machine-observable state;
6. test exploration under matched compute;
7. test continuity effects;
8. implement causal reflection only after the relation layer is sufficiently constrained.
