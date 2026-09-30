#!/usr/bin/env python3
"""Sound bit-vector state recovery for truncated SplitMix64.

This module is solver-backed. It never promotes UNKNOWN/timeout to a
substantive result.

For a fixed observed history:
  - unique      = exactly one 64-bit initial state;
  - ambiguous   = at least two 64-bit initial states;
  - unsat       = no state matches the requested concrete history;
  - unknown     = solver did not establish any of the above.

For global collision_status:
  - ambiguous   = a collision witness exists;
  - injective   = no collision exists (UNSAT);
  - unknown     = solver did not decide the finite bit-vector query.

The fixed SplitMix64 gamma is part of the experiment contract.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

from z3 import (
    BitVec,
    BitVecVal,
    Extract,
    LShR,
    SolverFor,
    ULT,
    sat,
    unsat,
)

MASK = (1 << 64) - 1
GAMMA = 0x9E3779B97F4A7C15
A = 0xBF58476D1CE4E5B9
B = 0x94D049BB133111EB

SOLVER_LOGIC = "QF_BV"
SOLVER_SEED = 20260930


def mix_bv(x):
    """Exact 64-bit SplitMix64 mixer as a QF_BV expression.

    Bit-vector width already supplies modulo 2^64 arithmetic, so no explicit
    mask-and is needed inside the symbolic expression.
    """
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


def make_solver(timeout_ms: int):
    """Create the dedicated quantifier-free bit-vector solver."""
    solver = SolverFor(SOLVER_LOGIC)
    solver.set(timeout=timeout_ms)
    solver.set("sat.random_seed", SOLVER_SEED)
    return solver


def observed_low_bits(output, bits: int):
    return Extract(bits - 1, 0, output)


def collision_status(bits: int, length: int, timeout_ms: int) -> dict[str, Any]:
    """Decide whether H_(length-1) is globally non-injective.

    The symmetry break ULT(left, right) removes the duplicate orientation of
    every unordered state pair. SAT returns a concrete collision witness;
    UNSAT proves injectivity for the requested history length.
    """
    if not 1 <= bits <= 64:
        raise ValueError("bits must be in [1,64]")
    if length < 1:
        raise ValueError("length must be positive")
    if timeout_ms < 1:
        raise ValueError("timeout_ms must be positive")

    left = BitVec("left_state", 64)
    right = BitVec("right_state", 64)
    solver = make_solver(timeout_ms)

    solver.add(ULT(left, right))

    for k in range(length):
        offset = BitVecVal((k + 1) * GAMMA & MASK, 64)
        left_output = mix_bv(left + offset)
        right_output = mix_bv(right + offset)
        solver.add(
            observed_low_bits(left_output, bits)
            == observed_low_bits(right_output, bits)
        )

    started = time.perf_counter()
    result = solver.check()
    elapsed = time.perf_counter() - started

    common = {
        "history_depth": length - 1,
        "elapsed_seconds": elapsed,
        "solver_logic": SOLVER_LOGIC,
        "solver_seed": SOLVER_SEED,
    }

    if result == sat:
        model = solver.model()
        s1 = model.eval(left).as_long()
        s2 = model.eval(right).as_long()
        mask = (1 << bits) - 1
        observations = [
            mix64((s1 + (k + 1) * GAMMA) & MASK) & mask
            for k in range(length)
        ]
        return {
            "status": "ambiguous",
            "states": [s1, s2],
            "observations": observations,
            **common,
        }

    if result == unsat:
        return {
            "status": "injective",
            **common,
        }

    return {
        "status": "unknown",
        "reason": solver.reason_unknown(),
        **common,
    }


def generate_outputs(seed: int, length: int) -> list[int]:
    state = seed & MASK
    out = []
    for _ in range(length):
        state = (state + GAMMA) & MASK
        out.append(mix64(state))
    return out


def recovery_status(
    observations: list[int],
    bits: int,
    timeout_ms: int,
) -> dict[str, Any]:
    """Determine whether one concrete history has 0, 1, or >=2 states."""
    if not 1 <= bits <= 64:
        raise ValueError("bits must be in [1,64]")
    if not observations:
        raise ValueError("at least one observation is required")
    if timeout_ms < 1:
        raise ValueError("timeout_ms must be positive")

    mask = (1 << bits) - 1
    start = BitVec("s0", 64)
    solver = make_solver(timeout_ms)

    for k, observed in enumerate(observations):
        state = start + BitVecVal((k + 1) * GAMMA & MASK, 64)
        output = mix_bv(state)
        solver.add(observed_low_bits(output, bits) == (observed & mask))

    t0 = time.perf_counter()
    first = solver.check()
    elapsed_first = time.perf_counter() - t0

    base = {
        "elapsed_first_seconds": elapsed_first,
        "solver_logic": SOLVER_LOGIC,
        "solver_seed": SOLVER_SEED,
    }

    if first == unsat:
        return {
            "status": "unsat",
            "solutions": 0,
            **base,
        }

    if first != sat:
        return {
            "status": "unknown",
            "solutions": None,
            "reason": solver.reason_unknown(),
            **base,
        }

    model = solver.model()
    witness = model.eval(start).as_long()
    solver.add(start != BitVecVal(witness, 64))

    t1 = time.perf_counter()
    second = solver.check()
    elapsed_second = time.perf_counter() - t1

    base.update({
        "witness1": witness,
        "elapsed_second_seconds": elapsed_second,
    })

    if second == sat:
        return {
            "status": "ambiguous",
            "solutions": ">=2",
            "witness2": solver.model().eval(start).as_long(),
            **base,
        }

    if second == unsat:
        return {
            "status": "unique",
            "solutions": 1,
            **base,
        }

    return {
        "status": "unknown",
        "solutions": None,
        "reason": solver.reason_unknown(),
        **base,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=lambda x: int(x, 0), default=0x123456789)
    parser.add_argument("--bits", type=int, nargs="+", default=[32, 16])
    parser.add_argument("--lengths", type=int, nargs="+", default=[2, 3, 7, 8])
    parser.add_argument("--timeout-ms", type=int, default=20_000)
    parser.add_argument(
        "--fail-on-unknown",
        action="store_true",
        help="exit nonzero if any solver query returns UNKNOWN/timeout",
    )
    args = parser.parse_args()

    max_length = max(args.lengths)
    outputs = generate_outputs(args.seed, max_length)
    unknown_seen = False

    print("== exact truncated SplitMix64 recovery for one observed stream ==")
    print(json.dumps({
        "seed": hex(args.seed),
        "timeout_ms": args.timeout_ms,
        "solver_logic": SOLVER_LOGIC,
        "solver_seed": SOLVER_SEED,
    }))

    for bits in args.bits:
        for length in args.lengths:
            result = recovery_status(outputs[:length], bits, args.timeout_ms)
            unknown_seen |= result["status"] == "unknown"
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
            unknown_seen |= result["status"] == "unknown"
            print(json.dumps({
                "bits": bits,
                "length": length,
                **result,
            }))

    if args.fail_on_unknown and unknown_seen:
        print(
            "\nERROR: at least one solver query returned UNKNOWN; "
            "no proof status is being promoted.",
            file=sys.stderr,
        )
        raise SystemExit(2)


if __name__ == "__main__":
    main()
