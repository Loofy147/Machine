# Bidirectional substrate verification v3

This directory contains the runnable harness and frozen result artifacts supplied with the `bidirectional-substrate-v3` research package.

## Contents

- `bidir_v3.py`, `bidir_v2.py`, and `bidir_pasted_original.py`: implementation and regression baselines.
- `substrate_lib.py`: substrate/index support code.
- `test_correctness.py`, `bench.py`, and `substrate_bench.c`: substrate correctness and benchmark entrypoints.
- `verify_v3.py`: bidirectional regression and optimality checks.
- `run_prov.py`, `exp_policies.py`, `analyze_policies.py`, `exp_scaling.py`, `claims_v2.py`, and `replicate.py`: experiment entrypoints.
- `*.json`, `*.yaml`, and `*.pkl` files: supplied result/provenance artifacts.
- `fetch_real_graphs.sh`: optional download of the Networkit input graphs used by the real-graph experiment.
- `bidir_harness_v3.zip` and `machine_substrate_artifacts.zip`: original nested archives, retained for provenance.

## Reproduction

Run commands from this directory. The substrate correctness suite is:

```sh
python3 test_correctness.py 400
```

The substrate benchmark can be run with:

```sh
python3 bench.py --out bench_results.json
gcc -O2 -o substrate_bench substrate_bench.c -lm
./substrate_bench 50000 4 7
```

The bidirectional baseline verification is:

```sh
python3 verify_v3.py
```

The full bidirectional workflow is documented in `README_v3.txt`. The real-graph stages require network access and first require:

```sh
sh fetch_real_graphs.sh
```

The bidirectional regression verifier requires the generated `orig_runs.pkl` and `prov_v2.pkl` inputs; those are not part of the supplied bidirectional archive. The newly supplied substrate artifact archive does provide the substrate correctness, benchmark, C source, and result files referenced by the formal specification.

## Provenance

Imported from the user-provided archives on 2026-09-21. The experiment code and result files are preserved without semantic edits; only this repository-level README and the surrounding destination paths were added for traceability.
