"""Machine Substrate Rev 2.1 contract crosswalk experiment.

Control:
  derive predecessor fibers directly from the same delta table.

Treatment:
  build target-oblivious inverse CSR R^-1 from that same delta table,
  then use the fiber representation for predecessor expansion.

The experiment does NOT treat the extra representation as free.
It reports:
  - semantic equivalence;
  - offline construction units;
  - incremental inverse-storage bytes;
  - online predecessor probes/entries;
  - backward-basin work.

The intended disposition is resource/representation relocation, not a
computational-power separation.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np

from substrate_lib import (
    build_csr_count,
    build_csr_np,
    basin_csr,
    gen_system,
    preds_naive,
    validate_csr,
)


def layered_scan_count(delta: np.ndarray, U: list[int]):
    """Reference backward fixpoint with explicit full-table inspection count."""
    n, k = delta.shape
    E = int((delta >= 0).sum())
    Z = np.zeros(n, dtype=bool)
    Z[list(U)] = True
    rounds = 0
    inspections = 0
    while True:
        rounds += 1
        inspections += n * k
        valid = delta >= 0
        safe = np.where(valid, delta, 0)
        hit = (Z[safe] & valid).any(axis=1)
        new = Z | hit
        if np.array_equal(new, Z):
            return Z, rounds, inspections, E
        Z = new


def fiber_pairs(offs: np.ndarray, src: np.ndarray, act: np.ndarray, u: int):
    lo, hi = int(offs[u]), int(offs[u + 1])
    return list(zip(src[lo:hi].tolist(), act[lo:hi].tolist()))


def run():
    rng = np.random.default_rng(20260927)
    configs = [
        (31, 3, 0.0, 0.0),
        (31, 4, 0.4, 0.0),
        (127, 3, 0.5, 0.0),
        (127, 5, 0.7, 0.10),
        (503, 4, 0.3, 0.0),
        (503, 6, 0.6, 0.05),
    ]
    systems = []
    lookup_rows = []
    basin_rows = []
    total_lookup = 0
    total_basin = 0
    semantic_failures = 0
    basin_failures = 0
    builder_failures = 0

    for family_id, (n, k, p_hub, undefined) in enumerate(configs):
        for rep in range(12):
            seed = 100000 + family_id * 1000 + rep
            hubs = max(3, min(25, n // 8))
            delta = gen_system(
                n=n,
                k=k,
                seed=seed,
                hubs=hubs,
                p_hub=p_hub,
                undefined=undefined,
            )
            E = int((delta >= 0).sum())

            offs, src, act = build_csr_np(delta)
            o2, s2, a2 = build_csr_count(delta.ravel().tolist(), n, k)
            builder_ok = (
                np.array_equal(offs, np.asarray(o2, dtype=np.int32))
                and np.array_equal(src, np.asarray(s2, dtype=np.int32))
                and np.array_equal(act, np.asarray(a2, dtype=np.uint8))
                and validate_csr(delta, offs, src, act)
            )
            if not builder_ok:
                builder_failures += 1

            # P-04 structural accounting: count E + prefix n + scatter E.
            offline_units = 2 * E + n

            # Incremental storage relative to the forward delta table.
            inverse_bytes = int(
                offs.nbytes + src.nbytes + act.nbytes
            )
            forward_bytes = int(delta.nbytes)

            systems.append(
                {
                    "family_id": family_id,
                    "rep": rep,
                    "n": n,
                    "k": k,
                    "E": E,
                    "offline_units": offline_units,
                    "forward_delta_bytes": forward_bytes,
                    "inverse_bytes": inverse_bytes,
                }
            )

            # Same target-oblivious representation: build is done before queries.
            for q in range(8):
                u = int(rng.integers(0, n))
                control = sorted(preds_naive(delta.tolist(), n, k, u))
                treatment = sorted(fiber_pairs(offs, src, act, u))
                ok = control == treatment
                if not ok:
                    semantic_failures += 1
                degree = len(treatment)
                lookup_rows.append(
                    {
                        "family_id": family_id,
                        "rep": rep,
                        "u": u,
                        "degree_in": degree,
                        "control_probes": n * k,
                        "treatment_entry_reads": degree,
                        "treatment_access_ops_lower_bound": 2 + degree,
                        "equivalent": ok,
                    }
                )
                total_lookup += 1

            for q in range(3):
                m = int(rng.integers(1, min(4, n) + 1))
                U = rng.choice(n, size=m, replace=False).tolist()
                ref, rounds, control_inspections, E2 = layered_scan_count(delta, U)
                got_bytes, got_count, treatment_entries = basin_csr(
                    offs.tolist(), src.tolist(), U
                )
                got = np.frombuffer(bytes(got_bytes), np.uint8).astype(bool)
                ok = np.array_equal(ref, got) and got_count == int(ref.sum())
                if not ok:
                    basin_failures += 1
                basin_rows.append(
                    {
                        "family_id": family_id,
                        "rep": rep,
                        "targets": U,
                        "basin_size": int(ref.sum()),
                        "layers": rounds,
                        "E": E2,
                        "control_full_table_inspections": control_inspections,
                        "treatment_fiber_entries": int(treatment_entries),
                        "equivalent": ok,
                    }
                )
                total_basin += 1

    lookup_control = sum(r["control_probes"] for r in lookup_rows)
    lookup_treatment_entries = sum(r["treatment_entry_reads"] for r in lookup_rows)
    lookup_treatment_ops = sum(r["treatment_access_ops_lower_bound"] for r in lookup_rows)
    basin_control = sum(r["control_full_table_inspections"] for r in basin_rows)
    basin_treatment = sum(r["treatment_fiber_entries"] for r in basin_rows)

    avg_inverse_bytes = float(np.mean([x["inverse_bytes"] for x in systems]))
    avg_forward_bytes = float(np.mean([x["forward_delta_bytes"] for x in systems]))
    avg_offline_units = float(np.mean([x["offline_units"] for x in systems]))

    out = {
        "status": "EXECUTED / CI",
        "contract": {
            "control": "same delta; online predecessor enumeration by scanning all n*k transition entries",
            "treatment": "same delta; target-oblivious inverse CSR built offline then queried by fiber slice",
            "timing": "inverse construction precedes all online queries",
            "information": "identical source relation delta",
            "correctness": "exact labeled predecessor pairs and backward-basin fixpoint",
            "cost": "structural operation counts; no wall-clock comparison used for classification",
        },
        "workload": {
            "systems": len(systems),
            "lookups": total_lookup,
            "basin_queries": total_basin,
            "families": len(configs),
        },
        "verification": {
            "builder_failures": builder_failures,
            "lookup_semantic_failures": semantic_failures,
            "basin_semantic_failures": basin_failures,
            "all_semantics_equal": (semantic_failures == 0 and basin_failures == 0),
        },
        "aggregate": {
            "lookup_control_probes": lookup_control,
            "lookup_treatment_entry_reads": lookup_treatment_entries,
            "lookup_treatment_access_ops_lower_bound": lookup_treatment_ops,
            "lookup_entry_read_ratio_control_over_treatment_ops": (
                lookup_control / lookup_treatment_ops
                if lookup_treatment_ops else None
            ),
            "basin_control_full_table_inspections": basin_control,
            "basin_treatment_fiber_entries": basin_treatment,
            "basin_inspection_ratio_control_over_treatment": (
                basin_control / basin_treatment
                if basin_treatment else None
            ),
            "mean_forward_delta_bytes": avg_forward_bytes,
            "mean_incremental_inverse_bytes": avg_inverse_bytes,
            "mean_offline_build_units": avg_offline_units,
        },
        "disposition": {
            "information_new": False,
            "target_dependent_preprocessing": False,
            "extra_representation_storage": True,
            "offline_work_charged": True,
            "semantic_frontier_shift_observed": True,
            "classification": "representation/resource relocation under the Rev 2.1 contract",
            "absolute_computational_power_claim": "NOT_SUPPORTED",
        },
        "sample_rows": {
            "lookup": lookup_rows[:20],
            "basin": basin_rows[:12],
        },
    }

    out_path = Path(__file__).with_name("RESULTS-V0.1.json")
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    run()
