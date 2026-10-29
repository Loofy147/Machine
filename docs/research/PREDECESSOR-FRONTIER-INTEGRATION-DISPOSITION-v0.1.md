# Predecessor Frontier Integration Disposition v0.1

**Status:** INTEGRATION / EXPERIMENT-SCOPED  
**Date:** 2026-10-29  
**Base:** `Loofy147/Machine@2d5f6bd0513ecd2d9f29f395d4d95c90849b2648`  
**Purpose:** Reconcile existing predecessor-access results on a clean branch without merging divergent research history.

## Decision

Do not classify direct predecessor access as a new computability primitive on the evidence currently available.

The defensible result is conditional:

- Under opaque-forward access, stored reverse relations are not operational unless the substrate provides a way to inspect and interpret them.
- Under generic random-access state plus arithmetic and finite iteration, the tested reverse-index representation reproduces the predecessor lookup semantics without a fiber-specific operation.
- A dedicated predecessor/fiber access path can still offer a different resource point. The result is not free: representation construction, storage, mutation and access cost must be accounted for.
- All-pairs policy tables can further reduce sampled online work by spending substantially more offline work and storage.
- The abstract Machine model does not select one of these access profiles as canonical.

## Existing contract carried forward

The existing `machine.substrate-resource-contract.v0.2` schema is copied without modification. It is frozen for P-07 normalized resource comparison, not for choosing one repository-wide production profile.

The comparison contract keeps read addressing and write/update addressing separate:

- Read profile: A0 opaque, A1 random access, or A2 specialized index.
- Write/update profile: W0 none, W1 generic cell write, or W2 structured update.
- Mutation profile: M0 static, M1 batched rebuild, or M2 dynamically maintained representation.
- Timing: target revelation relative to preprocessing.
- Cost: offline work, persistent representation, online structural work, and latency, preserving units rather than silently reducing them to one scalar.
- Correctness: exact labeled predecessor fibers and algorithm-level semantic checks.

The integration gate adds operational checks for the experiment: relation construction is charged; target-oblivious preprocessing cannot depend on the later query; output enumeration is charged; generic relation interpretation is allowed only in the declared A1 profile; and dedicated fiber access remains an explicit A2-style extension.

## Reproducible evidence brought into this branch

The historical branch results and source references remain labeled by their original provenance:

1. `research/machine-substrate-primitive-closure-v0` — contract-bound primitive-closure runner, v0.2 resource contract, and validators.
2. `research/active-frontier-cost-v0` — forward search, native bidirectional search, reverse-index, and all-pairs policy comparison.
3. Dynamic representation tests — generic read/write mutation and exact contiguous CSR maintenance, with explicit structural work accounting.

Historical results are not retroactively labeled as tests of this integration commit. The new CI run produces a separate aggregate artifact tied to its own source commit and includes the individual experiment outputs.

## Current integration gate

The workflow must:

1. Validate the original v0.1 contract schema and its concrete instance matrix.
2. Validate the unchanged v0.2 frozen comparison schema structurally.
3. Re-run predecessor semantic closure and require zero builder, predecessor, and basin failures.
4. Re-run generic mutable-index and exact-CSR mutation experiments, requiring zero semantic/invariant failures.
5. Re-run the Pareto experiment and verify that native bidirectional and reverse-index methods have identical sampled online frontiers, while the all-pairs policy improves online cost at higher offline/storage cost.
6. Write a machine-readable run result with source commit and SHA-256 fingerprints.

## Interpretation boundary

The online-work unit in the Pareto experiment is the runner's declared structural tick. This integration does **not** claim a physical latency calibration for a dedicated predecessor instruction, nor does it normalize every unlike event class into one cost unit. A physical-cost winner or a universal asymptotic closure theorem is not inferred.

## Open decision gates

- `OPEN`: canonical repository-wide primitive/access contract for the abstract Machine model.
- `OPEN`: normalized cost of a native predecessor operation versus generic indexed state access.
- `OPEN`: production choice among static, batched and dynamic representations under an actual query/update distribution.
- `OPEN`: extension from tested finite fixtures to independent graph families and an asymptotic result.

## Source provenance

- Main base: https://github.com/Loofy147/Machine/commit/2d5f6bd0513ecd2d9f29f395d4d95c90849b2648
- Primitive-closure research head inspected: https://github.com/Loofy147/Machine/commit/5db33b068c0973606e08b596a300e99952764aeb
- Frontier-cost research head inspected: https://github.com/Loofy147/Machine/commit/566aba464d0f47b22eb91de78a5cc97ca153bb3b
- Existing contract crosswalk and resource docs are retained at their original paths and status.
