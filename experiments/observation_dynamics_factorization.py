#!/usr/bin/env python3
"""Exact experiments for observation-dynamics factorization.

E1 inverse implementation
E2 independent conjugacy
E3 complete-output prediction
E4 sampled arbitrary-bijection conjugacy
E5 truncation sanity
E6 one-observation nonfactorization witnesses
E7 full-period certificate
E8 exact finite-history partition refinement
E9 single-cycle period/quotient check

The script is experimental evidence; the mathematical specification is separate.
"""

from __future__ import annotations

import argparse
import math
import random
from dataclasses import asdict, dataclass
from typing import Callable, Sequence

MASK = (1 << 64) - 1
MOD = 1 << 64

GAMMA = 0x9E3779B97F4A7C15
A = 0xBF58476D1CE4E5B9
B = 0x94D049BB133111EB
A_INV = 0x96DE1B173F119089
B_INV = 0x319642B2D24D8EC3


def mix64(x: int) -> int:
    x &= MASK
    x ^= x >> 30
    x = (x * A) & MASK
    x ^= x >> 27
    x = (x * B) & MASK
    x ^= x >> 31
    return x


def unmix64(y: int) -> int:
    y &= MASK
    y ^= (y >> 31) ^ (y >> 62)
    y = (y * B_INV) & MASK
    y ^= (y >> 27) ^ (y >> 54)
    y = (y * A_INV) & MASK
    y ^= (y >> 30) ^ (y >> 60)
    return y


def trunc_obs(bits: int) -> Callable[[int], int]:
    if not 1 <= bits <= 64:
        raise ValueError("bits must be in [1,64]")
    mask = (1 << bits) - 1
    return lambda s: mix64(s) & mask


def cycle_partition(perm: Sequence[int]) -> list[int]:
    seen = [False] * len(perm)
    lengths = []
    for start in range(len(perm)):
        if seen[start]:
            continue
        cur = start
        n = 0
        while not seen[cur]:
            seen[cur] = True
            cur = perm[cur]
            n += 1
        lengths.append(n)
    return sorted(lengths)


@dataclass(frozen=True)
class HistoryRow:
    depth: int
    classes: int
    largest_fiber: int
    discrete: bool
    stable_after_depth: bool


def analyze_history(
    states: Sequence[int],
    tau: Callable[[int], int],
    h: Callable[[int], int],
) -> dict:
    states = list(states)

    labels: dict[int, int] = {}
    partition = []
    for s in states:
        key = h(s)
        labels.setdefault(key, len(labels))
        partition.append(labels[key])

    orbit = list(states)
    previous_classes = None
    recovery_depth = 0 if len(set(partition)) == len(states) else None
    rows: list[HistoryRow] = []

    for depth in range(len(states)):
        counts: dict[int, int] = {}
        for label in partition:
            counts[label] = counts.get(label, 0) + 1

        classes = len(counts)
        discrete = classes == len(states)
        stable = previous_classes is not None and classes == previous_classes

        rows.append(
            HistoryRow(
                depth=depth,
                classes=classes,
                largest_fiber=max(counts.values()),
                discrete=discrete,
                stable_after_depth=stable,
            )
        )

        if discrete and recovery_depth is None:
            recovery_depth = depth

        if stable:
            return {
                "rows": [asdict(row) for row in rows],
                "stabilization_depth": depth - 1,
                "recovery_depth": recovery_depth,
            }

        previous_classes = classes
        orbit = [tau(s) for s in orbit]

        refined: dict[tuple[int, int], int] = {}
        next_partition = []
        for old, s_next in zip(partition, orbit):
            key = (old, h(s_next))
            refined.setdefault(key, len(refined))
            next_partition.append(refined[key])
        partition = next_partition

    raise RuntimeError("finite partition did not stabilize within |S| steps")


def least_period(word: Sequence[int]) -> int:
    n = len(word)
    for p in range(1, n + 1):
        if n % p:
            continue
        if all(word[i] == word[(i + p) % n] for i in range(n)):
            return p
    raise AssertionError("every finite cyclic word has a period")


def e1_inverse(samples: int = 200_000) -> dict:
    rng = random.Random(2026)
    a_inv = pow(A, -1, MOD)
    b_inv = pow(B, -1, MOD)
    fwd = 0
    for _ in range(samples):
        x = rng.getrandbits(64)
        if unmix64(mix64(x)) != x:
            fwd += 1
    bwd = 0
    for _ in range(samples):
        y = rng.getrandbits(64)
        if mix64(unmix64(y)) != y:
            bwd += 1
    edges = [0, 1, MASK, MASK - 1, 1 << 63, (1 << 63) - 1, GAMMA, A, B]
    edge_ok = all(unmix64(mix64(x)) == x and mix64(unmix64(x)) == x for x in edges)
    return {
        "A_inv_match": a_inv == A_INV,
        "B_inv_match": b_inv == B_INV,
        "A_inverse_identity": (A * a_inv) & MASK == 1,
        "B_inverse_identity": (B * b_inv) & MASK == 1,
        "gamma_odd": GAMMA & 1 == 1,
        "forward_failures": fwd,
        "backward_failures": bwd,
        "edge_ok": edge_ok,
        "samples": samples,
    }


def e2_conjugacy(samples: int = 200_000) -> dict:
    rng = random.Random(2026)
    failures = 0
    for _ in range(samples):
        s = rng.getrandbits(64)
        y = mix64(s)
        true_next = mix64((s + GAMMA) & MASK)
        formula_next = mix64((unmix64(y) + GAMMA) & MASK)
        failures += true_next != formula_next
    return {"failures": failures, "samples": samples}


def e3_prediction(length: int = 200) -> dict:
    rng = random.Random(2026)
    state = rng.getrandbits(64)
    outputs = []
    for _ in range(length):
        state = (state + GAMMA) & MASK
        outputs.append(mix64(state))
    recovered = unmix64(outputs[0])
    predicted = [mix64((recovered + k * GAMMA) & MASK) for k in range(length)]
    return {
        "length": length,
        "matches": predicted == outputs,
        "first_output": outputs[0],
    }


def e4_abstract_conjugacy(widths=(4, 6, 8, 10, 12, 14)) -> dict:
    rng = random.Random(42)
    rows = []
    for w in widths:
        m = 1 << w
        f = list(range(m))
        rng.shuffle(f)
        finv = [0] * m
        for s, y in enumerate(f):
            finv[y] = s

        for c in sorted(set([1, 3, m // 2, m // 4, m - 1])):
            if not 0 < c < m:
                continue
            g = math.gcd(c, m)
            tau = [(s + c) % m for s in range(m)]
            t = [f[(finv[y] + c) % m] for y in range(m)]
            expected = sorted([m // g] * g)
            cycles_ok = cycle_partition(tau) == cycle_partition(t)
            formula_ok = cycle_partition(tau) == expected

            s = rng.randrange(m)
            cur_s, cur_y = s, f[s]
            trajectory_ok = True
            for _ in range(min(m, 500)):
                cur_s = tau[cur_s]
                cur_y = t[cur_y]
                if f[cur_s] != cur_y:
                    trajectory_ok = False
                    break

            rows.append({
                "w": w,
                "c": c,
                "gcd": g,
                "cycle_match": cycles_ok,
                "formula_match": formula_ok,
                "trajectory_match": trajectory_ok,
            })

    return {
        "cases": len(rows),
        "all_pass": all(
            row["cycle_match"] and row["formula_match"] and row["trajectory_match"]
            for row in rows
        ),
        "rows": rows,
    }


def e4_exhaustive_small(max_width: int = 3) -> dict:
    """Exhaust all bijections and increments for widths <= max_width.

    This is a true exhaustive check over the permutation family for each
    included width, unlike E4's sampled-bijection experiment.
    """
    import itertools

    total_instances = 0
    rows = []

    for w in range(1, max_width + 1):
        m = 1 << w
        for f_tuple in itertools.permutations(range(m)):
            f = list(f_tuple)
            finv = [0] * m
            for s, y in enumerate(f):
                finv[y] = s

            for c in range(1, m):
                g = math.gcd(c, m)
                tau = [(s + c) % m for s in range(m)]
                t = [f[(finv[y] + c) % m] for y in range(m)]
                expected = sorted([m // g] * g)

                if cycle_partition(tau) != cycle_partition(t):
                    raise AssertionError((w, f_tuple, c, "cycle"))
                if cycle_partition(tau) != expected:
                    raise AssertionError((w, f_tuple, c, "cycle_formula"))

                for s0 in range(m):
                    cur_s = s0
                    cur_y = f[s0]
                    for _ in range(m):
                        cur_s = tau[cur_s]
                        cur_y = t[cur_y]
                        if f[cur_s] != cur_y:
                            raise AssertionError(
                                (w, f_tuple, c, s0, "trajectory")
                            )

                total_instances += 1

        rows.append({
            "w": w,
            "permutations": math.factorial(m),
            "increments": m - 1,
            "tested_bijection_increment_instances": math.factorial(m) * (m - 1),
        })

    return {
        "max_width": max_width,
        "total_instances": total_instances,
        "all_pass": True,
        "rows": rows,
    }
def e5_truncation_counts(bits=(32, 16, 8), trials=300_000) -> dict:
    rng = random.Random(7)
    out = {}
    for b in bits:
        mask = (1 << b) - 1
        seen = set()
        repeated = 0
        for _ in range(trials):
            y = mix64(rng.getrandbits(64)) & mask
            if y in seen:
                repeated += 1
            else:
                seen.add(y)
        out[b] = {
            "trials": trials,
            "distinct": len(seen),
            "repeated_arrivals": repeated,
            "exact_fiber_size": 1 << (64 - b),
        }
    return out


def e6_nonfactor_witness(bits=(32, 16, 8), attempts=100_000) -> dict:
    rng = random.Random(8)
    out = {}
    for b in bits:
        mask = (1 << b) - 1
        witness = None
        for attempt in range(1, attempts + 1):
            y1 = rng.getrandbits(64)
            y2 = y1 ^ (1 << b)
            s1 = unmix64(y1)
            s2 = unmix64(y2)
            n1 = mix64((s1 + GAMMA) & MASK) & mask
            n2 = mix64((s2 + GAMMA) & MASK) & mask
            if n1 != n2:
                witness = {
                    "attempt": attempt,
                    "state1": s1,
                    "state2": s2,
                    "same_observation": y1 & mask,
                    "next1": n1,
                    "next2": n2,
                }
                break
        out[b] = witness
    return out


def e7_full_period_certificate(bits=tuple(range(1, 64))) -> dict:
    """Use one deterministic witness whose low bit changes after 2^63 steps.

    If h_b(s) != h_b(tau^(2^63)(s)) for one state in a 2^64 single cycle,
    the cyclic observation word cannot have any proper period, because every
    proper divisor of 2^64 divides 2^63.
    """
    witness_state = 0x443CDEF36840FF07
    half_period_state = (witness_state + (1 << 63)) & MASK
    y1 = mix64(witness_state)
    y2 = mix64(half_period_state)
    out = {
        "witness_state": witness_state,
        "half_period_state": half_period_state,
        "full_outputs": (y1, y2),
        "xor": y1 ^ y2,
        "low_bit_differs": (y1 & 1) != (y2 & 1),
        "all_requested_widths_certified": True,
        "widths": {},
    }
    for b in bits:
        if not 1 <= b <= 63:
            raise ValueError("certificate widths must be in [1,63]")
        mask = (1 << b) - 1
        obs1 = y1 & mask
        obs2 = y2 & mask
        certified = obs1 != obs2
        out["widths"][b] = {
            "obs1": obs1,
            "obs2": obs2,
            "certifies_full_period": certified,
        }
        out["all_requested_widths_certified"] &= certified
    return out


def e8_history(widths=(6, 8, 10)) -> dict:
    out = {}
    for w in widths:
        m = 1 << w
        c = 0x9E37 % m
        f = list(range(m))
        random.Random(1000 + w).shuffle(f)
        b = w // 2
        mask = (1 << b) - 1

        def tau(s, c=c, m=m):
            return (s + c) % m

        def h(s, f=f, mask=mask):
            return f[s] & mask

        a = analyze_history(range(m), tau, h)
        out[w] = {
            "M": m,
            "c": c,
            "observation_bits": b,
            **a,
        }
    return out


def e9_single_cycle_period(widths=(4, 6, 8, 10)) -> dict:
    out = {}
    for w in widths:
        m = 1 << w
        c = 1
        states = list(range(m))
        f = list(states)
        random.Random(2000 + w).shuffle(f)
        b = max(1, w // 2)
        mask = (1 << b) - 1
        word = [f[s] & mask for s in states]
        period = least_period(word)

        def tau(s, m=m, c=c):
            return (s + c) % m

        def h(s, f=f, mask=mask):
            return f[s] & mask

        a = analyze_history(states, tau, h)
        stable_classes = a["rows"][-1]["classes"]
        out[w] = {
            "M": m,
            "c": c,
            "observation_bits": b,
            "least_period": period,
            "stable_quotient_classes": stable_classes,
            "stabilization_depth": a["stabilization_depth"],
            "recovery_depth": a["recovery_depth"],
            "period_matches_quotient": period == stable_classes,
            "full_period": period == m,
            "d_equals_r_when_full": (
                period != m or a["stabilization_depth"] == a["recovery_depth"]
            ),
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--e1-samples", type=int, default=200_000)
    parser.add_argument("--e2-samples", type=int, default=200_000)
    parser.add_argument("--prediction-length", type=int, default=200)
    parser.add_argument("--history-width", type=int, nargs="*", default=[6, 8, 10])
    args = parser.parse_args()

    print("== E1 inverse implementation ==")
    print(e1_inverse(args.e1_samples))

    print("\n== E2 independent conjugacy ==")
    print(e2_conjugacy(args.e2_samples))

    print("\n== E3 complete-output prediction ==")
    print(e3_prediction(args.prediction_length))

    print("\n== E4 abstract sampled-bijection conjugacy ==")
    e4 = e4_abstract_conjugacy()
    print({"cases": e4["cases"], "all_pass": e4["all_pass"]})

    print("\n== E4X exhaustive all-bijection conjugacy, w<=3 ==")
    e4x = e4_exhaustive_small(3)
    print({
        "total_instances": e4x["total_instances"],
        "all_pass": e4x["all_pass"],
        "rows": e4x["rows"],
    })

    print("\n== E5 truncation sanity ==")
    print(e5_truncation_counts())

    print("\n== E6 nonfactorization witnesses ==")
    print(e6_nonfactor_witness())

    print("\n== E7 full-period certificate ==")
    print(e7_full_period_certificate())

    print("\n== E8 exact history refinement ==")
    for w, row in e8_history(args.history_width).items():
        print(f"w={w}: d={row['stabilization_depth']} r={row['recovery_depth']}")
        for item in row["rows"]:
            print(" ", item)

    print("\n== E9 single-cycle period/quotient ==")
    print(e9_single_cycle_period())


if __name__ == "__main__":
    main()
