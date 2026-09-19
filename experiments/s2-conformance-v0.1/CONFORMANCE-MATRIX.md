# S2 Conformance Matrix v0.1

Derived exclusively from: docs/S2-CANDIDATE-SPEC-v0.3.md
Protocol: docs/S2-CONFORMANCE-FRONTIER-PROTOCOL-v0.2.md
Status: DERIVED TEST CONTRACT / TARGET-AGNOSTIC

| ID | Requirement | Spec source | Test class |
|---|---|---|---|
| S2-C01 | Present key produces `Hit(v)` with the abstract stored value | §4, §15 | hit |
| S2-C02 | Absent key produces `Miss` | §4, §11, §15 | miss |
| S2-C03 | `Miss` is distinct from every `Hit(v)` | §4, §8 | result separation |
| S2-C04 | Key equality uses declared `Eq_K` | §3, §4, §15 | equality |
| S2-C05 | `Eq_K` is reflexive/symmetric/transitive | §3 | equality algebra |
| S2-C06 | Equivalent keys denote the same association | §3, §4 | equality invariance |
| S2-C07 | Values are opaque | §8, §15 | value opacity |
| S2-C08 | Valid values resembling a concrete miss encoding remain `Hit(v)` | §8, §15 | sentinel collision |
| S2-C09 | Lookup preserves the abstract relation | §7, §15 | read-only |
| S2-C10 | Repeated lookup is semantically stable when R is unchanged | §6 | repeatability |
| S2-C11 | Empty relation yields `Miss` for valid keys | §11, §15 | empty relation |
| S2-C12 | Multiple relations are independently respected | §15 | relation isolation |
| S2-C13 | Abstractly equivalent concrete representations yield equivalent results | §9, §15 | representation independence |
| S2-C14 | No undeclared relation/hidden domain input changes the abstract result | §10 | information boundary |
| S2-C15 | Invalid inputs are not treated as normal `Miss`/`Hit` semantics | §11 | domain boundary |

## Normative rule

Only requirements above are derived from the candidate semantic specification.

Performance, timing, preprocessing, storage, access cost, and S1 derivability are deliberately absent because they belong to the separate frontier/conformance protocol.

## Target adapter rule

Each implementation target must provide a declared concrete-to-abstract mapping for:

    Rel
    K
    V
    Eq_K
    Miss
    Hit(v)

The adapter may not use target-internal knowledge of whether a key exists to manufacture a missing-result distinction that the target's observed output does not provide.