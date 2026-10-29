from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from core import (
    all_policies,
    bidirectional_dijkstra,
    build_must_expand_graph,
    dijkstra,
    interruptible_bidirectional_dijkstra,
    make_smaller_frontier,
    max_bipartite_matching,
    minimum_vertex_cover_from_matching,
    random_weighted_digraph,
)

ROOT = Path(__file__).resolve().parent
EXPECTED_SHA256 = {
    "core.py": "0f4129bf2f80682da0f90f85144fcb58dd74493bf47f72f005ba99031dc38673",
    "run_v0_4.py": "fda87949728e25cda2073eafd6f7c4e2984af714e0c98c7c93fcfec8e2ce48f6",
    "RESULTS-V0.4.json": "39dba82d7c66b606f005aa78d8ef00174d6be2a2a271012d32c61c359dc7b253",
    "canonical_postedge_regression_v4.json": "91b7edab17681d7757cfab9edfa8199191c6ae488f1c71e728c6713c439f3f7c",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fixed_policy(sequence: str):
    index = [0]

    def choose(_nf: int, _nb: int, _tf: int, _tb: int) -> str:
        value = sequence[index[0]]
        index[0] += 1
        return value

    return choose


class V04ReproducibilityTests(unittest.TestCase):
    def test_recovered_source_and_historical_artifact_hashes(self):
        for name, expected in EXPECTED_SHA256.items():
            with self.subTest(path=name):
                self.assertEqual(sha256(ROOT / name), expected)

    def test_canonical_post_edge_counterexample(self):
        fixture = json.loads(
            (ROOT / "canonical_postedge_regression_v4.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(fixture["semantics"], "post-edge-only")
        self.assertFalse(fixture["check_before_first_edge"])
        self.assertEqual(fixture["policy_schedule"], "FBFFFF")

        adjacency = {node: [] for node in range(fixture["n"])}
        for source, target, weight in fixture["edges"]:
            adjacency[source].append((target, weight))
        reverse = {node: [] for node in adjacency}
        for source, edges in adjacency.items():
            for target, weight in edges:
                reverse[target].append((source, weight))

        optimum = dijkstra(adjacency, fixture["s"])[fixture["t"]]
        active = interruptible_bidirectional_dijkstra(
            adjacency,
            reverse,
            fixture["s"],
            fixture["t"],
            fixed_policy(fixture["policy_schedule"]),
            active_guard=True,
            check_before_first_edge=False,
        )
        naive = interruptible_bidirectional_dijkstra(
            adjacency,
            reverse,
            fixture["s"],
            fixture["t"],
            fixed_policy(fixture["policy_schedule"]),
            active_guard=False,
            check_before_first_edge=False,
        )

        self.assertEqual(optimum, fixture["C_star"])
        self.assertEqual(active.mu, fixture["active_mu"])
        self.assertEqual(naive.mu, fixture["naive_mu"])
        self.assertTrue(active.terminated)
        self.assertTrue(naive.terminated)
        self.assertEqual(active.mu, optimum)
        self.assertGreater(naive.mu, optimum)

    def test_exact_historical_core_api_is_available(self):
        self.assertTrue(all(callable(function) for function in (
            all_policies,
            bidirectional_dijkstra,
            build_must_expand_graph,
            dijkstra,
            interruptible_bidirectional_dijkstra,
            make_smaller_frontier,
            max_bipartite_matching,
            minimum_vertex_cover_from_matching,
            random_weighted_digraph,
        )))


if __name__ == "__main__":
    unittest.main()
