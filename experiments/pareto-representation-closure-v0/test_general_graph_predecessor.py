import unittest
from collections import Counter
from unittest.mock import patch

from general_graph_validation import (
    DeclaredFiberProvider,
    adversarial_fixture,
    backward_reachable,
    backward_reachable_reference,
    build_declared_fiber_rows,
    build_reference_reverse_index,
    fixtures,
    generated_fixture,
    validate_suite,
)


class GeneralGraphPredecessorTests(unittest.TestCase):
    def test_fixture_set_contains_handcrafted_and_seeded_graphs(self):
        rows = fixtures()
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0].name, "handcrafted-adversarial")
        self.assertEqual([row.name for row in rows[1:]], [
            "generated-seed-11-n-7",
            "generated-seed-29-n-11",
            "generated-seed-101-n-17",
        ])

    def test_generated_fixtures_are_reproducible(self):
        self.assertEqual(generated_fixture(29, 11), generated_fixture(29, 11))

    def test_every_fiber_matches_reference_as_edge_identity_multiset(self):
        for graph in fixtures():
            reference = build_reference_reverse_index(graph)
            provider = DeclaredFiberProvider(build_declared_fiber_rows(graph))
            for target in range(graph.state_count):
                with self.subTest(graph=graph.name, target=target):
                    self.assertEqual(
                        Counter(provider.predecessors(target)),
                        Counter(reference[target]),
                    )

    def test_parallel_labeled_transitions_are_not_collapsed(self):
        provider = DeclaredFiberProvider(
            build_declared_fiber_rows(adversarial_fixture())
        )
        parallel = [
            (source, label)
            for source, label in provider.predecessors(1)
            if source == 0
        ]
        self.assertEqual(len(parallel), 2)
        self.assertEqual({label for _, label in parallel}, {
            "parallel-alpha", "parallel-beta"
        })

    def test_backward_reachability_matches_reference_for_all_targets(self):
        for graph in fixtures():
            reference = build_reference_reverse_index(graph)
            provider = DeclaredFiberProvider(build_declared_fiber_rows(graph))
            for target in range(graph.state_count):
                with self.subTest(graph=graph.name, target=target):
                    self.assertEqual(
                        backward_reachable(provider, target),
                        backward_reachable_reference(reference, target),
                    )

    def test_query_path_never_builds_reference_reverse_index(self):
        provider = DeclaredFiberProvider(
            build_declared_fiber_rows(adversarial_fixture())
        )
        with patch(
            "general_graph_validation.build_reference_reverse_index",
            side_effect=AssertionError("query attempted index construction"),
        ):
            self.assertEqual(
                backward_reachable(provider, 3), {0, 2, 3, 4, 5, 6, 7}
            )

    def test_zero_indegree_isolated_and_zero_outdegree_states(self):
        graph = adversarial_fixture()
        reference = build_reference_reverse_index(graph)
        provider = DeclaredFiberProvider(build_declared_fiber_rows(graph))
        self.assertEqual(backward_reachable(provider, 7), {7})
        self.assertEqual(backward_reachable(provider, 8), {8})
        self.assertEqual(backward_reachable(provider, 9), {5, 9})
        self.assertEqual(reference[7], ())
        self.assertEqual(reference[8], ())
        self.assertEqual(
            set(reference[1]),
            {(0, "parallel-alpha"), (0, "parallel-beta")},
        )

    def test_self_loops_terminate_and_remain_in_fiber(self):
        provider = DeclaredFiberProvider(
            build_declared_fiber_rows(adversarial_fixture())
        )
        self.assertEqual(provider.predecessors(0).count((0, "loop-at-0")), 1)
        self.assertEqual(backward_reachable(provider, 0), {0})
        self.assertEqual(provider.predecessors(9).count((9, "loop-at-9")), 1)

    def test_invalid_targets_are_rejected(self):
        provider = DeclaredFiberProvider(
            build_declared_fiber_rows(adversarial_fixture())
        )
        for target in (-1, provider.state_count, True, "0"):
            with self.subTest(target=target):
                with self.assertRaises(ValueError):
                    provider.predecessors(target)

    def test_provider_counters_charge_lookup_and_each_returned_entry(self):
        provider = DeclaredFiberProvider(
            build_declared_fiber_rows(adversarial_fixture())
        )
        entries = provider.predecessors(1)
        self.assertEqual(len(entries), 2)
        self.assertEqual(provider.lookup_calls, 1)
        self.assertEqual(provider.returned_entries, 2)

    def test_report_preserves_finite_scope_and_no_universal_claim(self):
        report = validate_suite()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["fixture_count"], 4)
        self.assertEqual(report["state_count_total"], 45)
        self.assertEqual(report["target_fibers_checked"], 45)
        self.assertEqual(report["backward_reachability_queries_checked"], 45)
        self.assertEqual(report["total_semantic_mismatches"], 0)
        self.assertFalse(report["query_path_builds_reverse_index"])
        self.assertEqual(
            report["arbitrary_graph_native_fiber_implementation"], "NOT CLAIMED"
        )
        self.assertGreaterEqual(report["disconnected_fixture_count"], 1)


if __name__ == "__main__":
    unittest.main()
