# S2 Conformance Results v0.1 — Experimental Target

Recorded: 2026-09-19
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0
Semantic source: docs/S2-CANDIDATE-SPEC-v0.3.md
Protocol: docs/S2-CONFORMANCE-FRONTIER-PROTOCOL-v0.2.md
Target: experiments/substrate-interpreter-v0.2/
Status: TARGET NON-CONFORMANT / STATIC SOURCE REVIEW

## 1. Execution status

Spec-derived conformance suite:

    experiments/s2-conformance-v0.1/

A repository-native GitHub Actions run was not registered for commit 8b90d6fb53a39b3c0f20556937088a0b959e89ab at inspection time.

A direct local run was not claimed because the execution environment could not resolve GitHub's raw-content host. Therefore this document does not claim a pytest execution result.

## 2. Static conformance result

The current experimental S2 implementation is non-conformant with the semantic S2 candidate.

Root defect:

    return args[0].get(args[1], NIL)

from:

    experiments/substrate-interpreter-v0.2/machine.py

This concrete encoding maps both:

    absent key      -> NIL
    present key with value NIL -> NIL

The S2 specification requires:

    absent key      -> Miss
    present key      -> Hit(v)

with Miss distinct from every Hit(v).

Therefore the target cannot realize the required disjoint result algebra for the full declared value domain.

## 3. Affected conformance requirements

| Requirement | Disposition | Reason |
|---|---|---|
| S2-C02 absent key -> Miss | FAIL | concrete miss is encoded as NIL with no distinct result tag |
| S2-C03 Miss distinct from Hit(v) | FAIL | NIL can denote both cases |
| S2-C08 valid value resembling miss encoding | FAIL | Hit(NIL) cannot be distinguished from Miss |
| S2-C11 empty relation -> Miss | FAIL | empty lookup returns the same NIL encoding |

These are manifestations of one output-encoding defect, not four independent implementation defects.

## 4. What is not yet classified

The following should not be marked PASS without execution of the derived suite:

- Eq_K conformance;
- value opacity across broader value domains;
- relation preservation under all target values;
- repeatability;
- representation independence;
- relation isolation.

Those remain UNVERIFIED rather than FAIL.

## 5. No specification change is justified

The observed defect does not justify weakening the S2 specification.

The specification deliberately requires a semantic distinction between:

    Miss
    Hit(v)

for all valid values v.

The correct repair direction is target-side: introduce a concrete result encoding that preserves the abstract distinction, then rerun the unchanged conformance suite.

## 6. Scientific disposition

    S2 specification        = unchanged / PRE-FREEZE
    experimental target     = NON-CONFORMANT on result algebra
    root cause              = concrete miss-value collision
    resource claims         = not implicated by this conformance result
    canonical Machine       = not assessed

Conformance failure is evidence about the target implementation. It is not evidence that the S2 semantic specification is incorrect.