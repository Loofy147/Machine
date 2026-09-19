# S2 Candidate Specification — Freeze Checklist v0.2

Purpose: verify semantic independence and boundary separation before conformance work.

## A. Independence

- [ ] No host-language type is normative.
- [ ] No current implementation primitive name is normative.
- [ ] No current benchmark number is normative.
- [ ] No current implementation sentinel is normative.
- [ ] No current access-tick value is normative.
- [ ] No current storage layout is normative.
- [ ] No current property-suite observation is normative.

## B. Semantic core

- [ ] `lookup(R,k)` is the intended semantic boundary.
- [ ] The relation abstraction is independently justified.
- [ ] `Miss | Hit(v)` is the intended result algebra.
- [ ] lookup is intended to preserve the abstract relation.
- [ ] valid values are opaque to lookup.
- [ ] invalid-input behavior is intentionally outside the core.

## C. Separation

- [ ] S1 derivability is not assumed.
- [ ] timing is not embedded as semantic meaning.
- [ ] preprocessing is not embedded as semantic meaning.
- [ ] resource cost is not embedded as semantic meaning.
- [ ] representation choice is not embedded as semantic meaning.

## D. Frontier protocol alignment

- [ ] availability timing is specified separately.
- [ ] representation/storage budget is specified separately.
- [ ] online work is specified separately.
- [ ] direct-access cost is specified separately.
- [ ] target-dependent preprocessing is explicitly controlled.

## E. Freeze rule

Only after A-D are accepted should the semantic specification be frozen and implementation conformance begin.

Any implementation mismatch is then classified as:

    PASS
    FAIL
    SPECIFICATION DEFECT

rather than being silently absorbed into the specification.