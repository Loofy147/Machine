# Machine P-07 Normalized Comparison Protocol v0.1

Status: **EXECUTABLE RESEARCH PROTOCOL**

## Objective

Compare the named P-07 mutation regimes with the already-tested A1+generic-write exact-CSR construction under one frozen comparison contract, without collapsing heterogeneous resource dimensions into one scalar.

## Profiles

1. **A1_RW_CSR / M2** — exact contiguous inverse CSR, generic indexed reads/writes, arithmetic, finite iteration, fixed capacity \`S*Sigma\`, no inverse-specific update primitive.
2. **P07_HASH / M2** — per-target predecessor buckets plus membership hash table. Hash complexity is expected-time.
3. **P07_CSR_REBUILD_M1** — ordinary delta mutation followed by full CSR rebuild at every publication boundary. This is deliberately M1, not M2.
4. **P07_CSR_OVERLAY / M2** — immutable CSR base plus one latest overlay record per changed \`(s,a)\`, explicit deletion handling, and periodic compaction.

## Common trace

Each case creates one initial partial deterministic transition table and one ordered trace. All four profiles receive the same trace.

The trace consists of 20 epochs. Each epoch has 25 update operations followed by 20 query targets.

Updates use:
- uniformly selected \`(s,a)\`;
- \`undefine\` with probability 0.20;
- otherwise a uniformly selected target state.

The query target is sampled from the initial in-degree ordering using four deterministic strata: the first three quartiles and the top 5 percent. The trace is synthetic and is not production telemetry.

The trace is hashed with FNV-1a 64-bit and the hash is reported per case and in aggregate.

## Correctness obligations

The exact semantic reference is:

\`F(u) = {(s,a) : delta(s,a) = u}\`.

A1_RW, P07_HASH, and P07_CSR_OVERLAY must satisfy:
- affected-fiber semantic correctness after every committed update;
- representation invariants after every committed update;
- exact query semantics at every query.

P07_CSR_REBUILD_M1 must satisfy:
- delta mutation correctness during the batch;
- full CSR invariant validation after each rebuild publication;
- exact query semantics after publication.

Validation work is excluded from the profile resource counters. It is a separate correctness channel.

## Resource accounting

The harness records separate structural event counters:

- state reads/writes;
- scan entries and output entries;
- hash probes/writes;
- fiber link writes;
- overlay writes;
- initial build entries;
- rebuild entries;
- compaction entries;
- CSR payload shifts;
- CSR offset writes;
- allocation count;
- persistent resident bytes;
- peak resident bytes.

This vector is the comparison object. No cross-dimension scalar score is produced.

The initial constructor contributes to \`B_off\`. Rebuild and compaction contribute to online maintenance work for the profile that performs them. Peak memory includes simultaneous old/new arrays during rebuild or compaction.

## Fixed capacity

All profiles use logical capacity \`S*Sigma\`. This isolates the representation comparison from allocator growth and reallocation policy.

The C harness uses 32-bit integer storage for the transition and CSR payload arrays. Therefore its \`bytes_persistent\` measurement is for the concrete experimental implementation, not a claim about the compact \`uint8\` action representation in Rev 2.1.

## Publication semantics

Dynamic profiles expose a complete post-update representation after each commit.

The batched rebuild profile exposes its rebuilt representation only at epoch boundaries. Its rebuild cost is charged at that publication boundary.

The overlay compacts after the overlay record count exceeds:

\`max(16, floor(S*Sigma/4))\`.

Compaction is part of the profile's measured maintenance frontier.

## Falsification boundary

The experiment can support:
- exact finite representability/closure observations;
- profile-specific structural resource vectors;
- explicit maintenance costs for the declared synthetic envelope;
- operational semantics for the tested overlay construction.

It cannot support:
- a production workload claim;
- a universal production winner;
- a scalar conversion between hash probes, shifts, bytes, and wall-clock;
- a general theorem beyond the declared finite workload/model.

## Provenance

CI records source commit, compiler version, host architecture, compiler flags, case seeds, trace hashes, profile names, and the raw JSON artifact digest.

The local replay is execution evidence for the source snapshot it names. CI is the authoritative verification record for the committed source snapshot.
