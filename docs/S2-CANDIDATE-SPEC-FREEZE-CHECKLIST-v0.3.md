# S2 Candidate Specification — Freeze Checklist v0.3

Purpose: verify semantic independence, internal coherence, and clean separation from frontier protocol.

## A. Independence

- [ ] No host-language type is normative.
- [ ] No implementation primitive name is normative.
- [ ] No benchmark result is normative.
- [ ] No concrete sentinel is normative.
- [ ] No current tick value is normative.
- [ ] No storage layout is normative.
- [ ] No current property-suite observation is normative.

## B. Semantic core

- [ ] S2 is direct point access, not membership-only.
- [ ] `lookup(R,k)` is the semantic boundary.
- [ ] `R : K ⇀ V` is the intended abstraction.
- [ ] `Eq_K` is a typed equivalence relation.
- [ ] `Miss | Hit(v)` is the intended result algebra.
- [ ] `Miss` is distinct from every valid value.
- [ ] lookup preserves the abstract relation.
- [ ] values are opaque.

## C. Partiality

- [ ] Missing keys are normal and produce Miss.
- [ ] Invalid inputs are outside the semantic core.
- [ ] Unknown/incomplete information is not silently mapped to Miss.

## D. Separation

- [ ] S1 derivability is not assumed.
- [ ] implementation representation is not semantic.
- [ ] timing is not semantic.
- [ ] preprocessing is not semantic.
- [ ] resource cost is not semantic.
- [ ] substrate-wide immutability is not required.

## E. Frontier alignment

- [ ] availability timing is specified separately.
- [ ] storage/representation budget is specified separately.
- [ ] online work is specified separately.
- [ ] access cost is specified separately.
- [ ] target-dependent preprocessing is explicitly controlled.

## F. Freeze

Only after A-E are accepted should v0.3 be frozen and implementation conformance begin.

Any mismatch is classified as:

    PASS
    FAIL
    SPECIFICATION-DEFECT

and is not silently absorbed into the specification.