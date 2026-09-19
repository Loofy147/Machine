# S2 Candidate Specification — Freeze Checklist v0.1

Purpose: verify that the candidate specification was authored without importing current implementation properties.

## Independence checks

- [ ] No host-language type is normative.
- [ ] No current implementation primitive name is normative.
- [ ] No current benchmark number is normative.
- [ ] No current implementation sentinel is normative.
- [ ] No current access-tick value is normative.
- [ ] No current implementation representation is normative.
- [ ] S1 expressibility is not assumed either way.
- [ ] Resource complexity is separated from semantic correctness.
- [ ] The specification defines required semantics before implementation conformance is evaluated.

## Required review questions

1. Is `lookup(R,k)` the intended semantic boundary of S2?
2. Is the relation model a partial function the intended abstraction?
3. Is `miss` required as a semantic outcome distinct from all valid values?
4. Should lookup be semantically observational/read-only?
5. Is target-dependent preprocessing intentionally excluded from S2 semantics?
6. Are resource guarantees intentionally deferred to a separate contract?
7. Are representation and host-language choices intentionally non-normative?

Any answer that changes the semantic core requires a revision of the candidate specification before conformance work starts.

## Status

PRE-FREEZE. Conformance testing must not be interpreted as evidence for the candidate specification until this checklist is accepted.