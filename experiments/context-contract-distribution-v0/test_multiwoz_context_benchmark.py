import json
import unittest

from context_contract_distribution import ContractContext, plan_distribution
from stress_test_multiwoz import (
    SOURCE_COMMIT,
    _scalar_values,
    _qualify_slot,
    dialogue_to_context,
    git_blob_sha1,
    independently_validate_plan,
    exact_objective_reference,
    build_compatibility_graph,
)


class MultiWOZConversionTests(unittest.TestCase):
    def test_extracts_real_schema_belief_state_and_unresolved_requested_slots(self):
        dialogue = {
            "dialogue_id": "SNG00001.json",
            "services": ["hotel"],
            "turns": [
                {
                    "turn_id": "0",
                    "speaker": "USER",
                    "utterance": "I need a cheap hotel.",
                    "frames": [
                        {
                            "service": "hotel",
                            "state": {
                                "active_intent": "find_hotel",
                                "requested_slots": ["phone", "name"],
                                "slot_values": {
                                    "hotel-pricerange": ["cheap"],
                                    "hotel-area": ["centre"],
                                },
                            },
                        }
                    ],
                },
                {
                    "turn_id": "1",
                    "speaker": "SYSTEM",
                    "utterance": "Would you like the phone number?",
                    "frames": [
                        {
                            "service": "hotel",
                            "state": {
                                "active_intent": "inform",
                                "requested_slots": [],
                                "slot_values": {"hotel-phone": ["555-0100"]},
                            },
                        }
                    ],
                },
            ],
        }

        context = dialogue_to_context(dialogue)

        self.assertEqual(context.context_id, "multiwoz-v2.2:SNG00001.json")
        self.assertEqual(context.facts["hotel-pricerange"], '["cheap"]')
        self.assertEqual(context.facts["hotel-area"], '["centre"]')
        self.assertNotIn("hotel-phone", context.facts, "SYSTEM frames must not leak into user state")
        self.assertEqual(set(context.needs), {"hotel-phone", "hotel-name"})
        self.assertEqual(context.value, 2)

    def test_latest_user_snapshot_replaces_old_slots_and_resolved_requests(self):
        dialogue = {
            "dialogue_id": "SNG00002.json",
            "turns": [
                {
                    "speaker": "USER",
                    "frames": [{
                        "service": "train",
                        "state": {
                            "requested_slots": ["trainid"],
                            "slot_values": {
                                "train-departure": ["Cambridge"],
                                "train-destination": ["Ely"],
                                "train-trainid": [],
                            },
                        },
                    }],
                },
                {
                    "speaker": "USER",
                    "frames": [{
                        "service": "train",
                        "state": {
                            "requested_slots": ["trainid", "price"],
                            "slot_values": {
                                "train-departure": ["Norwich"],
                                "train-destination": ["Ely"],
                                "train-trainid": ["TR123"],
                            },
                        },
                    }],
                },
            ],
        }

        context = dialogue_to_context(dialogue)

        self.assertEqual(context.facts["train-departure"], '["norwich"]')
        self.assertEqual(context.facts["train-trainid"], '["tr123"]')
        self.assertEqual(set(context.needs), {"train-price"})
        self.assertNotIn("train-trainid", context.needs)

    def test_multiwoz_list_valued_aliases_are_canonicalized_as_an_order_independent_set(self):
        self.assertEqual(_scalar_values([" 20:00 ", "after 19:45", "20:00", None]), ["20:00", "after 19:45".casefold()])
        self.assertEqual(_scalar_values(["expensive", "CHEAP"]), ["cheap", "expensive"])
        self.assertEqual(_qualify_slot("restaurant", "name"), "restaurant-name")
        self.assertEqual(_qualify_slot("restaurant", "restaurant-area"), "restaurant-area")
        self.assertIsNone(_qualify_slot("restaurant", "NONE"))

    def test_missing_state_frames_are_ignored_and_empty_dialogue_remains_a_context(self):
        context = dialogue_to_context({
            "dialogue_id": "SNG00003.json",
            "turns": [
                {"speaker": "USER", "frames": [{"service": "hotel"}]},
                {"speaker": "SYSTEM", "frames": []},
            ],
        })
        self.assertEqual(dict(context.facts), {})
        self.assertEqual(dict(context.needs), {})
        self.assertEqual(context.value, 0)

    def test_source_is_pinned_to_actual_multiwoz_repository_commit(self):
        self.assertEqual(SOURCE_COMMIT, "fe0c8e65cfcd8462bd33c86e35f21addc84ca82b")
        payload = b'{"dialogue_id":"SNG00000.json"}'
        self.assertEqual(git_blob_sha1(payload), "21747a119ed990c670c23a3b8abb2a0f69b32d03")


class MultiWOZPlannerIntegrationTests(unittest.TestCase):
    def test_real_schema_fixture_builds_valid_plan_and_matches_objective_reference(self):
        contexts = [
            dialogue_to_context({
                "dialogue_id": "D1",
                "turns": [{"speaker": "USER", "frames": [{
                    "service": "restaurant",
                    "state": {"requested_slots": ["phone"], "slot_values": {"restaurant-area": ["centre"]}},
                }]}],
            }),
            dialogue_to_context({
                "dialogue_id": "D2",
                "turns": [{"speaker": "USER", "frames": [{
                    "service": "restaurant",
                    "state": {"requested_slots": [], "slot_values": {
                        "restaurant-area": ["centre"], "restaurant-phone": ["123"]
                    }},
                }]}],
            }),
            ContractContext("D3", {"hotel-area": '["north"]'}, {"hotel-phone": None}, utility=1),
        ]
        anchor = {"restaurant-area": '["centre"]'}
        plan = plan_distribution(contexts, anchor)
        graph = build_compatibility_graph(contexts, anchor)
        by_id = {context.context_id: context for context in contexts}
        oracle = exact_objective_reference(graph, {context.context_id: context.value for context in contexts})
        valid, details = independently_validate_plan(plan, by_id, anchor)

        self.assertTrue(valid, details)
        self.assertEqual((plan.total_utility, len(plan.selected_contexts)), oracle)
        self.assertEqual(set(plan.selected_contexts), {"multiwoz-v2.2:D1", "multiwoz-v2.2:D2"})

    def test_requested_need_not_fulfilled_by_any_partner_does_not_create_an_edge(self):
        left = dialogue_to_context({
            "dialogue_id": "D4",
            "turns": [{"speaker": "USER", "frames": [{
                "service": "hotel",
                "state": {"requested_slots": ["phone"], "slot_values": {"hotel-area": ["north"]}},
            }]}],
        })
        right = dialogue_to_context({
            "dialogue_id": "D5",
            "turns": [{"speaker": "USER", "frames": [{
                "service": "restaurant",
                "state": {"requested_slots": [], "slot_values": {"restaurant-phone": ["123"]}},
            }]}],
        })
        plan = plan_distribution([left, right], {})
        self.assertEqual(plan.selected_contexts, ())


if __name__ == "__main__":
    unittest.main()
