import unittest

from context_contract_distribution import build_compatibility_graph, plan_distribution
from stress_test_sgd_independent_corpus import (
    dialogue_to_context,
    schema_intent_contexts,
)


class SgdIndependentCorpusTests(unittest.TestCase):
    def setUp(self):
        self.schemas = {
            "Hotels_2": {
                "service_name": "Hotels_2",
                "slots": [
                    {"name": "location", "is_categorical": False, "possible_values": []},
                    {"name": "date", "is_categorical": False, "possible_values": []},
                    {"name": "confirmation", "is_categorical": False, "possible_values": []},
                    {"name": "time", "is_categorical": False, "possible_values": []},
                ],
                "intents": [
                    {
                        "name": "BookHouse",
                        "required_slots": ["location", "date", "time"],
                    }
                ],
            },
            "Hotels_4": {
                "service_name": "Hotels_4",
                "slots": [
                    {"name": "location", "is_categorical": False, "possible_values": []},
                    {"name": "check_in", "is_categorical": False, "possible_values": []},
                ],
                "intents": [
                    {"name": "SearchHotel", "required_slots": ["location", "check_in"]}
                ],
            },
        }

    def test_service_namespaces_and_canonical_inform_values(self):
        dialogue = {
            "dialogue_id": "sgd-test-1",
            "services": ["Hotels_2", "Hotels_4"],
            "turns": [
                {
                    "speaker": "USER",
                    "frames": [
                        {
                            "service": "Hotels_2",
                            "state": {
                                "active_intent": "BookHouse",
                                "requested_slots": ["confirmation"],
                                "slot_values": {
                                    "location": ["New York"],
                                    "date": ["March 8th"],
                                },
                            },
                            "actions": [
                                {
                                    "act": "INFORM",
                                    "slot": "date",
                                    "canonical_values": ["2026-03-08"],
                                }
                            ],
                        },
                        {
                            "service": "Hotels_4",
                            "state": {
                                "active_intent": "SearchHotel",
                                "requested_slots": [],
                                "slot_values": {"location": ["Paris"]},
                            },
                            "actions": [
                                {
                                    "act": "INFORM",
                                    "slot": "location",
                                    "canonical_values": ["Paris"],
                                }
                            ],
                        },
                    ],
                },
                {
                    "speaker": "USER",
                    "frames": [
                        {
                            "service": "Hotels_2",
                            "state": {
                                "active_intent": "BookHouse",
                                "requested_slots": [],
                                "slot_values": {
                                    "location": ["New York"],
                                    "date": ["March 8th", "the 8th"],
                                },
                            },
                            "actions": [],
                        }
                    ],
                },
                {
                    "speaker": "SYSTEM",
                    "frames": [
                        {
                            "service": "Hotels_2",
                            "service_results": [{"confirmation": "ABC"}],
                        }
                    ],
                },
            ],
        }

        context, metadata = dialogue_to_context(dialogue, self.schemas)
        self.assertEqual(context.facts["Hotels_2::date"], "2026-03-08")
        self.assertEqual(context.facts["Hotels_2::location"], "New York")
        self.assertEqual(context.facts["Hotels_4::location"], "Paris")
        self.assertNotIn("Hotels_2::confirmation", context.facts)
        self.assertIn("Hotels_2::confirmation", context.needs)
        self.assertIn("Hotels_2::time", context.needs)
        self.assertIn("Hotels_4::check_in", context.needs)
        self.assertNotIn("Hotels_2::location", context.needs)
        self.assertNotIn("Hotels_2::date", context.needs)
        self.assertEqual(metadata["user_state_frames"], 3)
        self.assertEqual(metadata["requested_need_annotations"], 1)
        self.assertEqual(metadata["required_input_need_annotations"], 3)

    def test_schema_intents_compose_result_slots_with_required_inputs(self):
        schemas = {
            "ServiceA": {
                "intents": [
                    {
                        "name": "Lookup",
                        "result_slots": ["city"],
                        "required_slots": ["date"],
                    }
                ]
            },
            "ServiceB": {
                "intents": [
                    {
                        "name": "Book",
                        "result_slots": ["confirmation"],
                        "required_slots": ["city"],
                    }
                ]
            },
            "ServiceC": {
                "intents": [
                    {
                        "name": "Unrelated",
                        "result_slots": ["departure_city"],
                        "required_slots": ["passport"],
                    }
                ]
            },
        }

        contexts, metadata = schema_intent_contexts(schemas)
        self.assertEqual(metadata["intent_contexts"], 3)
        self.assertEqual(metadata["result_slot_count"], 3)
        self.assertEqual(metadata["required_slot_count"], 3)
        lookup = next(item for item in contexts if item.context_id.endswith("ServiceA::Lookup"))
        book = next(item for item in contexts if item.context_id.endswith("ServiceB::Book"))
        self.assertIn("city", lookup.facts)
        self.assertIn("city", book.needs)
        graph = build_compatibility_graph(contexts, {})
        self.assertEqual(graph.number_of_edges(), 1)
        self.assertTrue(graph.has_edge(lookup.context_id, book.context_id))
        plan = plan_distribution(contexts, {}, prebuilt_graph=graph)
        self.assertEqual(len(plan.pairs), 1)
        self.assertEqual(set(plan.selected_contexts), {lookup.context_id, book.context_id})

    def test_unknown_service_is_rejected(self):
        dialogue = {
            "dialogue_id": "sgd-test-unknown",
            "turns": [
                {
                    "speaker": "USER",
                    "frames": [
                        {
                            "service": "Unknown_1",
                            "state": {
                                "active_intent": "Unknown",
                                "requested_slots": [],
                                "slot_values": {"location": ["X"]},
                            },
                        }
                    ],
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "unknown SGD service"):
            dialogue_to_context(dialogue, self.schemas)


if __name__ == "__main__":
    unittest.main()
