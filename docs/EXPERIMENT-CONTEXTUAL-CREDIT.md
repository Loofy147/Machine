# Experiment: Contextual Credit Assignment

Status: EXPERIMENTALLY_SUPPORTED / LIMITED

## Purpose

Test whether historical outcome credit should be indexed by operating context rather than attached globally to an operation identity.

This experiment isolates proposal policy. Candidate correctness/performance profiles are measured separately and supplied to the policy layer so that the comparison does not conflate context indexing with live candidate execution.

## 1. Real context crossover

Two validation streams were measured independently:

| Context | Operator | Mean runtime | Correct |
|---|---|---:|---|
| REPEAT | `memo_cache` | 0.00013697 s | yes |
| REPEAT | `math_isqrt` | 0.00017740 s | yes |
| REPEAT | `sqrt_bound` | 0.00023697 s | yes |
| UNIQUE | `math_isqrt` | 0.00020029 s | yes |
| UNIQUE | `memo_cache` | 0.00024879 s | yes |
| UNIQUE | `sqrt_bound` | 0.00028149 s | yes |

The ordering therefore crosses between contexts: `memo_cache` is best in REPEAT, while `math_isqrt` is best in UNIQUE.

One validation stream also showed `off_by_one_bug` as correct in REPEAT while it failed in UNIQUE. This is a validation-coverage warning: candidate correctness cannot be inferred from one stream or from aggregate volume alone.

## 2. Policy comparison

Contexts were presented in the sequence:

```text
REPEAT -> UNIQUE -> REPEAT -> UNIQUE
```

Each block contained 50 generations. Sixty seeds were evaluated.

Two proposal policies were compared:

### Context-aware

Maintains separate outcome statistics for each explicit context:

```text
(context, operator) -> history
```

### Context-blind

Maintains one global history:

```text
operator -> history
```

The reward signal was whether the tested candidate was correct and faster than the current operator in the active context.

## 3. Return-to-context result

Metrics were measured on block 3, where REPEAT recurred after an intervening UNIQUE block.

| Policy | `memo_cache` weight at block start | active fraction in block | reacquire generation |
|---|---:|---:|---:|
| context-aware | 0.667 ± 0.000 | 0.989 ± 0.017 | 0.55 ± 0.83 |
| context-blind | 0.102 ± 0.013 | 0.956 ± 0.048 | 2.22 ± 2.40 |

Welch-style normal approximation:

```text
memo_weight_at_block_start: t = +326.35, p ≈ 0
active_fraction_in_block:   t = +5.08,  p = 3.773e-07
```

## 4. Claim

**EXPERIMENTALLY_SUPPORTED, TESTBED-SPECIFIC**

When an operation changes value across operating contexts, separating outcome history by context preserves useful operator-specific credit when a previous context recurs.

The causal distinction is:

```text
(context, operation) -> outcome history
```

versus:

```text
operation -> global outcome history
```

The result is evidence for context-indexed credit assignment in this controlled policy experiment.

## 5. What this does not establish

It does not establish:

- context discovery;
- autonomous identification of operating regimes;
- online candidate execution during every policy step;
- reusable learned executable structure;
- causal reflection;
- general learning outside the tested environment.

The context labels (`REPEAT`, `UNIQUE`) were supplied explicitly. The candidate performance profiles were also precomputed.

Therefore this is not yet a test of whether the machine discovers its own context representation from state or event history.

## 6. Metric limitation

`active_fraction` measures persistence of the selected configuration. It is not a complete policy-quality metric.

Future evaluation should include:

- cumulative regret against a per-context oracle;
- accepted improvements;
- bad proposals;
- proposal quality;
- recovery time after context switches;
- performance after history erasure or permutation controls.

## 7. Next discriminating experiment

Remove the explicit context label.

Derive context features from machine-observable state or recent event history, for example:

```text
recent event recurrence
value distribution
state-transition statistics
resource/load pattern
```

Compare:

```text
history erased
history global
history indexed by supplied label
history indexed by machine-derived context
```

The critical question is whether a machine can discover a useful operational regime distinction and use it to condition future credit assignment without receiving the regime name from the experiment harness.
