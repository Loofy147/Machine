import unittest
from cost_model import (
    AccessWeights, OPAQUE_FORWARD, GENERIC_REVERSE_INDEX,
    SPECIALIZED_FIBER_LOOKUP, query_events, weighted_query_cost,
    csr_resource_footprint, break_even_conditions,
)


class CostModelTests(unittest.TestCase):
    def test_profiles_return_same_output_cardinality(self):
        for profile in (OPAQUE_FORWARD, GENERIC_REVERSE_INDEX, SPECIALIZED_FIBER_LOOKUP):
            with self.subTest(profile=profile):
                self.assertEqual(query_events(profile, 20, 4)["output_entries"], 4)

    def test_generic_csr_reads_two_offsets_and_two_words_per_output(self):
        events = query_events(GENERIC_REVERSE_INDEX, 20, 4)
        self.assertEqual(events["generic_state_reads"], 10)
        self.assertEqual(events["fiber_lookup_calls"], 0)
        self.assertEqual(events["transition_probes"], 0)

    def test_opaque_profile_charges_transition_probes(self):
        events = query_events(OPAQUE_FORWARD, 20, 4)
        self.assertEqual(events["transition_probes"], 20)
        self.assertEqual(events["generic_state_reads"], 0)

    def test_specialized_profile_charges_explicit_call(self):
        events = query_events(SPECIALIZED_FIBER_LOOKUP, 20, 4)
        self.assertEqual(events["fiber_lookup_calls"], 1)
        self.assertEqual(events["generic_state_reads"], 0)
        self.assertEqual(events["output_entries"], 4)

    def test_break_even_depends_on_declared_cost_weight(self):
        degree = 4
        threshold = 2 + 2 * degree
        low = AccessWeights(1, 1, threshold - 1, 3)
        tie = AccessWeights(1, 1, threshold, 3)
        high = AccessWeights(1, 1, threshold + 1, 3)
        generic = weighted_query_cost(GENERIC_REVERSE_INDEX, 20, degree, low)
        self.assertLess(weighted_query_cost(SPECIALIZED_FIBER_LOOKUP, 20, degree, low), generic)
        self.assertEqual(weighted_query_cost(SPECIALIZED_FIBER_LOOKUP, 20, degree, tie), generic)
        self.assertGreater(weighted_query_cost(SPECIALIZED_FIBER_LOOKUP, 20, degree, high), generic)

    def test_csr_preprocessing_and_storage_are_explicit(self):
        self.assertEqual(
            csr_resource_footprint(10, 15),
            {"offline_build_work_units": 40, "persistent_bytes": 119},
        )

    def test_invalid_query_domain_is_rejected(self):
        with self.assertRaises(ValueError):
            query_events(GENERIC_REVERSE_INDEX, 3, 4)

    def test_unknown_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            query_events("free_oracle", 20, 1)

    def test_break_even_report_is_symbolic(self):
        conditions = break_even_conditions(20, 4)
        self.assertEqual(conditions["specialized_vs_generic"], "c_fiber_lookup < c_state_read * 10")
        self.assertIn("c_transition_probe", conditions["specialized_vs_opaque"])
        self.assertIn("same output cost", conditions["assumption"])

    def test_cost_weights_must_be_positive_and_finite(self):
        for value in (0, -1, float("inf"), float("nan")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    AccessWeights(1, 1, value, 1)


if __name__ == "__main__":
    unittest.main()
