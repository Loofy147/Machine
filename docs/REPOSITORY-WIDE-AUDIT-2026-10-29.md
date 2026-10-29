# Repository-Wide Audit — 2026-10-29

**Audit type:** repository structure + targeted code, evidence, CI, and research-state review  
**Repository:** Loofy147/Machine  
**Default-branch snapshot:** main @ 2d5f6bd0513ecd2d9f29f395d4d95c90849b2648  
**Integration candidate reviewed separately:** integration/predecessor-frontier-contract-v0.1 @ c1da8f9e89339aeabf0492880120f08ed7457c6a  
**Disposition:** no merge, branch deletion, production change, or license decision made by this audit.

## 1. Executive verdict

Machine is a **multi-line research workspace with a very small integration/governance default branch**, not currently a single self-contained, installable software release. That separation is consistent with the repository's own branch/evidence handling rules, but it creates a serious discoverability and reproducibility burden.

The most important distinctions are:

1. **A successful integration candidate exists:** PR #26 has a strict workflow that passes on its current head, with finite-scope evidence and explicit cost-model limits.
2. **At least one older high-profile result is not independently reproducible from its current branch tree:** the active-frontier v0.4 runner imports an unlocated core module. The evidence verifier does not execute that runner. Issue #22 correctly remains open.
3. **Research canonicalization remains unresolved:** many branches and PRs are stacked or divergent, and issue #5 explicitly tracks the required reconciliation.
4. **The current default branch is not release-ready as a software repository:** it has no tracked CI/test configuration, package definition, or license, and its README previously consisted of only a title.

These are different failure classes. The PR #26 pass does not close issue #22, make the research branches canonical, or turn the default branch into a tested release.

## 2. Method and limits

The audit inspected:
- GitHub repository metadata and the complete recursive tree of main;
- branch refs, distinct branch-head commits, open/closed PR metadata, and relevant files for PRs #26, #24, #23, #21, #20, #10, #9, #4, and #1;
- the relevant issue records, including issues #22, #5, and #2;
- recursive file inventories for major research head commits;
- current and historical Actions runs for the substrate, HSDCR, crosswalk, and observation-dynamics lines;
- the v0.4 runner, evidence-integrity verifier/workflow, solver logs, and PR #26 integration verifier/results.

This is not represented as a full semantic review of every line across all research branches; neither all experiment runners nor every historical commit were executed in this audit. Findings below distinguish facts directly checked from implications and remaining work.

## 3. Confirmed findings

### P0 — Evidence/reproduction blocker: active-frontier v0.4 core source missing

**Status: CONFIRMED BLOCKER — issue #22 remains OPEN.**

On branch research/active-frontier-adversarial-v0 @ c8ab7a889395b47c559162b14e1837b397277a37, experiments/bidirectional-grounded-v0.4/run_v0_4.py imports multiple functions from core, including dijkstra, interruptible_bidirectional_dijkstra, and make_smaller_frontier. The complete recursive tracked tree inspected for that branch contains the v0.4 runner, result JSON, protocol, canonical regression, and hash ledger, but no core.py, bidir_core.py, or package initializer.

The branch's tools/verify_evidence.py verifies manifest entries for a different subset of evidence; it does not run run_v0_4.py. The associated evidence-integrity-v0.yml is triggered on a different evidence-disposition branch and PR target, not on the active-frontier branch. The reviewed Actions history did not show a current branch run for research/active-frontier-adversarial-v0.

**Consequence:** the v0.4 record is durable as a historical evidence record, but it is not equivalent to a fresh, source-complete reproduction from this branch. Do not silently substitute the v3 implementation.

**Required closure:** recover and commit the exact core source, or document its external artifact and cryptographic provenance; pin the exact dependency; run the canonical post-edge regression and n=3 comparison suite; verify regenerated outputs against the recorded artifact; then update issue #22 with the exact source/result commits and outcome.

Reference: [Issue #22](https://github.com/Loofy147/Machine/issues/22).

### P1 — Research state is not yet canonicalized at repository level

**Status: CONFIRMED OPEN GOVERNANCE GAP — issue #5 remains OPEN.**

The branch API returned 33 branch refs with 26 distinct head SHAs. At least two ref groups require explicit disposition:
- Five refs point to the old initial commit 641517a26790c40295606f12fd6e4a87fcab7186: research/definition, research/machine-native-primitives, research/machine-native-primitives-v0-docs, research/machine-native-primitives-v0-issue, and research/test-write. Existing research documentation calls these archive candidates, not deleted branches.
- Four active-frontier refs share the exact same head 566aba464d0f47b22eb91de78a5cc97ca153bb3b: research/active-frontier-cost-v0, research/active-frontier-mep-v0, research/active-frontier-native-c-v0, and research/active-frontier-product-v0. Treat these as shared/placeholder refs until their distinct scope is recorded, not as proof that four distinct products have been implemented.

At the snapshot time, nine open PRs were present before this audit PR was created; the repository-wide audit is now proposed separately as draft PR #27. Several are stacked on research branches rather than targeting main: PRs #10 and #9 target research/bidirectional-substrate-v3; PR #23 is based on research/hsdcr-reassessment-v0; PRs #20 and #21 are based on research/active-frontier-program-v0; PR #4 is based on research/confirmatory-freeze-order-v0.1. This can be a valid workflow, but the dependency/merge order and canonical destinations are not yet represented as one authoritative map.

**Required closure:** file/spec ownership map, branch role/head/merge-base/supersession ledger, claim-to-evidence provenance, and explicit archive/alias decisions. Do not delete branches simply to reduce their count.

Reference: [Issue #5](https://github.com/Loofy147/Machine/issues/5).

### P1 — The default branch has no executable quality gate

**Status: CONFIRMED FROM THE TRACKED TREE.**

At snapshot 2d5f6bd0513ecd2d9f29f395d4d95c90849b2648, main has five tracked files:
- README.md;
- docs/ARCHITECTURE_CONVERGENCE_LINK_v0.1.md;
- docs/BRANCH-EVIDENCE-AND-RESEARCH-HANDLING.md;
- docs/experiment/EXPERIMENT_PROTOCOL_v0.1_INITIAL_FREEZE_CANDIDATE.md;
- docs/experiment/STATISTICAL_COMPARISON_PLAN_v0.1.md.

No tracked CI workflow, test suite, package/build definition, dependency lock, or release configuration exists on main. GitHub reports main as unprotected; the rulesets query returned no rulesets. The branch-protection API itself was not readable through this integration, so no additional settings beyond those responses are asserted here.

This is consistent with an intentionally minimal integration baseline, but it means main does not independently gate changes to itself and cannot be installed/tested as a software artifact from its tracked contents.

**Required closure:** explicitly decide whether main is documentation-only or should become a runnable integration surface. If it is intended to accept executable code, add an appropriate minimal CI gate and require it before merge. If it remains governance-only, document that as a deliberate contract.

### P1 — Observation-dynamics solver evidence is mixed, not all-green

**Status: CONFIRMED CI OUTCOME; scientific result remains NOT CONFIRMED for timed-out solver cases.**

On PR #24 at f9107642b533185bd1bcef13622983b0b1eb4b4d, the observation-dynamics and observation-collision jobs passed, as did the latest observation-recovery-bitwuzla run. The cvc5 and Z3 recovery jobs failed because queries returned UNKNOWN/TIMEOUT under the declared 30-second per-query bound. Their workflows use --fail-on-unknown, which correctly prevents promotion of timeout as proof.

The solver installation steps use unpinned pip install cvc5 and pip install z3-solver; the examined run logged cvc5 1.4.1 and z3-solver 5.1.0.0. This reduces reproducibility across future reruns.

**Consequence:** the timeouts are neither proof of a solution nor proof of impossibility. Keep the affected claims open. Pin solver versions, retain solver/runtime metadata, and separate timeout-budget experiments from mathematical claim status.

Reference: [PR #24](https://github.com/Loofy147/Machine/pull/24).

### P2 — PR #26 is green, but its claims remain narrowly scoped

**Status: VERIFIED FOR THE CURRENT PR HEAD'S DECLARED GATE.**

PR #26 head is c1da8f9e89339aeabf0492880120f08ed7457c6a. The latest push and pull-request workflow runs completed successfully:
- [push run](https://github.com/Loofy147/Machine/actions/runs/40927061808);
- [pull-request run](https://github.com/Loofy147/Machine/actions/runs/40927069110).

The gate verifies contract schemas, primitive-closure semantics, mutable-index and exact-CSR update invariants, Pareto resource accounting, the symbolic cost model, the A/B/C-family predecessor routine, and the new general-graph supplied-provider contract. The general-graph artifact checks four fixtures, 45 states, 101 labeled edges, 45 target fibers, and 45 backward-reachability queries with zero semantic mismatches.

The scope matters:
- the direct algebraic predecessor routine is specific to the A/B/C graph family;
- the general-graph test uses a fiber provider whose rows are supplied before queries;
- the tests do not establish a universal direct-predecessor algorithm;
- the physical cost of specialized access remains symbolic;
- no canonical production substrate or absolute computability advantage has been established.

The successful evidence artifact is an Actions artifact, not a committed source-controlled result. It is scheduled to expire on 2027-01-27 according to GitHub's artifact metadata. Long-lived claims should retain a committed, source-hash-bound evidence receipt or provide an explicit regeneration contract.

Reference: [PR #26](https://github.com/Loofy147/Machine/pull/26).

### P2 — Discoverability and release metadata are incomplete

**Status: CONFIRMED.**

The README on the audited main snapshot contained only # Machine. GitHub's repository metadata reports no license. Therefore:
- a newcomer cannot identify canonical entry points without reconstructing branch history;
- reuse/redistribution rights are unclear; do not infer an open-source license or add one without an explicit decision.

A reader-facing index should state that research work lives on scoped branches and that branch-local experiments are not automatically canonical. A license decision is separate from this audit.

### P2 — CI coverage is branch-specific by design, but the coverage boundary is not visible enough

**Status: CONFIRMED TRIGGER/INVENTORY GAP; impact varies by workstream.**

The machine-substrate primitive-closure branch had successful workflow runs on its inspected head on 2026-09-29 across its contract, primitive-closure, mutation-coupling, exact-CSR, representation-closure, profile/frontier, and substrate-conformance jobs. The HSDCR full-finding head had successful v0/v0.2/v0.3 end-to-end composition runs on 2026-09-29. The substrate crosswalk head's latest inspected runs on 2026-09-27 passed. These are branch-specific snapshots; they do not mean those lines have merged into main or that every intermediate historical run passed.

Conversely, the active-frontier branch has no workflow runs on its current head in the inspected Actions query, and the evidence-integrity workflow is bound to different branch/PR filters. Every research line needs an explicit declaration of which claims its workflow actually reruns.

## 4. Repository/PR snapshot

The audited open PR set was:
- **#26** predecessor-frontier integration — open, not merged; latest head CI passes; target is main.
- **#24** observation-dynamics factorization — draft; solver timeout jobs leave bounded claims unconfirmed.
- **#23** HSDCR full finding — draft; stacked on HSDCR reassessment; latest v0/v0.2/v0.3 composition CI passed at its inspected head.
- **#21** active-frontier n=2 post-edge minimality audit — draft; stacked on active-frontier program.
- **#20** active-frontier stopping invariant formalization — draft; stacked on active-frontier program.
- **#10** substrate primitive closure — open/non-draft; targets substrate v3, not main.
- **#9** substrate contract crosswalk — open/non-draft; targets substrate v3, not main.
- **#4** evidence integrity/disposition — draft; stacked on confirmatory-freeze line.
- **#1** implementation-independent machine model — draft; based on the initial historical commit, not the current main head.

Ten standalone issues were visible, including #22, #5, #2, and #3. The remaining active-frontier issues #14–#19 describe proof, counterexample, cost, generalization, native C implementation, and packaging work; those remain separate gates and should not be collapsed into one completion claim.

## 5. Priority-ordered action plan

### Gate 0 — restore exact reproducibility for v0.4
1. Resolve issue #22 by recovering the exact core dependency or documenting its cryptographic external source.
2. Run the canonical post-edge regression and n=3 comparison suite from that exact source.
3. Compare regenerated output with the hashed v0.4 result and report; preserve mismatches and killed controls.
4. Make the correct workflow trigger on the actual research ref and include this runner in the evidence gate only after dependencies are pinned and the run is self-contained.

### Gate 1 — canonical research map
1. Resolve issue #5 with a branch-role/supersession ledger.
2. Define the intended role of main: documentation-only governance baseline or executable integration surface.
3. Map every open PR to its dependency/base and canonical landing target.
4. Mark duplicate-head refs as aliases/placeholders and decide archive status for the five initial branches. Do not delete them automatically.

### Gate 2 — reproducibility contract by workstream

For each workstream, record exact branch + head SHA, exact command, dependency versions, seed/fixture, output paths, result hashes, CI run, and evidence claim. A verifier should fail on missing source, timeout/UNKNOWN when a proof is required, provenance mismatch, or changed expected outputs. Keep runtime/physical-cost studies distinct from semantic correctness.

### Gate 3 — repository usability and release decision
1. Keep this README and audit index current.
2. Add default-branch CI only if main is meant to gate executable code.
3. Decide whether a license is required before external reuse.
4. Do not promote experimental code to production merely to consolidate branches.

## 6. Claim ledger

| Claim | Status | Evidence / boundary |
|---|---|---|
| Current main is a five-file documentation baseline | **ESTABLISHED** | Recursive tree at 2d5f6bd… |
| PR #26 strict integration gate passes on its current head | **EXPERIMENTALLY_SUPPORTED** | Current push + PR workflow runs linked above |
| PR #26 establishes universal direct predecessor access | **NOT ESTABLISHED** | Family-specific formula and supplied-provider contract only |
| Active-frontier v0.4 can be cleanly rerun from the inspected branch tree | **CONTRADICTED** | core import not resolved in tracked tree; issue #22 |
| The cvc5/Z3 timeout cases prove recovery impossible | **CONTRADICTED** | Solver output is UNKNOWN/TIMEOUT, not UNSAT |
| Research branches are fully canonicalized | **OPEN** | Issue #5 remains open; multiple stacked PR/base lines |
| The repository is ready for licensed external distribution | **OPEN** | No repository license; no release contract |

## 7. Revalidation trigger

Re-run this audit after PR #26 is merged/closed, issue #22 is resolved, issue #5's branch/spec ledger is committed, or the default branch receives executable code/CI changes. Until then, this document records a dated state, not a timeless declaration about the repository.
