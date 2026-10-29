"""Reproduce v0.4's exact n=3 suite without overwriting historical results."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
SOURCE_SHA256 = {
    "core.py": "0f4129bf2f80682da0f90f85144fcb58dd74493bf47f72f005ba99031dc38673",
    "run_v0_4.py": "8fb20db1f8a3bee9c127209e0a32412e10386c625e81b1ceeb98677a5bfa3c63",
    "RESULTS-V0.4.json": "39dba82d7c66b606f005aa78d8ef00174d6be2a2a271012d32c61c359dc7b253",
    "canonical_postedge_regression_v4.json": "23929aa9c6a36270b2c5e0a6d310ea4fe69add954c7efbc9008985e44c5304cc",
}
EXPECTED_N3 = {
    "graph_states": 4096,
    "solvable_graphs": 3648,
    "schedule_runs": 233472,
    "active_guard_failures": 0,
    "naive_finite_failures": 3840,
    "mx_cover_failures": 0,
    "konig_failures": 0,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, help="optional path for the reproduction receipt")
    args = parser.parse_args()

    observed_hashes = {name: sha256(ROOT / name) for name in SOURCE_SHA256}
    if observed_hashes != SOURCE_SHA256:
        raise SystemExit(
            "SOURCE-HASH-MISMATCH: " +
            json.dumps({"expected": SOURCE_SHA256, "actual": observed_hashes}, sort_keys=True)
        )

    historical = json.loads((ROOT / "RESULTS-V0.4.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="machine-v04-n3-") as directory:
        temp_root = Path(directory)
        shutil.copy2(ROOT / "core.py", temp_root / "core.py")
        shutil.copy2(ROOT / "run_v0_4.py", temp_root / "run_v0_4.py")
        completed = subprocess.run(
            [sys.executable, "run_v0_4.py", "--experiment", "n3"],
            cwd=temp_root,
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
        )
        if completed.returncode != 0:
            raise SystemExit(
                "V04-N3-RUN-FAILED\nSTDOUT:\n" + completed.stdout +
                "\nSTDERR:\n" + completed.stderr
            )
        regenerated = json.loads(
            (temp_root / "RESULTS-V0.4.json").read_text(encoding="utf-8")
        )
        stdout_result = json.loads(completed.stdout)
        if stdout_result != regenerated:
            raise SystemExit("V04-N3-OUTPUT-FILE-AND-STDOUT-MISMATCH")

    actual_n3 = regenerated.get("weighted_n3")
    if actual_n3 != EXPECTED_N3:
        raise SystemExit(
            "V04-N3-EXPECTED-METRIC-MISMATCH: " +
            json.dumps({"expected": EXPECTED_N3, "actual": actual_n3}, sort_keys=True)
        )
    if actual_n3 != historical.get("weighted_n3"):
        raise SystemExit(
            "V04-N3-HISTORICAL-RESULT-MISMATCH: " +
            json.dumps({
                "historical": historical.get("weighted_n3"),
                "reproduced": actual_n3,
            }, sort_keys=True)
        )

    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()
    receipt = {
        "schema": "machine.bidirectional-grounded-v0.4-reproduction.v0.1",
        "status": "PASS",
        "source_commit": source_commit,
        "github_event_sha": os.environ.get("GITHUB_SHA", "LOCAL_UNSET"),
        "checkout_ref": os.environ.get("GITHUB_REF", "LOCAL_UNSET"),
        "python": sys.version.split()[0],
        "command": "python run_v0_4.py --experiment n3 (isolated temporary directory)",
        "source_sha256": observed_hashes,
        "source_pack_sha256": "68e065bff5ca06aaf180ebf062088e98764358454c6e3c2accfa291025b6b315",
        "matched_historical_weighted_n3": True,
        "result": actual_n3,
        "interpretation_limit": (
            "Exact source restoration and n=3 reproduction only. The full all-experiments run, "
            "including exhaustive weighted n=4, random n=4, and matched simple/multigraph runs, "
            "is not asserted by this receipt."
        ),
    }
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
