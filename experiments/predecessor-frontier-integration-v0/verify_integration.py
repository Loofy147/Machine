"""Strict integration gate for the predecessor-frontier evidence package.

All comparisons are contract-bound. This verifies semantic equivalence and
frontier relationships; it does not create a universal cost conversion.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/predecessor-frontier-integration-v0/RESULTS-INTEGRATION-V0.1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute_json(relative_path: str) -> dict[str, Any] | list[Any]:
    path = ROOT / relative_path
    completed = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"{relative_path} failed with exit {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"{relative_path} did not emit a single JSON document: {exc}\n"
            f"stdout tail:\n{completed.stdout[-2000:]}"
        ) from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    contract_dir = ROOT / "experiments/machine-substrate-resource-contract-v0"
    contract_v01_path = contract_dir / "CONTRACT-v0.1.json"
    contract_v02_path = contract_dir / "CONTRACT-v0.2.json"
    instances_v01_path = contract_dir / "CONTRACT-INSTANCES-v0.1.json"
    instances_v02_path = contract_dir / "CONTRACT-INSTANCES-v0.2-PROPOSED.json"

    contract_v02 = json.loads(contract_v02_path.read_text(encoding="utf-8"))
    require(
        contract_v02.get("schema") == "machine.substrate-resource-contract.v0.2",
        "unexpected v0.2 schema identifier",
    )
    require(
        contract_v02.get("status") == "FROZEN_COMPARISON_CONTRACT",
        "v0.2 must retain its frozen comparison-contract status",
    )
    axes = contract_v02.get("axes", {})
    required_axes = {"A_r", "A_w", "T", "D", "tau", "B_off", "R_extra", "B_on", "M", "K"}
    require(set(axes) == required_axes, "v0.2 axis set changed")
    require(
        set(axes["A_r"].get("allowed_profiles", []))
        == {"A0_OPAQUE", "A1_RANDOM_ACCESS", "A2_SPECIALIZED_INDEX"},
        "v0.2 read-addressing profiles changed",
    )
    require(
        set(axes["A_w"].get("allowed_profiles", []))
        == {"W0_NONE", "W1_GENERIC_CELL_WRITE", "W2_STRUCTURED_UPDATE"},
        "v0.2 write/update profiles changed",
    )
    require(
        set(axes["M"].get("allowed", []))
        == {"M0_STATIC", "M1_BATCHED", "M2_DYNAMIC"},
        "v0.2 mutation profiles changed",
    )
    # Parse the proposed instance file, but do not promote it to a frozen contract.
    proposed_instances = json.loads(instances_v02_path.read_text(encoding="utf-8"))
    require(isinstance(proposed_instances, dict), "proposed instances must remain valid JSON")
    contract_v01 = json.loads(contract_v01_path.read_text(encoding="utf-8"))
    instances_v01 = json.loads(instances_v01_path.read_text(encoding="utf-8"))

    v01_validation = execute_json(
        "experiments/machine-substrate-resource-contract-v0/validate_contract.py"
    )
    require(v01_validation.get("status") == "PASS", "v0.1 contract validator did not pass")

    instance_validation = execute_json(
        "experiments/machine-substrate-resource-contract-v0/validate_instances.py"
    )
    require(instance_validation.get("status") == "PASS", "v0.1 contract instance validator did not pass")

    primitive = execute_json(
        "experiments/machine-substrate-primitive-closure-v0/run_primitive_closure.py"
    )
    pv = primitive.get("verification", {})
    require(pv.get("all_equal") is True, "primitive-closure semantic equality failed")
    require(pv.get("builder_failures") == 0, "reverse-index builder failure")
    require(pv.get("predecessor_semantic_failures") == 0, "predecessor semantic failure")
    require(pv.get("basin_semantic_failures") == 0, "backward-basin semantic failure")
    require(primitive.get("workload", {}).get("systems") == 72, "unexpected primitive-closure system count")
    require(primitive.get("workload", {}).get("lookups") == 720, "unexpected primitive-closure lookup count")

    mutable = execute_json(
        "experiments/machine-substrate-m2-representation-closure-v0/run_m2_representation_closure.py"
    )
    require(mutable.get("semantic_and_invariant_failures") == 0, "mutable-index invariant failure")
    require(mutable.get("cases") == 100, "unexpected mutable-index case count")
    require(mutable.get("updates_total") == 19720, "unexpected mutable-index update count")

    exact_csr = execute_json(
        "experiments/machine-substrate-m2-exact-csr-closure-v0/run_exact_csr_closure.py"
    )
    require(exact_csr.get("semantic_and_structure_failures") == 0, "exact-CSR invariant failure")
    require(exact_csr.get("cases") == 100, "unexpected exact-CSR case count")
    require(exact_csr.get("updates_total") == 19720, "unexpected exact-CSR update count")

    pareto = execute_json("experiments/pareto-representation-closure-v0/run.py")
    require(isinstance(pareto, list), "Pareto runner must emit a frontier list")
    methods = {"forward", "native_bidi", "reverse_index", "policy"}
    require(len(pareto) == 12, "unexpected number of Pareto frontier rows")
    by_m: dict[int, dict[str, dict[str, Any]]] = {}
    for row in pareto:
        m = int(row["M"])
        name = row["method"]
        require(name in methods, f"unknown Pareto method: {name}")
        by_m.setdefault(m, {})[name] = row
    require(set(by_m) == {30, 100, 300}, "unexpected graph sizes in Pareto frontier")

    frontier_checks = []
    for m in sorted(by_m):
        group = by_m[m]
        require(set(group) == methods, f"incomplete methods at M={m}")
        native = group["native_bidi"]
        reverse = group["reverse_index"]
        policy = group["policy"]
        metrics = ("B_on_max_all_sampled", "B_on_median", "B_on_p90")
        equal_online = all(native[k] == reverse[k] for k in metrics)
        require(equal_online, f"native predecessor and reverse-index frontiers differ at M={m}")
        require(reverse["B_off"] > 0 and reverse["R"] > 0, "reverse-index preparation/storage not charged")
        require(policy["B_off"] > reverse["B_off"], "all-pairs preprocessing not larger than reverse-index build")
        require(policy["R"] > reverse["R"], "all-pairs representation not larger than reverse index")
        require(
            policy["B_on_max_all_sampled"] < reverse["B_on_max_all_sampled"],
            f"all-pairs policy did not reduce maximum sampled online budget at M={m}",
        )
        frontier_checks.append({
            "M": m,
            "native_vs_reverse_index_online_metrics_equal": True,
            "reverse_index_B_off": reverse["B_off"],
            "reverse_index_R": reverse["R"],
            "reverse_index_B_on_max": reverse["B_on_max_all_sampled"],
            "policy_B_off": policy["B_off"],
            "policy_R": policy["R"],
            "policy_B_on_max": policy["B_on_max_all_sampled"],
            "policy_improves_online_budget": True,
        })

    source_paths = [
        contract_v01_path,
        contract_v02_path,
        instances_v01_path,
        instances_v02_path,
        ROOT / "experiments/machine-substrate-resource-contract-v0/validate_contract.py",
        ROOT / "experiments/machine-substrate-resource-contract-v0/validate_instances.py",
        ROOT / "experiments/machine-substrate-primitive-closure-v0/run_primitive_closure.py",
        ROOT / "experiments/machine-substrate-m2-representation-closure-v0/run_m2_representation_closure.py",
        ROOT / "experiments/machine-substrate-m2-exact-csr-closure-v0/run_exact_csr_closure.py",
        ROOT / "experiments/pareto-representation-closure-v0/run.py",
    ]
    result = {
        "schema": "machine.predecessor-frontier-integration.v0.1",
        "status": "PASS",
        "source_commit": os.environ.get("GITHUB_SHA", "LOCAL_UNPINNED"),
        "python": sys.version.split()[0],
        "contract": {
            "v0.1_validation": "PASS",
            "v0.2_schema_preserved": True,
            "v0.2_status": contract_v02["status"],
            "v0.1_instance_validation": "PASS",
            "v0.2_proposal_promoted": False,
            "sha256": {
                "CONTRACT-v0.1.json": sha256(contract_v01_path),
                "CONTRACT-v0.2.json": sha256(contract_v02_path),
                "CONTRACT-INSTANCES-v0.1.json": sha256(instances_v01_path),
                "CONTRACT-INSTANCES-v0.2-PROPOSED.json": sha256(instances_v02_path),
            },
        },
        "primitive_closure": {
            "status": primitive.get("status"),
            "systems": primitive["workload"]["systems"],
            "lookups": primitive["workload"]["lookups"],
            "basin_queries": primitive["workload"]["basin_queries"],
            "all_semantics_equal": pv["all_equal"],
            "forward_only_online_probes": primitive["aggregate"]["control_total_online_probes"],
            "generic_random_state_reads": primitive["aggregate"]["random_state_total_reads"],
            "dedicated_fiber_primitive_ops": primitive["aggregate"]["fiber_primitive_total_ops"],
            "aggregate_forward_to_random_state_ratio": primitive["aggregate"]["random_state_ratio_control_over_treatment"],
        },
        "dynamic_representation": {
            "status": mutable.get("status"),
            "cases": mutable["cases"],
            "updates": mutable["updates_total"],
            "semantic_invariant_failures": mutable["semantic_and_invariant_failures"],
            "generic_rw_work": mutable["aggregate_generic_rw_update_work"],
            "specialized_update_work_reference": mutable["aggregate_specialized_update_work"],
        },
        "exact_csr": {
            "status": exact_csr.get("status"),
            "cases": exact_csr["cases"],
            "updates": exact_csr["updates_total"],
            "semantic_structure_failures": exact_csr["semantic_and_structure_failures"],
            "generic_rw_maintenance_work": exact_csr["generic_rw_csr_maintenance_work"],
        },
        "pareto_frontier": {
            "status": "PASS",
            "sizes": sorted(by_m),
            "native_predecessor_vs_reverse_index": "SAMPLED ONLINE FRONTIERS IDENTICAL",
            "all_pairs_policy": "LOWER SAMPLED ONLINE BUDGET; HIGHER OFFLINE WORK AND STORAGE",
            "rows": frontier_checks,
        },
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in source_paths},
        "classification": {
            "absolute_computability_advantage": "NOT ESTABLISHED",
            "reverse_index_under_generic_random_access": "REPRESENTATION-LEVEL CLOSURE IN TESTED FINITE SETTINGS",
            "opaque_forward_without_relation_access": "ACCESS EXTENSION REQUIRED UNDER DECLARED MODEL",
            "resource_bounded_online_frontier_shift": "SUPPORTED BUT CONTRACT-AND-COST-MODEL BOUND",
            "canonical_repository_wide_substrate": "OPEN",
            "native_predecessor_access_cost_normalization": "OPEN",
            "production_profile_selection": "OPEN",
        },
        "limits": [
            "Finite deterministic fixtures only; no general closure theorem.",
            "The Pareto runner uses its declared structural tick model; unlike event classes are not converted to a scalar cost.",
            "The dedicated predecessor operation's physical latency/access cost is not normalized by this experiment.",
            "Local historical results are not substituted for this run's branch/commit-bound output.",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "schema": result["schema"],
        "status": result["status"],
        "source_commit": result["source_commit"],
        "contract_validation": "PASS",
        "primitive_closure": "PASS",
        "dynamic_representation": "PASS",
        "exact_csr": "PASS",
        "pareto_frontier": "PASS",
        "result_path": str(OUT.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
