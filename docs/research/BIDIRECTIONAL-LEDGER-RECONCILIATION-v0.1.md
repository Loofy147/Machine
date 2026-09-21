# Bidirectional Ledger Reconciliation v0.1

Status: DURABLE RECONCILIATION RECORD
Repository: Loofy147/Machine
Branch: research/bidirectional-ledger-reconciliation-v0
Base: research/bidirectional-grounded-verification-v0 @ cc61765d6939788ab9c075f04ec3572203c89347
Recorded: 2026-09-21

## Purpose

Reconcile the finalized Rev 2.1 substrate discussion, the bidirectional-search evidence line, and the claim-ledger migration state without silently treating unavailable source files as verified.

## Source audit

The following exact source filenames were requested/referenced:

- machine_substrate_spec_rev2.md
- claims_revised.yaml
- ledger_core.py
- test_trace.py
- demo_claims_migration.py
- bidir_v3.py
- exp_policies.py
- exp_scaling.py
- replicate.py
- real_graph_meta.json

They are not present in the current Machine Git trees inspected from the active research branches, and they were not retrievable as exact files from the available conversation/library file index.

Therefore:

- no canonical copy of claims_revised.yaml is fabricated here;
- no harness result is promoted merely because its numeric value appears in conversation;
- missing source artifacts remain explicitly pending.

## Rev 2.1 semantic reconciliation

A prior verification docket available in the Library, M* — Verification Docket v3.4, describes an older substrate:

M* = <S, Sigma, delta, R^-1_rev, R^+_opt, Phi, Pi>

That docket is now treated as historical evidence, not the Rev 2.1 canonical signature.

The current Rev 2.1 target is:

M = (S, Sigma, delta, R, C)

The reconciliation rules recorded from the current Rev 2.1 discussion are:

1. Phi and P/Pi are not part of the Rev 2.1 signature.
2. R+_opt is not a separately required optimized relation: delta is the dense n x k forward table and forward evaluation is already O(1).
3. Player ownership is explicit: owner[s] in {0,1}; 0 is existential and 1 universal.
4. CPre/attractor semantics depend on ownership and correct multiplicity accounting.
5. The attractor multiplicity bug is a representation-contract failure: a deduplicated predecessor fiber cannot be paired with raw out-degree counters.
6. The unified Fiber implementation derives the counter convention from Fiber.deduped.

The M* docket itself records the older Phi/R+_opt form and is archived separately on the substrate research branch so historical provenance is not lost.

## Current executable substrate implementation

Branch:
research/substrate-rev2.1-v0

Final head:
9de32c4716000d0a4996e707afd1f531567250f6

The implementation profile and tests live under:

experiments/substrate-interpreter-v0/substrate.py
experiments/substrate-interpreter-v0/test_substrate.py
docs/SUBSTRATE-REV2.1-IMPLEMENTATION-PROFILE-v0.1.md
evidence/substrate-rev2.1-values-v0.1.json

CI workflow:
.github/workflows/substrate-rev2.1-conformance.yml

CI execution state is not upgraded to PASS because the available connector did not expose the push-triggered run for the commit.

## Bidirectional evidence already durable

Branch:
research/bidirectional-grounded-verification-v0

Head:
cc61765d6939788ab9c075f04ec3572203c89347

Current v0.4 artifacts include:

- exact weighted n=3: 4^6 graph states, 233472 schedules, 0 active-guard failures, 3840 finite naive failures;
- exact weighted n=4: 3^12 graph states, 488430 solvable, 976860 policy runs, 0 active-guard failures, 4374 finite naive failures;
- random n=4 all-schedule: 351232 runs, 0 active-guard failures, 4736 finite naive failures;
- matched simple/multigraph: 2000 matched pairs, 8000 policy runs, geometry/G_MX/VC/expansion equality under the declared dominated-parallel construction, mean W_multi/W_simple = 1.6734.

These numbers are repository-backed by the v0.4 runner/results/protocol/evidence files on that branch.

## Claim ledger migration state

The reported 15 claim IDs are:

- k4p8s3
- m9c5d2-a
- m9c5d2-b
- m9c5d2-c
- m9c5d2-d
- e7m2r1
- h2q9v4
- g1a8n2
- g2b5k7
- g3c9m4
- g4d6p1
- g5e3r8
- g6f7t2
- g7h1v5
- w3x7k1

The conversation reports that 3 claims are present in the demo migration and possibly a fourth logical entry is represented by a strong/weak split. The exact fourth ID and the canonical claims_revised.yaml source were not retrievable, so the repository ledger does not guess them.

Known-from-current-discussion migration anchors:

- g1a8n2 — referenced as a migrated bidirectional-search/literature-grounding claim.
- w3x7k1 — referenced as a migrated edge-scan amplification claim.
- m9c5d2-c — referenced as part of the migrated stage-decomposition/linear-scaling family.

All remaining claim IDs remain MIGRATION_PENDING until their source text and provenance are recovered.

## Harness migration state

The following source scripts were named but not located in the inspected Machine trees:

- bidir_v3.py
- exp_policies.py
- exp_scaling.py
- replicate.py
- real_graph_meta.json

Therefore v0.4 results are not retroactively labeled as re-runs of these exact scripts.

The v0.4 runner is a replacement executable for the declared weighted/scheduler experiments, with its own protocol and result manifest.

## Required next reconciliation

1. Recover the exact source files from the originating repository/archive.
2. Hash and ingest those files without rewriting their contents.
3. Map each of the 15 claims to:
   claim -> exact source -> experiment/proof -> artifact -> status.
4. Run the named original harnesses against the declared metadata/result files.
5. Compare original outputs with v0.4 replacement outputs.
6. Upgrade or contradict claims only after this differential check.

## Non-claims

This file does not assert that:

- the unavailable Rev 2.1 specification was fully read;
- all 15 claims are migrated;
- the named original harnesses have been re-run;
- the experimental active-guard result is a universal theorem for arbitrary consistent heuristics.

