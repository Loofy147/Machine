# Branch, Evidence, Assumption, and Suggestion Handling

Status: RESEARCH-OPERATING-PROTOCOL
Date: 2026-09-18

## Why this exists

This repository has multiple research branches whose maturity and contents differ materially. A repository-level conclusion must therefore not be derived from the default branch alone.

The recent correction between `Machine` and the older `log-os` project exposed a reusable failure mode: semantic similarity can identify a useful reference without identifying the active project, the current branch, or the provenance of the experiment.

## 1. Branch is part of project identity

Always treat:

`repository + branch + commit`

as the minimum location of a technical claim.

The repository name alone is insufficient when multiple branches contain different research states, experiments, or implementations.

Before interpreting an active project:

1. inspect the default branch;
2. enumerate relevant branches;
3. identify branches whose names or contents correspond to the current research task;
4. inspect recent commits on those branches;
5. use the branch-specific source/docs/tests as authoritative for claims about that branch;
6. compare with the default branch before describing something as current, merged, or canonical.

For the current Machine research line, `research/machine-native-primitives-v0` is the documented research branch reviewed in this audit. This does not by itself imply that it is merged into `main`.

## 2. Default branch is not automatically the research truth

`main` may contain a newer protocol, a frozen design candidate, an older implementation, or only a release-facing surface.

A branch may contain the actual implementation or research state under active investigation.

Therefore:

`default branch != automatically current experimental branch`

and:

`feature/research branch != automatically canonical`.

Both require explicit evidence.

## 3. Distinguish four different states

Never collapse these into one statement:

```text
repository identity
branch identity
documented research specification
implemented/executed behavior
```

A document can specify a target that the code does not yet implement.
A test can demonstrate a capability that the architecture document does not yet generalize.
A branch can contain an experiment that has not been promoted to the default branch.

Each must retain its own provenance.

## 4. Assumptions

Assumptions are working premises, not facts.

Every material assumption used during review should be expressed explicitly when it affects the conclusion.

Examples:

- assuming this branch contains the active implementation;
- assuming two similarly named repositories share lineage;
- assuming a documented experiment is implemented in this repository;
- assuming an external representation is causally consulted by the runtime.

Do not silently convert an assumption into `ESTABLISHED` or `EXPERIMENTALLY_SUPPORTED`.

Use the project claim vocabulary:

`ESTABLISHED`, `EXPERIMENTALLY_SUPPORTED`, `USER_REPORTED`, `INFERENCE`, `HYPOTHESIS`, `CONTRADICTED`, `UNKNOWN`, `OPEN`.

## 5. Suggestions

A suggestion is an action candidate, not evidence and not a claim.

For example:

`Use Log-Os as an interpreter reference`

is a suggestion.

It must not become:

`Machine derives its current interpreter architecture from Log-Os`

without lineage evidence.

Keep suggestions separate from:

- observed facts;
- experimentally supported results;
- architectural requirements;
- repository lineage.

## 6. Similarity is a discovery signal, not lineage

Search matches, terminology, architectural resemblance, and similar experiments are useful for finding references.

They are insufficient to establish:

- code lineage;
- conceptual inheritance;
- current implementation provenance;
- that one repository contains another project's experiment;
- equivalence of two mechanisms.

Promote a relationship only after inspecting the relevant source, history, commits, or explicit provenance.

Until then use `UNKNOWN` or a candidate relationship.

## 7. Historical reference handling

Older repositories remain valuable even when they are not the active project.

Treat them as reference implementations when they provide:

- useful substrate techniques;
- prior failure modes;
- tests;
- design precedents;
- counterexamples.

But do not import their claims into the active project automatically.

For example, `log-os` is useful historical evidence for interpreter machinery, lexical environments, CPS/trampolines, object-language dispatch, and AST-level `eval`. It is not evidence that the current Machine reflection experiment was implemented there.

## 8. Experiments versus mechanisms

An experiment may establish a capability without establishing the mechanism responsible for it.

Always separate:

```text
observed behavior
experimental mechanism tested
host-language mechanism
object-language mechanism
causal interpretation
architectural implication
```

A Python callback that changes behavior is not automatically an object-language primitive.
A hot-swap between invocations is not automatically online causal reflection.
A reified source description is not automatically reified live execution machinery.

## 9. Required workflow for ambiguous active-project questions

When the user refers to a project by its current research goal rather than its repository name:

```text
1. Search repository names and descriptions.
2. Search code/docs for distinctive phrases from the current task.
3. Enumerate branches.
4. Inspect candidate branches.
5. Inspect recent commits and branch-specific files.
6. Identify the current experiment/implementation frontier.
7. Only then name the repository.
8. If an older project is relevant, label it explicitly as historical/reference.
```

Do not answer from a semantic match to an older repository alone.

## 10. Portfolio reporting

When this process discovers a durable cross-project fact, relationship, provenance correction, or reusable primitive, record it in `Loofy147/Portfolio-Repository-Inventory`.

Do not create a portfolio relationship merely because two projects have similar names.

Preserve unresolved states and the exact branch/commit provenance needed for later re-verification.

## 11. Current correction

The recent Machine review established the following evidence boundary:

- `Loofy147/Machine` is the active repository for the current machine-native-primitives research.
- `research/machine-native-primitives-v0` contains the documented research frontier reviewed in the current audit.
- The Machine documentation distinguishes same-process hot-swap from the stronger target of online causal reflection.
- `Loofy147/log-os` is an older interpreter project and a useful historical reference.
- The inspected Log-Os surface does not establish that the current Machine prime-stream hot-swap experiment originated there.
- Direct Machine -> Log-Os code lineage remains `UNKNOWN`.
- Genuine object-language closure without a Python special case remains an open implementation target.

These statements are tied to the inspected repository/branch state on 2026-09-18 and must be rechecked before being treated as current after substantial branch movement.

## 12. Operating rule

> Never identify the active project from semantic resemblance alone. Identify it from current branch evidence, then distinguish implementation, experiment, assumption, suggestion, and historical reference before drawing conclusions.