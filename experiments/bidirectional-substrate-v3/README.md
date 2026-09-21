# Bidirectional substrate verification v3

This directory contains the runnable harness and frozen result artifacts supplied with the `bidirectional-substrate-v3` research package.

## Contents

- `bidir_v3.py`, `bidir_v2.py`, and `bidir_pasted_original.py`: implementation and regression baselines.
- `substrate_lib.py`: substrate/index support code.
- `verify_v3.py`: regression and optimality checks.
- `run_prov.py`, `exp_policies.py`, `analyze_policies.py`, `exp_scaling.py`, `claims_v2.py`, and `replicate.py`: experiment entrypoints.
- `*.json`, `*.yaml`, and `*.pkl` files: supplied result/provenance artifacts.
- `fetch_real_graphs.sh`: optional download of the Networkit input graphs used by the real-graph experiment.
- `bidir_harness_v3.zip`: the original nested archive, retained for provenance.

## Reproduction

Run commands from this directory. The baseline verification is:

```sh
python3 verify_v3.py
```

The full workflow is documented in `README_v3.txt`. The real-graph stages require network access and first require:

```sh
sh fetch_real_graphs.sh
```

The supplied package does not include `machine_substrate_artifacts.zip`, although the imported specification references it. Substrate-artifact-dependent claims therefore remain documented as supplied evidence and are not represented as newly reproduced by this branch.

## Provenance

Imported from the user-provided archive on 2026-09-21. The experiment code and result files are preserved without semantic edits; only this repository-level README and the surrounding destination paths were added for traceability.
