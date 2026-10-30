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

## Decision and remaining gates

**Decision:** retain as an opt-in experimental backend for repeated graph computations. Do not replace the Python reference or enable Rust by default yet.

Remaining work before any promotion:

1. Repeat on independent actual datasets and realistic changing context/anchor traces.
2. Measure cold start, graph-cache hit, pair-overlap, memory/eviction, TTL expiry, and process-restart behavior under controlled conditions.
3. Benchmark end-to-end planner latency with parity checks separated from production-path execution; include maximum-weight matching and serialization costs.
4. Add explicit property tests for graph-cache key order invariance, utility-only reuse, invalidation/version changes, TTL, and capacity eviction.
5. Evaluate whether the process-local cache is sufficient or a persistent/shared cache is justified.

These results establish equivalence and observed graph-build performance only for the current v0.1 contract, this pinned MultiWOZ conversion, and the recorded CI environment. They do not establish production suitability or performance for business/legal contract workloads.
