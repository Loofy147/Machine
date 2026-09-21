# Machine Substrate Rev 2.1 — Reconciliation Record

Status: RECONCILED IMPLEMENTATION PROFILE
Repository: Loofy147/Machine
Branch: research/substrate-rev2.1-v0
Recorded: 2026-09-21

## Canonical target signature for Rev 2.1

The Rev 2.1 target is:

M = (S, Sigma, delta, R, C)

No Phi, P, or Pi component is included in this signature.

## 1. Phi / P disposition

Decision:
DROPPED.

Rationale:
The Rev 2.1 signature does not contain Phi or P. Their historical appearance belongs to earlier M* documentation and is preserved only as archived provenance.

## 2. R+_opt disposition

Decision:
NOT A SEPARATE REV 2.1 COMPONENT.

The dense forward transition table delta is n x k and forward evaluation is already O(1) per state/action. A separately optimized forward mirror is therefore not required by the Rev 2.1 interface.

Any historical R+_opt measurements remain historical representation evidence, not a normative dependency.

## 3. Player partition / CPre

The owner function is explicit:

owner[s] in {0,1}

with:

- owner[s] = 0: existential state; enter the attractor when any successor enters Z.
- owner[s] = 1: universal state; enter the attractor only when every applicable successor enters Z.

The exact deadlock convention must be declared by the attractor contract; it is not inferred from graph connectivity.

## 4. Multiplicity contract

A labeled Fiber preserves one record per valid (source, action) transition.

A deduplicated Fiber stores one record per distinct predecessor.

These representations require different universal-state counters:

- labeled Fiber -> raw outgoing-edge multiplicity;
- deduplicated Fiber -> distinct-successor cardinality.

The caller must not supply a separate counter convention. The implementation derives the convention from Fiber.deduped.

This closes the specific historical bug class where a deduplicated predecessor fiber was paired with raw out-degree counters.

## 5. What is currently experimentally supported

The unified substrate implementation on this branch tests:

- adaptive CSR dtype boundaries;
- labeled Fiber exactness;
- deduplicated Fiber basin equivalence;
- labeled/deduplicated attractor agreement with the dense reference on the parallel-transition regression;
- Hopcroft/Moore agreement on a deterministic randomized fixture;
- retrograde shortest-path agreement with an independent reference.

## 6. What remains specification debt

- A canonical semantic specification independent of the implementation.
- Broader randomized attractor cross-checks over duplicate-transition rates and owner distributions.
- Formal proof of every Rev 2.1 contract.
- Independent conformance of the canonical Machine substrate rather than only the experimental module.

## 7. Historical source boundary

For the historical M* docket, see:

docs/archive/MSTAR-VERIFICATION-DOCKET-v3.4.md

Do not import historical M* components back into Rev 2.1 without an explicit new decision record.
