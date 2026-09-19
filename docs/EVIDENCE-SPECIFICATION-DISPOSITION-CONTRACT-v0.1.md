# Evidence, Specification, and Disposition Contract v0.1

**Status:** RESEARCH-OPERATING-CONTRACT / INITIAL

## Purpose

The repository must distinguish a specification, an observation, evidence, and a conclusion.

A successful command is not by itself evidence for the scientific claim that motivated the command.

## 1. Evidence-bearing specification

Every material specification carries an evidence obligation:

\`\`\`text
Specification
  -> Claims
  -> Verification obligation
  -> Evidence
  -> Disposition
  -> Regression protection
\`\`\`

An unverified specification remains a supported working model only at its declared status. It must not silently become an established fact.

Evidence does not have one mandatory form. Depending on the claim, appropriate evidence may be:

- reproducible execution;
- controlled experiment;
- proof or derivation;
- contract test;
- benchmark;
- authoritative external source;
- cross-substrate equivalence;
- adversarial/security test.

## 2. Result is not conclusion

A result is an observation produced by an evaluator.

\`\`\`text
Result
  !=
Conclusion
\`\`\`

Before a result can update a claim, evaluate:

- evaluator/oracle validity;
- reproducibility;
- environment and scope;
- causal interpretation;
- contradiction;
- independence of supporting evidence;
- limitations.

An invalid evaluator result must first repair the evaluator or protocol.

## 3. Disposition states

A material result must terminate in one of:

\`\`\`text
CONFIRMED
PARTIALLY_CONFIRMED
CONTRADICTED
REFINED
INCONCLUSIVE
INVALID_RESULT
CONTEXT_BOUND
REGRESSION
NOVEL_SIGNAL
OPEN
\`\`\`

\`OPEN\` is a valid state only when the next discriminating action or blocking condition is recorded.

A concern must never disappear merely because the surrounding conversation or branch changed.

## 4. Durable claim record

A durable claim should be traceable to:

\`\`\`text
claim_id
claim_text
scope
status
spec_revision
evidence_ids
supporting_runs
contradicting_evidence
assumptions
limits
last_verified
next_discriminating_test
regression_protection
\`\`\`

The repository may implement this as JSON, YAML, database state, or another machine-readable store. The semantics are more important than the representation.

## 5. Evidence promotion rule

A runtime observation becomes a reusable capability only after:

\`\`\`text
Observed
  + Explained sufficiently
  + Generalized
  + Freshly verified
  + Institutionalized
  + Regression-protected
\`\`\`

Until then, keep it as an observation, signal, hypothesis, or open issue.

## 6. Specification drift

Specification debt occurs when:

- implementation changes while the specification does not;
- supporting evidence becomes stale;
- scope or assumptions change;
- a claimed invariant is no longer reproduced;
- two branches carry incompatible versions without explicit status.

Branch identity is part of specification provenance:

\`\`\`text
repository + branch + commit
\`\`\`

There is no repository-wide "current specification" for a claim whose branch/commit provenance is ambiguous.

## 7. Evidence regression gate

For every completed reproducible experiment, CI should prefer:

\`\`\`text
execute
  -> normalize result
  -> compare against evidence contract
  -> fail on drift
\`\`\`

over:

\`\`\`text
execute
  -> file exists
\`\`\`

An execution that succeeds while its recorded evidence changes is an evidence-integrity failure.

## 8. Current implementation

This branch contains a self-contained initial evidence package for three reproduced experiment surfaces:

```text
confirmatory-pilot-v0.1
error-source-localization-v0
target-oblivious-frontier-v0
```

`tools/verify_evidence.py` executes each referenced harness from this branch and checks the corresponding manifest/result contract.

The gate validates the **evidence path**, not the underlying scientific hypotheses.

## 9. Human-to-machine research path

The current process may begin with human evaluation because the semantics are still being established:

\`\`\`text
human concern
  -> explicit claim
  -> evidence obligation
  -> experiment/evaluation
  -> disposition
  -> machine-operational candidate
\`\`\`

The human description itself is not promoted into a machine primitive.

The eventual research question is whether the required disposition operation can be reduced to a minimal machine-native state transition and tested independently.

## 10. Governing invariant

> No important claim may disappear into context. It must resolve to evidence, contradiction, refinement, invalidation, or an explicitly maintained OPEN state.
