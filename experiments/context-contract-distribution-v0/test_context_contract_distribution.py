import random
import unittest
from itertools import combinations

import networkx as nx

from context_contract_distribution import (
    ContractContext,
    build_compatibility_graph,
    compare_plans,
    plan_distribution,
)


def _swarm_family(graph):
    family = {frozenset()}
    node_ids = sorted(graph.nodes)
    for size in range(2, len(node_ids) + 1, 2):
        for subset in combinations(node_ids, size):
            matching = nx.max_weight_matching(graph.subgraph(subset), maxcardinality=True)
            if 2 * len(matching) == size:
                family.add(frozenset(subset))
    return family


def _exchange_holds(family):
    for first in family:
        for second in family:
            difference = first ^ second
            for x in difference:
                if not any(frozenset(first ^ {x, y}) in family for y in difference):
                    return False
    return True


def _pair_move_distance(family, start, target):
    current = frozenset(start)
    target = frozenset(target)
    moves = 0
    while current != target:
        difference = sorted(current ^ target)
        found = None
        for i, x in enumerate(difference):
            for y in difference[i + 1:]:
                candidate = frozenset(current ^ {x, y})
                if candidate in family:
                    found = candidate
                    break
            if found is not None:
                break
        if found is None:
            return None
        current = found
        moves += 1
    return moves


def _random_contexts(rng, count, key_count=9):
    keys = [f"k{i}" for i in range(key_count)]
    contexts = []
    for i in range(count):
        chosen = rng.sample(keys, rng.randint(2, min(5, key_count)))
        facts = {key: rng.choice(["0", "1"]) for key in chosen}
        candidates = [key for key in keys if key not in facts]
        needs = {key: rng.choice([None, "0", "1"]) for key in rng.sample(candidates, rng.randint(1, min(2, len(candidates))))}
        contexts.append(ContractContext(f"c{i}", facts, needs, utility=rng.randint(0, 5)))
    return contexts


class ContractDistributionTests(unittest.TestCase):
    def test_anchor_excludes_conflicting_contexts_and_reports_conflict(self):
        contexts = [
            ContractContext("alpha", {"project": "alpha", "goal": "ship"}, {"deadline"}),
            ContractContext("calendar", {"project": "alpha", "deadline": "fri"}, {"goal": "ship"}),
            ContractContext("legacy", {"project": "beta", "deadline": "mon"}, {"goal": "ship"}),
        ]
        plan = plan_distribution(contexts, {"project": "alpha"})

        self.assertEqual(plan.eligible_contexts, ("alpha", "calendar"))
        self.assertEqual([x.context_id for x in plan.anchor_exclusions], ["legacy"])
        self.assertEqual(plan.anchor_exclusions[0].conflicts["project"], ("beta", "alpha"))

    def test_need_value_is_enforced_and_presence_only_remains_supported(self):
        consumer_value = ContractContext("value-consumer", {}, {"budget": "20k"}, utility=4)
        provider_wrong = ContractContext("wrong-provider", {"budget": "10k"}, {}, utility=4)
        plan_wrong = plan_distribution([consumer_value, provider_wrong], {})
        self.assertEqual(plan_wrong.selected_contexts, ())

        consumer_presence = ContractContext("presence-consumer", {}, {"budget"}, utility=4)
        plan_presence = plan_distribution([consumer_presence, provider_wrong], {})
        self.assertEqual(set(plan_presence.selected_contexts), {"presence-consumer", "wrong-provider"})
        pair = plan_presence.pairs[0]
        self.assertEqual(pair.services[0].consumer, "presence-consumer")
        self.assertEqual(pair.services[0].provider, "wrong-provider")

    def test_conflicting_facts_prevent_pairing_even_when_a_need_matches(self):
        a = ContractContext("a", {"region": "eu"}, {"rules": "gdpr"})
        b = ContractContext("b", {"region": "us", "rules": "gdpr"}, {})
        plan = plan_distribution([a, b], {})
        self.assertEqual(plan.selected_contexts, ())
        self.assertEqual(plan.unmatched_eligible, ("a", "b"))

    def test_exact_matching_returns_only_paired_contexts(self):
        contexts = [
            ContractContext("spec", {"goal": "ship"}, {"deadline"}, utility=10),
            ContractContext("calendar", {"deadline": "fri"}, {"budget"}, utility=7),
            ContractContext("budget", {"budget": "10k"}, {"goal": "ship"}, utility=7),
            ContractContext("unused", {"region": "eu"}, {}, utility=50),
        ]
        plan = plan_distribution(contexts, {})

        self.assertEqual(len(plan.selected_contexts), 2)
        self.assertIn("spec", plan.selected_contexts)
        self.assertIn(set(plan.selected_contexts) - {"spec"}, [{"calendar"}, {"budget"}])
        self.assertEqual(len(plan.pairs) * 2, len(plan.selected_contexts))
        self.assertEqual(plan.total_utility, sum(c.value for c in contexts if c.context_id in plan.selected_contexts))
        self.assertIn("unused", plan.unmatched_eligible)
        self.assertEqual(len(plan.unmatched_eligible), 2)
        self.assertIn(set(plan.unmatched_eligible) - {"unused"}, [{"calendar"}, {"budget"}])

    def test_zero_utility_is_secondary_to_value_but_pair_count_breaks_ties(self):
        contexts = [
            ContractContext("zero-a", {}, {"x"}, utility=0),
            ContractContext("zero-b", {"x": "present"}, {}, utility=0),
        ]
        plan = plan_distribution(contexts, {})
        self.assertEqual(set(plan.selected_contexts), {"zero-a", "zero-b"})
        self.assertEqual(plan.total_utility, 0)

    def test_anchor_update_replans_and_reports_delta(self):
        contexts = [
            ContractContext("a", {"project": "alpha", "goal": "ship"}, {"deadline"}),
            ContractContext("b", {"project": "alpha", "deadline": "fri"}, {"goal": "ship"}),
            ContractContext("c", {"project": "beta", "goal": "ship"}, {"deadline"}),
            ContractContext("d", {"project": "beta", "deadline": "mon"}, {"goal": "ship"}),
        ]
        before = plan_distribution(contexts, {"project": "alpha"})
        after = plan_distribution(contexts, {"project": "beta"})
        delta = compare_plans(before, after)

        self.assertEqual(set(delta.newly_excluded), {"a", "b"})
        self.assertEqual(set(delta.selected_removed), set(before.selected_contexts) - set(after.selected_contexts))
        self.assertEqual(set(delta.newly_eligible), {"c", "d"})
        self.assertEqual(set(delta.selected_added), {"c", "d"})

    def test_duplicate_ids_and_invalid_utility_are_rejected(self):
        with self.assertRaises(ValueError):
            plan_distribution([ContractContext("same", {}), ContractContext("same", {})], {})
        with self.assertRaises(ValueError):
            ContractContext("bad", {}, utility=-1)

    def test_repeat_run_has_same_serialized_plan_and_digest(self):
        contexts = [
            ContractContext("a", {"goal": "ship"}, {"deadline"}, utility=3),
            ContractContext("b", {"deadline": "fri"}, {"goal": "ship"}, utility=3),
            ContractContext("c", {"budget": "10k"}, {"goal": "ship"}, utility=3),
        ]
        first = plan_distribution(contexts, {})
        second = plan_distribution(contexts, {})
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_small_random_pools_match_brute_force_lexicographic_optimum(self):
        rng = random.Random(1847)
        keys = [f"k{i}" for i in range(6)]
        for case in range(20):
            contexts = []
            for i in range(8):
                chosen = rng.sample(keys, rng.randint(1, 3))
                facts = {k: rng.choice(["0", "1"]) for k in chosen}
                need_key = rng.choice([k for k in keys if k not in facts])
                need_value = None if rng.random() < 0.5 else rng.choice(["0", "1"])
                needs = {need_key: need_value}
                contexts.append(ContractContext(f"c{i}", facts, needs, utility=rng.randint(0, 5)))
            anchor_key = rng.choice(keys)
            anchor = {anchor_key: rng.choice(["0", "1"])}

            plan = plan_distribution(contexts, anchor)
            by_id = {c.context_id: c for c in contexts}
            eligible = [c for c in contexts if all(
                k not in anchor or (type(v) is type(anchor[k]) and v == anchor[k])
                for k, v in c.facts.items()
            )]
            graph = nx.Graph()
            graph.add_nodes_from(c.context_id for c in eligible)
            for a, b in combinations(eligible, 2):
                compatible = all(
                    k not in b.facts or (type(v) is type(b.facts[k]) and v == b.facts[k])
                    for k, v in a.facts.items()
                ) and all(
                    k not in a.facts or (type(v) is type(a.facts[k]) and v == a.facts[k])
                    for k, v in b.facts.items()
                )
                if not compatible:
                    continue
                def served(consumer, provider):
                    for key, expected in consumer.needs.items():
                        if key not in provider.facts:
                            continue
                        supplied = provider.facts[key]
                        if expected is None or (type(expected) is type(supplied) and expected == supplied):
                            return True
                    return False
                if served(a, b) or served(b, a):
                    graph.add_edge(a.context_id, b.context_id)

            best = (0, 0)
            ids = sorted(graph.nodes)
            for r in range(0, len(ids) + 1, 2):
                for subset in combinations(ids, r):
                    matching = nx.max_weight_matching(graph.subgraph(subset), maxcardinality=True)
                    if 2 * len(matching) != r:
                        continue
                    score = (sum(by_id[x].value for x in subset), len(subset))
                    best = max(best, score)
            actual = (plan.total_utility, len(plan.selected_contexts))
            self.assertEqual(actual, best, f"case={case}")

    def test_even_swarm_family_exchange_and_two_context_reconfiguration(self):
        rng = random.Random(55)
        for case in range(8):
            contexts = _random_contexts(rng, 8)
            anchor = {f"k{rng.randrange(9)}": rng.choice(["0", "1"])}
            family = _swarm_family(build_compatibility_graph(contexts, anchor))
            self.assertTrue(_exchange_holds(family), f"exchange failed in case={case}")
            for first in family:
                for second in family:
                    distance = _pair_move_distance(family, first, second)
                    self.assertIsNotNone(distance, f"stuck pair in case={case}")
                    self.assertEqual(distance, len(first ^ second) // 2)

    def test_anchor_is_a_restriction_of_the_unanchored_swarm_family(self):
        rng = random.Random(91)
        for case in range(10):
            contexts = _random_contexts(rng, 8)
            full_graph = build_compatibility_graph(contexts, {})
            anchor = {f"k{rng.randrange(9)}": rng.choice(["0", "1"])}
            anchored_graph = build_compatibility_graph(contexts, anchor)
            full_family = _swarm_family(full_graph)
            anchored_family = _swarm_family(anchored_graph)
            valid = set(anchored_graph.nodes)
            expected = {swarm for swarm in full_family if swarm <= valid}
            self.assertEqual(anchored_family, expected, f"restriction mismatch in case={case}")
            self.assertTrue(_exchange_holds(anchored_family), f"exchange failed in case={case}")

    def test_anchor_repair_bound_by_dropping_each_broken_pair(self):
        rng = random.Random(2701)
        for case in range(12):
            contexts = _random_contexts(rng, 8)
            anchor1 = {"k0": rng.choice(["0", "1"])}
            old_plan = plan_distribution(contexts, anchor1)
            old_graph = build_compatibility_graph(contexts, anchor1)
            # Change an anchor fact that was not already fixed by anchor1.
            anchor2 = dict(anchor1, k1=rng.choice(["0", "1"]))
            new_graph = build_compatibility_graph(contexts, anchor2)
            new_family = _swarm_family(new_graph)
            broken = set(old_plan.selected_contexts) - set(new_graph.nodes)
            old_set = frozenset(old_plan.selected_contexts)
            nearest_distance = min(len(old_set ^ candidate) for candidate in new_family)
            self.assertLessEqual(nearest_distance, 2 * len(broken), f"repair bound failed in case={case}")

    def test_fixed_direction_signs_can_make_a_valid_swarm_matrix_singular(self):
        contexts = [
            ContractContext("c0", {}, {"e01": "x", "e02": "x"}),
            ContractContext("c1", {"e01": "x"}, {"e13": "x"}),
            ContractContext("c2", {"e02": "x"}, {"e23": "x"}),
            ContractContext("c3", {"e13": "x", "e23": "x"}, {}),
        ]
        graph = build_compatibility_graph(contexts, {})
        self.assertEqual(len(nx.max_weight_matching(graph, maxcardinality=True)), 2)
        ids = ["c0", "c1", "c2", "c3"]
        index = {context_id: i for i, context_id in enumerate(ids)}
        fixed = [[0] * 4 for _ in range(4)]
        weighted = [[0] * 4 for _ in range(4)]
        edge_weights = {("c0", "c1"): 2, ("c0", "c2"): 3, ("c1", "c3"): 5, ("c2", "c3"): 7}
        for left, right, attrs in graph.edges(data=True):
            service = attrs["services"][0]
            consumer, provider = index[service.consumer], index[service.provider]
            fixed[consumer][provider], fixed[provider][consumer] = 1, -1
            weight = edge_weights[tuple(sorted((left, right)))]
            weighted[consumer][provider], weighted[provider][consumer] = weight, -weight

        def pfaffian4(matrix):
            return (matrix[0][1] * matrix[2][3]
                    - matrix[0][2] * matrix[1][3]
                    + matrix[0][3] * matrix[1][2])

        self.assertEqual(pfaffian4(fixed), 0)
        self.assertNotEqual(pfaffian4(weighted), 0)
        self.assertEqual(pfaffian4(weighted) ** 2, 1)

    def test_partial_service_explicitly_reports_unmet_partner_needs(self):
        consumer = ContractContext("consumer", {}, {"deadline": None, "budget": "20k"})
        provider = ContractContext("provider", {"deadline": "fri", "budget": "10k"})
        plan = plan_distribution([consumer, provider], {})
        self.assertEqual(len(plan.pairs), 1)
        service = next(s for s in plan.pairs[0].services if s.consumer == "consumer")
        self.assertEqual([need.key for need in service.needs], ["deadline"])
        self.assertEqual([need.key for need in service.unmet_needs], ["budget"])
        self.assertFalse(service.to_dict()["all_needs_satisfied_by_this_partner"])

    def test_fact_equality_is_type_strict_for_boolean_and_integer(self):
        a = ContractContext("a", {"flag": True}, {"x": "v"})
        b = ContractContext("b", {"flag": 1, "x": "v"})
        plan = plan_distribution([a, b], {})
        self.assertEqual(plan.selected_contexts, ())

    def test_digest_ignores_input_order_but_changes_when_anchor_changes(self):
        contexts = [
            ContractContext("a", {"goal": "ship"}, {"deadline"}),
            ContractContext("b", {"deadline": "fri"}, {"goal": "ship"}),
        ]
        first = plan_distribution(contexts, {})
        reordered = plan_distribution(list(reversed(contexts)), {})
        changed = plan_distribution(contexts, {"goal": "ship"})
        self.assertEqual(first.input_digest, reordered.input_digest)
        self.assertNotEqual(first.input_digest, changed.input_digest)

    def test_plan_delta_reports_service_and_utility_changes(self):
        old_contexts = [
            ContractContext("a", {}, {"x": "one"}, utility=2),
            ContractContext("b", {"x": "one"}, {}, utility=3),
        ]
        new_contexts = [
            ContractContext("a", {}, {"x": "two"}, utility=4),
            ContractContext("b", {"x": "two"}, {}, utility=3),
        ]
        before = plan_distribution(old_contexts, {})
        after = plan_distribution(new_contexts, {})
        delta = compare_plans(before, after)
        self.assertEqual(delta.service_changed_pairs, (("a", "b"),))
        self.assertEqual(delta.utility_changed_contexts, ("a",))
        self.assertEqual(delta.utility_delta, 2)


if __name__ == "__main__":
    unittest.main()
