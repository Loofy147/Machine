# S2 Experimental Substrate Profile v0.1

Recorded: 2026-09-19
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0
Evidence source: experiments/substrate-interpreter-v0.2/

## Status

This is an experimental substrate profile, not the canonical specification of S2. The active semantic candidate is `docs/S2-CANDIDATE-SPEC-v0.3.md`; the active test/frontier protocol is `docs/S2-CONFORMANCE-FRONTIER-PROTOCOL-v0.2.md`.
It records properties observed or established in the concrete experimental implementation currently labeled S2. The profile is evidence about that implementation and must not be promoted into the semantic definition of S2 merely because the implementation was named S2.

## 1. Experimental identification

The implementation under test uses:

    S1 = generic state read + comparison + branching + iteration
    S2 = S1 + relation_lookup_direct

The matched v0.2 experiment gives S1 and S2 the same persistent representation:

    state["rel"] : host-language Mapping[key, value]

The direct expression is:

    relation_lookup_direct(state_read("rel"), key)

Thus, in this experiment, S2 changes access to an already-read relation value. It does not itself establish a new information source or earlier information availability.

## 2. Profiled properties

### P1 — Additive implementation delta

The experimental S2 implementation exposes exactly one additional primitive:

    relation_lookup_direct

No additional state storage, syntax, control form, continuation form, or closure representation was introduced.

Status: ESTABLISHED BY IMPLEMENTATION INSPECTION

### P2 — Matched persistent information

The v0.2 experiment gives S1 and S2 the same relation object and stored entries.

Status: EXPERIMENTALLY_SUPPORTED

Scope:
- five-entry mapping fixture;
- five benchmark queries;
- current experimental interpreter.

### P3 — Tested preservation of S1 behavior

The added S2 primitive does not alter the tested behavior of S1-only programs. The property suite checks equal result and machine-data contents for selected S1 programs under S1 and S2.

Status: EXPERIMENTALLY_SUPPORTED

Boundary:
- tested programs only;
- not a formal conservativity theorem for all programs.

### P4 — Read-only behavior in the current fixture

The direct primitive performs a mapping lookup and increments access accounting. The added property test checks that it does not modify machine_data for the current dict-backed fixture.

Status: EXPERIMENTALLY_SUPPORTED

Boundary:
- current host-level Mapping semantics.

### P5 — Current lookup behavior

For the implementation under test:
- two arguments are expected;
- argument 0 must satisfy the host Mapping interface;
- argument 1 is the key;
- an existing key returns its mapped value;
- an absent key returns NIL;
- S1 rejects the primitive because it is outside the S1 contract.

Status: ESTABLISHED BY IMPLEMENTATION + TEST

### P6 — Explicit measured access charge

The current implementation charges one access tick for the direct lookup, separately from the state_read access.

Status: ESTABLISHED BY IMPLEMENTATION + TEST

This is an experimental accounting rule, not an asymptotic complexity theorem.

### P7 — No internal preprocessing

The current direct primitive does not construct a reverse index, cache, or target-specific table during lookup.

Status: ESTABLISHED BY IMPLEMENTATION INSPECTION

The benchmark's reported offline construction cost remains a property of the experiment harness/representation setup, not of the primitive itself.

### P8 — Finite semantic match

For:

    [k4, k0, k2, missing, k3]

the observed outputs are:

    [40, 0, 20, NIL, 30]

for both S1 and S2.

Status: EXPERIMENTALLY_SUPPORTED

Boundary:
- finite workload only.

### P9 — Host-semantics dependency

The current implementation relies on:

    isinstance(x, Mapping)
    x.get(key, NIL)

Therefore the profile is not yet a closed object-language semantic specification of relation access.

Status: SPECIFICATION DEBT

### P10 — Capability conclusion remains unresolved

The profile does not establish that S2 is a new absolute computational capability, nor that it can never change an admissible task set under a different resource/substrate contract.

Status: OPEN

## 3. Resource observation

Under the v0.2 matched-representation experiment:

    S1:
      transition_ticks = 676
      access_ticks = 291

    S2:
      transition_ticks = 20
      access_ticks = 10

    offline construction = 5
    stored entries = 5

Observed ratios:

    transition = 33.8x
    access     = 29.1x

This supports the bounded claim:

The experimental S2 access mechanism can provide a large measured online-resource advantage over the tested generic traversal implementation while preserving observed finite-workload semantics.

## 4. What this profile is evidence for

It is evidence about:

    this implementation
    under this contract
    with this representation
    under this cost model
    on this tested workload.

It is not evidence that these properties constitute the definition of S2 in the canonical Machine model.

## 5. Required separation

The research state must maintain two distinct artifacts:

    S2 semantic specification
        docs/S2-CANDIDATE-SPEC-v0.2.md (pre-freeze)

    S2 experimental profile
        observed properties of the implementation currently labeled S2

The profile can falsify or constrain a proposed S2 specification. It cannot by itself define that specification without circularity.

## 6. Next discriminating action

1. review/freeze the independently authored S2 semantic candidate;
2. derive conformance obligations from the frozen semantic core;
3. keep accidental implementation properties (for example host Mapping semantics) outside the normative specification;
4. derive implementation tests from that frozen specification;
5. reproduce the property suite on the canonical Machine substrate.

## 7. Validity boundary

The experimental profile belongs to research/substrate-interpreter-v0 and must not be silently transferred to the canonical Machine substrate.