#!/usr/bin/env python3
"""Bitwuzla QF_BV oracle for truncated SplitMix64 collisions."""

from __future__ import annotations

import argparse
import json
import time
from typing import Any

import bitwuzla
from bitwuzla import Kind, Option, Options, TermManager, Bitwuzla

MASK = (1 << 64) - 1
GAMMA = 0x9E3779B97F4A7C15
A = 0xBF58476D1CE4E5B9
B = 0x94D049BB133111EB


def bv(tm: TermManager, sort, value: int):
    return tm.mk_bv_value(sort, value)


def mix_bv(tm: TermManager, sort, x):
    x = tm.mk_term(
        Kind.BV_XOR,
        [x, tm.mk_term(Kind.BV_LSHR, [x, bv(tm, sort, 30)])],
    )
    x = tm.mk_term(Kind.BV_MUL, [x, bv(tm, sort, A)])
    x = tm.mk_term(
        Kind.BV_XOR,
        [x, tm.mk_term(Kind.BV_LSHR, [x, bv(tm, sort, 27)])],
    )
    x = tm.mk_term(Kind.BV_MUL, [x, bv(tm, sort, B)])
    x = tm.mk_term(
        Kind.BV_XOR,
        [x, tm.mk_term(Kind.BV_LSHR, [x, bv(tm, sort, 31)])],
    )
    return x


def model_u64(solver: Bitwuzla, term) -> int:
    return int(solver.get_value(term).value(16), 16)


def collision_status(bits: int, length: int, timeout_ms: int) -> dict[str, Any]:
    tm = TermManager()
    options = Options()
    options.set(Option.PRODUCE_MODELS, True)
    options.set(Option.SAT_SOLVER, "cadical")

    sort = tm.mk_bv_sort(64)
    left = tm.mk_const(sort, "left_state")
    right = tm.mk_const(sort, "right_state")

    solver = Bitwuzla(tm, options)

    # Unsigned symmetry break.
    solver.assert_formula(tm.mk_term(Kind.BV_ULT, [left, right]))

    for k in range(length):
        off = bv(tm, sort, (k + 1) * GAMMA)
        lstate = tm.mk_term(Kind.BV_ADD, [left, off])
        rstate = tm.mk_term(Kind.BV_ADD, [right, off])
        lo = tm.mk_term(Kind.BV_EXTRACT, [mix_bv(tm, sort, lstate)], [bits - 1, 0])
        ro = tm.mk_term(Kind.BV_EXTRACT, [mix_bv(tm, sort, rstate)], [bits - 1, 0])
        solver.assert_formula(tm.mk_term(Kind.EQUAL, [lo, ro]))

    deadline = time.monotonic() + timeout_ms / 1000.0

    def terminator(_):
        return time.monotonic() >= deadline

    solver.configure_terminator(terminator)

    started = time.perf_counter()
    result = solver.check_sat()
    elapsed = time.perf_counter() - started

    if str(result) == "sat":
        return {
            "status": "ambiguous",
            "states": [model_u64(solver, left), model_u64(solver, right)],
            "elapsed_seconds": elapsed,
            "solver": "bitwuzla",
        }
    if str(result) == "unsat":
        return {
            "status": "injective",
            "elapsed_seconds": elapsed,
            "solver": "bitwuzla",
        }
    return {
        "status": "unknown",
        "reason": str(result),
        "elapsed_seconds": elapsed,
        "solver": "bitwuzla",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", type=int, nargs="+", default=[32])
    parser.add_argument("--lengths", type=int, nargs="+", default=[2, 3])
    parser.add_argument("--timeout-ms", type=int, default=30000)
    args = parser.parse_args()

    for bits in args.bits:
        for length in args.lengths:
            result = collision_status(bits, length, args.timeout_ms)
            print(json.dumps({"bits": bits, "length": length, **result}))


if __name__ == "__main__":
    main()
