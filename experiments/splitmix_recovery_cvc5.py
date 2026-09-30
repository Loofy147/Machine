#!/usr/bin/env python3
"""Independent cvc5 oracle for truncated SplitMix64.

This intentionally mirrors the Z3 QF_BV formulation so that solver
performance can be compared without changing the mathematical query.
UNKNOWN/TIMEOUT is never promoted to a proof.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

import cvc5
from cvc5 import Kind

MASK = (1 << 64) - 1
GAMMA = 0x9E3779B97F4A7C15
A = 0xBF58476D1CE4E5B9
B = 0x94D049BB133111EB

SOLVER_LOGIC = "QF_BV"


def bv_const(slv: cvc5.Solver, width: int, value: int):
    return slv.mkBitVector(width, value & ((1 << width) - 1))


def bv_and(slv, a, b):
    return slv.mkTerm(Kind.BITVECTOR_AND, a, b)


def mix_bv(slv: cvc5.Solver, x):
    sixty4 = bv_const(slv, 64, MASK)
    # Preserve explicit width semantics in the expression.
    x = bv_and(slv, x, sixty4)
    x = slv.mkTerm(
        Kind.BITVECTOR_XOR,
        x,
        slv.mkTerm(Kind.BITVECTOR_LSHR, x, bv_const(slv, 64, 30)),
    )
    x = slv.mkTerm(Kind.BITVECTOR_MULT, x, bv_const(slv, 64, A))
    x = slv.mkTerm(
        Kind.BITVECTOR_XOR,
        x,
        slv.mkTerm(Kind.BITVECTOR_LSHR, x, bv_const(slv, 64, 27)),
    )
    x = slv.mkTerm(Kind.BITVECTOR_MULT, x, bv_const(slv, 64, B))
    x = slv.mkTerm(
        Kind.BITVECTOR_XOR,
        x,
        slv.mkTerm(Kind.BITVECTOR_LSHR, x, bv_const(slv, 64, 31)),
    )
    return x


def low_bits(slv, output, bits: int):
    op = slv.mkOp(Kind.BITVECTOR_EXTRACT, bits - 1, 0)
    return slv.mkTerm(op, output)


def make_solver(timeout_ms: int, bitblast: str, bv_sat_solver: str,
                 bv_abstraction: bool):
    slv = cvc5.Solver()
    slv.setLogic(SOLVER_LOGIC)
    slv.setOption("produce-models", "true")
    slv.setOption("tlimit-per", str(timeout_ms))
    slv.setOption("bitblast", bitblast)
    slv.setOption("bv-sat-solver", bv_sat_solver)
    slv.setOption("bv-abstraction", "true" if bv_abstraction else "false")
    return slv


def value_u64(slv, term) -> int:
    value = slv.getValue(term)
    return int(value.getBitVectorValue(16), 16)


def mix64(x: int) -> int:
    x &= MASK
    x ^= x >> 30
    x = (x * A) & MASK
    x ^= x >> 27
    x = (x * B) & MASK
    x ^= x >> 31
    return x


def generate_outputs(seed: int, length: int) -> list[int]:
    state = seed & MASK
    out = []
    for _ in range(length):
        state = (state + GAMMA) & MASK
        out.append(mix64(state))
    return out


def collision_status(bits: int, length: int, timeout_ms: int,
                     bitblast: str, bv_sat_solver: str,
                     bv_abstraction: bool) -> dict[str, Any]:
    slv = make_solver(timeout_ms, bitblast, bv_sat_solver, bv_abstraction)
    s1 = slv.mkConst(slv.mkBitVectorSort(64), "left_state")
    s2 = slv.mkConst(slv.mkBitVectorSort(64), "right_state")

    # Unsigned symmetry break.
    slv.assertFormula(slv.mkTerm(Kind.BITVECTOR_ULT, s1, s2))

    for k in range(length):
        off = bv_const(slv, 64, (k + 1) * GAMMA)
        o1 = mix_bv(slv, slv.mkTerm(Kind.BITVECTOR_ADD, s1, off))
        o2 = mix_bv(slv, slv.mkTerm(Kind.BITVECTOR_ADD, s2, off))
        slv.assertFormula(
            slv.mkTerm(
                Kind.EQUAL,
                low_bits(slv, o1, bits),
                low_bits(slv, o2, bits),
            )
        )

    started = time.perf_counter()
    result = slv.checkSat()
    elapsed = time.perf_counter() - started

    common = {
        "history_depth": length - 1,
        "elapsed_seconds": elapsed,
        "solver": "cvc5",
        "solver_version": getattr(cvc5, "__version__", "unknown"),
        "solver_logic": SOLVER_LOGIC,
        "bitblast": bitblast,
        "bv_sat_solver": bv_sat_solver,
        "bv_abstraction": bv_abstraction,
    }

    if result.isSat():
        return {
            "status": "ambiguous",
            "states": [value_u64(slv, s1), value_u64(slv, s2)],
            **common,
        }
    if result.isUnsat():
        return {"status": "injective", **common}

    return {
        "status": "unknown",
        "reason": str(result),
        **common,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", type=int, nargs="+", default=[32])
    parser.add_argument("--lengths", type=int, nargs="+", default=[2, 3])
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--bitblast", choices=["lazy", "eager"], default="eager")
    parser.add_argument(
        "--bv-sat-solver",
        choices=["cadical", "kissat", "cryptominisat", "minisat"],
        default="kissat",
    )
    parser.add_argument("--bv-abstraction", action="store_true")
    parser.add_argument("--fail-on-unknown", action="store_true")
    args = parser.parse_args()

    unknown_seen = False
    print(json.dumps({
        "solver": "cvc5",
        "solver_version": getattr(cvc5, "__version__", "unknown"),
        "logic": SOLVER_LOGIC,
        "timeout_ms": args.timeout_ms,
        "bitblast": args.bitblast,
        "bv_sat_solver": args.bv_sat_solver,
        "bv_abstraction": args.bv_abstraction,
    }))

    for bits in args.bits:
        for length in args.lengths:
            result = collision_status(
                bits,
                length,
                args.timeout_ms,
                args.bitblast,
                args.bv_sat_solver,
                args.bv_abstraction,
            )
            unknown_seen |= result["status"] == "unknown"
            print(json.dumps({
                "bits": bits,
                "length": length,
                **result,
            }))

    if args.fail_on_unknown and unknown_seen:
        print(
            "ERROR: cvc5 returned UNKNOWN/TIMEOUT; no proof promoted.",
            file=sys.stderr,
        )
        raise SystemExit(2)


if __name__ == "__main__":
    main()
