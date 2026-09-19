#!/usr/bin/env python3
"""Evidence-integrity gate for the currently reproduced experiment set.

This gate verifies evidence artifacts, not scientific truth. It checks that
committed harnesses reproduce their recorded numerical/invariant claims.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence/manifest-v0.1.json"
CLAIMS = ROOT / "evidence/claims-v0.1.json"
OPEN_CLAIMS = ROOT / "evidence/open-claims-v0.1.json"

def fail(message: str) -> None:
    raise SystemExit(f"EVIDENCE-INTEGRITY-FAIL: {message}")

def run(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        fail(f"command failed: {' '.join(command)}")
    return proc

def git_show(commit: str, path: str) -> bytes:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        fail(f"cannot resolve provenance {commit}:{path}: {proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout

def verify_file_provenance(commit: str, path: str) -> None:
    current = (ROOT / path).read_bytes()
    historical = git_show(commit, path)
    if historical != current:
        fail(f"provenance drift: {path} differs from {commit}:{path}")

def verify_entry_provenance(entry: dict) -> None:
    required = ("code_commit", "result_commit", "code_path", "result_path")
    for key in required:
        if not entry.get(key):
            fail(f"manifest entry {entry.get('evidence_id')} missing {key}")
    verify_file_provenance(entry["code_commit"], entry["code_path"])
    verify_file_provenance(entry["result_commit"], entry["result_path"])

def parse_metric(output: str, name: str) -> float:
    match = re.search(rf"^{re.escape(name)}=([-+0-9.]+)$", output, re.MULTILINE)
    if not match:
        fail(f"missing {name} in harness output")
    return float(match.group(1))

def verify_pilot(entry: dict) -> None:
    proc = run([sys.executable, entry["code_path"]])
    expected = entry["expected"]
    for name, expected_value in expected.items():
        actual = parse_metric(proc.stdout, name)
        if actual != expected_value:
            fail(f"pilot {name}: expected {expected_value}, got {actual}")

    recorded = (ROOT / entry["result_path"]).read_text(encoding="utf-8")
    for fragment in (
        "**Status:** REPRODUCIBILITY-CORRECTED",
        "theta_D=0.462500",
        "theta_P=-1.000000",
        "theta_R=0.000000",
        "stale/mismatched result",
        "does **not** establish",
    ):
        if fragment not in recorded:
            fail(f"pilot record missing {fragment!r}")


def verify_record_fragments(path: Path, fragments: list[str], regexes: list[str] | None = None) -> None:
    if not path.is_file():
        fail(f'missing recorded result: {path}')
    recorded = path.read_text(encoding='utf-8')
    for fragment in fragments:
        if fragment not in recorded:
            fail(f'recorded result missing {fragment!r}')
    for pattern in regexes or []:
        if re.search(pattern, recorded, re.MULTILINE) is None:
            fail(f'recorded result missing pattern {pattern!r}')

def verify_error_source(entry: dict) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = str(Path(tmp) / "results.json")
        command = [
            sys.executable,
            entry["code_path"],
            "--episodes", "100",
            "--seed", "20260916",
            "--budget", "4",
            "--out", out,
        ]
        run(command)
        payload = json.loads(Path(out).read_text(encoding="utf-8"))

    aggregate = payload.get("aggregate")
    if not isinstance(aggregate, dict):
        fail("error-source result artifact missing aggregate")

    for mode, expected in entry["expected"].items():
        if mode not in aggregate:
            fail(f"error-source result missing mode {mode}")
        actual = aggregate[mode]
        for key, expected_value in expected.items():
            if actual.get(key) != expected_value:
                fail(
                    f"error-source {mode}.{key}: "
                    f"expected {expected_value}, got {actual.get(key)}"
                )

    verify_record_fragments(
        ROOT / entry["result_path"],
        [
            "| oracle | 1.00 | 1.00 | 0.80 | 1.00 | 1.00 |",
            "| probe | 1.00 | 1.00 | 2.00 | 1.00 | 1.00 |",
            "| adaptive | 1.00 | 1.00 | 2.22 | 1.00 | 1.00 |",
            "| random | 0.72 | 0.72 | 2.17 | 0.7725 | 0.7725 |",
            "| local | 0.67 | 0.67 | 2.30 | 0.82 | 0.82 |",
        ],
    )

def verify_target(entry: dict) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = str(Path(tmp) / "target.json")
        proc = run([
            sys.executable,
            entry["code_path"],
            "--m", "30",
            "--m", "300",
            "--m", "3000",
            "--queries", "200",
            "--look-depth", "2",
            "--out", out,
        ])
        rows = json.loads(proc.stdout)
        written = json.loads(Path(out).read_text(encoding="utf-8"))
        if rows != written:
            fail("target-oblivious stdout and output file differ")

    by_m = {}
    for row in rows:
        by_m.setdefault(row["M"], []).append(row)

    for m, mrows in by_m.items():
        base = next(r for r in mrows if r["h"] == 0)["strict_heldout"]
        for row in mrows:
            h = row["h"]
            if h <= m // 2:
                got = row["strict_heldout"]
                if got["hits"] != 0:
                    fail(f"target-oblivious M={m}, h={h}: heldout hits != 0")
                if got["success_rate"] != base["success_rate"]:
                    fail(f"target-oblivious M={m}, h={h}: heldout success drift")
                if got["avg_online_work"] != base["avg_online_work"]:
                    fail(f"target-oblivious M={m}, h={h}: heldout work drift")

    expected_rows = entry["expected_iid_summary_rounding"]["rows"]
    doc_patterns = []
    for m, h, expected_success, expected_work in expected_rows:
        row = next(r for r in rows if r["M"] == m and r["h"] == h)
        actual_success = round(row["iid"]["success_rate"], 3)
        actual_work = round(row["iid"]["avg_online_work"], 2)
        if actual_success != expected_success or actual_work != expected_work:
            fail(
                f"target-oblivious M={m}, h={h}: "
                f"expected rounded ({expected_success}, {expected_work}), "
                f"got ({actual_success}, {actual_work})"
            )
        doc_patterns.append(
            rf"\| {m} \| {h} \| .* \| .* \| {expected_success:.3f} \| {expected_work:.2f} \|"
        )
    verify_record_fragments(ROOT / entry["result_path"], [], doc_patterns)

def main() -> None:
    if not MANIFEST.is_file():
        fail(f"missing manifest: {MANIFEST}")
    if not CLAIMS.is_file():
        fail(f"missing claim registry: {CLAIMS}")
    if not OPEN_CLAIMS.is_file():
        fail(f"missing open-claim registry: {OPEN_CLAIMS}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
    open_claims = json.loads(OPEN_CLAIMS.read_text(encoding="utf-8"))
    if manifest.get("schema") != "machine.evidence-manifest.v0.2":
        fail("unexpected evidence manifest schema")

    entries = manifest.get("entries", [])
    claim_ids = {c.get("claim_id") for c in claims.get("claims", [])}
    if claims.get("schema") != "machine.claim-registry.v0.1":
        fail("unexpected claim registry schema")
    if len(claim_ids) != 3 or None in claim_ids:
        fail("claim registry must contain exactly three initial claim IDs")
    if len(entries) != 3:
        fail(f"expected 3 verified entries, found {len(entries)}")

    open_rows = open_claims.get("claims", [])
    open_ids = [row.get("claim_id") for row in open_rows]
    if open_claims.get("schema") != "machine.open-claim-registry.v0.1":
        fail("unexpected open-claim registry schema")
    if len(open_ids) != len(set(open_ids)) or None in open_ids:
        fail("open-claim registry claim_id values must be unique and non-null")
    if set(open_ids) & claim_ids:
        fail("verified and open claim registries must not reuse claim_id values")
    for row in open_rows:
        if row.get("status") != "OPEN":
            fail(f"open claim {row.get("claim_id")} must remain OPEN")
        if row.get("evidence_status") != "UNVERIFIED_PACKAGE":
            fail(f"open claim {row.get("claim_id")} must remain UNVERIFIED_PACKAGE")
        if not row.get("documented_source"):
            fail(f"open claim {row.get("claim_id")} missing documented_source")
        if not row.get("source_branch") or not row.get("source_commit"):
            fail(f"open claim {row.get("claim_id")} missing source provenance")
        if not row.get("next_discriminating_test"):
            fail(f"open claim {row.get("claim_id")} missing next_discriminating_test")

    evidence_ids = [e.get("evidence_id") for e in entries]
    if len(evidence_ids) != len(set(evidence_ids)) or None in evidence_ids:
        fail("manifest evidence_id values must be unique and non-null")
    if len(claim_ids) != len(claims.get("claims", [])):
        fail("claim registry claim_id values must be unique and non-null")

    manifest_by_id = {e["evidence_id"]: e for e in entries}
    for claim in claims.get("claims", []):
        linked = claim.get("evidence_ids", [])
        if not linked:
            fail(f"claim {claim.get('claim_id')} has no evidence_ids")
        for evidence_id in linked:
            if evidence_id not in manifest_by_id:
                fail(f"claim {claim.get('claim_id')} references unknown evidence: {evidence_id}")

    for entry in entries:
        verify_entry_provenance(entry)
        if entry.get("claim_id") not in claim_ids:
            fail(f"manifest references unknown claim: {entry.get('claim_id')}")
        if entry.get("status") != "REPRODUCIBILITY_VERIFIED":
            fail(f"entry {entry.get('evidence_id')} is not marked reproducibility verified")
        if entry["experiment"] == "confirmatory-pilot-v0.1":
            verify_pilot(entry)
        elif entry["experiment"] == "error-source-localization-v0":
            verify_error_source(entry)
        elif entry["experiment"] == "target-oblivious-frontier-v0":
            verify_target(entry)
        else:
            fail(f"unknown experiment in manifest: {entry['experiment']}")

    print("EVIDENCE-INTEGRITY-PASS")
    print("verified experiments: confirmatory-pilot-v0.1, error-source-localization-v0, target-oblivious-frontier-v0")
    print("scientific interpretation remains bounded by each experiment's declared boundary")

if __name__ == "__main__":
    main()
