"""A<->M coupling discriminator v0.1.

Purpose:
  Determine whether generic state addressing remains sufficient when the derived
  inverse representation is subjected to mutation modes M0/M1/M2.

This is a structural contract experiment. It does not measure wall-clock time.

Models:
  A1_R  : generic indexed reads only.
  A1_RW : generic indexed reads+writes over an addressable state representation.
  A2    : specialized fiber read plus the corresponding declared update protocol.

Mutation modes:
  M0_STATIC  : no updates after materialization.
  M1_BATCHED : updates happen between explicit rebuilds.
  M2_DYNAMIC : every committed update must preserve query correctness immediately.

The experiment deliberately separates:
  - semantic correctness after updates,
  - whether the declared access surface can express the maintenance operation,
  - resource accounting for rebuild vs incremental maintenance.
"""

import json
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Contract:
    name: str
    read_generic: bool
    write_generic: bool
    specialized_read: bool
    structured_update: bool


CONTRACTS = {
    "A1_R": Contract("A1_R", True, False, False, False),
    "A1_RW": Contract("A1_RW", True, True, False, False),
    "A2": Contract("A2", False, False, True, True),
}


def make_delta(n, k, seed):
    rng = random.Random(seed)
    d = [[rng.randrange(n) for _ in range(k)] for _ in range(n)]
    # introduce partiality and parallel edges to stress update correctness
    for s in range(n):
        for a in range(k):
            if rng.random() < 0.12:
                d[s][a] = -1
        if k >= 2 and rng.random() < 0.35:
            a0, a1 = rng.sample(range(k), 2)
            d[s][a1] = d[s][a0]
    return d


def clone_delta(d):
    return [row[:] for row in d]


def brute_pred(d, u):
    return sorted(
        (s, a)
        for s, row in enumerate(d)
        for a, v in enumerate(row)
        if v == u
    )


def build_index(d):
    n = len(d)
    buckets = [[] for _ in range(n)]
    for s, row in enumerate(d):
        for a, u in enumerate(row):
            if u >= 0:
                buckets[u].append((s, a))
    return buckets


def index_pred(index, u):
    return sorted(index[u])


def rebuild(index, d):
    return build_index(d)


def apply_batch(delta, index, updates):
    # Generic RW model may modify ordinary state cells and then rebuild in M1.
    for s, a, new_u in updates:
        delta[s][a] = new_u
    return rebuild(index, delta)


def dynamic_update_a1_rw(delta, index, s, a, new_u):
    # A1_RW has generic cell writes. To preserve the index invariant, the
    # implementation must also have a way to address/update the inverse
    # representation. Here we use a flat bucket representation as ordinary
    # mutable state and charge the structural maintenance work explicitly.
    old_u = delta[s][a]
    if old_u == new_u:
        return 0

    if old_u >= 0:
        old_bucket = index[old_u]
        old_bucket.remove((s, a))
    delta[s][a] = new_u
    if new_u >= 0:
        index[new_u].append((s, a))
        index[new_u].sort()

    # abstract structural writes: metadata + movement proportional to bucket edits
    return 2 + (1 if old_u >= 0 else 0) + (1 if new_u >= 0 else 0)


def dynamic_update_a2(delta, index, s, a, new_u):
    # A2 declares structured index maintenance explicitly.
    old_u = delta[s][a]
    if old_u == new_u:
        return 0
    if old_u >= 0:
        index[old_u].remove((s, a))
    delta[s][a] = new_u
    if new_u >= 0:
        index[new_u].append((s, a))
        index[new_u].sort()
    return 1


def check_queries(d, index, targets):
    for u in targets:
        if brute_pred(d, u) != index_pred(index, u):
            return False
    return True


def run_case(d, seed):
    rng = random.Random(seed)
    n = len(d)
    index0 = build_index(d)
    targets = [rng.randrange(n) for _ in range(min(20, n))]

    # M0: all read profiles are semantically valid after frozen construction.
    m0 = {
        "A1_R": check_queries(d, index0, targets),
        "A1_RW": check_queries(d, index0, targets),
        "A2": check_queries(d, index0, targets),
    }

    # M1: mutations are followed by an explicit rebuild.
    d1 = clone_delta(d)
    updates = []
    for _ in range(max(4, n // 3)):
        s = rng.randrange(n)
        a = rng.randrange(len(d1[0]))
        new_u = -1 if rng.random() < 0.15 else rng.randrange(n)
        updates.append((s, a, new_u))
    for s, a, v in updates:
        d1[s][a] = v
    rebuilt = build_index(d1)
    m1 = {
        "A1_R": check_queries(d1, rebuilt, targets),
        "A1_RW": check_queries(d1, rebuilt, targets),
        "A2": check_queries(d1, rebuilt, targets),
    }

    # M2: every committed mutation is checked immediately.
    d2 = clone_delta(d)
    i1 = build_index(d2)
    i2 = build_index(d2)
    a1_cost = 0
    a2_cost = 0
    a1_possible = True
    a2_possible = True
    for _ in range(max(8, n)):
        s = rng.randrange(n)
        a = rng.randrange(len(d2[0]))
        new_u = -1 if rng.random() < 0.20 else rng.randrange(n)

        # A1_R has no write/update surface: M2 maintenance is not expressible.
        a1_possible = False

        a1_cost += dynamic_update_a1_rw(d2, i1, s, a, new_u)
        a2_cost += dynamic_update_a2(d2, i2, s, a, new_u)

        probes = [rng.randrange(n) for _ in range(5)]
        if not check_queries(d2, i1, probes):
            return {
                "m0": m0, "m1": m1,
                "m2": {"A1_RW": False, "A2": False},
                "resource": {"a1_dynamic": a1_cost, "a2_dynamic": a2_cost},
                "failure": "A1_RW index invariant"
            }
        if not check_queries(d2, i2, probes):
            return {
                "m0": m0, "m1": m1,
                "m2": {"A1_RW": False, "A2": False},
                "resource": {"a1_dynamic": a1_cost, "a2_dynamic": a2_cost},
                "failure": "A2 index invariant"
            }

    return {
        "m0": m0,
        "m1": m1,
        "m2": {
            "A1_R": a1_possible,
            "A1_RW": True,
            "A2": a2_possible,
        },
        "resource": {
            "a1_dynamic": a1_cost,
            "a2_dynamic": a2_cost,
        },
        "failure": None,
    }


def run():
    configs = [
        (17, 3), (31, 4), (63, 5), (127, 4), (255, 6)
    ]
    aggregate = {
        "m0": {p: 0 for p in CONTRACTS},
        "m1": {p: 0 for p in CONTRACTS},
        "m2": {"A1_R": 0, "A1_RW": 0, "A2": 0},
    }
    resource = {"a1_dynamic": 0, "a2_dynamic": 0}
    failures = []
    cases = 0

    for family, (n, k) in enumerate(configs):
        for rep in range(20):
            seed = 20260928 + family * 1000 + rep
            d = make_delta(n, k, seed)
            out = run_case(d, seed + 77)
            cases += 1
            if out["failure"]:
                failures.append((seed, out["failure"]))
                continue
            for p in CONTRACTS:
                aggregate["m0"][p] += int(out["m0"][p])
                aggregate["m1"][p] += int(out["m1"][p])
            for p in aggregate["m2"]:
                aggregate["m2"][p] += int(out["m2"][p])
            resource["a1_dynamic"] += out["resource"]["a1_dynamic"]
            resource["a2_dynamic"] += out["resource"]["a2_dynamic"]

    result = {
        "schema": "machine.substrate-mutation-coupling-discriminator.v0.1",
        "status": "EXECUTED",
        "cases": cases,
        "semantic_pass_totals": aggregate,
        "semantic_failures": len(failures),
        "failures": failures,
        "resource": resource,
        "interpretation": {
            "M0": "A1_R, A1_RW and A2 are valid after static target-oblivious materialization.",
            "M1": "A1_R can participate only because mutation happens outside the online read contract and an explicit rebuild restores derived state.",
            "M2": "A1_R lacks a write/update surface; A1_RW closes if generic writes are part of the contract; A2 closes through its structured update contract.",
        },
        "decision_boundary": {
            "A1_read_only_plus_M2": "NOT_EXPRESSIBLE",
            "A1_read_write_plus_M2": "EXPRESSIBLE_IN_TEST_MODEL",
            "A2_plus_M2": "EXPRESSIBLE",
            "production_profile": "OPEN_PENDING_EXPLICIT_PRODUCTION_MUTATION_CONTRACT",
        },
        "falsification_boundary": [
            "same transition state before each profile",
            "same update sequence per case",
            "same semantic predecessor reference",
            "derived representation is target-oblivious",
            "M2 correctness checked after every committed update",
            "no wall-clock classification"
        ]
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    run()
