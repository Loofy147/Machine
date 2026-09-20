# S2 Conformance / Frontier Full Audit v0.1

Recorded: 2026-09-20
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0
Audit head: 4869c11681ec0f1245a691cd9f092d3d51545c8c

## Audit disposition

The post-repair execution path is reproducible and internally consistent for the current executable suite and finite resource fixture.

However, the current evidence must not be described as full S2 semantic conformance or as verification against a frozen/canonical S2 specification.

Current classification:

- candidate-spec conformance on executed assertions: EXPERIMENTALLY_SUPPORTED
- target repair correctness for Miss/Hit(NIL): ESTABLISHED + EXECUTIONALLY SUPPORTED
- resource-vector replay equality: EXPERIMENTALLY_SUPPORTED AS RECORDED
- canonical/final S2 conformance: OPEN
- complete 15-item semantic coverage: OPEN
- canonical Machine substrate conformance: OPEN
- asymptotic/resource theorem: OPEN

## 1. Verified execution chain

GitHub Actions run #10 (35466392638) on commit 6100337bb75bd180c75ac874ea1021d3bd69c792:

- conformance command completed successfully;
- 11 passed;
- audit exit 0;
- all six compared evidence fields were equal before/after;
- resource values reproduced exactly:
  - offline construction field = 5;
  - stored entries = 5;
  - S1 scan = 676 transition / 291 access;
  - S2 direct = 20 transition / 10 access;
  - ratios = 33.8x / 29.1x;
  - workload outputs = [40, 0, 20, NIL, 30].

Run #11 (35466483337) on evidence-only commit 4869c11681ec0f1245a691cd9f092d3d51545c8c independently repeated the same execution path and succeeded with the same vector.

Replay artifacts:
- run #10 artifact 10590214678;
- run #11 artifact 10591461981.

## 2. Specification status correction

docs/S2-CANDIDATE-SPEC-v0.3.md is explicitly CANDIDATE SPECIFICATION / PRE-FREEZE, and its current-status section still says implementation conformance is NOT YET ASSESSED.

The freeze checklist docs/S2-CANDIDATE-SPEC-FREEZE-CHECKLIST-v0.3.md is an unchecked template.

Therefore the correct claim is:

    conformant with the tested obligations derived from candidate v0.3

not:

    conformant with a frozen/canonical S2 specification.

This is a documentation/provenance defect, not a failure of the target repair.

## 3. Matrix coverage audit

The matrix declares 15 semantic requirement IDs, but the executable suite contains 11 tests.

The current approximate mapping is:

| Requirement | Current executable coverage | Disposition |
|---|---|---|
| S2-C01 Hit(v) | test_present_key | EXECUTED |
| S2-C02 Miss | test_absent_key, test_empty_relation | EXECUTED |
| S2-C03 Miss != Hit(v) | test_miss_is_distinct_from_valid_nil_like_value | EXECUTED |
| S2-C04 Eq_K used | test_eq_k_invariance | EXECUTED, narrow |
| S2-C05 Eq_K laws | test_eq_k_laws | EXECUTED, weak adversarial coverage |
| S2-C06 equivalent keys same association | test_eq_k_invariance | EXECUTED |
| S2-C07 value opacity | test_value_opacity | EXECUTED |
| S2-C08 miss-encoding collision | test_miss_is_distinct_from_valid_nil_like_value | EXECUTED |
| S2-C09 read-only | test_read_only | EXECUTED |
| S2-C10 repeatability | test_repeatability | EXECUTED |
| S2-C11 empty relation | test_empty_relation | EXECUTED |
| S2-C12 relation isolation | test_relation_isolation | EXECUTED |
| S2-C13 representation independence | test_representation_independence | EXECUTED, narrow |
| S2-C14 information boundary | no direct test | UNVERIFIED |
| S2-C15 invalid-input boundary | no direct test | UNVERIFIED |

Therefore the statement that all 15 requirements are exercised is too strong.

## 4. Evaluator/oracle audit

oracle.py defines expected_lookup, but test_semantics.py imports it without using it.

The executed tests therefore rely primarily on hand-written assertions rather than an executable oracle derived from the abstract semantic function.

Disposition:

    evaluator contract = VALID ENOUGH FOR CURRENT TARGET REPLAY
    oracle independence = OPEN
    oracle-backed conformance = NOT ESTABLISHED

Required next repair:

- make the abstract oracle the source of expected results for generic Hit/Miss cases;
- separately retain explicit adversarial assertions where oracle use would hide the defect being tested.

## 5. Eq_K audit

The adapter defines EqKey(token) and eq_k(a,b) = a == b.

The current law test uses three distinct objects carrying the same token, which gives some nontrivial object identity separation, but there is no explicit non-equivalent key pair in the semantic law test.

Required next test:

    EqKey("a") == EqKey("a") -> equivalent
    EqKey("a") != EqKey("b") -> non-equivalent

and lookup cases proving that non-equivalent keys do not alias.

This is required by protocol sections 3 and 6.

## 6. Information-boundary audit

There is no executable test that changes undeclared/irrelevant state while holding (R,k) fixed and demonstrates that the abstract result is unchanged.

Source inspection supports the narrow implementation claim that relation_lookup_direct only consumes its two arguments, but that is not the same as execution-level information-boundary verification.

Disposition:

    C14 = UNVERIFIED

## 7. Invalid-input boundary audit

There is no direct conformance test for:

- non-Relation input;
- invalid key-domain input;
- unresolved/incomplete representation.

The current implementation does raise host/substrate-specific errors for several such cases, but this behavior is not currently tested through the semantic adapter.

Disposition:

    C15 = UNVERIFIED

This does not imply a target failure: the specification explicitly places invalid inputs outside the normal S2 result algebra.

## 8. Representation-independence audit

The current test compares:

    {"a":1,"b":2}
    {"b":2,"a":1}

This checks insertion-order independence for the current Python dict representation.

It does not establish general representation independence across independently constructed concrete representations.

Disposition:

    C13 = finite/narrowly supported

Do not generalize this test to arrays, tuples, alternate maps, serialized relations, or other concrete encodings without adding those cases.

## 9. Audit normalization boundary

run_audit.py normalizes RelationLookupMiss -> NIL before comparing S1 scan results with S2 direct results.

This is appropriate for the resource experiment's workload-value comparison, but it intentionally erases the Miss/Hit(NIL) distinction.

Therefore:

    audit semantic_equivalence = workload-value equivalence after normalization

It is not by itself evidence of full Miss | Hit(v) conformance.

The separate conformance suite is what tests the repaired disjoint result algebra.

## 10. Resource-vector audit

The protocol asks for:

    B_off, R, B_on, C_access

The current JSON uses:

    offline_representation.construction_ticks
    offline_representation.stored_entries
    object_language_scan/direct.transition_ticks_total
    object_language_scan/direct.access_ticks_total

These can serve as an experimental mapping to the protocol dimensions, but the mapping is not explicitly named in the result schema.

More importantly, run_audit.py currently assigns:

    offline = 5

directly in the harness.

Therefore construction_ticks = 5 is a declared fixture accounting value, not an instrumented measurement of an actual preprocessing execution.

Disposition:

    stored_entries = observed
    online transition/access totals = executed measurements under abstract tick model
    offline construction_ticks = FIXTURE-ASSIGNED, NOT INSTRUMENTED

The replay proves preservation of the recorded value; it does not establish that 5 is a physically or implementation-derived preprocessing cost.

## 11. Direct-access cost boundary

The direct primitive explicitly increments access_ticks by one, while state_read is charged separately.

This is internally consistent with the experimental cost model.

It is not:

- a host-runtime benchmark;
- an asymptotic complexity proof;
- an implementation-independent access cost.

The existing interpretation boundary is correct and should remain.

## 12. Canonical substrate boundary

The experimental interpreter remains separate from the canonical Machine interpreter.

Current evidence therefore establishes only:

    experimental S1/S2 contract
    +
    experimental CEK-style interpreter
    +
    finite mapping fixture

It does not establish:

    canonical Machine substrate == experimental S1

or:

    canonical Machine substrate == experimental S2

The repository's own earlier substrate-audit claim correctly keeps this OPEN.

## 13. Resource interpretation

The current evidence supports this bounded statement:

Direct indexed lookup produced substantially fewer measured online transitions and access ticks than generic object-language traversal for the same five-entry persistent mapping and five-query workload under the declared experimental contract.

It does not establish:

- a universal resource advantage for all relation workloads;
- asymptotic O(1) behavior;
- a computability-power separation;
- a canonical Machine frontier shift;
- general representation closure.

## 14. Priority defects to repair

P0 — provenance/claim wording:
- remove "frozen S2 contract" wording;
- replace with "candidate v0.3 obligations".

P0 — semantic coverage:
- add explicit C14 information-boundary test;
- add explicit C15 invalid-input boundary test.

P1 — evaluator strength:
- make oracle.py operationally authoritative where appropriate;
- keep adversarial Miss/Hit(NIL) tests outside the oracle's ability to mask output collisions.

P1 — Eq_K:
- add non-equivalent-key tests;
- retain distinct-object equivalent-key tests.

P1 — representation:
- add at least one genuinely different concrete representation or explicitly narrow C13 scope to dict insertion-order independence.

P1 — resource accounting:
- rename/mark construction_ticks as fixture-assigned unless actual construction instrumentation is added;
- explicitly map result fields to (B_off, R, B_on, C_access).

P2 — provenance hygiene:
- reconcile the file path evidence/s2-conformance-target-claims-v0.1.json with its internal schema machine.s2-conformance-target-claims.v0.2;
- preferably introduce a v0.2 file and retire the misleading v0.1 filename.

## 15. Overall disposition

The Miss/Hit(NIL) defect and its target-side repair are real and correctly handled.

The post-repair execution is successful and reproducible.

The resource replay is internally stable.

The remaining issue is not that the current result is wrong; it is that several layers of the surrounding claim are stronger than the currently executed discriminating tests.

Next discriminating action:

    repair evaluator + C14/C15 + Eq_K adversarial coverage
        ->
    rerun unchanged candidate-derived suite
        ->
    rerun audit
        ->
    explicitly remap resource vector
        ->
    only then consider freeze review of S2 candidate
        ->
    canonical-substrate replay remains a separate gate
