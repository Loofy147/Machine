# Context Contract Distribution Center v0.1

Offline planning core for matching fact-consistent, dependency-linked contract contexts under a fixed anchor. It emits JSON plans with paired context IDs, directional need witnesses, conflict explanations, a canonical input digest, and deltas after anchor updates.

This is an **experimental prototype**, not a production contract authority or remote dispatcher. Pair admission is existential (at least one need must be satisfied in one direction); other needs are explicitly reported as unmet with that partner.

## Run the unit and property tests

    python -m pip install -r requirements.txt
    python -m unittest -v
    python run_demo.py

## Actual-data benchmark: MultiWOZ 2.2

`stress_test_multiwoz.py` downloads the pinned MultiWOZ 2.2 test shards from the official `budzianowski/multiwoz` repository, verifies each Git blob hash, and uses actual dialogue IDs, per-service belief-state slot values, and unresolved requested slots. One dialogue becomes one context; anchors come from held-out real dialogue states. No feature discretization or synthetic needs are used.

    python -m pip install -r requirements.txt
    python -m unittest -v
    PYTHONHASHSEED=0 python stress_test_multiwoz.py

The runner writes `MULTIWOZ-REAL-DATA-RESULTS.json`, including pinned source provenance, checksums, context/graph statistics, exact-objective comparison, raw-fact plan validation, policy reconfiguration and real-anchor repair results. It downloads the corpus only when not cached, and makes no model calls.

Utility is deliberately limited to the number of distinct populated slots; this is a benchmark proxy, not business value. MultiWOZ dialogue records are genuine task-oriented dialogues, but they are not business/legal contracts. This test establishes planner behavior on a real dialogue corpus, not production contract performance or a universal proof.

## Supplementary synthetic controls

`stress_test_real_datasets.py` remains a separate synthetic control using feature distributions from scikit-learn's bundled Wine, Diabetes, Breast Cancer, and Digits datasets. Its need sets and partial contexts are generated, so it must not be described as actual-context validation.

    python -m pip install -r requirements-benchmark.txt
    PYTHONHASHSEED=0 python stress_test_real_datasets.py

See `docs/research/CONTEXT-CONTRACT-DISTRIBUTION-CENTER-v0.1.md` for the contract, provenance, test interpretation and promotion gates.
