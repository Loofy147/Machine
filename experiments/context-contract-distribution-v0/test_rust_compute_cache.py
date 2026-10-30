import time
import unittest

from context_contract_distribution import (
    ContractContext,
    build_compatibility_graph,
)
from rust_compute_cache import (
    RustCompatibilityCacheClient,
    graph_signature,
)


def _fixture():
    return [
        ContractContext(
            "a-consumer",
            {"region": "north", "active": True},
            {"deadline": None, "budget": "20k"},
            utility=5,
        ),
        ContractContext(
            "b-provider",
            {"region": "north", "active": True, "deadline": "friday", "budget": "10k"},
            {"owner": None},
            utility=7,
        ),
        ContractContext(
            "c-owner",
            {"region": "north", "active": True, "owner": "team-a"},
            {},
            utility=3,
        ),
        ContractContext(
            "d-conflict",
            {"region": "south", "active": True, "deadline": "friday"},
            {"owner": None},
            utility=50,
        ),
        ContractContext(
            "e-type-conflict",
            {"region": "north", "active": 1, "deadline": "friday"},
            {"owner": None},
            utility=2,
        ),
    ]


class RustComputeCacheTests(unittest.TestCase):
    def test_rust_graph_matches_python_graph_and_reuses_pairs_across_utility_changes(self):
        contexts = _fixture()
        python_graph = build_compatibility_graph(contexts, {})
        with RustCompatibilityCacheClient() as cache:
            rust_graph, cold = cache.build_graph(contexts)
            self.assertEqual(graph_signature(rust_graph), graph_signature(python_graph))
            self.assertEqual(cold["pair_lookups"], len(contexts) * (len(contexts) - 1) // 2)
            self.assertEqual(cold["cache_misses"], cold["pair_lookups"])
            self.assertEqual(cold["cache_hits"], 0)

            changed_utility = [
                ContractContext(
                    item.context_id,
                    item.facts,
                    item.needs,
                    utility=item.value * 10,
                )
                for item in contexts
            ]
            rust_changed, warm = cache.build_graph(changed_utility)
            python_changed = build_compatibility_graph(changed_utility, {})
            self.assertEqual(graph_signature(rust_changed), graph_signature(python_changed))
            self.assertTrue(warm["graph_cache_hit"])
            self.assertEqual(warm["cache_misses"], 0)
            self.assertEqual(warm["pair_lookups"], 0)
            self.assertNotEqual(
                rust_graph["a-consumer"]["b-provider"]["weight"],
                rust_changed["a-consumer"]["b-provider"]["weight"],
            )

    def test_ttl_expiry_invalidates_graph_and_pair_cache_entries(self):
        contexts = _fixture()
        with RustCompatibilityCacheClient(
            environment={"MACHINE_CACHE_TTL_MS": "80"}
        ) as cache:
            first_graph, first = cache.build_graph(contexts)
            self.assertEqual(first["graph_cache_misses"], 1)

            warm_graph, warm = cache.build_graph(contexts)
            self.assertEqual(graph_signature(warm_graph), graph_signature(first_graph))
            self.assertTrue(warm["graph_cache_hit"])

            time.sleep(0.18)
            expired_graph, expired = cache.build_graph(contexts)
            self.assertEqual(graph_signature(expired_graph), graph_signature(first_graph))
            self.assertFalse(expired["graph_cache_hit"])
            self.assertEqual(expired["graph_cache_misses"], 1)
            self.assertEqual(expired["cache_misses"], expired["pair_lookups"])
            self.assertGreater(expired["cache_misses"], 0)

    def test_graph_key_is_input_order_invariant_and_utility_independent(self):
        contexts = _fixture()
        with RustCompatibilityCacheClient() as cache:
            first_graph, first = cache.build_graph(contexts)
            changed_utility_and_order = [
                ContractContext(
                    item.context_id,
                    item.facts,
                    item.needs,
                    utility=item.value + 100,
                )
                for item in reversed(contexts)
            ]
            second_graph, second = cache.build_graph(changed_utility_and_order)

        self.assertEqual(graph_signature(first_graph), graph_signature(second_graph))
        self.assertFalse(first["graph_cache_hit"])
        self.assertTrue(second["graph_cache_hit"])
        self.assertEqual(second["pair_lookups"], 0)

    def test_anchor_filter_is_applied_before_rust_pair_work(self):
        contexts = _fixture()
        anchor = {"region": "north"}
        eligible = [
            item for item in contexts
            if all(key not in anchor or item.facts[key] == value for key, value in anchor.items())
        ]
        reference = build_compatibility_graph(contexts, anchor)
        with RustCompatibilityCacheClient() as cache:
            rust_graph, metrics = cache.build_graph(eligible)
        self.assertEqual(set(rust_graph.nodes), set(reference.nodes))
        self.assertEqual(graph_signature(rust_graph), graph_signature(reference))
        self.assertEqual(metrics["contexts"], len(eligible))

    def test_changed_pair_facts_or_needs_cause_cache_misses(self):
        contexts = _fixture()
        with RustCompatibilityCacheClient() as cache:
            _, first = cache.build_graph(contexts)
            modified = list(contexts)
            modified[1] = ContractContext(
                "b-provider",
                {"region": "north", "active": True, "deadline": "saturday", "budget": "10k"},
                {"owner": None},
                utility=7,
            )
            _, changed = cache.build_graph(modified)
        self.assertGreater(changed["cache_misses"], 0)
        self.assertLess(changed["cache_misses"], first["pair_lookups"])

    def test_negative_results_are_reused(self):
        contexts = [
            ContractContext("a", {"region": "north"}, {}),
            ContractContext("b", {"region": "south"}, {}),
        ]
        with RustCompatibilityCacheClient() as cache:
            first_graph, first = cache.build_graph(contexts)
            second_graph, second = cache.build_graph(contexts)
        self.assertEqual(first_graph.number_of_edges(), 0)
        self.assertEqual(second_graph.number_of_edges(), 0)
        self.assertEqual(first["cache_misses"], 1)
        self.assertEqual(second["cache_hits"], 0)
        self.assertEqual(second["cache_misses"], 0)
        self.assertTrue(second["graph_cache_hit"])


if __name__ == "__main__":
    unittest.main()
