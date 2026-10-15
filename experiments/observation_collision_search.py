#!/usr/bin/env python3
"""Fast concrete collision search for truncated SplitMix64 histories.

This is a SAT-witness finder only. It can prove a lower bound on depth when
it finds two distinct states with equal observed histories. Failure to find a
collision is never treated as injectivity.
"""

from __future__ import annotations

import argparse
import json
import random
import time

MASK = (1 << 64) - 1
GAMMA = 0x9E3779B97F4A7C15
A = 0xBF58476D1CE4E5B9
B = 0x94D049BB133111EB


def mix64(x: int) -> int:
    x &= MASK
    x ^= x >> 30
    x = (x * A) & MASK
    x ^= x >> 27
    x = (x * B) & MASK
    x ^= x >> 31
    return x


def history_key(seed: int, bits: int, length: int) -> tuple[int, ...]:
    mask = (1 << bits) - 1
    state = seed & MASK
    out = []
    for _ in range(length):
        state = (state + GAMMA) & MASK
        out.append(mix64(state) & mask)
    return tuple(out)


def search(bits: int, length: int, samples: int, seed: int) -> dict:
    if not 1 <= bits <= 64:
        raise ValueError("bits must be in [1,64]")
    if length < 1:
        raise ValueError("length must be positive")
    rng = random.Random(seed)
    seen: dict[tuple[int, ...], int] = {}
    started = time.perf_counter()

    for i in range(samples):
        s = rng.getrandbits(64)
        key = history_key(s, bits, length)
        previous = seen.get(key)
        if previous is not None and previous != s:
            elapsed = time.perf_counter() - started
            return {
                "status": "collision_found",
                "bits": bits,
                "length": length,
                "history_depth": length - 1,
                "samples_examined": i + 1,
                "state1": previous,
                "state2": s,
                "history": key,
                "elapsed_seconds": elapsed,
            }
        seen[key] = s

    return {
        "status": "not_found",
        "bits": bits,
        "length": length,
        "history_depth": length - 1,
        "samples_examined": samples,
        "elapsed_seconds": time.perf_counter() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", type=int, nargs="+", default=[32])
    parser.add_argument("--lengths", type=int, nargs="+", default=[2, 3])
    parser.add_argument("--samples", type=int, default=1 << 22)
    parser.add_argument("--seed", type=int, default=20260930)
    args = parser.parse_args()

    for bits in args.bits:
        for length in args.lengths:
            print(json.dumps(search(bits, length, args.samples, args.seed)))


if __name__ == "__main__":
    main()
