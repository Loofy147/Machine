# Error-Source Localization v0 Harness

Status: EXPERIMENT / HARNESS VALIDATION

## Purpose

Validate the execution harness for distinguishing four intervention layers under a hidden deterministic fault, before treating any controller behavior as evidence of machine-native source localization.

## Fixtures

The task is XOR over binary inputs `(x1, x2)`.

- Rich representation: `(x1, x2, x1*x2)`.
- Collapsed representation: `(x1, x2)`.
- Healthy baseline uses the rich representation.
- F0 healthy: no injected fault.
- F1 operation fault: execution transform inverts the prediction.
- F2 policy fault: scheduling transform inverts the prediction.
- F3 representation fault: representation is collapsed and loses the interaction term.
- F4 model fault: predictive transform inverts the prediction.

The hidden fault label is retained only by the harness for scoring.

## Interventions

All four intervention classes have one unit cost in v0:

`operate`, `reschedule`, `remodel`, `repartition`.

Each intervention can be tested on any fault. Wrong interventions do not reveal the hidden label; they only expose their measured pre/post score delta.

## Controllers

- `oracle`: applies the known minimal intervention; cost upper bound only.
- `local`: chooses randomly among non-repartition interventions; cannot change representation.
- `random`: samples any intervention independently.
- `probe`: fixed intervention order, stopping after recovery. This is a harness baseline, not learned diagnosis.
- `adaptive`: maintains action-level success/failure history across episodes and samples the next intervention from that history. It receives no fault labels and no context labels.

## Protocol

Default run:

```bash
python3 experiments/error-source-localization/harness.py \
  --episodes 100 \
  --seed 20260916 \
  --budget 4 \
  --out experiments/error-source-localization/results-v0.json
```

The fault schedule is deterministic: `F0,F1,F2,F3,F4` repeated. Train/test inputs are deterministic and fixed. Intervention cost is matched.

## Metrics

The harness records separately:

- recovery rate;
- localization rate (first recovery intervention equals the known minimal intervention for the fixture);
- mean intervention cost;
- final train score;
- final held-out score.

## Interpretation boundary

This v0 harness does **not** establish that a machine discovered the existence of representation faults, invented an ontology of fault layers, or performed causal introspection. The intervention classes are supplied by the experiment design, and the diagnostic actions are explicit interface choices.

The next research step is to remove the fixed action-to-fault correspondence from the controller's useful prior, introduce hidden fault switching and matched intervention costs, and then test whether the machine can infer when a representation change is causally necessary rather than merely eventually finding one.
