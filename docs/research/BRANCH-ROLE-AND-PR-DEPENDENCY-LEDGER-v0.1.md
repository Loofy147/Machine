# Branch Roles and PR Dependency Ledger v0.1

**Snapshot:** 2026-10-29  
**Repository:** Loofy147/Machine  
**Main:** 2d5f6bd0513ecd2d9f29f395d4d95c90849b2648  
**Purpose:** make branch identity, shared heads, PR landing targets, and unresolved disposition visible before any promotion or deletion.

## 1. Snapshot counts

- 37 branch references after opening PR #30's fix branch.
- 30 distinct branch-head commits.
- Four active-frontier refs share one identical commit.
- Five old research refs share the initial commit.
- 13 open PRs at the refreshed snapshot on 2026-10-29.

These counts describe Git refs, not 29 independent implementations or experiments. Multiple names can point to the same tree. A branch prefix, PR title, or successful historical CI run is not proof that the named work is current, canonical, or merged.

## 2. Branch-head ledger

| Branch reference(s) | Exact head | Observed role / evidence | Disposition |
|---|---|---|---|
| main | 2d5f6bd0513ecd2d9f29f395d4d95c90849b2648 | Default integration authority; five tracked files at snapshot; documentation/governance baseline | Canonical integration baseline; currently no executable CI/test gate |
| audit/repository-wide-state-2026-10-29 | f23f75f650c7419c7d3a90df3bf675663750fc0b | Repository audit and entrypoint documentation; draft PR #27 to main | Documentation-only candidate; do not conflate with research implementation |
| fix/restore-v04-core-repro-v0.1 | edddcf0a328d040e8c4f3b8716344a1bcaaa1595 | Restored hash-verified v0.4 core; canonical regression and exact n=3 reproduction gate; draft PR #29 targets active-frontier-adversarial | Fix candidate; merge into its target only after review; broader n=4/matched results remain historical |
| integration/predecessor-frontier-contract-v0.1 | c1da8f9e89339aeabf0492880120f08ed7457c6a | Substrate contract, finite frontier experiments, cost model, integration workflow; PR #26 targets main | Integration candidate; latest declared gate passes; not yet canonical |
| research/active-frontier-adversarial-v0 | c8ab7a889395b47c559162b14e1837b397277a37 | Active-frontier v0.4 research line and PR #21 head; PR #29 targets this branch | Research line; restored core is proposed separately, not present on this head until PR #29 is merged |
| research/active-frontier-cost-v0; research/active-frontier-mep-v0; research/active-frontier-native-c-v0; research/active-frontier-product-v0 | 566aba464d0f47b22eb91de78a5cc97ca153bb3b | Four distinct refs resolve to the same exact commit | Shared-head aliases/role placeholders. No claim of four separate implementations follows from their names; decide roles before branching additional work |
| research/active-frontier-program-v0 | 9a6509b2afac89623156fc4ba60108e136dcd0a2 | Base branch for PRs #20 and #21 | Parent research line; preserve dependency order |
| research/active-frontier-proof-v0 | a6182207aa236b8c093ebe47ca48d63dbc173e61 | Stopping-invariant formalization; draft PR #20 targets active-frontier-program | Proof workstream; separate from finite regression results |
| research/bidirectional-grounded-verification-v0 | cc61765d6939788ab9c075f04ec3572203c89347 | Historical v0.4 evidence/grounded-verification snapshot with hash record | Historical source of evidence; current v0.4 reproducibility fix is being proposed on a descendant branch |
| research/bidirectional-ledger-reconciliation-v0 | 7403c1a6351048bee34dd50540caa76745e97dd7 | Evidence and claim-ledger reconciliation line | Research/evidence state; do not merge claim files without claim-level reconciliation |
| research/bidirectional-substrate-v3 | 59fab62704875193801db77c7cb8361475297f48 | Base target for PRs #9 and #10 | Substrate research integration parent; not the default branch |
| research/confirmatory-freeze-order-v0.1 | 6f724f9c6b4f3c979587a4117f8bdcde8a5ccc48 | Parent of draft evidence-disposition PR #4 | Confirmatory design lineage; freeze requirements must not be inferred complete from candidate docs |
| research/definition; research/machine-native-primitives; research/machine-native-primitives-v0-docs; research/machine-native-primitives-v0-issue; research/test-write | 641517a26790c40295606f12fd6e4a87fcab7186 | Five refs all point to the initial commit | Archive candidates already identified by repository docs. Retain until explicit archive/supersession decision; do not delete automatically |
| research/evidence-disposition-v0 | 137f76bc7fb56138a40b3bc98ed2a3291fe7acf5 | Evidence-integrity and claim-disposition infrastructure; draft PR #4 head | Stacked on confirmatory-freeze-order; does not establish unrelated experiments by itself |
| research/general-graph-predecessor-property-suite-v0.1 | 23d4e744b2ef4e6cbe9e821ca6ebfeecf9404247 | 120-graph sparse/medium/dense property sweep; draft PR #28 targets integration branch; CI passes | Stacked follow-up to PR #26; after #26 is integrated, rebase/retarget and rerun before treating the test as part of main |
| research/hsdcr-e2e-composition-v0 | d1bf7c52bb20023ab6b98cd82673aba4bf4523d6 | Earlier HSDCR composition-reduction experiment | Historical/stacked research line; preserve relation to reassessment/full finding |
| research/hsdcr-full-finding-v0 | c5a083a4b0dad4ec1a3b6542c3400645edb4ed23 | HSDCR full-finding draft PR #23 head | Targets research/hsdcr-reassessment-v0; do not land directly on main independently of its base |
| research/hsdcr-neighborhood-crosswalk-v0 | c635fa557b13223edb0d4662376a8eb03c2986b3 | Capability-substitution crosswalk research line | Related lineage; current disposition and supersession should be recorded in HSDCR map |
| research/hsdcr-reassessment-v0 | dc11fb21dc3ba136b2193e9ea6c324a0aa79a2f1 | Parent of HSDCR full-finding PR #23 | Research base; settle claim/spec hierarchy before integrating the child |
| research/machine-native-primitives-v0 | f752aac015d9f837bc6a89d44eed50e0325b60a6 | Implementation-independent machine model; draft PR #1 targets main | Old/draft research work; PR is not a substitute for a claim/evidence disposition review |
| research/machine-substrate-crosswalk-v0 | 3c7d5bca90262c867f7063a5506c452daacd54d5 | Substrate contract crosswalk; PR #9 head | Targets bidirectional-substrate-v3; latest inspected CI passed |
| research/machine-substrate-primitive-closure-v0 | 5db33b068c0973606e08b596a300e99952764aeb | Contract/primitive closure, M2, mutation-coupling and resource-frontier suite; PR #10 head | Targets bidirectional-substrate-v3; multiple workflows passed on inspected head |
| research/observation-dynamics-factorization-v0.1 | f9107642b533185bd1bcef13622983b0b1eb4b4d | SplitMix64 observation-dynamics draft PR #24 | Structural jobs pass; cvc5/Z3 recovery jobs return UNKNOWN/TIMEOUT. Keep solver-dependent claims open and pin tool versions |
| fix/pin-observation-solver-versions-v0.1 | 209acc7aff4fe6d824c70fc567d9a8af32a13ada | Pin Z3 5.1.0.0, cvc5 1.4.1, retain Bitwuzla 0.9.1; version-contract CI passed; draft PR #30 | Stacked on PR #24; reproducibility improves, but prior Z3/cvc5 UNKNOWN/TIMEOUT results remain unresolved |
| research/orchestration-benchmark-2026-09-27 | cdcda922223212ee60edde7b9ab059658c0ab105 | Orchestration benchmark snapshot | Research evidence; refresh before treating results as current |
| research/substrate-c1c7-verification | 63b07920ca230d3b64a8afc8ef9a32c4f3b66ddf | Substrate conformance verification branch | Historical/verification lineage; tie any reused result to its source and runner |
| research/substrate-interpreter-v0 | d935495355ac6b827a17d6147d7f38fbcaaeb15f | Separately versioned substrate-interpreter research | Experimental; specification versions must not be treated as interchangeable |
| research/substrate-rev2.1-v0 | 9bf84642e25773dfc761ea00fcc9f43cf8a4d1fe | Historical substrate rev2.1 base/verification line | Keep as lineage evidence; adoption requires contract reconciliation |
| research/target-oblivious-frontier-v0 | 5decefaafb5b6abad2364629dafa1d96a5ffdba0 | Target-oblivious frontier experiment | Research state; promotion requires source-bound reproduction and explicit claim limits |

## 3. Open pull-request dependency map

| PR | Head branch | Base target | Current gate / dependency | Action |
|---|---|---|---|---|
| #29 | fix/restore-v04-core-repro-v0.1 | research/active-frontier-adversarial-v0 | Push + PR CI pass; source and n=3 reproduction restored | Review/merge into the research branch before promoting PR #21; full n=4/matched suites remain outside this gate |
| #28 | research/general-graph-predecessor-property-suite-v0.1 | integration/predecessor-frontier-contract-v0.1 | Push + PR CI pass; 120 fixtures, 2,376 states, 2,376 fiber checks, 2,376 reachability checks, zero mismatches | Keep stacked behind #26; after #26 lands, rebase/retarget and rerun |
| #27 | audit/repository-wide-state-2026-10-29 | main | Documentation-only audit/README | Review as independent docs change |
| #26 | integration/predecessor-frontier-contract-v0.1 | main | Latest strict integration CI passes | Main integration candidate; claims remain bounded to declared contracts and fixtures |
| #24 | research/observation-dynamics-factorization-v0.1 | main | Structural checks pass; cvc5/Z3 recovery timeouts | Pin solver versions and keep timeouts as UNKNOWN, not proof |
| #30 | fix/pin-observation-solver-versions-v0.1 | research/observation-dynamics-factorization-v0.1 | Version-contract CI passes; pins Z3/cvc5 and preserves fail-on-unknown | Merge/rebase only into PR #24's research line; unresolved solver timeouts remain open |
| #23 | research/hsdcr-full-finding-v0 | research/hsdcr-reassessment-v0 | Composition workflows passed at inspected head | Resolve base-branch claim/spec dispositions before promotion |
| #21 | research/active-frontier-adversarial-v0 | research/active-frontier-program-v0 | Draft; minimality and scheduling scope still open | Consume #29 first; then evaluate remaining n=2/general scheduler obligations |
| #20 | research/active-frontier-proof-v0 | research/active-frontier-program-v0 | Draft; formal invariant workstream | Keep distinct from experimental regression results |
| #10 | research/machine-substrate-primitive-closure-v0 | research/bidirectional-substrate-v3 | Multiple substrate CI workflows passed on inspected head | Claim/spec review before merging into substrate v3 |
| #9 | research/machine-substrate-crosswalk-v0 | research/bidirectional-substrate-v3 | Crosswalk/conformance workflows passed on inspected head | Claim/spec review before merging into substrate v3 |
| #4 | research/evidence-disposition-v0 | research/confirmatory-freeze-order-v0.1 | Draft evidence integrity gate | Reconcile claim and manifest ownership before promotion |
| #1 | research/machine-native-primitives-v0 | main | Draft model/spec proposal; historical research lineage | Do not merge from title alone; reconcile with current main contract first |

## 4. Safe propagation rules

1. **Branch identity is repository + branch + exact commit.** A result or CI pass on a different head does not transfer automatically.
2. **Shared heads are aliases until proven otherwise.** Do not infer separate implementations or delete them solely from their names.
3. **Stacked PRs require explicit dependency ordering.** Do not merge a child PR into main while its intended base is not integrated or rebased.
4. **A green CI run certifies only that workflow's checked scope.** The v0.4 reproduction gate covers the canonical regression and n=3 suite, not n=4 or matched multigraphs.
5. **Historical evidence is not silently upgraded.** Keep original hashes, current source hashes, test commands, and claim status distinct.
6. **No automatic branch deletion or license decision.** Archive/supersession remains a human-reviewed state change.

## 5. Canonicalization decisions still open

This ledger is an observed snapshot, not a claim that all branch roles are finally resolved. Issue #5 remains open because:
- the shared-head active-frontier refs lack distinct documented roles;
- the five initial refs still need explicit archive/supersede decisions;
- the file/spec/claim ownership map is not yet complete at individual claim level;
- stacked PRs require explicit landing order;
- HSDCR and substrate-rev2.1 lineages require claim-level reconciliation.

The next closeout should add the exact merge base and supersedes/superseded-by relation for each branch, map material claims to evidence receipts, and record decisions without deleting references automatically.
