#!/usr/bin/env python3
"""Target-oblivious precomputation / online computation frontier v0."""

from __future__ import annotations

import argparse
import json
import math
import random
from array import array
from collections import deque
from pathlib import Path

TARGET_ORDER_SEED = 0x5EED
IID_QUERY_SEED = 0xC001
HELDOUT_QUERY_SEED = 0xBEEF


def op(v: int, which: int, m: int) -> int:
    return ((v + 1) % m, (v + 7) % m, (2 * v) % m)[which]


def circ_dist(a: int, b: int, m: int) -> int:
    d = abs(a - b) % m
    return min(d, m - d)


def shortest_len(start: int, target: int, m: int) -> int:
    if start == target:
        return 0
    seen = bytearray(m)
    seen[start] = 1
    q = deque([(start, 0)])
    while q:
        v, d = q.popleft()
        for which in range(3):
            nv = op(v, which, m)
            if nv == target:
                return d + 1
            if not seen[nv]:
                seen[nv] = 1
                q.append((nv, d + 1))
    raise AssertionError("unreachable")


def build_target_policy(m: int, target: int):
    action = bytearray([255]) * m
    dist = array("i", [-1]) * m
    dist[target] = 0
    q = deque([target])
    while q:
        v = q.popleft()
        nd = dist[v] + 1

        p = (v - 1) % m
        if dist[p] < 0:
            dist[p] = nd
            action[p] = 0
            q.append(p)

        p = (v - 7) % m
        if dist[p] < 0:
            dist[p] = nd
            action[p] = 1
            q.append(p)

        if m % 2 == 0:
            if v % 2 == 0:
                for p in ((v // 2) % m, (v // 2 + m // 2) % m):
                    if dist[p] < 0:
                        dist[p] = nd
                        action[p] = 2
                        q.append(p)
        else:
            p = (v * pow(2, -1, m)) % m
            if dist[p] < 0:
                dist[p] = nd
                action[p] = 2
                q.append(p)

    assert all(x >= 0 for x in dist)
    return action, dist


def lookahead(start: int, target: int, budget: int, m: int, depth: int):
    """Fixed transition topology; future depth is budget-capped."""
    v = start
    expanded = 0

    while budget > 0 and v != target:
        further = min(depth, budget - 1)
        best = None

        for which in range(3):
            nv = op(v, which, m)

            def score(x: int, d: int) -> int:
                nonlocal expanded
                expanded += 1
                if d == 0:
                    return circ_dist(x, target, m)
                best_value = circ_dist(x, target, m)
                for child in range(3):
                    best_value = min(best_value, score(op(x, child, m), d - 1))
                return best_value

            cand = (score(nv, further), which, nv)
            if best is None or cand < best:
                best = cand

        v = best[2]
        budget -= 1

    return v == target, expanded


def cached(start: int, target: int, budget: int, m: int, policy):
    v = start
    work = 0
    while budget > 0 and v != target:
        which = policy[v]
        if which == 255:
            return False, work
        v = op(v, which, m)
        work += 1
        budget -= 1
    return v == target, work


def target_order(m: int):
    xs = list(range(m))
    random.Random(TARGET_ORDER_SEED).shuffle(xs)
    return xs


def iid_queries(m: int, n: int):
    r = random.Random(IID_QUERY_SEED)
    return [(r.randrange(m), r.randrange(m)) for _ in range(n)]


def heldout_queries(m: int, n: int):
    order = target_order(m)
    targets = order[m // 2:]
    r = random.Random(HELDOUT_QUERY_SEED)
    return [(r.randrange(m), r.choice(targets)) for _ in range(n)]


def sizes(m: int):
    return sorted({0, max(1, int(math.sqrt(m))), max(1, m // 10), max(1, m // 2), m})


def evaluate(m: int, queries, policies, depth: int):
    total = solved = hits = work = 0
    for start, target in queries:
        if start == target:
            continue
        length = shortest_len(start, target, m)
        budget = length + 2
        total += 1

        policy = policies.get(target)
        if policy is not None:
            hits += 1
            ok, w = cached(start, target, budget, m, policy)
        else:
            ok, w = lookahead(start, target, budget, m, depth)
        solved += int(ok)
        work += w

    return {
        "queries": total,
        "solved": solved,
        "success_rate": solved / total,
        "hits": hits,
        "hit_rate": hits / total,
        "online_work": work,
        "avg_online_work": work / total,
    }


def self_test():
    for target in range(30):
        action, dist = build_target_policy(30, target)
        for state in range(30):
            if state == target:
                continue
            nxt = op(state, action[state], 30)
            assert dist[state] == dist[nxt] + 1

    assert lookahead(0, 5, 4, 30, 0)[0] is False
    assert lookahead(0, 5, 4, 30, 2)[0] is True

    m = 300
    order = target_order(m)
    q = heldout_queries(m, 100)
    assert all(target not in set(order[:m // 2]) for _, target in q)

    empty = evaluate(m, q, {}, 2)
    partial = {t: build_target_policy(m, t)[0] for t in order[:m // 2]}
    partial_result = evaluate(m, q, partial, 2)
    assert empty["hits"] == partial_result["hits"] == 0
    assert empty["online_work"] == partial_result["online_work"]
    assert empty["success_rate"] == partial_result["success_rate"]

    full = {t: build_target_policy(m, t)[0] for t in range(m)}
    assert evaluate(m, iid_queries(m, 100), full, 2)["success_rate"] == 1.0


def run(m: int, queries: int, depth: int):
    order = target_order(m)
    iid = iid_queries(m, queries)
    held = heldout_queries(m, queries)
    policies = {}
    built = 0
    out = []

    for h in sizes(m):
        while built < h:
            target = order[built]
            policies[target] = build_target_policy(m, target)[0]
            built += 1

        out.append({
            "M": m,
            "h": h,
            "offline_work_states": h * m,
            "offline_storage_bytes": h * m,
            "iid": evaluate(m, iid, policies, depth),
            "strict_heldout": evaluate(m, held, policies, depth),
        })

    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--m", type=int, action="append", default=None)
    p.add_argument("--queries", type=int, default=200)
    p.add_argument("--look-depth", type=int, default=2)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--out", type=Path)
    args = p.parse_args()

    self_test()
    if args.self_test:
        print("SELF-TEST PASS")
        return

    ms = args.m or [30, 300, 3000]
    results = []
    for m in ms:
        results.extend(run(m, args.queries, args.look_depth))

    print(json.dumps(results, indent=2))
    if args.out:
        args.out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
