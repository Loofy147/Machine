# Ledger Entry — Contract Pilot v0.1

This entry is linked to `CONFIRMATORY_FREEZE_LEDGER_V0.1.md` and records the mini-pilot without modifying the scientific freeze state.

## Evidence boundary

Status: **EXPERIMENTALLY_SUPPORTED / CONTRACT TEST ONLY**.

The pilot exercises the baseline/transfer plumbing and the separation between diagnostic/probe effects and repair machinery. It is not confirmatory evidence and cannot determine any practical-effect margin.

## Configuration

- Seed: `20260916`
- Source: 40 `persistence/decay-fault` cases
- Target: 80 fresh `context-discrimination-fault` cases
- Policy: S2-like sequential probing
- Transfer artifact: diagnostic identification/probe-selection only
- Repair controller: identical across arms

## Results

| Metric | Baseline | Transfer | Difference |
|---|---:|---:|---:|
| Diagnostic success | 0.5875 | 1.0000 | `theta_D = 0.4125` |
| Mean probe cost | 2.0 | 1.0 | `theta_P = -1.0` |
| Mean repair cost | 8.0 | 8.0 | `theta_R = 0` |

## Interpretation

The pilot validates the intended contract shape:

```text
transfer artifact -> diagnostic/probe behavior may change
transfer artifact -/> repair controller may change directly
```

It does not establish transport, WHAT-learning, causal mechanism identification, generalization, or practical significance.

The toy effect sizes are ineligible for selection of `delta_D`, `delta_R+`, or `delta_R-`.

See:

- `experiments/confirmatory-pilot-v0.1/harness.py`
- `experiments/confirmatory-pilot-v0.1/RESULTS-V0.md`
- `CONFIRMATORY_FREEZE_LEDGER_V0.1.md`
