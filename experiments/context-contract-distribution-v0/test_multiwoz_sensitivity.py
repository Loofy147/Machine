import unittest

from context_contract_distribution import ContractContext
from stress_test_multiwoz_sensitivity import run_sensitivity_sweep


def _contexts(count=24):
    contexts = []
    for index in range(count):
        offered = index % 4
        requested = (offered + 1) % 4
        facts = {
            "task-scope": "shared",
            f"task-offer-{offered}": "ready",
            f"task-detail-{index}": f"value-{index}",
        }
        needs = {f"task-offer-{requested}": None}
        contexts.append(
            ContractContext(
                f"fixture-{index:03d}",
                facts,
                needs,
                utility=len(facts),
            )
        )
    return contexts


class MultiWOZSensitivityTests(unittest.TestCase):
    def test_fixed_seeds_repeat_metrics_and_pass_invariants(self):
        contexts = _contexts()
        first = run_sensitivity_sweep(contexts, [], seed_count=2, start_seed=15)
        second = run_sensitivity_sweep(contexts, [], seed_count=2, start_seed=15)

        self.assertEqual(first["runs"], second["runs"])
        self.assertTrue(first["summary"]["all_seed_runs_passed"])
        self.assertEqual(first["summary"]["checks_passed"], first["summary"]["checks_total"])
        self.assertEqual([row["seed"] for row in first["runs"]], [15, 16])
        self.assertTrue(all(row["slot_count_policy"]["raw_plan_valid"] for row in first["runs"]))
        self.assertTrue(all(row["request_priority_policy"]["raw_plan_valid"] for row in first["runs"]))

    def test_alternative_utility_preserves_facts_and_eligibility_scope(self):
        result = run_sensitivity_sweep(_contexts(), [], seed_count=1, start_seed=2026)
        row = result["runs"][0]
        self.assertEqual(row["candidate_contexts"], len(_contexts()) - 4)
        self.assertEqual(
            row["slot_count_policy"]["eligible_contexts"],
            row["request_priority_policy"]["eligible_contexts"],
        )
        self.assertEqual(
            row["slot_count_policy"]["compatibility_edges"],
            row["request_priority_policy"]["compatibility_edges"],
        )

    def test_invalid_seed_and_anchor_parameters_are_rejected(self):
        with self.assertRaises(ValueError):
            run_sensitivity_sweep(_contexts(), [], seed_count=0)
        with self.assertRaises(ValueError):
            run_sensitivity_sweep(_contexts(), [], anchor_context_count=1)
        with self.assertRaises(ValueError):
            run_sensitivity_sweep(_contexts(5), [], anchor_context_count=4)


if __name__ == "__main__":
    unittest.main()
