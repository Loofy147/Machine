# Context Contract Distribution Center v0.1

**Status:** EXPERIMENTAL-PROTOTYPE  
**Repository:** Loofy147/Machine  
**Purpose:** Produce an auditable offline plan for selecting compatible, dependency-linked contexts under a fixed anchor.  
**Production gate:** Not approved. This module does not publish contracts, mutate remote systems, authorize actions, or replace the frozen Machine Substrate Resource Contract v0.2.

## 1. Contract model

Each context has a stable context ID, a partial facts map, needs, and optional non-negative integer utility. Facts are finite JSON scalar values. If utility is omitted, the planner uses the number of facts as a weak demo proxy; this is not a validated measure of contract value.

The anchor is a fixed partial state. A context is eligible when every fact key shared with the anchor has the same type and value. Missing keys are not conflicts. The anchor filters candidates only; it is not a serving context and does not satisfy needs.

Two eligible contexts may be paired only when their shared facts are consistent and at least one context satisfies at least one need of the other. A need such as {"deadline":"fri"} requires an exact value. A null expected value means presence-only, as does a list/string-set style need. Therefore v0.1 does not express a requirement for the provider's actual JSON null value.

The service relation is directed, while the compatibility graph is undirected. A pair may have one or two service directions.

**Important scope boundary:** pair admission is existential, matching the original bool(c.needs & d.facts.keys()) behavior. It does not mean the partner satisfies every need. Output reports satisfied needs and unmet needs with that partner separately. Full dependency closure is an open extension.

A swarm is the endpoint set of a matching in the eligible compatibility graph. Every selected context belongs to exactly one pair.

## 2. Optimizer

The greedy selector is replaced as the correctness mechanism by general-graph maximum-weight matching. For every eligible compatible edge (u,v), the planner uses:

    w(u,v) = (utility(u) + utility(v)) * (N + 1) + 2

where N is the number of eligible contexts. Total matching weight therefore maximizes total utility first and selected context count second. The N+1 multiplier makes a one-unit utility improvement dominate any possible selected-count difference. The secondary criterion retains zero-utility pairs when doing so does not reduce utility.

The result includes chosen pairs, service directions, need witnesses, anchor conflicts, unmatched/isolated eligible contexts, objective values, and a canonical SHA-256 input digest.

## 3. Replanning and audit

Run the planner again after an anchor or contract change. compare_plans reports registrations and removals, eligibility changes, selected-context changes, added/removed pairings, changed service witnesses, per-context utility changes, total utility delta, old/new algorithm/schema IDs, and input digests.

The digest is a reproducibility identifier, not a signature or authorization token.

Under this model, if an anchor update invalidates k contexts in an old swarm, removing each invalidated context and its former partner leaves a feasible retained swarm after at most 2k removals. This is a feasibility bound, not an optimality guarantee; re-optimization may produce a better plan.

## 4. Corrected hazards and improvements

1. **Exact optimization:** maximum-weight matching replaces a greedy selector as the optimizer.
2. **Typed equality:** Python's True == 1 does not permit an accidental fact match; equality checks both type and value.
3. **Value-aware needs:** declared values are checked; presence-only needs remain available for backward compatibility.
4. **Explanations:** output records anchor conflicts, service direction, satisfied needs, and remaining unmet needs.
5. **Change awareness:** service witnesses or utilities may change even when selected IDs do not; deltas report these changes.
6. **Reproducibility:** IDs are unique, inputs are canonicalized, invalid scalar/utility inputs are rejected, and plans carry an input digest.
7. **Matrix encoding hazard:** fixed +1/-1 signs can cancel in a skew-symmetric determinant even when a perfect matching exists. Random weights reduce some cancellation cases but are not an exact oracle. This planner uses matching directly.

## 5. Verification record

Local verification for this candidate:
- 17/17 unit tests passed.
- 20 deterministic random pools of eight contexts matched a brute-force lexicographic oracle for (total utility, selected context count).
- Small randomized graph checks covered even-family exchange, two-context connectivity, anchor restriction, and an anchor repair-distance bound.
- A four-context cycle fixture reproduced a fixed-sign singular-matrix hazard despite the existence of a perfect matching.

These are finite executable checks, not a universal proof or a scalability claim. The dedicated GitHub Actions workflow reruns the tests and demo checks for the PR.

## 6. Claim boundary

| Claim | Status | Boundary |
|---|---|---|
| Selected contexts are endpoints of returned pairs | ESTABLISHED by implementation and tests | Uses matching solver and supported input schema |
| Selection optimizes utility, then selected count | EXPERIMENTALLY_SUPPORTED by brute-force cross-checks; objective reduction is exact | Utility values may poorly represent real importance |
| Anchor filtering is a restriction of the unanchored swarm family | EXPERIMENTALLY_SUPPORTED by finite randomized checks | Not a standalone proof for every graph |
| A partner fully resolves every need | CONTRADICTED as a blanket v0.1 claim | Pair admission only requires one fulfilled need; remaining needs are reported |
| This is ready as a central production service | OPEN | Persistence, auth, lifecycle, approvals, audit storage/API and realistic scale tests are absent |
| Random skew weights always make a matchable graph matrix nonsingular | CONTRADICTED as an exact guarantee | Random/finite-field cancellation remains possible |

## 7. Run

From this experiment directory:

    python -m pip install -r requirements.txt
    python -m unittest -v
    python run_demo.py

A different JSON input can be supplied as the runner's first argument. contracts.demo.json illustrates the original eight contexts and a second anchor.

## 8. Promotion gates

Do not wire this to a live control plane yet. Before promotion:
1. Replace demo utility with a versioned, evidence-backed utility policy.
2. Decide whether pair admission stays existential or requires complete dependency closure.
3. Add contract issuer/owner, version, scope, expiry, and provenance.
4. Add persisted registry, approvals, idempotent plan IDs, and append-only decision/evidence records.
5. Test stale-anchor handling, context-version conflicts, malformed inputs, and realistic portfolio scale.
6. Define a separate authorization/dispatch gateway. The optimizer must remain a planner, not an unrestricted authority to enact selected contracts.


## 9. Real-dataset stress battery (fixed seed 2026)

A fixed-seed stress runner is located at `experiments/context-contract-distribution-v0/stress_test_real_datasets.py`. It loads the bundled Wine (178×13), Diabetes (442×10), Breast Cancer (569×30), and Digits (1797×64) feature matrices; generated context pools remain synthetic partial observations. Each continuous feature is discretized into three quantile bins, then context facts, needs and anchors are sampled. The bottleneck follow-up makes supply scarcer using Zipf-skewed observed features and more needs.

Local environment: Python 3.13.5, NumPy 2.3.5, NetworkX 3.6.1, scikit-learn 1.8.0; seed 2026; `PYTHONHASHSEED=0`. The repeatable run completed all eight suite gates in about 7.9 seconds. Per-case numerical metrics remained stable on repeated local runs after the sampled matching edges were sorted; timings naturally vary.

| Suite | Observed result | Interpretation boundary |
|---|---|---|
| H1 | 16 cases; 0 objective mismatches; 0 invalid swarms; mean uplift over greedy edge-pair baseline 4.3% | Matching-reference comparison over synthetic contexts derived from four bundled datasets |
| H2 | 3 adversarial anchor cases passed | Includes an impossible anchor and restrictive full-row anchors |
| H3 | 12 walks; 7 non-trivial; 0 stuck; 0 non-pair moves; 0 incorrect path lengths | Finite feasible-family reconfiguration checks |
| H4 | 40 anchor updates; 0 infeasible repairs; 0 bound violations; mean repair churn 3.9 vs reoptimization churn 2.7; mean utility regret 8.0 | Repair is feasible, not necessarily optimal; churn/regret depend on the generated trace |
| H5 | At matrix sizes 4, 8, 12, 16, 20, 24, fixed-sign matrices were singular in 1, 4, 7, 3, 2, 2 of 25 trials respectively; random modular encoding was singular in 0 of 150 trials | No singular random samples in a finite test is not a guarantee; matching remains the decision mechanism |
| B1 | 6 scarce-supply cases; 0 objective mismatches; 0 invalid swarms; selected fraction 86–100%; mean uplift over greedy edge-pair baseline 14.8% | Synthetic scarcity is non-trivial in at least one case; some other cases still match every eligible context |
| B2 | 18 walks; 16 non-trivial; 0 stuck; 0 non-pair moves; 0 incorrect path lengths; mean 4.6 moves on non-trivial walks | Weight changes selection while feasibility is tested after each move |
| B3 | 30 anchor updates; 3 updates broke selected contexts; 0 infeasible repairs; 0 bound violations; mean repair churn 1.3 vs reoptimization churn 1.3; mean utility regret 2.0 | One finite anchor-drift trace only |

**Claim status:** EXPERIMENTALLY_SUPPORTED for these fixed seeds, pools and dependency versions. These tests do not validate actual business/legal contracts, establish production performance, or prove general theorems. The workflow uploads `REAL-DATASET-STRESS-RESULTS.json` as commit-specific evidence, including environment metadata and per-case metrics.
