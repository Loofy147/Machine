"""Generate source-bound evidence for the general-graph property sweep."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from general_graph_validation import validate_generated_sweep

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent.parent
OUTPUT = ROOT / "GENERAL-GRAPH-PREDECESSOR-PROPERTY-SWEEP-V0.1.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds-per-family", type=int, default=40)
    args = parser.parse_args()

    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True,
    ).strip()
    result = validate_generated_sweep(args.seeds_per_family)
    result.update({
        "source_commit": source_commit,
        "github_event_sha": os.environ.get("GITHUB_SHA", "LOCAL_UNSET"),
        "checkout_ref": os.environ.get("GITHUB_REF", "LOCAL_UNSET"),
        "python": sys.version.split()[0],
        "source_sha256": {
            "general_graph_validation.py": sha256(ROOT / "general_graph_validation.py"),
            "test_general_graph_property_sweep.py": sha256(
                ROOT / "test_general_graph_property_sweep.py"
            ),
            "run_general_graph_property_sweep.py": sha256(Path(__file__)),
        },
    })
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "source_commit": source_commit,
        "fixture_count": result["fixture_count"],
        "family_counts": result["family_counts"],
        "state_count_total": result["state_count_total"],
        "edge_count_total": result["edge_count_total"],
        "target_fibers_checked": result["target_fibers_checked"],
        "backward_reachability_queries_checked": result[
            "backward_reachability_queries_checked"
        ],
        "total_semantic_mismatches": result["total_semantic_mismatches"],
        "result_path": str(OUTPUT.relative_to(REPO_ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
