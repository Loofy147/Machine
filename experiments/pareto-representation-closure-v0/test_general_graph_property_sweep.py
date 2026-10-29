import unittest
from collections import Counter

from general_graph_validation import (
    build_declared_fiber_rows,
    build_reference_reverse_index,
    generated_sweep_fixtures,
    validate_generated_sweep,
    DeclaredFiberProvider,
    backward_reachable,
    backward_reachable_reference,
)


class GeneralGraphPropertySweepTests(unittest.TestCase):
    def test_sweep_is_deterministic_and_covers_density_families(self):
        first = generated_sweep_fixtures(seeds_per_family=4)
        second = generated_sweep_fixtures(seeds_per_family=4)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 12)
        self.assertEqual({g.family for g in first}, {"sparse", "medium", "dense"})

    def test_each_generated_fixture_has_required_adversarial_structure(self):
        for graph in generated_sweep_fixtures(seeds_per_family=4):
            with self.subTest(graph=graph.name):
                labels = [edge.label for edge in graph.edges]
                self.assertEqual(len(labels), len(set(labels)))
                parallel = [
                    edge for edge in graph.edges
                    if edge.source == 0 and edge.target == 1
                ]
                self.assertGreaterEqual(len(parallel), 2)
                self.assertEqual(
                    len({edge.label for edge in parallel}),
                    len(parallel),
                )
                self.assertTrue(
                    any(edge.source == edge.target for edge in graph.edges)
                )
                zero_indegree = graph.state_count - 2
                isolated = graph.state_count - 1
                self.assertFalse(
                    any(edge.target == zero_indegree for edge in graph.edges)
                )
                self.assertFalse(
                    any(
                        edge.source == isolated or edge.target == isolated
                        for edge in graph.edges
                    )
                )
                self.assertTrue(
                    any(edge.source == zero_indegree for edge in graph.edges)
                )

    def test_all_sweep_fibers_and_reachability_match_independent_reference(self):
        for graph in generated_sweep_fixtures(seeds_per_family=4):
            reference = build_reference_reverse_index(graph)
            provider = DeclaredFiberProvider(build_declared_fiber_rows(graph))
            for target in range(graph.state_count):
                with self.subTest(graph=graph.name, target=target):
                    self.assertEqual(
                        Counter(provider.predecessors(target)),
                        Counter(reference[target]),
                    )
                    self.assertEqual(
                        backward_reachable(provider, target),
                        backward_reachable_reference(reference, target),
                    )

    def test_report_preserves_scope_and_counts_every_target(self):
        report = validate_generated_sweep(seeds_per_family=4)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["fixture_count"], 12)
        self.assertEqual(report["family_counts"], {
            "dense": 4,
            "medium": 4,
            "sparse": 4,
        })
        self.assertEqual(
            report["target_fibers_checked"], report["state_count_total"]
        )
        self.assertEqual(
            report["backward_reachability_queries_checked"],
            report["state_count_total"],
        )
        self.assertEqual(report["total_semantic_mismatches"], 0)
        self.assertFalse(report["query_path_builds_reverse_index"])
        self.assertEqual(
            report["arbitrary_graph_native_fiber_implementation"],
            "NOT CLAIMED",
        )
        self.assertIn("symbolic", report["physical_access_cost"].lower())


if __name__ == "__main__":
    unittest.main()
