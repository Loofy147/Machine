# Bidirectional Substrate v3 — Integration Record

Status: INTEGRATED_WITH_REPRODUCIBILITY_CONTRACT
Date: 2026-09-21

## Integration

The v3 research branch was integrated into the current Rev 2.1 substrate line through PR #6.

- Source branch: `research/bidirectional-substrate-v3`
- Source head before merge: `00bf324111ffd05c3965edc84f8125756687466f`
- Target branch: `research/substrate-rev2.1-v0`
- Target head before merge: `6694f00b0d6619acf9ec92b97989e2b66508d2e8`
- Merge commit: `d8bce8a6751d449965a69860c52b1eddef28fddc`
- PR: #6

The merge commit has a valid GitHub signature. Main was not modified by this integration.

## Included artifacts

The integrated changes include:

- `docs/research/BIDIRECTIONAL-SUBSTRATE-GROUNDED-RESEARCH-v3.md`
- `docs/research/MACHINE-SUBSTRATE-SPEC-REV2.1.md`
- `evidence/BIDIRECTIONAL-SUBSTRATE-CLAIMS-REVISED.yaml`
- `experiments/bidirectional-substrate-v3/` source and supplied result artifacts
- `.github/workflows/bidirectional-substrate-v3-conformance.yml`
- `docs/research/BIDIRECTIONAL-SUBSTRATE-V3-REPRODUCIBILITY-v0.1.md`

## Reproducibility disposition

The regression inputs `orig_runs.pkl` and `prov_v2.pkl` are generated build outputs, not committed evidence.

The declared reproduction path is:

1. `python bidir_pasted_original.py`
2. `python run_prov.py`
3. `python verify_v3.py`

The new CI workflow performs those generation steps before the full regression.

## Verification boundary

Established from repository inspection:

- v3 source, supplied results, and provenance archive are present.
- the seven-policy smoke test source is present.
- JSON/YAML validation is part of the CI contract.
- the full regression has a deterministic source path and no longer depends on hand-supplied pickle files.
- `machine_substrate_artifacts.zip` is now present in the integrated v3 artifact package; the previous NOT_SUPPLIED boundary is closed for the substrate correctness/benchmark package. The package includes the C1-C7 correctness harness, B1-B10 benchmark sources, C benchmark, and `substrate_results.json`.
- external Networkit real-graph acquisition remains a separate network-dependent stage.

CI verification completed successfully for the pre-artifact v3 integration commit: GitHub Actions run `35584149685` (Bidirectional Substrate v3 Conformance) concluded `success`, and `verify_v3.py` plus prior validation steps completed successfully. The repository also recorded substrate Rev 2.1 conformance run `35584149682` as `success`. After integration of the machine-substrate artifact package, the same two workflows were triggered on merge commit `e03b541b679bd2141a67f3a55247a3854545597a`; the Rev 2.1 conformance run completed successfully, while the post-artifact v3 run `35585041468` was still in progress at the time of this record update. No PASS is claimed for that final post-artifact v3 run until GitHub reports completion.

## Claim-status rule

This integration does not promote imported measurements to independent reproduction merely because the files are now in the repository. A claim is upgraded only when the corresponding execution or proof evidence exists.

## Lineage rule

The v3 branch was based on an older Machine commit, but the merge was performed against the latest Rev 2.1 substrate head. The resulting merge commit therefore preserves both histories and places the v3 artifacts on the current Rev 2.1 research line.
