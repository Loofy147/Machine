# Predecessor Access Cost Normalization v0.1

**Status:** SYMBOLIC COST MODEL / TESTED  
**Scope:** Query-access comparison under the existing Machine substrate resource contract. This does not select a canonical production substrate.

## Why this follows the integrated frontier experiment

The prior experiments establish semantic closure for tested finite representations and report structural work. They do not establish that one specialized fiber lookup costs the same as one generic state read. Counting an API invocation as a single unit would silently assume the conclusion.

This extension preserves event vectors and makes scalar comparisons conditional on caller-supplied weights.

## Event model

Let (E) be the transition count scanned by the opaque profile and (d) the number of predecessor entries returned. Let (c_p), (c_r), (c_f), and (c_o) denote the costs of an opaque transition probe, generic state-word read, specialized fiber lookup (including its internal access work), and output entry respectively.

| Profile | Probes | Generic state reads | Specialized lookup calls | Returned entries |
|---|---:|---:|---:|---:|
| Opaque forward | (E) | 0 | 0 | (d) |
| Generic CSR lookup | 0 | (2+2d) | 0 | (d) |
| Specialized fiber lookup | 0 | 0 | 1 | (d) |

The generic CSR count charges two offset reads and source/action reads for each returned predecessor. The specialized profile uses the same prebuilt CSR representation; only the access interface differs. Output cardinality is equal.

[
C_0 = E c_p + d c_o
]

[
C_1 = (2+2d)c_r + d c_o
]

[
C_2 = c_f + d c_o
]

The specialized operation is never assigned a default cost.

## Falsifiable break-even conditions

The specialized access path beats generic CSR access exactly when:

[
c_f < (2+2d)c_r
]

It beats the opaque scan exactly when:

[
c_f < E c_p
]

Generic CSR access beats the opaque scan exactly when:

[
(2+2d)c_r < E c_p
]

These are conditional equations, not empirical speed claims. A physical winner cannot be declared until relevant weights are measured or otherwise justified for a specific substrate.

## Offline and storage accounting

For the declared CSR builder abstraction:

[
B_{off}=2E+n
]

where (n) is the state count; this counts edge counting, prefix work and edge scattering at the experiment's stated granularity.

For int32 offsets, int32 source payload and uint8 action payload:

[
R_{CSR}=4(n+1)+5E	ext{ bytes}
]

The generic and specialized CSR profiles have the same offline build and persistent representation in this comparison. The opaque profile does not allocate inverse CSR. Bytes, build events, reads, probes and fiber calls are not reduced to one scalar without explicit weights.

## Verification

The integration gate adds 10 unit tests covering dimensions, unknown profiles, output equivalence, event counts, positive finite weights, symbolic break-even conditions and CSR footprint accounting. It also sweeps 11 ((E,d)) combinations across all three profiles and checks three explicit CSR footprints. The generated `COST-NORMALIZATION-V0.1.json` records the sweep at the CI source commit.

## Disposition

- **ESTABLISHED within this model:** event accounting and symbolic break-even conditions are internally consistent and regression-tested.
- **EXPERIMENTALLY_SUPPORTED:** predecessor representation closure in tested finite settings, preserved by the integration gate.
- **OPEN:** physical implementation-specific (c_f), (c_r), and (c_p); canonical Machine primitive set; production winner under real query/update rates.
- **NOT ESTABLISHED:** absolute computability advantage or universal superiority of a named mechanism.


## Follow-up audit: hidden query-time construction corrected

The inherited Pareto runner initially rebuilt reverse adjacency inside every `native_bidi` query while reporting no offline build or storage for that profile. Those builds were omitted from its query tick counter. Earlier frontier values from that runner are historical and overly favorable for the native profile; they are not normalized physical-cost evidence.

The integration follow-up replaces that hidden build with an explicit direct-fiber primitive for the declared A/B/C graph family. It charges one direct-fiber access event and each returned predecessor entry. The reverse-index profile separately charges one bucket-access event and each returned entry. Equal structural tick weights are an explicit abstract comparison convention; they do not claim that physical native access and memory lookup have equal latency. Symbolic physical weights remain separate in `cost_model.py`.

A regression test checks every target fiber against a reverse index for M in {3, 5, 30, 100, 300}, preserving duplicate predecessor sources from different labeled operations. Another test patches full edge enumeration and index construction to fail if either is called by the native query path.
