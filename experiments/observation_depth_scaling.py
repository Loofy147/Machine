#!/usr/bin/env python3
"""Scaling experiments for exact/sample observation depth.

The exact cyclic depth of a finite single-cycle observation word is the
longest repeated cyclic block length. This script uses exact integer window
encoding; no probabilistic hash is used.

Two modes are provided:

1. exact balanced-word null model for small finite widths;
2. prefix-only SplitMix64 measurement for 64-bit states.

A prefix result is a local lower-bound observation for the full 2^64 word:
if a repeated L-block is found in the prefix, then the full word also has
a repeated L-block and therefore d_b >= L. Absence of a collision in the
prefix is not a proof of the global value.

The balanced null model is exact for uniformly random bijections followed
by b-bit truncation, because the induced word is a uniformly random
permutation of a multiset containing 2^(n-b) copies of each b-bit symbol.
"""

from __future__ import annotations

import argparse
import math
import random
import statistics
import time
from dataclasses import dataclass


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


def balanced_word(M: int, b: int, seed: int) -> list[int]:
    if M <= 0 or M & (M - 1):
        raise ValueError("M must be a positive power of two")
    if not 1 <= b <= int(math.log2(M)):
        raise ValueError("b must satisfy 1 <= b <= log2(M)")

    q = 1 << b
    repeat = M // q
    word = [a for a in range(q) for _ in range(repeat)]
    random.Random(seed).shuffle(word)
    return word


def splitmix_prefix(length: int, seed: int) -> list[int]:
    if length <= 0:
        raise ValueError("length must be positive")

    state = seed & MASK
    out = []
    for _ in range(length):
        state = (state + GAMMA) & MASK
        out.append(mix64(state))
    return out


def has_repeated_cyclic_block(word: list[int], bits: int, length: int) -> bool:
    """Exact test for a repeated cyclic block of a given length."""
    n = len(word)
    if length <= 0:
        return True
    if length > n:
        return False

    q = 1 << bits
    high = 1 << (bits * (length - 1))
    stream = word + word[: length - 1]

    code = 0
    for value in stream[:length]:
        code = (code << bits) | value

    seen = {code}
    for i in range(1, n):
        code = (code - stream[i - 1] * high) * q + stream[i + length - 1]
        if code in seen:
            return True
        seen.add(code)

    return False


def max_repeated_cyclic_block(word: list[int], bits: int) -> int:
    """Return the exact longest repeated cyclic block length.

    Exact for finite words. Python integers are used for window encoding, so
    there is no hash-collision risk.
    """
    n = len(word)
    if n < 2:
        return 0

    # Existence of a repeated block is monotone in the block length:
    # if length L repeats, every shorter length also repeats.
    lo, hi = 1, n - 1
    if not has_repeated_cyclic_block(word, bits, lo):
        return 0

    best = 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if has_repeated_cyclic_block(word, bits, mid):
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1

    return best


def exact_cyclic_depth(word: list[int], bits: int) -> int:
    return max_repeated_cyclic_block(word, bits)


def has_repeated_linear_block(word: list[int], bits: int, length: int) -> bool:
    """Exact test for a repeated block in a linear prefix."""
    n = len(word)
    if length <= 0:
        return True
    if length > n:
        return False

    q = 1 << bits
    high = 1 << (bits * (length - 1))

    code = 0
    for value in word[:length]:
        code = (code << bits) | value

    seen = {code}
    for i in range(1, n - length + 1):
        code = (code - word[i - 1] * high) * q + word[i + length - 1]
        if code in seen:
            return True
        seen.add(code)

    return False


def sampled_prefix_depth(word: list[int], bits: int) -> int | None:
    """Return exact repeated-block depth for a linear prefix.

    If the returned depth is d, length d+1 blocks are not all necessarily
    unique; rather d is the longest repeated block length discovered before
    the first unique length. If the search limit is reached while repetitions
    remain, the returned value is a lower-bound witness only.
    """
    n = len(word)
    if n < 2:
        return 0

    max_length = min(n, max(1, 64 // bits))
    for length in range(1, max_length + 1):
        if not has_repeated_linear_block(word, bits, length):
            return length - 1

    return max_length


@dataclass(frozen=True)
class ScalingRow:
    width: int
    bits: int
    trial: int
    depth: int
    information_lower_bound: int
    birthday_scale: int


def run_balanced_scaling(widths, bits_list, trials: int) -> list[ScalingRow]:
    rows = []
    for w in widths:
        M = 1 << w
        for b in bits_list:
            if b > w:
                continue
            for trial in range(trials):
                word = balanced_word(M, b, 50_000 + 1000 * w + 100 * b + trial)
                depth = exact_cyclic_depth(word, b)
                rows.append(
                    ScalingRow(
                        width=w,
                        bits=b,
                        trial=trial,
                        depth=depth,
                        information_lower_bound=math.ceil(w / b) - 1,
                        birthday_scale=math.ceil(2 * w / b) - 1,
                    )
                )
    return rows


def print_balanced_summary(rows: list[ScalingRow]) -> None:
    groups = {}
    for row in rows:
        groups.setdefault((row.width, row.bits), []).append(row.depth)

    print("width bits depths mean info_lb birthday_scale")
    for (w, b), depths in groups.items():
        print(
            w,
            b,
            depths,
            f"{statistics.mean(depths):.3f}",
            math.ceil(w / b) - 1,
            math.ceil(2 * w / b) - 1,
        )


def run_splitmix_prefix(length: int, bits_list, seed: int) -> list[dict]:
    full = splitmix_prefix(length, seed)
    rows = []
    for b in bits_list:
        mask = (1 << b) - 1
        word = [x & mask for x in full]
        depth = sampled_prefix_depth(word, b)
        rows.append(
            {
                "length": length,
                "bits": b,
                "sampled_depth": depth,
                "information_lb_for_64bit_state": math.ceil(64 / b) - 1,
                "sample_birthday_scale": math.ceil(2 * math.log2(length) / b) - 1,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--balanced-widths", type=int, nargs="*", default=[10, 12, 14, 16, 18])
    parser.add_argument("--balanced-bits", type=int, nargs="*", default=[1, 2, 4, 8])
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--prefix-length", type=int, default=1 << 19)
    parser.add_argument("--prefix-seed", type=lambda x: int(x, 0), default=0x123456789)
    parser.add_argument("--skip-balanced", action="store_true")
    args = parser.parse_args()

    if not args.skip_balanced:
        print("== exact balanced-word null scaling ==")
        started = time.perf_counter()
        rows = run_balanced_scaling(
            args.balanced_widths,
            args.balanced_bits,
            args.trials,
        )
        print_balanced_summary(rows)
        print(f"elapsed_seconds={time.perf_counter() - started:.6f}")

    print("\n== SplitMix64 prefix scaling ==")
    started = time.perf_counter()
    rows = run_splitmix_prefix(
        args.prefix_length,
        [1, 2, 4, 8, 16, 32],
        args.prefix_seed,
    )
    for row in rows:
        print(row)
    print(f"elapsed_seconds={time.perf_counter() - started:.6f}")


if __name__ == "__main__":
    main()
