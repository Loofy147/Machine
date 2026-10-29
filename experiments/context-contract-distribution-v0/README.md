# Context Contract Distribution Center v0.1

Offline planning core for matching fact-consistent, dependency-linked contract contexts under a fixed anchor. It emits JSON plans with paired context IDs, directional need witnesses, conflict explanations, a canonical input digest, and deltas after anchor updates.

This is an **experimental prototype**, not a production contract authority or remote dispatcher. Pair admission is existential (at least one need must be satisfied in one direction); other needs are explicitly reported as unmet with that partner.

## Run the unit and property tests

    python -m pip install -r requirements.txt
    python -m unittest -v
    python run_demo.py

## Real-dataset stress battery

The stress runner uses scikit-learn's bundled Wine, Diabetes, Breast Cancer, and Digits datasets to synthesize partial-observation contexts from discretized feature values. It runs the H1-H5 hard-test suites plus the B1-B3 scarce-supply follow-up and writes `REAL-DATASET-STRESS-RESULTS.json`.

    python -m pip install -r requirements-benchmark.txt
    PYTHONHASHSEED=0 python stress_test_real_datasets.py

The runtime reads local bundled datasets and performs no model calls or dataset downloads. The benchmark's contexts, anchors, feature subsets, and needs are still synthetic. Results are finite seeded evidence, not a production workload assessment or a universal proof. The JSON record includes software versions, pool-level metrics, per-suite outcomes, and an interpretation boundary.

See `docs/research/CONTEXT-CONTRACT-DISTRIBUTION-CENTER-v0.1.md` for the contract and promotion gates.
