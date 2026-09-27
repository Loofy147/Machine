# HSDCR Composition Reduction v0.1 — Results

Status: **INTERNAL MODEL CHECK / LOCAL REPLAY**

Repository: `Loofy147/Machine`
Branch: `research/hsdcr-reassessment-v0`
Base: `research/bidirectional-substrate-v3@59fab62704875193801db77c7cb8361475297f48`

## Question

After separating domain semantics from known substrate capabilities and methodological constraints, does the remaining candidate require a new execution or repository primitive?

## Result

```
single_family_absorption = NOT_IDENTIFIED
composition_can_be_described_with_existing_capabilities = TRUE
new_execution_primitive_detected = FALSE
new_repository_primitive_detected = FALSE
architectural_novelty = OPEN
```

## Component-removal observations

Removing each declared domain-semantic role collapses a required distinction:

- observation: signal/evidence separation disappears;
- evidence: observation would need to carry evidentiary status;
- authority: evidence/decision would need to carry mutation permission;
- decision/acceptance: canonicalization becomes implicit;
- contribution/proposal: the pre-canonical proposal locus disappears;
- reconstruction: durable reconstruction semantics disappear.

However, each role can still be encoded as ordinary typed data plus explicit relations/transitions in the remaining state substrate.

Therefore:

```
semantic necessity != new primitive
```

## Provider substitution observation

The real GitHub PR #10 → native AT repository-record substitution remains non-equivalent for the specific proposal-before-canonical-acceptance boundary. An application-level proposal/acceptance record is required.

This is a **direct substitution collision**, not a general limitation of AT Protocol.

## Evidence class

This experiment is an internal deterministic model check. It is not independent empirical evidence about production systems and does not establish architectural novelty.

## Regression finding

The first GitHub Actions execution of this gate failed at the **evidence comparison step**, while the harness itself passed. The stored result did not byte-match the current executable output. The fixture was corrected and the gate is now configured to run on both push and pull_request events.

The failure is treated as an **evidence-integrity / reproducibility defect in the experiment package**, not as evidence against the research hypothesis.

## Canonical payload hash

`e487676f13317834e3a330889a9c28666c571832af4c02ff8cae1ad00d2c5d4a`

## Next discriminating test

Execute a mixed real/normalized end-to-end composition with two providers at each critical boundary and test:

- contribution non-canonicality;
- evidence/authority separation;
- duplicate-safe acceptance;
- durable reconstruction after signal loss;
- provider replacement without ontology leakage;
- semantic equivalence separately from resource/authority/durability equivalence.
