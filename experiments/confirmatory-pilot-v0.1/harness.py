#!/usr/bin/env python3
"""Small deterministic pilot for the confirmatory transfer contract.

This is an EXPLORATORY CONTRACT TEST, not confirmatory evidence.
It checks that a diagnostic artifact can change D without directly changing R.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

SEED = 20260916
N_SOURCE = 40
N_TARGET = 80


@dataclass(frozen=True)
class Case:
    fault: str
    context: int
    context_boundary: int = 1


def make_cases(n: int, fault: str, rng: random.Random) -> list[Case]:
    return [Case(fault=fault, context=rng.randrange(2)) for _ in range(n)]


def learn_transfer_artifact(source_cases: list[Case]) -> dict[str, int]:
    """Learn one diagnostic probe preference from source-class episodes.

    The artifact is intentionally restricted to diagnosis/probing semantics.
    It contains no target label, target outcomes, or repair candidates.
    """
    boundary_rate = sum(c.context_boundary for c in source_cases) / len(source_cases)
    return {"context_boundary_probe_priority": int(boundary_rate > 0.5)}


def diagnose(case: Case, artifact: dict[str, int] | None, rng: random.Random) -> tuple[bool, int]:
    if artifact and artifact["context_boundary_probe_priority"]:
        # One probe, selected from the transferred diagnostic artifact.
        return case.fault == "context-discrimination-fault", 1

    # Baseline: same S2 interface/budget, but no transferred diagnostic artifact.
    # The toy baseline has a pre-declared 55% probability of choosing the useful
    # causal probe after spending two probe units.
    return (
        case.fault == "context-discrimination-fault" and rng.random() < 0.55,
        2,
    )


def repair_cost(case: Case) -> int:
    # Identical repair controller for both arms. The transfer artifact cannot
    # modify repair search in this pilot.
    return 8 if case.fault == "context-discrimination-fault" else 7


def evaluate(target: list[Case], artifact: dict[str, int] | None, rng: random.Random) -> dict[str, float]:
    correct = []
    probe_cost = []
    repair_costs = []
    for case in target:
        y, cp = diagnose(case, artifact, rng)
        correct.append(int(y))
        probe_cost.append(cp)
        repair_costs.append(repair_cost(case))
    return {
        "diagnostic_success": sum(correct) / len(correct),
        "mean_probe_cost": sum(probe_cost) / len(probe_cost),
        "mean_repair_cost": sum(repair_costs) / len(repair_costs),
    }


def main() -> None:
    rng = random.Random(SEED)
    source = make_cases(N_SOURCE, "persistence/decay-fault", rng)
    target = make_cases(N_TARGET, "context-discrimination-fault", rng)
    artifact = learn_transfer_artifact(source)

    baseline_rng = random.Random(SEED + 1)
    transfer_rng = random.Random(SEED + 2)
    baseline = evaluate(target, None, baseline_rng)
    transfer = evaluate(target, artifact, transfer_rng)

    theta_d = transfer["diagnostic_success"] - baseline["diagnostic_success"]
    theta_p = transfer["mean_probe_cost"] - baseline["mean_probe_cost"]
    theta_r = transfer["mean_repair_cost"] - baseline["mean_repair_cost"]

    print(f"seed={SEED}")
    print(f"source_n={N_SOURCE} target_n={N_TARGET}")
    print(f"baseline={baseline}")
    print(f"transfer={transfer}")
    print(f"theta_D={theta_d:.6f}")
    print(f"theta_P={theta_p:.6f}")
    print(f"theta_R={theta_r:.6f}")


if __name__ == "__main__":
    main()
