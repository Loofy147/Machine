# Evidence Coverage Audit v0.1

**Branch:** \`research/evidence-disposition-v0\`  
**Status:** IMPLEMENTED / SELF-CONTAINED / CI-VERIFIED  
**Date:** 2026-09-18

## Purpose

Record the result of the second audit as durable repository state.

This document is an evidence-coverage report, not a scientific result.

## Verified execution set

### 1. Confirmatory contract pilot v0.1

Status:

\`\`\`text
REPRODUCIBILITY-CORRECTED
\`\`\`

Observed from the current committed harness:

\`\`\`text
theta_D = 0.462500
theta_P = -1.000000
theta_R = 0.000000
\`\`\`

Previous recorded \`theta_D=0.4125\` was stale/mismatched and is superseded.

Interpretation:

- contract separation is exercised;
- no nontrivial source learning is established;
- the fixture's \`context_boundary=1\` is constant across source cases.

Evidence gate: **PASS**.

### 2. Error-source-localization v0

The deterministic harness reproduces the recorded aggregate values for:

- oracle;
- probe;
- adaptive;
- random;
- local.

The declared interpretation boundary remains:

\`\`\`text
harness validation
!=
causal reflection
!=
self-discovered fault ontology
\`\`\`

Evidence gate: **PASS**.

### 3. Target-oblivious frontier v0

The replayed harness satisfies the strict-heldout invariants:

\`\`\`text
for every h <= M/2:
    hits = 0
    success_rate(h) = success_rate(0)
    avg_online_work(h) = avg_online_work(0)
\`\`\`

The stored IID summary values also match the replayed values at the precision declared by the result document.

Evidence gate: **PASS**.

## Unverified / incomplete experiment set

The following experiments remain documented but do not yet have the same executable evidence package on this branch:

- nine-mechanism ablation;
- B-clean executable mutation/search comparison;
- online reflective learning;
- history/identity ablation;
- contextual-credit experiment.

Their documented claims remain at their existing bounded status. No evidence status is promoted by repetition of prose.

## Specification debt / disposition gaps identified

### A. Claim identity

An initial machine-readable Claim Registry now covers the three reproduced evidence surfaces. A separate `evidence/open-claims-v0.1.json` registry now keeps documented-but-unpackaged claims explicitly `OPEN` with a required next discriminating test. A repository-wide registry linking all material claims is still missing:

\`\`\`text
claim_id
→ evidence_ids
→ runs
→ status
→ scope
→ limits
→ next test
→ regression protection
\`\`\`

Status: **PARTIALLY IMPLEMENTED / OPEN**.

### B. Concern lifecycle

Important concerns are currently represented primarily through documents/issues rather than a durable state machine.

Required terminal states:

\`\`\`text
CONFIRMED
PARTIALLY_CONFIRMED
CONTRADICTED
REFINED
INCONCLUSIVE
INVALID_RESULT
CONTEXT_BOUND
REGRESSION
NOVEL_SIGNAL
OPEN + next discriminating test
\`\`\`

Status: **OPEN**.

### C. Branch/specification canonicalization

\`main\`, \`research/machine-native-primitives-v0\`, \`research/target-oblivious-frontier-v0\`, and \`research/confirmatory-freeze-order-v0.1\` represent different research states.

Status: **OPEN until explicit canonicalization/reconciliation is recorded**.

### E. Unpackaged-claim visibility

The following documented research surfaces are now represented explicitly in the open-claim registry rather than relying only on prose:

```text
nine-mechanism ablation
B-clean executable adaptation
online reflective learning boundary
contextual credit assignment
history/identity ablation
```

Their records remain:

```text
status = OPEN
evidence_status = UNVERIFIED_PACKAGE
next_discriminating_test = required
```

This prevents documentation presence from being mistaken for evidence-package completion.

### D. Stale branches

The currently observed stale branches have no unique changes relative to current \`main\`:

\`\`\`text
research/definition
research/machine-native-primitives
research/machine-native-primitives-v0-docs
research/machine-native-primitives-v0-issue
research/test-write
\`\`\`

Disposition: **ARCHIVE/SUPERSEDE decision required**.

## Self-containment correction

The first evidence package referenced two experiment paths that existed only on separate research branches. That made the manifest/verifier non-self-contained even though the experiments themselves were reproducible elsewhere.

The missing harnesses, protocols, and result records have now been copied into this branch. The manifest records the exact commits that created those copied evidence files.

Verification history:

```text
run #25 = EVIDENCE-INTEGRITY-PASS
run #41 = verifier implementation failure (syntax error)
run #43 = EVIDENCE-INTEGRITY-PASS
```

Run #43 used full-history checkout and verified:
- executed experiment outputs;
- recorded result documents;
- claim/evidence bindings;
- explicit OPEN/unpackaged-claim registry;
- exact code/result file provenance against recorded commits.

The run is fresh CI evidence for the integrity gate. It does not upgrade the scientific claims.

## New repository controls implemented

### Evidence manifest

\`evidence/manifest-v0.1.json\`

The manifest records evidence identity, code/result paths, provenance, expected observations, and interpretation boundaries.

### Evidence verifier

\`tools/verify_evidence.py\`

The verifier executes the reproduced experiment set and compares machine-readable results against the manifest and recorded evidence.

### CI gate

\`.github/workflows/evidence-integrity-v0.yml\`

The workflow makes evidence drift a CI-visible failure rather than a documentation-only discrepancy.

## Governing rule

> A successful execution is not sufficient evidence that the recorded claim is still true. The execution artifact, result record, scope, and interpretation boundary must remain mutually consistent.

## Current machine-native research implication

The audit provides a concrete operational candidate for the next machine-native layer:

\`\`\`text
evidence
→ validity
→ relation to claim
→ conflict/support
→ claim-state transition
→ retention/invalidation
→ next discriminating action
\`\`\`

This is a research candidate, not yet an architectural primitive.
