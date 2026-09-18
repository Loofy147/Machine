#!/usr/bin/env python3
"""Evidence-integrity gate for the current reproducibility-corrected pilot.

This verifier does not establish the scientific hypothesis. It verifies that:
1. the committed harness executes successfully;
2. its declared output matches the recorded evidence;
3. the recorded result explicitly preserves the interpretation boundary.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "experiments/confirmatory-pilot-v0.1/harness.py"
RESULTS = ROOT / "experiments/confirmatory-pilot-v0.1/RESULTS-V0.md"

EXPECTED = {
    "theta_D": 0.462500,
    "theta_P": -1.000000,
    "theta_R": 0.000000,
}

def fail(message: str) -> None:
    raise SystemExit(f"EVIDENCE-INTEGRITY-FAIL: {message}")

def parse_metric(output: str, name: str) -> float:
    match = re.search(rf"^{re.escape(name)}=([-+0-9.]+)$", output, re.MULTILINE)
    if not match:
        fail(f"missing {name} in harness output")
    return float(match.group(1))

def main() -> None:
    if not HARNESS.is_file():
        fail(f"missing harness: {HARNESS}")
    if not RESULTS.is_file():
        fail(f"missing result record: {RESULTS}")

    proc = subprocess.run(
        [sys.executable, str(HARNESS)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        fail(f"harness exited with code {proc.returncode}")

    for name, expected in EXPECTED.items():
        actual = parse_metric(proc.stdout, name)
        if actual != expected:
            fail(f"{name}: expected {expected:.6f}, got {actual:.6f}")

    recorded = RESULTS.read_text(encoding="utf-8")
    required_fragments = (
        "**Status:** REPRODUCIBILITY-CORRECTED",
        "theta_D=0.462500",
        "theta_P=-1.000000",
        "theta_R=0.000000",
        "stale/mismatched result",
        "does **not** establish",
    )
    for fragment in required_fragments:
        if fragment not in recorded:
            fail(f"recorded evidence missing required fragment: {fragment!r}")

    print("EVIDENCE-INTEGRITY-PASS")
    print("confirmatory-pilot-v0.1: harness result matches recorded evidence")
    print("scientific status: contract-test only; transferable learning remains unestablished")

if __name__ == "__main__":
    main()
