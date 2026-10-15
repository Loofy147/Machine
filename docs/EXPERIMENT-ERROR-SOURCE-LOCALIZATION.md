# Experiment: Error-Source Localization

Status: EXPERIMENT DESIGN / OPEN

## Purpose

Test whether a machine can detect that a persistent failure is not caused by the current operation or local optimization procedure, but by the representation/partition that defines the problem space itself.

The experiment asks a narrower machine-native question:

> Can a machine detect when continued optimization inside its current representation is no longer useful, generate an alternative representation, and select the smallest intervention level that removes the failure?

This is not a test of human-like introspection. The machine is not given the name of the fault. It is given executable intervention mechanisms and consequences from which the causal source may be inferred.

## 1. Core distinction

A bad result can originate at different levels:

```text
world / input
    -> representation / partition
    -> model / prediction
    -> policy / scheduling
    -> operation
    -> execution
    -> result
```

The same observed failure can therefore have different causes.

The experiment must distinguish at least:

```text
F0  no fault
F1  operation fault
F2  policy/process fault
F3  representation/partition fault
F4  model/prediction fault
```

The fault identity is hidden from the machine and retained only by the experiment harness for ground-truth scoring.

## 2. Primary hypothesis

A machine with only local optimization tends to remain inside the current representation and can waste computation after the attainable performance ceiling has been reached.

A machine with controlled representation interventions can detect a diagnostic pattern such as:

```text
local process changes -> little/no improvement
representation change -> large improvement
```

and therefore allocate future computation to representation revision.

Status: HYPOTHESIS.

## 3. Critical anti-cheating condition

The machine must not receive:

- the fault class;
- a representation-quality score;
- a label such as `partition_wrong`;
- direct access to the hidden target mapping;
- an oracle telling it which intervention is correct.

It may receive only normal operational observations and the measurable consequences of interventions it chooses to perform.

## 4. Minimal machine interface

The testbed exposes a small set of intervention classes:

```text
operate            modify local operation parameters/choice
reschedule         modify policy or scheduling parameters
remodel            modify prediction/model parameters
repartition        modify the representation/partition
```

The machine may also choose:

```text
continue            spend another budget unit without structural change
probe               evaluate a proposed intervention on controlled inputs
commit              retain an intervention
revert              return to the previous configuration
```

The interface is deliberately explicit. It does not claim that these intervention classes are universal machine primitives.

## 5. Deterministic fault environments

Each environment is deterministic and constructed so that the true source of failure is known to the harness.

### E0 — healthy

The original representation, model, policy, and operation can achieve the task.

### E1 — operation fault

The representation and model retain sufficient information. One local operation is incorrect or inefficient, but an allowed operation change can restore performance without changing the representation.

Expected minimum sufficient intervention:

```text
operate
```

### E2 — policy fault

The available operations and representation are sufficient, but the scheduler repeatedly chooses an inferior operation/path.

Expected minimum sufficient intervention:

```text
reschedule
```

### E3 — representation/partition fault

The representation maps distinct task-relevant states to the same operational state:

```text
P(x_a) == P(x_b)
```

while:

```text
Target(x_a) != Target(x_b)
```

No operation, scheduler, or model restricted to the collapsed representation can achieve the required distinction.

A legal repartition can restore the missing distinction.

Expected minimum sufficient intervention:

```text
repartition
```

### E4 — model fault

The representation preserves the required information, but the predictive model is systematically wrong. A model revision can restore performance without repartitioning.

Expected minimum sufficient intervention:

```text
remodel
```

## 6. Simpson-style partition condition

One environment family should include a deterministic aggregation reversal.

For contexts `C1` and `C2`:

```text
score(A | C1) > score(B | C1)
score(A | C2) > score(B | C2)
```

while under an aggregated partition:

```text
score(A) < score(B)
```

The machine is not told that the aggregate relation is misleading.

A successful representation intervention must expose a conditional variable or partition that preserves the stable within-context relation.

This is used as a controlled representation-failure fixture, not as evidence that every representation error is a Simpson's paradox.

## 7. XOR-style partition fixture

A second minimal fixture uses the same optimizer with two representations:

```text
P0 = (x1, x2)
P1 = (x1, x2, x1*x2)
```

with an XOR-like target that is not linearly separable under `P0` but is representable under `P1`.

The fixture establishes the expected signature:

```text
more optimization under P0 -> plateau
representation change P0 -> P1 -> large improvement
```

This is a sanity check for the experiment harness. It is not itself evidence that the machine can diagnose the fault.

## 8. Required controls

### C0 — Local-optimization control

The machine can modify operation/policy parameters but cannot repartition.

Expected result on E3:

```text
persistent ceiling
```

### C1 — Random-intervention control

All intervention classes are available, but the next intervention is sampled independently of history.

This measures the benefit of causal diagnosis over random structural change.

### C2 — Oracle-layer upper bound

The fault class is revealed only to the oracle controller, which applies the known minimal intervention.

This is a reference upper bound, not a realistic machine condition.

### C3 — Full diagnostic policy

The machine observes consequences of interventions and may update its belief over fault layers.

This is the experimental condition of interest.

### C4 — Shuffled-history diagnostic control

The same diagnostic mechanism is given history with layer/outcome associations shuffled across episodes.

This tests whether improvement comes from causal history rather than merely from additional state or compute.

## 9. Diagnostic state

The machine may retain records such as:

```text
{
  intervention,
  pre_score,
  post_score,
  delta,
  affected_inputs,
  resource_cost,
  reversible,
  committed
}
```

The record must not contain the hidden fault label.

A diagnostic belief may be represented as:

```text
P(fault_level | intervention history, observed consequences)
```

This notation describes the experiment; it does not require a probabilistic implementation.

## 10. Causal signature of representation failure

Representation failure should produce a distinctive intervention pattern:

```text
operate changes
    -> low or unstable gain

reschedule changes
    -> low or unstable gain

remodel changes
    -> low or unstable gain

repartition changes
    -> large persistent gain
```

The signature is not assumed to be universal. It is the discriminating pattern for the deterministic fixture.

## 11. Primary metrics

### Detection

Did the machine infer that the current representation may be insufficient before exhausting the available budget?

### Localization

Did it assign the highest diagnostic probability to the true fault level before correction?

### Minimal intervention depth

How many intervention levels were changed before the task recovered?

The ideal E3 trajectory is:

```text
observe plateau
-> test representation hypothesis
-> repartition
-> recover
```

not:

```text
operation changes
-> policy changes
-> model changes
-> repeated retries
-> eventual random repartition
```

### Diagnostic regret

Extra computation spent on interventions that could not remove the true fault.

### Recovery cost

Total resource cost from first failure until stable recovery.

### Stability

Whether the recovered system remains correct on held-out inputs and under repeated replay.

## 12. Metrics must separate four capabilities

Do not collapse these into one score:

```text
failure detection
fault localization
intervention selection
post-intervention generalization
```

A system can detect failure without localizing it, or localize correctly without choosing a useful intervention.

## 13. Stronger test: hidden fault switching

After the machine learns a diagnostic policy, change the hidden fault source across deterministic episodes:

```text
E1 -> E3 -> E2 -> E4 -> E3
```

The machine is not told when the fault class changes.

This tests whether the diagnostic policy is context-sensitive rather than a fixed association between one benchmark and one repair.

## 14. Stronger test: representation expansion is not enough

A representation system must pay an explicit cost for every additional distinction it introduces.

Otherwise the machine can always solve the problem by creating a maximally detailed representation.

Therefore the benchmark must include a controlled tradeoff:

```text
representation richness
vs
memory / compute / generalization cost
```

The desired machine should identify a sufficient representation, not simply maximize representational detail.

## 15. Falsifiers

The hypothesis is weakened if:

1. a local optimizer reliably escapes representation ceilings without representation change;
2. random intervention performs as well as diagnostic intervention after matched compute;
3. the diagnostic policy depends on the hidden fault label or another leaked oracle variable;
4. representation changes improve training cases but fail on held-out cases;
5. the machine repeatedly over-repartitions healthy or merely policy-faulted tasks;
6. there is no reproducible intervention signature distinguishing representation fault from lower-level faults;
7. all gains disappear when intervention costs are matched.

## 16. Main question

> How can a machine discover that the problem is not the result, the local operation, or the search procedure, but the way the problem has been partitioned into a space of possible operations?

A successful answer would not be "the machine introspected correctly."

The stronger machine-native answer would be:

```text
persistent failure
+ targeted intervention
+ counterfactual response
+ causal history
-> representation diagnosis
-> minimum sufficient structural change
```

## 17. Relation to the broader Machine program

This experiment sits between:

```text
context-conditioned credit
        ↓
error-source localization
        ↓
representation adaptation
        ↓
reusable executable structure
        ↓
causal reflection
```

It tests whether adaptive behavior can arise from the machine's own intervention structure rather than from a human-labeled cognitive module.

It does not establish emotion, intelligence, consciousness, or a universal theory of representation.
