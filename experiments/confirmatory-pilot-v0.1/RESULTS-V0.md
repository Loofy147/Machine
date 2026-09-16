# Confirmatory Contract Pilot v0.1 — Results

**Status:** EXPERIMENTALLY_SUPPORTED / CONTRACT TEST ONLY  
**Not confirmatory evidence.**

## Purpose

This pilot tests the plumbing of the frozen transfer contract before building the full generator family `E`:

```text
source-class training
    -> diagnostic artifact
    -> fresh target cases
    -> compare baseline vs transfer
```

The transferred artifact is restricted to diagnostic identification/probe selection. The repair controller is identical across arms.

## Fixed configuration

- Seed: `20260916`
- Source cases: 40 `persistence/decay-fault`
- Target cases: 80 fresh `context-discrimination-fault`
- Primary policy: S2-like sequential probing
- Baseline: no transferred diagnostic artifact; 2 probe units; useful probe selected with pre-declared toy probability 0.55
- Transfer: one probe selected from a source-trained diagnostic artifact
- Repair controller: identical between arms

The artifact is generated from source episodes and contains no target labels, target outcomes, target repair candidates, or hidden class identifiers.

## Results

| Arm | Diagnostic success | Mean probe cost | Mean repair cost |
|---|---:|---:|---:|
| baseline | 0.5875 | 2.0 | 8.0 |
| transfer | 1.0000 | 1.0 | 8.0 |

Therefore:

\[
\theta_D = 1.0000-0.5875=0.4125
\]

\[
\theta_P = 1.0-2.0=-1.0
\]

\[
\theta_R = 8.0-8.0=0
\]

## Interpretation

### EXPERIMENTALLY_SUPPORTED — contract behavior

The pilot demonstrates that the current arm design can produce:

```text
transfer -> diagnostic change
transfer -> probe-cost change
transfer -/> repair-controller change
```

This is useful because it exercises the intended separation between `D`, `P`, and `R`.

### UNKNOWN — scientific claim

The pilot does **not** establish:

- transferable WHAT-learning;
- causal identification of either real mechanism;
- transport across a real generator-family shift;
- generalization;
- practical significance of `theta_D=0.4125`;
- equivalence of repair behavior in a realistic repair search;
- any confirmatory hypothesis.

The toy baseline probability and deterministic repair-cost rule are deliberately constructed fixtures, so the observed effect size cannot be used to select `delta`.

## Design findings

1. The transfer artifact must be auditable as a first-class artifact with version and provenance.
2. The repair controller must remain cryptographically/configurationally identical across arms in the real experiment.
3. The baseline diagnostic policy must be fully specified; otherwise `theta_D` conflates transfer with an unspecified baseline policy.
4. The real experiment must replace the toy probability and fixed repair cost with generator-derived observations and predeclared budgets.
5. Practical-effect margins remain independent inputs and must not be estimated from this pilot.

## Reproducibility

Run:

```bash
python3 experiments/confirmatory-pilot-v0.1/harness.py
```

Expected key outputs:

```text
theta_D=0.412500
theta_P=-1.000000
theta_R=0.000000
```

## Evidence classification

**EXPERIMENTALLY_SUPPORTED / CONTRACT TEST ONLY**

The result validates the experimental plumbing, not the scientific hypothesis.
