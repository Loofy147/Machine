import unittest
from unittest.mock import patch

from run import build_reverse_index, make_graph, native_bidi, native_predecessors


class NativePredecessorPrimitiveTests(unittest.TestCase):
    def test_direct_fibers_match_reverse_index_for_odd_and_even_sizes(self):
        for size in (3, 5, 30, 100, 300):
            reverse, _, _ = build_reverse_index(make_graph(size), size)
            for target in range(size):
                with self.subTest(size=size, target=target):
                    self.assertEqual(native_predecessors(target, size), sorted(reverse[target]))

    def test_native_query_does_not_enumerate_or_build_reverse_index(self):
        succ = make_graph(30)
        with patch("run.all_edges", side_effect=AssertionError("query attempted full relation enumeration")), \
             patch("run.build_reverse_index", side_effect=AssertionError("query attempted reverse-index build")):
            found, _ticks = native_bidi(succ, 0, 17, 30, 10000)
        self.assertTrue(found)

    def test_invalid_target_or_size_is_rejected(self):
        with self.assertRaises(ValueError):
            native_predecessors(0, 1)
        with self.assertRaises(ValueError):
            native_predecessors(30, 30)


if __name__ == "__main__":
    unittest.main()
