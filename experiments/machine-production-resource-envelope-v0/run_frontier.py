"""Production resource-envelope frontier for A1_RW vs A2.

No production winner is selected.

For each workload, compute exact structural access work:
  A1 query = 2 + 2*d
  A2 query = 1 + d

A1 dynamic update uses the exact contiguous-CSR maintenance operation count
from the M2 closure model.

A2 dynamic update is intentionally parameterized as c2 because the Rev 2.1
structured-update resource contract does not yet expose a comparable structural
unit count. This avoids silently treating P-07 as free.

For every workload mix (Q,U), derive the break-even c2:
    c2_threshold = mean_A1_update + (Q/U) * mean_query_delta

A2 is within the same aggregate online-access budget as A1 whenever:
    c2 <= c2_threshold

Storage is reported separately. For the M2 exact-CSR model, live CSR bytes and
the maximum reserved logical cell capacity S*Sigma are both shown; the latter
is a capacity bound, not a claim about the concrete Rev 2.1 allocator.
"""

import json
import random
import statistics


def make_delta(n, k, seed):
    rng = random.Random(seed)
    d = [[rng.randrange(n) for _ in range(k)] for _ in range(n)]
    for s in range(n):
        for a in range(k):
            if rng.random() < 0.15:
                d[s][a] = -1
        if k >= 2 and rng.random() < 0.35:
            a0, a1 = rng.sample(range(k), 2)
            d[s][a1] = d[s][a0]
    return d


def edges(d):
    return [(s, a, u) for s, row in enumerate(d) for a, u in enumerate(row) if u >= 0]


def build(d):
    n = len(d)
    es = edges(d)
    offs = [0] * (n + 1)
    for _, _, u in es:
        offs[u + 1] += 1
    for u in range(n):
        offs[u + 1] += offs[u]
    cur = offs[:-1].copy()
    src = [0] * len(es)
    act = [0] * len(es)
    for s, a, u in es:
        i = cur[u]
        src[i], act[i] = s, a
        cur[u] += 1
    for u in range(n):
        lo, hi = offs[u], offs[u + 1]
        pairs = sorted(zip(src[lo:hi], act[lo:hi]))
        for i, pair in enumerate(pairs, start=lo):
            src[i], act[i] = pair
    return offs, src, act


def locate(offs, src, act, target, s, a):
    lo, hi = offs[target], offs[target + 1]
    for i in range(lo, hi):
        if src[i] == s and act[i] == a:
            return i
    return -1


def delete_csr(offs, src, act, s, a, target):
    n = len(offs) - 1
    pos = locate(offs, src, act, target, s, a)
    old_len = len(src)
    src.pop(pos)
    act.pop(pos)
    for u in range(target + 1, n + 1):
        offs[u] -= 1
    return (old_len - pos - 1) + 2 + (n - target)


def insert_csr(offs, src, act, s, a, target):
    n = len(offs) - 1
    old_len = len(src)
    pos = offs[target + 1]
    src.insert(pos, s)
    act.insert(pos, a)
    for u in range(target + 1, n + 1):
        offs[u] += 1
    return (old_len - pos) + 2 + (n - target)


def update_csr(d, offs, src, act, s, a, new_u):
    old_u = d[s][a]
    if old_u == new_u:
        return 0
    cost = 0
    if old_u >= 0:
        cost += delete_csr(offs, src, act, s, a, old_u)
    d[s][a] = new_u
    if new_u >= 0:
        cost += insert_csr(offs, src, act, s, a, new_u)
    return cost


def run_case(n, k, seed, updates=200):
    rng = random.Random(seed)
    d = make_delta(n, k, seed)
    offs, src, act = build(d)
    E = len(src)
    degrees = [offs[u + 1] - offs[u] for u in range(n)]
    query_costs = [2 + 2 * degrees[u] for u in range(n)]
    delta_query = [1 + degrees[u] for u in range(n)]

    d2 = [row[:] for row in d]
    o2, s2, a2 = offs[:], src[:], act[:]
    update_costs = []
    noops = 0
    for _ in range(updates):
        s = rng.randrange(n)
        a = rng.randrange(k)
        new_u = -1 if rng.random() < 0.20 else rng.randrange(n)
        c = update_csr(d2, o2, s2, a2, s, a, new_u)
        if c == 0:
            noops += 1
        else:
            update_costs.append(c)

    return {
        "n": n,
        "k": k,
        "E": E,
        "mean_indegree": statistics.mean(degrees),
        "p95_indegree": sorted(degrees)[min(n - 1, int(0.95 * n))],
        "mean_A1_query": statistics.mean(query_costs),
        "mean_query_delta_A1_minus_A2": statistics.mean(delta_query),
        "mean_A1_update": statistics.mean(update_costs) if update_costs else 0.0,
        "p95_A1_update": sorted(update_costs)[min(len(update_costs) - 1, int(0.95 * len(update_costs)))] if update_costs else 0.0,
        "updates": updates,
        "effective_updates": len(update_costs),
        "noops": noops,
        "live_csr_bytes": 4 * (n + 1) + 4 * E + E,
        "max_logical_cells_Sigma": n * k,
    }


def frontier_for_case(case, ratios):
    out = []
    for q_over_u in ratios:
        threshold = case["mean_A1_update"] + q_over_u * case["mean_query_delta_A1_minus_A2"]
        out.append({
            "Q_over_U": q_over_u,
            "A2_break_even_update_cost": threshold,
        })
    return out


def aggregate(cases):
    return {
        "mean_A1_update": statistics.mean(c["mean_A1_update"] for c in cases),
        "median_A1_update": statistics.median(c["mean_A1_update"] for c in cases),
        "mean_query_delta": statistics.mean(c["mean_query_delta_A1_minus_A2"] for c in cases),
        "mean_live_csr_bytes": statistics.mean(c["live_csr_bytes"] for c in cases),
        "mean_max_logical_cells": statistics.mean(c["max_logical_cells_Sigma"] for c in cases),
    }


def run():
    configs = [(31, 4), (63, 5), (127, 4), (255, 6), (511, 4)]
    cases = []
    for family, (n, k) in enumerate(configs):
        for rep in range(10):
            cases.append(run_case(n, k, 20260928 + family * 1000 + rep))

    ratios = [0.01, 0.1, 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, 128]
    agg = aggregate(cases)

    result = {
        "schema": "machine.production-resource-envelope-frontier.v0.1",
        "status": "EXECUTED",
        "cases": len(cases),
        "workload_model": {
            "query_count": "Q",
            "update_count": "U",
            "profile_A1_query": "2 + 2*d",
            "profile_A2_query": "1 + d",
            "profile_A1_update": "exact contiguous CSR generic RW logical operation count",
            "profile_A2_update": "parameter c2; no free-update assumption",
        },
        "aggregate": agg,
        "break_even_formula": "c2 <= mean_A1_update + (Q/U) * mean_query_delta_A1_minus_A2",
        "frontier": frontier_for_case(agg | {"mean_A1_update": agg["mean_A1_update"], "mean_query_delta_A1_minus_A2": agg["mean_query_delta"]}, ratios),
        "storage": {
            "A1_M2_live_CSR_bytes_formula": "4*(S+1) + 4*E + E",
            "A1_M2_capacity_bound_formula": "4*(S+1) + 4*(S*Sigma) + (S*Sigma) if fully reserved",
            "capacity_bound_is_normative": False,
            "A2_storage": "UNRESOLVED until concrete P-07 representation/accounting is frozen",
        },
        "decision_boundary": {
            "production_profile": "OPEN",
            "reason": "A2 structured-update cost and dynamic storage/consistency contract remain unnormalized against A1_RW.",
            "next_gate": "freeze c2 resource semantics + capacity policy + query/update mix, then evaluate admissibility rather than selecting a universal winner",
        },
        "falsification_boundary": [
            "same generated delta families",
            "same CSR semantics",
            "same exact contiguous logical update operation count for A1",
            "A2 update cost remains an explicit parameter",
            "no wall-clock classification",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    run()
