# Machine

Machine is a research repository for machine-native substrate design, active-frontier search, observation dynamics, evidence integrity, and related experimental claims.

**Repository rule:** locate every technical claim by repository + branch/ref + commit + source path + evidence. A green workflow on one branch is not evidence that the same code is merged into main. A stored result is not automatically a reproduced result.

## Current repository status — 2026-10-29

- **Default branch:** main, commit 2d5f6bd0513ecd2d9f29f395d4d95c90849b2648.
- **Integration:** [PR #26 — predecessor-frontier contract and evidence gate](https://github.com/Loofy147/Machine/pull/26) is **open and unmerged**. Its latest head has a successful integration CI run. Claims are limited to the documented finite fixtures and cost model.
- **v0.4 restoration:** draft [PR #29](https://github.com/Loofy147/Machine/pull/29) restores the exact hash-verified core module. Its canonical regression and exact n=3 comparison suite pass; the wider n=4 and matched-graph runs remain historical pending separate reproduction. [Issue #22](https://github.com/Loofy147/Machine/issues/22) remains open until review/merge.
- **General-graph property gate:** draft [PR #28](https://github.com/Loofy147/Machine/pull/28) checks 120 deterministic sparse/medium/dense multigraphs with 2,376 predecessor-fiber checks and 2,376 backward-reachability queries; CI reports zero mismatches. It is stacked behind PR #26.
- **Research state:** substantive source, harnesses, and evidence are distributed across named research branches. Many PRs are intentionally stacked on research branches rather than targeted at main.
- **Main branch:** currently a governance/documentation baseline, not a runnable release. It has no tracked test/CI configuration, package/build definition, or repository license.

Read the [repository-wide audit snapshot](docs/REPOSITORY-WIDE-AUDIT-2026-10-29.md) and [branch-role/PR-dependency ledger](docs/research/BRANCH-ROLE-AND-PR-DEPENDENCY-LEDGER-v0.1.md) for the branch inventory, dependency order, evidence status, reproducibility gaps, and recommended work order.

## Start here

1. [Branch, evidence, assumption, and suggestion handling](docs/BRANCH-EVIDENCE-AND-RESEARCH-HANDLING.md) — rules for identifying the correct branch and avoiding claim promotion by implication.
2. [Experiment protocol v0.1 — initial freeze candidate](docs/experiment/EXPERIMENT_PROTOCOL_v0.1_INITIAL_FREEZE_CANDIDATE.md) — a design candidate, not an empirical result.
3. [Statistical comparison plan v0.1](docs/experiment/STATISTICAL_COMPARISON_PLAN_v0.1.md) — pre-registration candidate; confirmatory thresholds and freeze obligations remain explicit.
4. [Architecture convergence link](docs/ARCHITECTURE_CONVERGENCE_LINK_v0.1.md) — how bounded findings can propagate to the wider architecture without automatically adopting research code.
5. [Branch roles and PR dependencies](docs/research/BRANCH-ROLE-AND-PR-DEPENDENCY-LEDGER-v0.1.md) — exact branch-head identity, alias groups, stacked PRs, and safe propagation order.

## Main research lines

These links identify workstreams; they do not mean their code or claims have been adopted into main.

- [Machine substrate primitive closure](https://github.com/Loofy147/Machine/tree/research/machine-substrate-primitive-closure-v0) — contract, representation, mutation-coupling, and closure experiments. Related work remains under review in [PR #10](https://github.com/Loofy147/Machine/pull/10).
- [Active-frontier verification](https://github.com/Loofy147/Machine/tree/research/active-frontier-adversarial-v0) — Dijkstra/UCS stopping-boundary research. Exact v0.4 core restoration is proposed in [PR #29](https://github.com/Loofy147/Machine/pull/29); only the canonical fixture and n=3 suite are freshly reproduced by that gate.
- [Observation-dynamics factorization](https://github.com/Loofy147/Machine/tree/research/observation-dynamics-factorization-v0.1) — SplitMix64 and finite observation dynamics; the current draft has solver jobs returning UNKNOWN/TIMEOUT and does not promote them to proofs. See [PR #24](https://github.com/Loofy147/Machine/pull/24).
- [HSDCR full-finding line](https://github.com/Loofy147/Machine/tree/research/hsdcr-full-finding-v0) — composition-reduction evidence and a draft handoff. See [PR #23](https://github.com/Loofy147/Machine/pull/23).
- [Substrate interpreter line](https://github.com/Loofy147/Machine/tree/research/substrate-interpreter-v0) — separately versioned experimental specifications; v0.1–v0.3 are not interchangeable without a recorded disposition.

## Interpretation and adoption

Use the claim status appropriate to the evidence: **ESTABLISHED**, **EXPERIMENTALLY_SUPPORTED**, **USER_REPORTED**, **INFERENCE**, **HYPOTHESIS**, **CONTRADICTED**, **UNKNOWN**, or **OPEN**. An experimental pass closes only its stated test scope. It does not by itself prove a general theorem, justify a physical cost claim, or select a production abstraction.

Do not delete stale branches, promote specifications, license the project, or merge research work merely to reduce branch count. Those require explicit decisions. The current branch/specification reconciliation is tracked in [Issue #5](https://github.com/Loofy147/Machine/issues/5).

## Scope of the audit

The linked audit is a structural repository inventory plus targeted inspection of high-risk reproduction, evidence, CI, and PR paths. It does **not** claim a line-by-line semantic proof of every source file on every divergent branch or a rerun of every branch-specific experiment.
