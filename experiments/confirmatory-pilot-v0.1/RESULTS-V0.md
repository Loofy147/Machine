# Confirmatory Contract Pilot v0.1 — Results

**Status:** REPRODUCIBILITY-CORRECTED / EXPERIMENTALLY_SUPPORTED / CONTRACT TEST ONLY  
**Not confirmatory evidence.**

## Purpose

This pilot tests the plumbing of the frozen transfer contract before building the full generator family \`E\`:

\`\`\`text
source-class training
    -> diagnostic artifact
    -> fresh target cases
    -> compare baseline vs transfer
\`\`\`

The transferred artifact is restricted to diagnostic identification/probe selection. The repair controller is identical across arms.

## Fixed configuration

- Seed: \`20260916\`
- Source cases: 40 \`persistence/decay-fault\`
- Target cases: 80 fresh \`context-discrimination-fault\`
- Primary policy: S2-like sequential probing
- Baseline: no transferred diagnostic artifact; 2 probe units; useful probe selected with pre-declared toy probability 0.55
- Transfer: one probe selected from the source-derived diagnostic artifact
- Repair controller: identical between arms

### Important implementation boundary

The current pilot fixture sets \`context_boundary=1\` for every generated source case. Consequently, \`learn_transfer_artifact()\` deterministically produces:

\`\`\`text
context_boundary_probe_priority = 1
\`\`\`

This means the pilot validates **transfer-arm contract separation**, not learning of a nontrivial source pattern. The artifact should therefore be described as source-derived/deterministic in this v0 fixture, not as evidence of transferable learning.

## Corrected execution result

The stored result from the original recording did not match the current committed harness. The current harness was re-evaluated directly under the declared seed and sample sizes.

| Arm | Diagnostic success | Mean probe cost | Mean repair cost |
|---|---:|---:|---:|
| baseline | 0.5375 | 2.0 | 8.0 |
| transfer | 1.0000 | 1.0 | 8.0 |

Therefore:

\[
\theta_D = 1.0000-0.5375=0.4625
\]

\[
\theta_P = 1.0-2.0=-1.0
\]

\[
\theta_R = 8.0-8.0=0
\]

The previous recorded \`theta_D=0.4125\` was a stale/mismatched result and is **superseded** by this reproducibility-corrected result.

## What is established

### EXPERIMENTALLY_SUPPORTED — contract behavior

The pilot exercises the intended separation:

\`\`\`text
transfer -> diagnostic behavior changes
transfer -> probe cost changes
transfer -/> repair controller
\`\`\`

The current code and corrected result are now linked by an explicit reproducibility check.

### NOT ESTABLISHED

The pilot does **not** establish:

- transferable WHAT-learning;
- causal identification of either real mechanism;
- transport across a real generator-family shift;
- generalization;
- practical significance of \`theta_D=0.4625\`;
- equivalence of repair behavior in a realistic repair search;
- any confirmatory hypothesis.

The toy baseline probability and deterministic repair-cost rule are constructed fixtures, so this effect size must not be used to select practical-effect margins.

## Required next scientific gate

Replace the deterministic \`context_boundary=1\` source fixture with a nontrivial source distribution in which the transferred artifact must infer a source property from observations, while keeping target labels/outcomes unavailable to the artifact.

That change creates a **new experiment version**; it must not silently overwrite v0.

## Reproducibility

Run:

\`\`\`bash
python3 experiments/confirmatory-pilot-v0.1/harness.py
\`\`\`

Expected key outputs from the current harness:

\`\`\`text
theta_D=0.462500
theta_P=-1.000000
theta_R=0.000000
\`\`\`

The evidence verifier in \`tools/verify_evidence.py\` checks these values directly.

## Evidence classification

**REPRODUCIBILITY-CORRECTED / EXPERIMENTALLY_SUPPORTED / CONTRACT TEST ONLY**

The result validates the experimental plumbing and its declared contract boundary, not the scientific transfer hypothesis.
