from __future__ import annotations

import itertools
import json
from pathlib import Path

from core import dijkstra, interruptible_bidirectional_dijkstra

ROOT = Path(__file__).resolve().parent


def reverse(adj):
    out = {u: [] for u in adj}
    for u, es in adj.items():
        for v, w in es:
            out[v].append((u, w))
    return out


def fixed_policy(seq):
    i = [0]

    def policy(nF, nB, topF, topB):
        x = seq[i[0]]
        i[0] += 1
        return x

    return policy


def exhaustive_n2():
    n = 2
    states = range(4)  # 0=absent, 1..3=positive weight
    edges = [(u, v) for u in range(n) for v in range(n) if u != v]
    schedules = list(itertools.product("FB", repeat=2 * n))

    out = {
        "graph_states": 0,
        "solvable_graphs": 0,
        "schedule_runs": 0,
        "active_guard_failures": 0,
        "naive_finite_failures": 0,
        "exceptions": 0,
        "witnesses": [],
        "semantics": "post-edge-only",
        "check_before_first_edge": False,
    }

    for code in itertools.product(states, repeat=len(edges)):
        out["graph_states"] += 1
        adj = {u: [] for u in range(n)}
        for (u, v), state in zip(edges, code):
            if state:
                adj[u].append((v, state))

        rev = reverse(adj)
        ds = dijkstra(adj, 0)
        c_star = ds.get(1)
        if c_star is None:
            continue
        out["solvable_graphs"] += 1

        for seq in schedules:
            try:
                active = interruptible_bidirectional_dijkstra(
                    adj, rev, 0, 1, fixed_policy(seq),
                    active_guard=True,
                    check_before_first_edge=False,
                )
                naive = interruptible_bidirectional_dijkstra(
                    adj, rev, 0, 1, fixed_policy(seq),
                    active_guard=False,
                    check_before_first_edge=False,
                )
            except (IndexError, KeyError, ValueError):
                out["exceptions"] += 1
                continue

            out["schedule_runs"] += 1

            if active.mu != c_star:
                out["active_guard_failures"] += 1
                if len(out["witnesses"]) < 10:
                    out["witnesses"].append({
                        "kind": "active_failure",
                        "edges": code,
                        "schedule": "".join(seq),
                        "C_star": c_star,
                        "active_mu": active.mu,
                    })

            if naive.mu not in (c_star, float("inf")):
                out["naive_finite_failures"] += 1
                if len(out["witnesses"]) < 10:
                    out["witnesses"].append({
                        "kind": "naive_finite_failure",
                        "edges": code,
                        "schedule": "".join(seq),
                        "C_star": c_star,
                        "naive_mu": naive.mu,
                    })

    return out


if __name__ == "__main__":
    result = exhaustive_n2()
    (ROOT / "RESULTS-N2-POSTEDGE.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))