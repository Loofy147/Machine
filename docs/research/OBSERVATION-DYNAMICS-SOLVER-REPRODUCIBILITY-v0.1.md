# Observation-Dynamics Solver Reproducibility Contract v0.1

**Scope:** package/environment reproducibility for the observation-dynamics research branch  
**Status:** solver versions pinned; mathematical recovery claims remain bounded and open where solver output is UNKNOWN/TIMEOUT.

## Pinned versions

| Solver | Exact package version | Evidence basis |
|---|---:|---|
| Z3 | z3-solver==5.1.0.0 | Version emitted in the 2026-09-30 CI run |
| cvc5 | cvc5==1.4.1 | Version emitted in the 2026-09-30 CI run |
| Bitwuzla | bitwuzla==0.9.1 | Version already pinned in the workflow and now guarded by a contract test |

Z3 and cvc5 workflows print their installed package version before running the boundary. The package pins, timeout budget, and fail-on-unknown behavior are protected by a standard-library Python regression suite in experiments/test_solver_workflow_contract.py.

## Interpretation of the prior runs

The 2026-09-30 Z3 and cvc5 jobs returned UNKNOWN/TIMEOUT under the declared 30-second per-query bound. Pinning the versions makes a rerun better specified; it does not resolve the solver timeout and does not make the result a proof of recovery or impossibility.

The workflows retain --fail-on-unknown for these proof-oriented solver boundaries. A timeout remains unresolved and must not be promoted to SAT, UNSAT, or scientific success.

## Reproduction

    python -m unittest experiments.test_solver_workflow_contract -v

CI: .github/workflows/solver-version-contract.yml.

The existing solver jobs can still time out. This is expected to remain a distinct unresolved research limitation rather than be hidden by weakening the pass/fail policy.
