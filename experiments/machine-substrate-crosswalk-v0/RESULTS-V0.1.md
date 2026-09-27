# Machine Substrate Contract Crosswalk v0.1 — Results

Status: EXPERIMENTALLY_SUPPORTED / CI EXECUTED
Run: `36350447694`
Job: `108707987716`
Head: `b1afea87bf8f10c0edc313be0797d8e540f8fc9c`
Base contract branch: `research/bidirectional-substrate-v3@59fab62704875193801db77c7cb8361475297f48`

## Workload

- 72 generated systems
- 576 predecessor lookups
- 216 backward-basin queries
- 6 graph/system families
- deterministic seeds recorded by the runner

## Contract

Control:
- same `delta`;
- predecessor enumeration scans all `n*k` transition entries online.

Treatment:
- same `delta`;
- `R^-1) is constructed target-obliviously before online queries;
- online predecessor enumeration uses the CSR fiber representation.

The treatment pays its offline construction work and incremental persistent representation storage.

## Verification

- CSR builder failures: 0
- predecessor semantic failures: 0
- backward-basin semantic failures: 0
- overall semantic equality: TRUE

Thus the inverse representation reproduced the exact labeled predecessor sets and the exact backward-basin fixpoint on the tested workload.

## Aggregate structural work

Predecessor lookup:

- control probes: **601,248**
- treatment fiber entry reads: **2,675**
- treatment lower-bound access operations (2 fiber-bound reads + entries): **3,827**
- control / treatment lower-bound ratio: **157.11×**

Backward basin:

- control full-table inspections: **1,378,965**
- treatment fiber entries touched: **204,752**
- inspection ratio: **6.73×**

Representation/accounting:

- mean forward `delta` storage: **8,350.67 bytes**
- mean incremental inverse CSR storage: **5,927.69 bytes**
- mean offline construction accounting: **2,237.28 units**

## Interpretation

The experiment changes no source information: `R^-1` is derived from the same `delta`.

It does introduce:
- additional persistent representation;
- explicit offline construction work;
- a different online access path.

Therefore the observed frontier shift is classified as:

**representation/resource relocation under the Rev 2.1 contract**

not as a new information source and not as evidence of an absolute computational-power separation.

## Important boundary

This result establishes closure for the tested Rev 2.1 representation/access contract.

It does not prove that every abstract Machine substrate can derive the same access path from generic state operations, because the abstract Machine model intentionally leaves its concrete state-access primitive set open.

## Raw artifact

CI artifact:
`machine-substrate-crosswalk-v0.1`

Artifact ID: `10942405552`
Artifact ZIP SHA-256: `1f93998bfc57d84e06924e16bd1317f911669a65bad233e65beb72f039511aa0`

Raw `RESULTS-V0.1.json` inside the artifact:
- size: 10,188 bytes
- SHA-256: `e175ee43cd433cad8b1baa11bdd668733cc77dc18979727b081da63d2a6bf61e`

## Disposition

`INFORMATION_NEW = false`
`TARGET_DEPENDENT_PREPROCESSING = false`
`EXTRA_REPRESENTATION_STORAGE = true`
`OFFLINE_WORK_CHARGED = true`
`SEMANTIC_EQUIVALENCE = true`

Current claim:

> Under the concrete Rev 2.1 contract, target-oblivious inverse-fiber representation relocates predecessor-discovery work from online scans into offline construction and persistent representation while preserving tested semantics.

Status:
**EXPERIMENTALLY_SUPPORTED / CONTRACT-BOUND**

Next discriminating question:

> Is the Rev 2.1 inverse-fiber access path already derivable from the abstract Machine substrate primitives, or does its access semantics constitute an additional substrate capability?
