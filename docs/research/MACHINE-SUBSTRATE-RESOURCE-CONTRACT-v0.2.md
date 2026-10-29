# Machine Substrate Resource Contract v0.2

Status: **FROZEN COMPARISON CONTRACT**

This revision does not modify the frozen v0.1 schema. It freezes the missing coupling between state read addressing, state write/update addressing, mutation mode, and P-07 resource accounting for the normalized comparison experiment.

## 1. Access tuple

The access contract is:

`A=(A_r,A_w)`

where `A_r` declares how state can be read and `A_w` declares how state can be written or updated.

`A_r`:

- A0_OPAQUE
- A1_RANDOM_ACCESS
- A2_SPECIALIZED_INDEX

`A_w`:

- W0_NONE
- W1_GENERIC_CELL_WRITE
- W2_STRUCTURED_UPDATE

A1 read access does not imply write access. M2 requires an admitted write/update surface capable of preserving the declared representation contract.

## 2. Mutation semantics

M0 is static materialized state.

M1 is batched mutation followed by explicit rebuild/materialization. The derived representation is not claimed valid between publication boundaries.

M2 is dynamic mutation. After each committed update, the declared derived representation must satisfy the semantic and structural correctness contract.

The comparison includes `P07_CSR_REBUILD_M1` as an explicit batched reference. It must not be interpreted as an M2-equivalent implementation.

## 3. Resource vector

No scalar score is frozen.

The normalized report is a vector of structural event counters:

`(reads,writes,scans,outputs,hash_probes,hash_writes,link_writes,overlay_writes,build,rebuild,compaction,shifts,offset_writes)`

together with:

`(B_{off},R_{persistent},R_{peak},B_{on},latency)`

where each component keeps its declared unit.

Wall-clock time is measured separately. No conversion such as "one hash probe equals X logical operations" is permitted without a separately validated calibration experiment.

## 4. Persistent representation

The experiment uses fixed capacity `S*Sigma` for all profiles to remove allocator-growth ambiguity.

The reported `bytes_persistent` is the total resident allocation of that profile implementation. The corresponding extra representation over the baseline transition table is derived as:

`R_extra = bytes_persistent - 4*S*Sigma`

for the fixed C harness, whose transition table uses 32-bit integers.

Peak memory must include coexistence of old and new arrays during rebuild/compaction.

## 5. Common trace

Each case generates one initial transition table and one ordered trace:

`update_1,...,update_U,query_1,...,query_Q`

repeated across fixed epochs.

The query targets are selected deterministically from the initial in-degree quartiles plus a top-5-percent target stratum. This is a synthetic skew envelope, not a claim about production traffic.

Every profile receives the same trace.

## 6. P-07 profiles

### P07-HASH

Uses per-target predecessor buckets and a membership hash table. Update cost is reported through hash probes, hash writes, and link writes. The hash-table model is expected-time; no worst-case deterministic O(1) claim is made here.

### P07-CSR-REBUILD

Uses ordinary delta-state writes and rebuilds the CSR at every publication boundary. Rebuild work is explicitly charged. Its mutation mode is M1.

### P07-CSR-OVERLAY

Uses an immutable CSR base plus one latest update record per changed `(s,a)`. Delete is represented explicitly. Query reconciles base entries with overlay entries. Compaction is triggered at `max(16,floor(S*Sigma/4))` overlay records and its full rebuild work is charged.

### A1_RW_CSR

Maintains the exact contiguous CSR representation using generic indexed state writes, payload shifts, and offset writes. No inverse-specific update operation is used.

## 7. Correctness

The semantic reference is always:

`F(u)={(s,a):delta(s,a)=u}`

with exact labels and multiplicity.

Dynamic profiles validate affected fibers and representation invariants after every committed update. M1 rebuild validates at each publication boundary.

A run is invalid if the profile reports structural or semantic failure.

## 8. Classification boundary

This experiment is intentionally incapable of selecting a universal production winner.

It can establish:

- representational closure under A1+W1;
- explicit resource-vector differences;
- the cost and consistency shape of the named P-07 regimes;
- whether the current P-07 overlay description can be made operationally precise.

It cannot establish a production workload fact when only synthetic traces are used, and it cannot collapse different resource dimensions into a single scalar without a separately frozen cost model.

## 9. Provenance requirements

Every CI result must identify:

- source commit;
- compiler version and flags;
- host architecture;
- deterministic case/seed;
- trace hash;
- contract version;
- profile configuration;
- raw per-run JSON digest.

The committed local replay is execution evidence for the source snapshot it names. CI artifacts tied to a commit are the authoritative verification record for that commit.
