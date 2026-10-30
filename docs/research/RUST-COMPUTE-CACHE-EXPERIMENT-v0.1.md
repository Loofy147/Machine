# Rust Pair-Compatibility Computation Cache v0.1

**Status:** EXPERIMENTAL — correctness and graph-build performance evaluated in Machine PR #31; not a production default.
**Implementation:** `runtime/rust-context-compute-cache/`
**Python adapter:** `experiments/context-contract-distribution-v0/rust_compute_cache.py`
**CI run:** [40993076325](https://github.com/Loofy147/Machine/actions/runs/40993076325)
**Evidence artifact:** [context-contract-distribution-v0.1](https://github.com/Loofy147/Machine/actions/runs/40993076325/artifacts/12950251652)

## Purpose

Test whether a Rust implementation can memoize the expensive compatibility-graph construction used by the context-contract planner. This is a computation cache, not the unrelated LLM exact-response/token cache prototype.

The existing Python implementation remains the reference. Rust returns compatible pairs and directed service witnesses; Python validates graph parity and continues to run the exact NetworkX maximum-weight matching. No production routing, persistence, or authorization boundary is changed.

## Cache design

### Pair cache

- Each context is fingerprinted from cache schema, context ID, facts, and needs using SHA-256 over deterministic JSON serialization.
- A pair key combines the two ordered context fingerprints.
- Utility is deliberately excluded: compatibility and need witnesses do not change when the objective's utility scores change.
- Both compatible and incompatible pair outcomes are cached.
- Moka uses a 30-minute TTL and an approximate 128 MiB weighted capacity.

### Whole-graph cache

- The graph key is the ordered set of eligible context fingerprints plus the cache schema.
- The cache stores the complete list of compatible edges and directional service witnesses.
- Utility is excluded so the same graph can serve another utility policy without re-running the pair loop.
- Moka uses a 30-minute TTL and an approximate 64 MiB weighted capacity.

Both capacities are cache weights, not hard process-RSS guarantees. Both caches are process-local and are lost when the runner process exits. There is no persistent or cross-process cache backend.

## Correctness contract

The Rust implementation mirrors the current Python v0.1 compatibility contract:

- shared facts must be consistent, with JSON value types preserved (boolean is not integer; integer is not float);
- a need is satisfied by an exact expected value, or by key presence when its expected value is JSON null (presence-only);
- either service direction may create an edge, but each direction records its satisfied and unmet needs;
- a pair with conflicting facts or no satisfied need in either direction is not an edge.

The planner validates prebuilt graphs before matching: node IDs and utility values must match the anchor-eligible contexts; each edge must have the expected objective weight; and service witnesses must refer to the edge endpoints.

## Executable verification

Exact verified head: `1a7734f6520fce5b43bc1a79a1946126dfb90bab`.

- Rust: 6/6 unit tests; `cargo fmt --check`, `cargo test`, and release build passed.
- Python: 32/32 unit and integration tests passed.
- Synthetic controls: 8/8 passed.
- Primary real MultiWOZ checks: 8/8 passed. These include raw-data validation, exact objective comparison, non-trivial reconfiguration, anchor repair, scarcity subset, Rust graph equivalence, Rust full-plan equivalence, and cache-boundary checks.
- Eight-seed sensitivity: 88/88 checks passed, including graph and full-plan equality for both utility policies and confirmation of whole-graph hits on the repeated utility evaluation.

## Measured results

Measurements include eligible-context filtering, payload serialization, JSON-lines transport to the Rust process, response parsing, and NetworkX graph reconstruction. Python timings include the existing Python graph builder. These are graph-construction-path comparisons, not full application or production latency measurements.

### Repeated graph / changed utility (eight seeds)

| Path | Mean | Median |
|---|---:|---:|
| Python reference graph builder | 0.1965 s (request-priority) | 0.2266 s |
| Rust warm whole-graph cache | 0.0312 s | 0.0349 s |

The measured Rust warm path was about 6.3× faster by mean graph-build time for these eight repeated-graph utility evaluations. The graph cache hit in all eight seeds. The pair cache accumulated 867,533 lookups, 467,202 hits, and 400,331 misses (53.85% hit rate).

### Slot-count graph across eight anchor seeds

| Path | Mean | Median |
|---|---:|---:|
| Python reference graph builder | 0.2238 s | 0.2523 s |
| Rust pair/graph cache path | 0.1945 s | 0.1930 s |

The slot-count path includes changing eligible-context sets. It is not uniformly faster for every seed; results vary with overlap and hit rate.

### Primary 1,000-dialogue benchmark

- 1,000 actual MultiWOZ 2.2 test dialogues; 524 eligible contexts; 1,432 compatibility edges; 188 selected contexts (94 pairs).
- All 8 primary checks passed and Python/Rust graphs and full plans matched.
- Pair cache: 782,729 pair lookups, 402,030 hits, 380,699 misses (51.36% hit rate).
- Whole-graph cache: five graph misses, zero hits. The main anchor, three replacement anchors, and scarce subset each produce a different eligible context set.
- Initial cold Rust graph path: 0.3909 s; Python reference graph build: 0.2472 s. Cold Rust is slower in this first run; the pair cache benefit appears as later anchors reuse overlapping pairs.

The full CI benchmark deliberately executes both implementations for parity. Its total runtime therefore includes duplicate work and is not evidence that the complete planner request is faster in production.

## Follow-up lifecycle and end-to-end verification (2026-10-30)

**Exact verified head:** `1bf1bb64d35a91475b8497832a02596a167a3210`.  
**CI:** [run 41009623330](https://github.com/Loofy147/Machine/actions/runs/41009623330).  
**Evidence:** [artifact 12956722703](https://github.com/Loofy147/Machine/actions/runs/41009623330/artifacts/12956722703).

### Verification gates

- Rust: **9/9** tests passed, including pair/graph TTL expiry, pair-cache capacity eviction, and whole-graph-cache capacity eviction.
- Python: **34/34** tests passed, including subprocess TTL configuration and graph-key order/utility invariance.
- Supplementary synthetic controls: **8/8**.
- Primary MultiWOZ checks: **8/8**.
- Eight-seed sensitivity and parity checks: **88/88**.
- Changing-context trace: **41/41** checks across **12/12** snapshots.
- End-to-end path benchmark: **6/6** checks.

### TTL and bounded-capacity results

The production defaults remain 30 minutes, with approximate weighted capacities of 128 MiB for pair entries and 64 MiB for graph entries. Test processes can override these through `MACHINE_CACHE_TTL_MS`, `MACHINE_CACHE_PAIR_CAPACITY_BYTES`, and `MACHINE_CACHE_GRAPH_CAPACITY_BYTES`; the normal defaults are unchanged.

- With an 80 ms test TTL, a repeated graph first hits the whole-graph cache; after a 180 ms wait, the graph and pair entries expire and the same request recomputes.
- Pair-cache pressure test: 256-byte pair capacity, 1-byte graph capacity, 20 distinct incompatible pairs. The test confirms bounded entry count and both cache hits and recomputation on the second pass.
- Graph-cache pressure test: 136-byte graph capacity, 1 MiB pair capacity, 20 distinct small graphs plus a frequently reused graph. The test confirms that the graph cache cannot retain every distinct graph and that some requests must rebuild while hot entries can remain reusable.

These tests validate Moka's configured weighted-cache behavior. They do **not** establish a hard process-RSS ceiling; weighted capacity is an approximate cache-accounting limit, not a memory sandbox.

### Changing-context workload

The lifecycle runner uses 180 actual MultiWOZ-derived contexts and a 12-snapshot deterministic trace:
- baseline and utility-only change;
- alternate anchor;
- add, remove, and replace contexts;
- one fact mutation, one need mutation, and three-context mutation;
- restore and repeat the original context set under changed utility;
- a different set with the same context count.

All 12 snapshots preserved exact Rust/Python graph and plan equality. Aggregate cache results:

| Metric | Result |
|---|---:|
| Snapshot checks | 41/41 |
| Whole-graph cache hits / misses | 3 / 9 |
| Pair lookups | 137,989 |
| Pair-cache hits | 118,115 |
| Pair-cache misses | 19,874 |
| Pair-cache hit rate | 85.60% |

A single fact mutation invalidated the whole graph and caused exactly 179 pair misses (one changed context paired with 179 unchanged contexts); the other 15,931 pair results were reused. A single need mutation produced the same 179/15,931 split. This demonstrates the intended invalidation granularity for this trace.

### Separate end-to-end planner latency

The new benchmark times two independent request paths; it does not execute Python reference and Rust backend together on every timed request. It uses 1,000 actual MultiWOZ test dialogues, 996 candidate contexts, 524 anchor-eligible contexts, and 1,432 Python-reference edges.

- Python path: full Python graph construction plus exact NetworkX matching.
- Rust path: Rust cache request, JSON/process transport, NetworkX graph reconstruction, prebuilt-graph validation, and the same exact NetworkX matching.
- Rust process startup is measured separately; the Rust process remains alive across timed warm requests.
- Cold and warm paths are reported separately; parity work is outside timed intervals.

**Cold request (one observation):**

| Path | End-to-end request time |
|---|---:|
| Python reference | 0.4197 s |
| Rust, cache-cold (process startup excluded) | 0.4523 s |
| Rust process startup | 0.00095 s |

The cold Rust request was slower in this single observation. Do not treat one cold sample as a stable performance estimate.

**Seven warm requests:**

| Metric | Python reference | Rust cache + Python matching |
|---|---:|---:|
| Median end-to-end | 0.41995 s | 0.26531 s |
| Mean end-to-end | 0.44667 s | 0.29275 s |
| p95 (maximum of seven samples) | 0.60175 s | 0.45681 s |

The median Python/Rust ratio was **1.5829×**. All **7/7** timed Rust requests hit the whole-graph cache. Cold graph equality and complete-plan parity passed; representative warm plans at indices 0, 3, and 6 also matched Python exactly.

This is an end-to-end result for the measured planner request path, not a Rust matching speedup: matching and prebuilt-graph validation remain Python/NetworkX. The result is one CI environment, one pinned corpus conversion, and seven warm samples. Independent datasets and production-like concurrency are still needed.

## Decision and remaining gates

**Decision:** retain as an opt-in experimental backend. The evidence now supports correctness under TTL/capacity pressure, reuse across changing contexts, and a measured warm end-to-end benefit for repeated graph identity. Do not replace the Python reference or enable Rust by default yet.

Remaining work before any promotion:

1. Repeat the end-to-end comparison across independent real datasets and workload traces with different graph-reuse rates.
2. Measure actual process RSS, cache admission/eviction rates, concurrency, contention, and process-restart behavior under production-like conditions.
3. Evaluate whether a process-local cache is sufficient or a persistent/shared cache is justified.
4. Validate on actual business/legal contract-like data; MultiWOZ remains a travel/service dialogue proxy.

These results establish equivalence and observed performance only for the current v0.1 contract, pinned MultiWOZ conversion, and recorded CI environment. They do not establish production suitability or performance for business/legal contract workloads.
