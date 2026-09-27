# Error-Source Localization v0 — First Run

Status: EXPERIMENTALLY_SUPPORTED / HARNESS VALIDATION ONLY

Command:

```bash
python3 experiments/error-source-localization/harness.py --episodes 100 --seed 20260916 --budget 4 --out results-v0.json
```

## Aggregate result

| controller | recovery | localization | mean cost | final train | final held-out |
|---|---:|---:|---:|---:|---:|
| oracle | 1.00 | 1.00 | 0.80 | 1.00 | 1.00 |
| probe | 1.00 | 1.00 | 2.00 | 1.00 | 1.00 |
| adaptive | 1.00 | 1.00 | 2.22 | 1.00 | 1.00 |
| random | 0.72 | 0.72 | 2.17 | 0.7725 | 0.7725 |
| local | 0.67 | 0.67 | 2.30 | 0.82 | 0.82 |

Fault-specific recovery:

| fault | local | random | probe | adaptive | oracle |
|---|---:|---:|---:|---:|---:|
| F0 healthy | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| F1 operation | 0.70 | 0.65 | 1.00 | 1.00 | 1.00 |
| F2 policy | 0.80 | 0.65 | 1.00 | 1.00 | 1.00 |
| F3 representation | 0.00 | 0.65 | 1.00 | 1.00 | 1.00 |
| F4 model | 0.85 | 0.65 | 1.00 | 1.00 | 1.00 |

## What this run establishes

1. The fixture distinguishes a representation ceiling from lower-level injected faults: `F3` cannot be recovered by the local controller because repartitioning is unavailable.
2. The intervention API and metrics are operational: all hidden fault classes have deterministic minimal repairs, and held-out replay tracks training recovery in this fixture.
3. A history-bearing action policy can recover all five fixture classes without receiving fault labels, but its mean intervention cost is still well above the oracle upper bound.

## What it does **not** establish

This run does not show causal reflection, self-discovered fault classes, or autonomous discovery that a representation is wrong. The `probe` controller succeeds through a fixed intervention order supplied by the experimenter, and `adaptive` receives the action vocabulary and learns only action-level success statistics.

The current strongest interpretation is therefore: **the harness is valid enough for the next experiment, but the machine-native diagnosis claim remains open.**

## Next discriminating test

Use hidden fault switching with the same observable input family, add a cost for representational richness, and randomize the mapping between intervention action names and internal mechanisms. Require the controller to choose whether to continue operating, test another layer, or repartition before recovery, with no fixed action order. The key measure becomes whether representation changes are selected because local interventions systematically fail, rather than because `repartition` is simply tried eventually.
