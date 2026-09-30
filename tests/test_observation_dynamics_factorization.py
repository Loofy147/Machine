#!/usr/bin/env python3
"""Regression tests for the observation-dynamics experiment.

Run from repository root with:

    python3 -m unittest discover -s tests -p 'test_observation_dynamics*.py'
"""
import unittest

from experiments.observation_dynamics_factorization import (
    A,
    A_INV,
    B,
    B_INV,
    MASK,
    e4_exhaustive_small,
    e7_full_period_certificate,
    mix64,
    unmix64,
    information_lower_bound,
)


class ObservationDynamicsRegressionTests(unittest.TestCase):
    def test_modular_inverse_constants(self):
        self.assertEqual(pow(A, -1, 1 << 64), A_INV)
        self.assertEqual(pow(B, -1, 1 << 64), B_INV)
        self.assertEqual((A * A_INV) & MASK, 1)
        self.assertEqual((B * B_INV) & MASK, 1)

    def test_round_trip_edges(self):
        edges = [
            0,
            1,
            MASK,
            MASK - 1,
            1 << 63,
            (1 << 63) - 1,
        ]
        for x in edges:
            with self.subTest(x=x):
                self.assertEqual(unmix64(mix64(x)), x)
                self.assertEqual(mix64(unmix64(x)), x)

    def test_universal_full_period_certificate(self):
        result = e7_full_period_certificate()
        self.assertTrue(result["low_bit_differs"])
        self.assertTrue(result["all_requested_widths_certified"])
        self.assertEqual(len(result["widths"]), 63)
        self.assertTrue(
            all(
                row["certifies_full_period"]
                for row in result["widths"].values()
            )
        )

    def test_exhaustive_small_conjugacy(self):
        result = e4_exhaustive_small(3)
        self.assertTrue(result["all_pass"])
        self.assertEqual(result["total_instances"], 282314)

    def test_information_lower_bound(self):
        self.assertEqual(information_lower_bound(64, 64), 0)
        self.assertEqual(information_lower_bound(64, 32), 1)
        self.assertEqual(information_lower_bound(64, 16), 3)
        self.assertEqual(information_lower_bound(64, 8), 7)
        self.assertEqual(information_lower_bound(64, 1), 63)


    def test_longest_repeat_depth_matches_partition_depth(self):
        from experiments.observation_depth_scaling import exact_cyclic_depth

        cases = [
            ([0, 1, 0, 1], 1),
            ([0, 0, 1, 1, 0, 1], 1),
            ([0, 1, 1, 0, 1, 0, 0, 1], 1),
        ]

        # Each case is checked through an independent direct partition
        # computation for the full cyclic word.
        for word, bits in cases:
            q = 1 << bits
            n = len(word)

            part = {}
            labels = []
            for x in word:
                part.setdefault(x, len(part))
                labels.append(part[x])

            previous = None
            expected = None
            obs = list(word)

            for depth in range(n):
                classes = len(set(labels))
                if previous is not None and classes == previous:
                    expected = depth - 1
                    break
                previous = classes
                next_obs = obs[1:] + obs[:1]
                refined = {}
                new_labels = []
                for old, nxt in zip(labels, next_obs):
                    key = (old, nxt)
                    refined.setdefault(key, len(refined))
                    new_labels.append(refined[key])
                labels = new_labels
                obs = next_obs

            self.assertIsNotNone(expected)
            self.assertEqual(exact_cyclic_depth(word, bits), expected)

    def test_balanced_word_small_cardinality(self):
        from experiments.observation_depth_scaling import balanced_word

        word = balanced_word(8, 2, 123)
        counts = {x: word.count(x) for x in range(4)}
        self.assertEqual(counts, {0: 2, 1: 2, 2: 2, 3: 2})
        self.assertEqual(len(word), 8)

if __name__ == "__main__":
    unittest.main()
