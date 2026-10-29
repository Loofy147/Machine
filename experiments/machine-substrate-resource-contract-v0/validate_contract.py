"""Validate the frozen Machine Substrate Resource Contract schema.

This is intentionally a schema/disclosure gate, not a performance benchmark.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent

REQUIRED = {
    "A","T","D","tau","B_off","R_extra","B_on","M","K"
}

ALLOWED_A = {"A0_OPAQUE","A1_RANDOM_ACCESS","A2_SPECIALIZED_INDEX"}
ALLOWED_M = {"M0_STATIC","M1_BATCHED","M2_DYNAMIC"}
ALLOWED_TAU = {
    "T0_TARGET_BEFORE_PREPROCESSING",
    "T1_TARGET_AFTER_TARGET_OBLIVIOUS_PREPROCESSING",
    "T2_TARGET_BEFORE_TARGET_DEPENDENT_PREPROCESSING",
}


def validate_contract(c):
    errors = []
    if set(c.get("axes", {})) != REQUIRED:
        errors.append("axis set must be exactly A,T,D,tau,B_off,R_extra,B_on,M,K")

    for name, axis in c.get("axes", {}).items():
        if axis.get("required") is not True and name not in {"A","tau","M"}:
            errors.append(f"{name}: required declaration missing")

    if set(c.get("axes",{}).get("A",{}).get("allowed_profiles",[])) != ALLOWED_A:
        errors.append("A profiles mismatch")

    if set(c.get("axes",{}).get("M",{}).get("allowed",[])) != ALLOWED_M:
        errors.append("M profiles mismatch")

    if set(c.get("axes",{}).get("tau",{}).get("allowed",[])) != ALLOWED_TAU:
        errors.append("tau profiles mismatch")

    rules = c.get("classification_rules", {})
    if set(rules) != {"R","E","F","X"}:
        errors.append("classification rules must contain R,E,F,X")

    if c.get("normative_boundary") != (
        "The schema is canonical for disclosure/comparison, not for selecting one physical access profile."
    ):
        errors.append("normative boundary changed")

    return errors


def main():
    schema = json.loads((ROOT / "CONTRACT-v0.1.json").read_text())
    errors = validate_contract(schema)
    result = {
        "schema": "machine.substrate-resource-contract.v0.1.validation",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    (ROOT / "VALIDATION-V0.1.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
