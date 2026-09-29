# HSDCR End-to-End Composition v0.2

Status: **RESEARCH / NON-NORMATIVE / OPEN**

This is a hardened re-run of the v0.1 semantic-junction experiment.

## What changed from v0.1

The v0.2 harness removes two methodological weaknesses identified during review:

1. Signal loss is now executed, not represented by a hard-coded boolean. The signal stream is created, counted, cleared, and reconstruction is performed from durable acceptance history only.
2. The result hash is computed over a canonical payload that explicitly excludes the self-hash field. This removes the ambiguous two-pass/self-reference convention.

## Scope

The experiment still uses two real source observations at the contribution boundary:

- GitHub Machine PR #10;
- a real public AT Protocol repository record.

The evidence and authority objects remain normalized fixtures. They are semantic slots used to test separation, not claims of live security, authority, durability, or performance equivalence.

## Kill target

The target remains the strongest current non-novelty hypothesis:

`repository/change substrate + signal/observation + evidence/provenance + authority/capability + explicit acceptance transition + control/orchestration`

If the tested semantic junction remains expressible with ordinary typed data, explicit transition/policy rules, and known capabilities, no new repository or execution primitive is required by this test.

## Result interpretation

A passing run means only that the declared composition check reproduced its stored evidence and did not detect an irreducible primitive at this boundary.

It does **not** prove architectural novelty, protocol status, production security, or provider equivalence.

## Next discriminating test

Replace the normalized evidence and authority fixtures with two independent real implementations/sources, while keeping the same abstract transition oracle and the same separate equivalence dimensions.
