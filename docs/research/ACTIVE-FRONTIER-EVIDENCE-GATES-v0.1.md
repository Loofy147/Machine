# Active Frontier Program — Evidence Gate Matrix v0.1

Date: 2026-09-28
Repository: Loofy147/Machine
Program: research/active-frontier-program-v0
Baseline: research/bidirectional-grounded-verification-v0

## Gate principle

A branch may progress independently, but a claim may only advance when its source, execution, artifact, scope, and status are all traceable.

## Evidence matrix

| Item | Current status | Evidence anchor | Exact source state | Next gate |
|---|---|---|---|---|
| Naive top-only guard failure | CONTRADICTED | v0.4 n=3 + regression | durable | none for contradiction itself |
| Active-vertex guard | EXPERIMENTALLY_SUPPORTED | v0.4 exact/random suites | durable result; source closure incomplete | formal proof + repository reproduction |
| n=2 minimality | HISTORICAL | v0.3 bounded record | not freshly executed in this program | execute new audit |
| n=3 smallest vertex count | OPEN beyond finite-space scope | v0.4 exact n=3 + historical n=2 | scope-limited | fresh n=2 + arbitrary scheduling |
| Arbitrary scheduling | OPEN | none yet in this program | not tested | adversarial runner |
| General consistent heuristics | OPEN | v0.4 explicitly limits claim | not attempted | MEP branch |
| Predecessor access total economics | OPEN | substrate measurements separate preprocessing/query | partial | controlled break-even experiment |
| Simple-digraph theoretical separation | OPEN | matched construction only | no lower-bound family | adversarial construction |
| Native C equivalence | OPEN | prior C substrate measurements are separate | not ported in this program | native branch |
| Product readiness | CLOSED | technical gates incomplete | not releasable | A-E gates |

## Critical source-closure finding

The v0.4 runner path is experiments/bidirectional-grounded-v0.4/run_v0_4.py
Git blob SHA: f3ca79d450d56e393c50805465278c003462d394

It imports core, but no core.py or equivalent module was found in the repository path checks performed on 2026-09-28.

The durable v0.4 hash manifest reports:
- runner_sha256 = fda87949728e25cda2073eafd6f7c4e2984af714e0c98c7c93fcfec8e2ce48f6
- results_sha256 = 39dba82d7c66b606f005aa78d8ef00174d6be2a2a271012d32c61c359dc7b253
- report_sha256 = c322f6711ffab29ddb5acb097918c4e46b66c9abfe2fb4549e3885c43842c28a
- protocol_sha256 = bdb60ef62c62445d98821f9e9da5e20612b56da723ebdf2a488413785a21eb1d
- evidence_sha256 = 7aff21d6380fd1a83acc1c4ea87e1c916867516ef37c9a8ecf37b5dd984a0624
- regression_sha256 = 91b7edab17681d7757cfab9edfa8199191c6ae488f1c71e728c6713c439f3f7c
- local_pack_zip_sha256 = 68e065bff5ca06aaf180ebf062088e98764358454c6e3c2accfa291025b6b315

These SHA-256 values are recorded claims from the repository hash manifest; they are not independently recomputed in this audit.

## Separation rule

Do not treat:
- v0.3 historical n=2 evidence as a fresh execution;
- v3 implementation as the v0.4 source;
- imported/local-pack presence as repository integration;
- zero observed failures as a proof;
- product packaging as evidence of market demand.

## Promotion gates

### Gate P — Proof
Required: theorem/proof with explicit interruption-state semantics and assumptions.
Failure: countermodel.

### Gate R — Reproduction
Required: exact v0.4 core source or immutable external source boundary; clean reproduction of canonical regression and small exhaustive suite.
Failure: output mismatch or provenance gap.

### Gate A — Adversarial
Required: n=2 fresh execution, arbitrary schedules, multigraphs, minimization.
Failure: smaller witness or active-guard counterexample.

### Gate H — Heuristic
Required: MEP-consistent formalization and differential tests.
Failure: finite false-stop.

### Gate C — Cost
Required: end-to-end preprocessing/query break-even curves.
Failure: no useful regime under declared resource envelope.

### Gate N — Native
Required: reference/native semantic equivalence plus performance measurements.
Failure: semantic mismatch.

### Gate X — Product
Required: supported-model contract, reproducible package, regression suite, benchmark envelope, integration example.
Failure: any unresolved source/provenance blocker.

## Current decision

Do not freeze the active-guard claim as a theorem.
Do not freeze the v0.4 repository re-execution as CLOSED.
Proceed in parallel on P, R, A, H, C, N; keep X gated.