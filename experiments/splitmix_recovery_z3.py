#!/usr/bin/env python3
"""Sound bit-vector state recovery for truncated SplitMix64.

This module is intentionally solver-backed. It does not infer uniqueness from
sampling: for a fixed observation history it asks a bit-vector solver whether
there is zero, one, or at least two satisfying 64-bit initial states.

The solver is an optional research dependency (z3-solver). A result of
"unknown" remains UNKNOWN and is never promoted to uniqueness or ambiguity.
"""

from __future__ import annotations

import argparse
import json
import time
from typing import Any

from z3 import BitVec, BitVecVal, Extract, LShR, Solver, sat, unsat, unknown

MASK = (1 << 64) - 1
GAMMA = 0x9E3779B97F4A7C15
A = 0xBF58476D1CE4E5B9
B = 0x94D049BB133111EB


def mix_bv(x):
    x = x & BitVecVal(MASK, 64)
    x = x ^ LShR(x, 30)
    x = x * BitVecVal(A, 64)
    x = x ^ LShR(x, 27)
    x = x * BitVecVal(B, 64)
    x = x ^ LShR(x, 31)
    return x


def mix64(x: int) -> int:
    x &= MASK
    x ^= x >> 30
    x = (x * A) & MASK
    x ^= x >> 27
    x = (x * B) & MASK
    x ^= x >> 31
    return x


def collision_status(bits: int, length: int, timeout_ms: int) -> dict[str, Any]:
    """Decide whether H_{length-1} is globally non-injective.

    SAT gives two distinct hidden states with identical observed history.
    UNSAT proves no such pair exists and therefore proves injectivity of
    the length-history map for the specified b and length.
    UNKNOWN is retained as UNKNOWN.
    """
    if not 1 <= bits <= 64:
        raise ValueError("bits must be in [1,64]")
    if length < 1:
        raise ValueError("length must be positive")

    mask = (1 << bits) - 1
    left = BitVec("left_state", 64)
    right = BitVec("right_state", 64)
    solver = Solver()
    solver.set(timeout=timeout_ms)
    solver.add(left != right)

    for k in range(length):
        offset = BitVecVal((k + 1) * GAMMA & MASK, 64)
        left_output = mix_bv(left + offset)
        right_output = mix_bv(right + offset)
        solver.add(
            Extract(bits - 1, 0, left_output)
            == Extract(bits - 1, 0, right_output)
        )

    started = time.perf_counter()
    result = solver.check()
    elapsed = time.perf_counter() - started

    if result == sat:
        model = solver.model()
        s1 = model.eval(left).as_long()
        s2 = model.eval(right).as_long()
        return {
            "status": "ambiguous",
            "history_depth": length - 1,
            "states": [s1, s2],
            "observations": [
                mix64((s1 + (k + 1) * GAMMA) & MASK) & mask
                for k in range(length)
            ],
            "elapsed_seconds": elapsed,
        }

    if result == unsat:
        return {
            "status": "injective",
            "history_depth": length - 1,
            "elapsed_seconds": elapsed,
        }

    return {
        "status": "unknown",
        "history_depth": length - 1,
        "reason": solver.reason_unknown(),
        "elapsed_seconds": elapsed,
    }


def generate_outputs(seed: int, length: int) -> list[int]:
    state = seed & MASK
    out = []
    for _ in range(length):
        state = (state + GAMMA) & MASK
        out.append(mix64(state))
    return out


def recovery_status(observations: list[int], bits: int, timeout_ms: int) -> dict[str, Any]:
    if not 1 <= bits <= 64:
        raise ValueError("bits must be in [1,64]")
    if not observations:
        raise ValueError("at least one observation is required")

    mask = (1 << bits) - 1
    start = BitVec("s0", 64)
    solver = Solver()
    solver.set(timeout=timeout_ms)

    for k, observed in enumerate(observations):
        state = start + BitVecVal((k + 1) * GAMMA & MASK, 64)
        output = mix_bv(state)
        solver.add(Extract(bits - 1, 0, output) == (observed & mask))

    t0 = time.perf_counter()
    first = solver.check()
    elapsed_first = time.perf_counter() - t0

    if first == unsat:
        return {
            "status": "unsat",
            "solutions": 0,
            "elapsed_first_seconds": elapsed_first,
        }
    if first == unknown:
        return {
            "status": "unknown",
            "solutions": None,
            "reason": solver.reason_unknown(),
            "elapsed_first_seconds": elapsed_first,
        }

    model = solver.model()
    witness = model.eval(start).as_long()

    solver.add(start != BitVecVal(witness, 64))

    t1 = time.perf_counter()
    second = solver.check()
    elapsed_second = time.perf_counter() - t1

    if second == sat:
        second_model = solver.model().eval(start).as_long()
        return {
            "status": "ambiguous",
            "solutions": ">=2",
            "witness1": witness,
            "witness2": second_model,
            "elapsed_first_seconds": elapsed_first,
            "elapsed_second_seconds": elapsed_second,
        }

    if second == unsat:
        return {
            "status": "unique",
            "solutions": 1,
            "witness": witness,
            "elapsed_first_seconds": elapsed_first,
            "elapsed_second_seconds": elapsed_second,
        }

    return {
        "status": "unknown",
        "solutions": None,
        "reason": solver.reason_unknown(),
        "witness1": witness,
        "elapsed_first_seconds": elapsed_first,
        "elapsed_second_seconds": elapsed_second,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=lambda x: int(x, 0), default=0x123456789)
    parser.add_argument("--bits", type=int, nargs="+", default=[32, 16])
    parser.add_argument("--lengths", type=int, nargs="+", default=[2, 3, 7, 8])
    parser.add_argument("--timeout-ms", type=int, default=20_000)
    args = parser.parse_args()

    max_length = max(args.lengths)
    outputs = generate_outputs(args.seed, max_length)

    print("== exact truncated SplitMix64 recovery for one observed stream ==")
    print(json.dumps({
        "seed": hex(args.seed),
        "timeout_ms": args.timeout_ms,
    }))

    for bits in args.bits:
        for length in args.lengths:
            history = outputs[:length]
            result = recovery_status(history, bits, args.timeout_ms)
            print(json.dumps({
                "bits": bits,
                "length": length,
                "history_depth_k": length - 1,
                **result,
            }))

    print("\n== global history injectivity collision check ==")
    for bits in args.bits:
        for length in args.lengths:
            result = collision_status(bits, length, args.timeout_ms)
            print(json.dumps({
                "bits": bits,
                "length": length,
                **result,
            }))


if __name__ == "__main__":
    main()
