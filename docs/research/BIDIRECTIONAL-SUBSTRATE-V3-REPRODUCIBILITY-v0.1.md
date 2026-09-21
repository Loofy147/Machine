# Bidirectional Substrate v3 — Reproducibility Contract

Status: REPRODUCIBILITY-CONTRACT
Date: 2026-09-21

## Generated inputs are build outputs, not committed evidence

The v3 regression program consumes two intermediate pickle files:

- `orig_runs.pkl`
- `prov_v2.pkl`

These files are intentionally not committed. They are generated deterministically from the source harness before `verify_v3.py` runs:

1. `python bidir_pasted_original.py` -> `orig_runs.pkl`
2. `python run_prov.py` -> `prov_v2.pkl`
3. `python verify_v3.py`

Therefore their absence from Git does not invalidate the regression protocol; it means the previous manual invocation skipped the build step.

## CI contract

The workflow `.github/workflows/bidirectional-substrate-v3-conformance.yml` performs:

- Python syntax compilation;
- the 7-policy smoke test;
- JSON/YAML parsing;
- generation of both intermediate regression inputs;
- the full `verify_v3.py` suite.

The workflow does not download the external Networkit real-graph corpus. The real-graph experiment remains a separate, explicitly network-dependent stage.

## Independent substrate artifact boundary

The imported specification references `machine_substrate_artifacts.zip`, but that archive is not present in this package. Claims that depend exclusively on that archive remain imported/supplied evidence rather than newly reproduced evidence on this branch.

## Evidence rule

A CI pass establishes execution of the declared source-level regression on the CI environment. It does not upgrade literature claims, asymptotic proofs, or external benchmark provenance beyond what the respective source and evidence records support.
