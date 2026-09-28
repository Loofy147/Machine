# P-07 Resource Semantics Audit and Production Workload Freeze Gate v0.1

Status: **SOURCE-AUDITED / CONTRACT NOT FROZEN / PRODUCTION OPEN**

Audit target:
- Source: `docs/research/MACHINE-SUBSTRATE-SPEC-REV2.1.md`
- Base revision: `59fab62704875193801db77c7cb8361475297f48`
- Scope: P-07 arc mutation, its representations, and comparability with the M2 exact-CSR A1_RW experiment.

## 1. Source-grounded P-07 contract

Rev 2.1 P-07 states:
- hash-indexed fibers: expected O(1) arc update;
- CSR: rebuild in Θ(n+E) or use a delta-overlay;
- evidence B10: 200,000 mixed redefine/undefine updates; resulting fibers equal a fresh rebuild and I1–I4 hold;
- measured hash-indexed update: 0.63 µs/update in the reported Python environment;
- one NumPy rebuild: 16.9 ms, approximately 26,900 measured hash updates;
- deleting from the top-hub fiber: 35.1 µs list-backed vs 0.061 µs set-backed.

These are not a single implementation contract. They are three materially different mutation regimes.

## 2. Split P-07 into explicit profiles

### P07-HASH (dynamic hash-indexed fibers)
- Semantic update: redefine or undefine one (s,a) transition.
- Index mutation: remove old (s,a) from old target's bucket; insert into new target's bucket.
- Bound: expected O(1) per arc update under the hash-table model; not worst-case deterministic O(1).
- Correctness: I1–I4-equivalent fiber consistency after each committed update; source B10 validates final fibers against fresh rebuild.
- Storage: hash table + per-target sets/buckets + forward delta. Exact byte accounting is not supplied by the P-07 row; layout benchmark reports 19.36 MiB for its dynamic-hash implementation at n=50k, E=200k.
- Mutation consistency point: after both old-bucket removal and new-bucket insertion are committed. Atomicity/rollback behavior is not specified by Rev 2.1.
- Structural unit cost: UNKNOWN; 0.63 µs is environment-specific wall-clock evidence, not directly comparable to the logical-word count in the A1_RW harness.

### P07-CSR-REBUILD
- Mutation: change delta, then rebuild inverse CSR.
- Rebuild bound: Θ(n+E) time and space.
- Source measurement: NumPy rebuild 16.9 ms in the stated benchmark environment.
- Amortization: rebuild cost must be charged to the batch/update epoch that triggers it. It cannot be counted as zero per update.
- Consistency point: after rebuild completes and the rebuilt index passes I1–I4. During rebuild, whether readers see old snapshot, block, or see mixed state is unspecified.
- Required declaration: batch size / rebuild cadence and snapshot publication protocol.

### P07-CSR-OVERLAY
- Base: immutable CSR snapshot.
- Delta: an update overlay records insertions/deletions or overrides.
- Query: base fiber plus overlay reconciliation.
- Rev 2.1 names this option but does not define overlay representation, tombstones, duplicate suppression, lookup bound, storage growth, compaction trigger, or publication/consistency protocol.
- Therefore query/update/storage costs and correctness contract are OPEN. No numeric c2 may be assigned from the current specification.

## 3. Comparability defect

The previous break-even expression
`c2 <= c1 + (Q/U)*(q1-q2)`
is only valid when c1, c2, q1, q2 are measured in the same additive resource unit and the same accounting boundary.

Currently:
- A1_RW exact CSR: logical operation-count units from an explicit shift/offset model.
- P07-HASH: measured microseconds in a specific Python runtime, plus expected-time asymptotic claim.
- P07-CSR-REBUILD: Θ(n+E) rebuild work and one environment-specific wall-clock measurement.
- P07-CSR-OVERLAY: no concrete cost contract.

Thus the numerical thresholds computed by combining A1 logical units with an unspecified A2 cost are **illustrative only**, not a validated production break-even frontier. They must not be treated as decision evidence until normalized.

## 4. Required common accounting model

For each profile, record a resource vector rather than collapsing dimensions prematurely:

`R = (W_read, W_write, W_hash, W_scan, bytes_peak, bytes_persistent,
alloc_count, rebuild_work, query_latency_distribution, update_latency_distribution)`

For cross-language comparisons, use at least two separate views:
1. abstract operation counts under a frozen word-RAM / data-structure contract;
2. wall-clock + peak memory under a frozen hardware/runtime/build environment.

Do not convert between them with an unvalidated scalar.

For dynamic correctness, define the linearization/publication point and require that every observable query sees either:
- the complete pre-update state, or
- the complete post-update state,
never a mixed index/delta state.

## 5. Workload envelope: do not invent production Q/U

No production query/update distribution is evidenced in the Rev 2.1 source. Therefore Q/U remains OPEN.

Freeze workload as a vector, not a single ratio:
- queries per epoch Q;
- committed effective updates U_eff (exclude no-op updates but report them);
- update batch size and burst distribution;
- query target distribution over in-degree quantiles/hubs;
- fraction of queries requiring exact labeled fibers vs distinct predecessor states;
- maximum n, k, E, and density E/(n*k);
- allowed query/update latency and peak/persistent memory budgets;
- rebuild/compaction deadline and maximum overlay growth;
- required consistency semantics.

At minimum, report a sensitivity grid over Q/U_eff and skew strata, but label it a scenario grid—not production evidence.

## 6. Decision gates

Gate G1 — P07-HASH:
- reproduce B10 on current code/ref;
- instrument operation classes and memory bytes;
- define atomic publication/rollback;
- retain expected-time qualification.

Gate G2 — P07-CSR-REBUILD:
- define batching policy;
- charge full rebuild work and peak coexistence memory (old + new index if snapshot-safe);
- validate atomic publication.

Gate G3 — P07-CSR-OVERLAY:
- specify exact overlay semantics and duplicate/tombstone handling;
- derive query cost as base fiber scan + overlay scan/reconciliation;
- specify compaction threshold and amortized compaction charge;
- test I1–I4-equivalent correctness after each commit and after compaction.

Gate G4 — common workload:
- obtain USER/PRODUCTION workload trace or explicitly freeze a synthetic envelope as a design assumption;
- never promote synthetic Q/U to production fact.

Gate G5 — profile selection:
- compare admissibility against explicit memory, latency, throughput, and consistency budgets;
- no universal winner absent a workload and resource envelope.

## 7. Current disposition

- Rev 2.1 P-07 source alternatives: ESTABLISHED.
- P07-HASH measured 0.63 µs/update: SOURCE-REPORTED MEASUREMENT; environment-specific.
- A1_RW exact-CSR M2 representability: EXPERIMENTALLY_SUPPORTED by local replay, not a production-cost comparison.
- Numeric A1-vs-A2 break-even values: WITHDRAWN AS DECISION EVIDENCE pending unit normalization; retain only as algebraic sensitivity illustrations.
- P07-CSR-OVERLAY contract: OPEN.
- Production Q/U and target skew: OPEN.
- Production profile: OPEN.

## 8. Next discriminating experiment

Implement a common C or Rust harness with:
- one shared delta/update trace and exact labeled-fiber semantics;
- P07-HASH, P07-CSR-REBUILD (batch-size parameter), P07-CSR-OVERLAY (fully specified);
- A1_RW generic contiguous CSR mutation;
- counters for reads, writes, shifts, hash probes, bytes allocated, peak bytes, rebuild/compaction work;
- correctness check after every committed update;
- query traces stratified by in-degree, including hubs;
- wall-clock medians and dispersion reported separately from operation counts.

The experiment must emit raw per-run JSON and identify source commit, compiler/runtime, flags, hardware, seed, trace hash, and profile configuration. Until then, no production selection.
