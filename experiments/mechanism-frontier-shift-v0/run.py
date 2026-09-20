"""Fair mechanism-frontier comparison.

B_off=R=0. Primary tick: one candidate-edge examination.
Baseline: forward BFS + visited set.
Variant: bidirectional BFS with online predecessor access; no stored reverse graph.
A fixed-budget gap is a Pareto-frontier shift under this contract, not by itself
proof of an absolute new computational capability.
"""
from collections import deque
import math
import random
import statistics


def make_graph(M):
    return (
        lambda v: (v + 1) % M,
        lambda v: (v + 7) % M,
        lambda v: (v * 2) % M,
    )


def reverse_neighbors(v, M):
    """Derive predecessors online; no reverse adjacency is precomputed."""
    preds = [(v - 1) % M, (v - 7) % M]
    if M % 2:
        inv2 = pow(2, -1, M)
        preds.append((v * inv2) % M)
    elif v % 2 == 0:
        x = v // 2
        preds.append(x)
        preds.append((x + M // 2) % M)
    return preds


def forward_bfs_capped(start, target, M, cap):
    """Strong single-direction baseline: BFS + visited set.

    One tick = one candidate-edge examination.
    """
    if start == target:
        return True, 0, 0
    ops = make_graph(M)
    visited = {start}
    q = deque([start])
    ticks = expanded = 0
    while q:
        u = q.popleft()
        expanded += 1
        for fn in ops:
            v = fn(u)
            ticks += 1
            if ticks > cap:
                return False, ticks, expanded
            if v == target:
                return True, ticks, expanded
            if v not in visited:
                visited.add(v)
                q.append(v)
    return False, ticks, expanded


def bidirectional_bfs_capped(start, target, M, cap):
    """Bidirectional BFS with online inverse-transition access."""
    if start == target:
        return True, 0, 0
    ops = make_graph(M)
    f_seen = {start}
    b_seen = {target}
    f_q = deque([start])
    b_q = deque([target])
    ticks = expanded = 0
    while f_q and b_q:
        if len(f_q) <= len(b_q):
            u = f_q.popleft()
            expanded += 1
            for fn in ops:
                v = fn(u)
                ticks += 1
                if ticks > cap:
                    return False, ticks, expanded
                if v in b_seen:
                    return True, ticks, expanded
                if v not in f_seen:
                    f_seen.add(v)
                    f_q.append(v)
        else:
            u = b_q.popleft()
            expanded += 1
            for v in reverse_neighbors(u, M):
                ticks += 1
                if ticks > cap:
                    return False, ticks, expanded
                if v in f_seen:
                    return True, ticks, expanded
                if v not in b_seen:
                    b_seen.add(v)
                    b_q.append(v)
    return False, ticks, expanded


def benchmark_queries(M, n=200, seed=7):
    rng = random.Random(seed)
    return [
        (s, t) for s, t in
        ((rng.randrange(M), rng.randrange(M)) for _ in range(n))
        if s != t
    ]


def solve_count(solver, queries, M, cap):
    return sum(solver(s, t, M, cap)[0] for s, t in queries)


def frontier_gap(solver_a, solver_b, queries, M, cap):
    return [
        (s, t) for s, t in queries
        if not solver_a(s, t, M, cap)[0]
        and solver_b(s, t, M, cap)[0]
    ]


def min_budget_distribution(solver, queries, M, max_cap=20000):
    rows = []
    for s, t in queries:
        lo, hi = 0, max_cap
        ok, _, _ = solver(s, t, M, hi)
        if not ok:
            rows.append((s, t, math.inf))
            continue
        while lo < hi:
            mid = (lo + hi) // 2
            ok, _, _ = solver(s, t, M, mid)
            if ok:
                hi = mid
            else:
                lo = mid + 1
        rows.append((s, t, lo))
    return rows


def run():
    caps = (10, 20, 40, 80, 160, 320)
    print("CONTRACT")
    print("B_off=0")
    print("R=0")
    print("No target-dependent persistent state")
    print("Primary online tick = one candidate-edge examination")
    print("No precomputed reverse adjacency; predecessors are derived online.")
    print()

    for M in (30, 300, 3000):
        queries = benchmark_queries(M)
        print(f"M={M} queries={len(queries)}")
        for cap in caps:
            fwd = solve_count(forward_bfs_capped, queries, M, cap)
            bidi = solve_count(bidirectional_bfs_capped, queries, M, cap)
            gap = frontier_gap(
                forward_bfs_capped, bidirectional_bfs_capped, queries, M, cap
            )
            reverse_gap = frontier_gap(
                bidirectional_bfs_capped, forward_bfs_capped, queries, M, cap
            )
            print(
                f"  B_on={cap:<4} forward={fwd:<4} bidi={bidi:<4} "
                f"frontier_shift={len(gap):<4} reverse_gap={len(reverse_gap)}"
            )
        print()

        fdist = min_budget_distribution(forward_bfs_capped, queries, M)
        bdist = min_budget_distribution(bidirectional_bfs_capped, queries, M)
        comparable = [
            (f[2], b[2])
            for f, b in zip(fdist, bdist)
            if math.isfinite(f[2]) and math.isfinite(b[2])
        ]
        bidi_cheaper = sum(b < f for f, b in comparable)
        fwd_cheaper = sum(f < b for f, b in comparable)
        equal = sum(f == b for f, b in comparable)
        print("FULL-BUDGET PROFILE")
        print(f"  both eventually solved: {len(comparable)}/{len(queries)}")
        print(f"  bidirectional cheaper:   {bidi_cheaper}")
        print(f"  forward cheaper:         {fwd_cheaper}")
        print(f"  equal:                    {equal}")
        if comparable:
            ratios = [b / f for f, b in comparable if f > 0]
            print(f"  median bidi/forward cost: {statistics.median(ratios):.4f}")
        print()


if __name__ == "__main__":
    run()
