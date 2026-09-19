# Research State Canonicalization v0.1

**Status:** OPEN / RECONCILIATION REQUIRED  
**Repository:** `Loofy147/Machine`  
**Recorded:** 2026-09-19

## Purpose

Prevent branch-local specifications, evidence, and research results from being mistaken for one repository-wide canonical state.

Branch identity is part of research provenance:

```text
repository + branch + commit
```

A branch is not canonical merely because it is newer, larger, or more detailed.

## Current repository states

| Role | Branch | Head | Relation to `main` | Current role |
|---|---|---|---|---|
| Integration baseline | `main` | `1626bac2f5c478294afa4b9463f694608c322117` | canonical production/integration baseline | authoritative integration state |
| Machine-native research | `research/machine-native-primitives-v0` | `081f649f5c4cc31c52cbeb7af0fbda4ee90c5478` | 48 commits ahead / 3 behind; diverged | broad machine-model research |
| Target-oblivious research | `research/target-oblivious-frontier-v0` | `5decefaafb5b6abad2364629dafa1d96a5ffdba0` | 52 commits ahead / 3 behind; diverged | resource/frontier experiment |
| Confirmatory freeze | `research/confirmatory-freeze-order-v0.1` | `6f724f9c6b4f3c979587a4117f8bdcde8a5ccc48` | 25 commits ahead / 1 behind; diverged | confirmatory protocol/spec freeze |
| Evidence integration | `research/evidence-disposition-v0` | `8e1e51eb860ceb8722012ef0bc0f76e766bd013f` | 53 commits ahead / 1 behind; diverged | evidence-integrity controls and reproduced evidence package |

The machine-native and target-oblivious branches share merge base:

```text
641517a26790c40295606f12fd6e4a87fcab7186
```

The confirmatory freeze and evidence branch share the later research lineage based on:

```text
9d9a86325014b416431931e99b0c9132d591cd49
```

These are distinct research states, not interchangeable aliases.

## Explicit canonicalization rules

### 1. `main` is the integration authority

No research claim, experiment, or specification becomes part of the repository's canonical integration state until its provenance and evidence status are explicitly reconciled.

### 2. Research branches remain authoritative only for their declared scope

A result recorded on a research branch is authoritative for that branch/ref only until:

- its evidence is reproduced from a canonicalized source;
- conflicting specifications are resolved;
- the disposition is recorded;
- regression protection exists.

### 3. Evidence branch is not automatically scientific authority

`research/evidence-disposition-v0` supplies evidence-integrity infrastructure and a reproduced subset. It does not supersede the underlying research branches or convert their claims into established science.

### 4. Divergence is a tracked state

A branch that diverges from the integration baseline must carry:

```text
role
head_commit
merge_base
scope
status
supersedes
superseded_by
canonicalization_decision
```

### 5. Stale branches require explicit disposition

The following branches currently point to the same old research state at:

```text
641517a26790c40295606f12fd6e4a87fcab7186
```

- `research/definition`
- `research/machine-native-primitives`
- `research/machine-native-primitives-v0-docs`
- `research/machine-native-primitives-v0-issue`
- `research/test-write`

They are **ARCHIVE CANDIDATES**, not yet deleted.

## Current reconciliation decision

**OPEN**

Do not merge research lines into `main` merely to reduce branch count.

The next required action is a file/specification-level reconciliation:

```text
machine-native-v0
        +
target-oblivious-v0
        +
confirmatory-freeze-v0.1
        +
evidence-disposition-v0
        |
        v
canonical research map
        |
        +--> authoritative documents
        +--> reproduced evidence
        +--> unresolved conflicts
        +--> superseded material
        +--> next discriminating experiments
```

## Reliability invariant

> A claim is not repository-canonical until its branch/ref provenance, evidence status, specification compatibility, and regression protection are all explicit.

This document records repository state; it is not itself a scientific claim.
