# A↔M Mutation Coupling Gap v0.1

Status: **SPECIFICATION DEBT IDENTIFIED**

Recorded: 2026-09-27

## Finding

The frozen substrate contract defines:

- A0/A1/A2 under **state addressing**;
- M0/M1/M2 under **mutation**.

However, A1 currently specifies generic indexed **reads** only. The contract does not state
whether mutation has corresponding generic write/update addressing or whether derived-state
maintenance may use an operation not admitted by A.

This matters for production-substrate selection.

## Consequences by mutation mode

### M0 — STATIC

No online update is required.

The executed profile discriminator is sufficient for the inverse-dependent read/query family:

- A0 closes semantically by repeated forward probes;
- A1 closes using generic state reads over target-oblivious CSR;
- A2 closes using specialized fiber lookup.

### M1 — BATCHED

A derived index may be rebuilt/materialized after a batch.

A1 can only be considered sufficient when the contract explicitly admits the required offline
writes/rebuild work and charges them under B_off.

This is compatible with the existing resource model, but is not implied by "generic state
reads" alone.

### M2 — DYNAMIC

The derived representation must remain valid under online updates.

A read-only A1 declaration does not establish this capability. A separate update/write
addressing contract or an explicit mutation primitive is required, together with:

- update cost;
- invalidation semantics;
- consistency timing;
- representation invariants after mutation.

The same issue applies to A2: P-05 establishes inverse-fiber read access, but dynamic
maintenance is a separate contract concern (e.g. P-07 variants in Rev 2.1).

## Decision boundary

Therefore:

> **A0/A1/A2 is currently sufficient to classify read/access closure, but not sufficient by itself
> to select a production profile when M2_DYNAMIC is part of the production contract.**

No v0.1 field is retroactively changed.

Instead, the missing coupling is recorded as specification debt for the next contract revision.

## Required next discriminating action

Freeze one of the following before a mutable production profile is selected:

1. **A includes read/write addressing**, with explicit costs and semantics; or
2. **M declares its update primitive/interface independently**, with an explicit compatibility
   relation to A.

Then rerun profile closure under M0, M1, and M2 using the same semantic workloads and a
matched resource frontier.

## Current status

- Concrete Rev 2.1 interface: **A2_SPECIALIZED_INDEX**.
- Minimal generic read closure for the tested inverse workload: **A1_RANDOM_ACCESS**.
- Repository-wide production profile: **OPEN**.
- Reason: production mutation/access coupling is not yet frozen.
