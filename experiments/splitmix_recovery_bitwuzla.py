#!/usr/bin/env python3
"""Bitwuzla QF_BV oracle for truncated SplitMix64 collisions.

The formula is emitted as SMT-LIB and parsed by Bitwuzla, avoiding dependence
on Python enum spelling while preserving the exact fixed-width semantics.
"""

from __future__ import annotations

import argparse
import json
import time
from typing import Any

from bitwuzla import Options, Option, Parser, TermManager

MASK = (1 << 64) - 1
GAMMA = 0x9E3779B97F4A7C15
A = 0xBF58476D1CE4E5B9
B = 0x94D049BB133111EB


def mix_smt(x: str) -> str:
    return (
        f"(bvxor {x} (bvlshr {x} (_ bv30 64)))"
        f""
    )


def mix_smt_full(x: str) -> str:
    z1 = f"(bvxor {x} (bvlshr {x} (_ bv30 64)))"
    z2 = f"(bvmul {z1} (_ bv{A} 64))"
    z3 = f"(bvxor {z2} (bvlshr {z2} (_ bv27 64)))"
    z4 = f"(bvmul {z3} (_ bv{B} 64))"
    return f"(bvxor {z4} (bvlshr {z4} (_ bv31 64)))"


def collision_status(bits: int, length: int, timeout_ms: int, bv_solver: str) -> dict[str, Any]:
    if not 1 <= bits <= 64:
        raise ValueError("bits must be in [1,64]")
    if length < 1:
        raise ValueError("length must be positive")

    tm = TermManager()
    options = Options()
    options.set(Option.PRODUCE_MODELS, True)
    options.set(Option.SAT_SOLVER, "cadical")
    options.set(Option.BV_SOLVER, bv_solver)

    parser = Parser(tm, options)

    assertions = [
        "(set-logic QF_BV)",
        "(set-option :produce-models true)",
        "(declare-const left_state (_ BitVec 64))",
        "(declare-const right_state (_ BitVec 64))",
        "(assert (bvult left_state right_state))",
    ]

    for k in range(length):
        off = (k + 1) * GAMMA & MASK
        lstate = f"(bvadd left_state (_ bv{off} 64))"
        rstate = f"(bvadd right_state (_ bv{off} 64))"
        lo = (
            f"((_ extract {bits - 1} 0) "
            f"{mix_smt_full(lstate)})"
        )
        ro = (
            f"((_ extract {bits - 1} 0) "
            f"{mix_smt_full(rstate)})"
        )
        assertions.append(f"(assert (= {lo} {ro}))")

    formula = "".join(assertions)

    parser.parse(formula, True, False)
    solver = parser.bitwuzla()
    left = parser.parse_term("left_state")
    right = parser.parse_term("right_state")

    deadline = time.monotonic() + timeout_ms / 1000.0

    def terminator():
        return time.monotonic() >= deadline

    solver.configure_terminator(terminator)

    started = time.perf_counter()
    result = solver.check_sat()
    elapsed = time.perf_counter() - started

    status = str(result).lower()
    common = {
        "elapsed_seconds": elapsed,
        "solver": "bitwuzla",
        "timeout_ms": timeout_ms,
        "bv_solver": bv_solver,
    }

    if status == "sat":
        return {
            "status": "ambiguous",
            "states": [
                int(solver.get_value(left).value(16), 16),
                int(solver.get_value(right).value(16), 16),
            ],
            **common,
        }
    if status == "unsat":
        return {
            "status": "injective",
            **common,
        }
    return {
        "status": "unknown",
        "reason": status,
        **common,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", type=int, nargs="+", default=[32])
    parser.add_argument("--lengths", type=int, nargs="+", default=[2, 3])
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--bv-solver", choices=["bitblast", "prop"], default="bitblast")
    args = parser.parse_args()

    for bits in args.bits:
        for length in args.lengths:
            print(json.dumps({
                "bits": bits,
                "length": length,
                **collision_status(
                    bits, length, args.timeout_ms, args.bv_solver
                ),
            }))


if __name__ == "__main__":
    main()
