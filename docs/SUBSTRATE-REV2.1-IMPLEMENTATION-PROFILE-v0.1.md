# Unified Machine Substrate Rev 2.1 — Implementation Profile v0.1

Status: EXPERIMENTAL IMPLEMENTATION PROFILE
Repository: Loofy147/Machine
Branch: research/substrate-interpreter-v0
Recorded: 2026-09-21

## Scope

This profile records executable additions to the unified substrate module:

experiments/substrate-interpreter-v0/substrate.py

The module combines adaptive CSR predecessor fibers with basin, retrograde shortest paths, Hopcroft/Moore refinement, and attractor computation.

It is implementation evidence. It is not by itself the canonical semantic specification of Machine.

## Added substrate-native values

Fiber now exposes:

- record_count(): number of stored predecessor records;
- edge_count(): raw transition count for labeled fibers only;
- max_in_degree(): maximum stored fiber cardinality;
- dtype_profile(): actual offset/source/action dtypes;
- memory_bytes(): exact NumPy backing storage size;
- contract(): a serializable representation/cost profile.

The distinction between raw edges and deduplicated predecessor records is explicit.

## Adaptive representation contract

CSR offsets, source identifiers, and action identifiers select the smallest unsigned dtype sufficient for their actual value range.

Boundary examples verified by tests:

- 255 -> uint8;
- 256 -> uint16;
- 65,535 -> uint16;
- 65,536 -> uint32;
- 2^32 -> uint64.

The implementation rejects negative or >uint64 maxima rather than silently narrowing.

## Attractor multiplicity contract

The attractor counter convention is derived from Fiber.deduped:

- labeled fiber -> out-edge multiplicity;
- deduplicated fiber -> distinct-successor count.

No caller-supplied counter convention is exposed.

The regression test requires:

attractor(labeled fiber) == attractor(deduplicated fiber) == attractor_naive

on a game containing parallel transitions.

This closes the previously observed failure mode where mixing a deduplicated fiber with raw out-degree counters produced incorrect attractors.

## Other conformance checks

The test suite checks:

- labeled CSR exactness against naive predecessor enumeration;
- basin equivalence for labeled and deduplicated fibers;
- Hopcroft/Moore partition agreement on a randomized deterministic system;
- retrograde shortest-path result agreement with an independent reference.

## Limits

- This profile does not establish a canonical Machine semantic specification.
- Hopcroft and retrograde tests are finite randomized/regression checks.
- Attractor correctness is tested against the dense reference on the declared fixtures.
- Memory figures cover NumPy backing arrays only, not Python object overhead.

## Provenance

Parent substrate branch head before this addition:

d935495355ac6b827a17d6147d7f38fbcaaeb15f

Primary new files:

- experiments/substrate-interpreter-v0/substrate.py
- experiments/substrate-interpreter-v0/test_substrate.py
- docs/SUBSTRATE-REV2.1-IMPLEMENTATION-PROFILE-v0.1.md
- evidence/substrate-rev2.1-values-v0.1.json
- docs/research/CONVERSATION-HANDOFF-2026-09-21.md
