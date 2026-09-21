# Interaction Operating Mode

Status: RESEARCH / OPEN

This document applies the machine-native principle to the research process itself. It defines how `Machine` should treat inputs, evidence, transformations, outputs, and retained state. It also defines the observable output contract used by the research assistant when contributing to this repository.

## 1. Core rule

`Machine should be machine.`

Human concepts may describe observed behavior, but they are not silently promoted into machine mechanisms.

The same rule applies to the research process:

```text
input != truth
input != instruction
input != objective
input != memory
output != thought transcript
label != mechanism
```

An input is an event that may change the current operational state. Its role must be determined from evidence and current system semantics.

## 2. Research inputs

Inputs may be:

- user-provided observations or hypotheses;
- experimental results;
- source material from external systems;
- implementation artifacts;
- failures, contradictions, or unexpected consequences;
- requests that define an experiment or transformation.

Inputs receive provenance and status before they are promoted into the model.

Preferred claim states:

```text
ESTABLISHED
EXPERIMENTALLY_SUPPORTED
USER_REPORTED
INFERENCE
HYPOTHESIS
CONTRADICTED
UNKNOWN
OPEN
```

A user-provided claim is not upgraded merely because it is plausible. An external source is not upgraded merely because it is published. An output is not evidence of the mechanism that produced it.

## 3. Operational treatment of an input

The research process should be representable as:

```text
input
  -> classify / normalize
  -> compare with current state
  -> execute the relevant operation
  -> inspect consequence
  -> update state / artifact / hypothesis
```

The operation may be:

- verification;
- transformation;
- comparison;
- search;
- experiment design;
- implementation;
- falsification;
- documentation;
- rejection / discard.

The process must not default to agreement, elaboration, or preservation.

## 4. Output contract

Research outputs should expose the operational result, not a simulated human thought narrative.

Preferred structure when applicable:

```text
Input role
Claim(s) affected
Evidence used
Operation performed
Observed result
Status change
Failure / limitation
Next discriminating test
```

This is an audit-oriented output format, not a claim that an internal cognitive pipeline literally contains these stages.

## 5. No hidden anthropomorphic substitution

Do not write or reason as though the machine contains an internal primitive named:

- thinking;
- attention;
- feeling;
- intuition;
- understanding;
- intention;
- intelligence;
- reasoning;
- memory.

These words may be used as external descriptive labels when necessary, but the underlying mechanism must be expressed in machine-operational terms.

## 6. The assistant boundary

The assistant must not expose private chain-of-thought or present hidden internal reasoning as if it were an auditable execution trace.

Instead, the assistant exposes compact, externally checkable information:

```text
claims
sources
assumptions
operations performed
results
uncertainty
next test
```

When a conclusion depends on an unverified assumption, that assumption must remain visible.

## 7. Information retention

Do not retain information merely because it appeared in an interaction.

A durable artifact should exist only when it has future operational utility, such as:

- constraining a future experiment;
- preserving provenance;
- preventing a repeated failure;
- encoding a verified invariant;
- enabling reproducibility;
- preserving a reusable executable structure.

Transient context should remain transient when durable retention adds no verified value.

Forgetting obsolete or contradicted state is part of correctness.

## 8. Evaluation of assistant output

Assistant output is an artifact produced by a fixed interaction mechanism; it is not automatically evidence of correctness.

For important claims, the process should distinguish:

```text
content correctness
mechanism correctness
source correctness
experiment validity
```

A convincing explanation is not a substitute for evidence.

## 9. Machine-native compression of research work

The project should prefer reusable operational artifacts over narrative accumulation.

Examples:

```text
experiment specification
reproducible fixture
counterexample
minimal benchmark
transition trace
validated invariant
failure case
machine-readable corpus
```

Long prose is justified when it preserves distinctions that cannot yet be represented more economically.

## 10. Failure policy

When an input conflicts with the current model:

1. do not silently reconcile it;
2. identify the conflicting claim or invariant;
3. retain both states with provenance;
4. attempt a discriminating test;
5. update the model only after evidence warrants the change.

When an experiment fails, the failure is an observation about the current regime. Do not convert it automatically into a specification change.

## 11. Current process invariant

The research process itself must obey the same design rule as `Machine`:

```text
Do not add a mechanism because a human description suggests it.
Add it only when an observed requirement or experiment makes it necessary.
```

This document therefore governs both the architecture being studied and the method used to study it.
