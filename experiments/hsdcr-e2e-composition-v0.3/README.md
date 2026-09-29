# HSDCR End-to-End Composition v0.3

Status: RESEARCH / FINALIZED EXPERIMENT / NON-NORMATIVE

This version closes the methodological weaknesses found during review of v0.1/v0.2.

## Closed weaknesses

1. Signal loss is actually executed by clearing the signal stream.
2. Acceptance history is serialized to a temporary persistent representation, in-memory history is cleared, and the history is rehydrated before reconstruction.
3. The result digest excludes its own digest field by definition.
4. The provider-comparison field is explicitly named abstract boundary equivalence. This prevents the harness from claiming live provider semantic equivalence from normalized projections.
5. The GitHub PR fixture uses the current observed PR #10 head. The AT record remains explicitly pinned as a historical fixture because a live recheck on 2026-09-29 returned a temporary 504.

## What the experiment establishes

The declared semantic junction can be modeled as:

proposal -> evidence -> authority -> decision -> canonical state -> reconstruction

and, within the test model:

- evidence does not itself grant authority;
- rejected decisions do not canonicalize;
- accepted transition is explicit;
- duplicate acceptance is a no-op;
- signal loss does not destroy the reconstructible result;
- reconstruction can consume rehydrated acceptance history;
- no new repository primitive is detected;
- no new execution primitive is detected.

## What it does not establish

This experiment does not establish:

- live semantic equivalence between providers;
- production durability;
- crash/restart safety;
- security of a real authority provider;
- equivalence of resource costs;
- architectural novelty;
- protocol status.

Evidence and authority remain normalized fixtures. The persistence test is a local serialization/rehydration exercise, not a crash-consistency proof.

## Kill target

The current strongest non-novelty model remains:

repository/change substrate + signal/observation + evidence/provenance + authority/capability + explicit acceptance transition + orchestration/control

A residual is promotion-worthy only if it survives provider substitution, ordinary-data/adaptor reduction, explicit transition modeling, and the independent equivalence dimensions.

## Next discriminating test

Use independent real evidence and authority implementations, then add an actual crash/restart test against the persistence boundary.
