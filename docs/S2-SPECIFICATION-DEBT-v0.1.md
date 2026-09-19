# S2 Specification Debt v0.1

Recorded: 2026-09-19
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0
Status: OPEN / PRE-FREEZE

## Question

What semantic definition of S2 should be frozen for implementation conformance?

## Current disposition

A candidate semantic specification now exists:

    docs/S2-CANDIDATE-SPEC-v0.3.md

It is still PRE-FREEZE. Therefore canonical S2 semantics remain OPEN until its independent review checklist is accepted.

Earlier v0.1/v0.2 candidates were superseded as the semantic boundary was refined.

## What evidence establishes

The experimental implementation currently labeled S2 has an evidence-backed profile:

    docs/S2-EXPERIMENTAL-SUBSTRATE-PROFILE-v0.1.md

That profile remains evidence about an implementation. It does not define S2.

## Remaining specification questions

The independent candidate still requires review of:

- whether `lookup(R,k)` is the intended semantic boundary;
- whether relations should be abstract partial functions;
- whether `Miss | Hit(v)` is the intended abstract result algebra;
- whether lookup must preserve the abstract relation;
- whether invalid-input behavior should remain outside the semantic core.

These are specification decisions, not implementation findings.

## Separate protocol debt

Frontier/conformance concerns are now separated into:

    docs/S2-CONFORMANCE-FRONTIER-PROTOCOL-v0.1.md

That protocol must be aligned with `docs/SUBSTRATE-FRONTIER-CONTRACT-v0.1.md` before resource claims are made.

## Non-circularity rule

Do not promote implementation properties into S2 semantics after the fact.
The order remains:

    candidate semantics
        ↓
    freeze
        ↓
    implementation targets
        ↓
    conformance evidence
        ↓
    revise only on explicit specification grounds

## Next action

Review and accept/revise the v0.3 semantic candidate and its freeze checklist. Then derive the conformance suite without consulting current implementation-specific behavior as a source of normative requirements.