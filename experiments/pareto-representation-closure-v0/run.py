from collections import deque
import csv
import json
import random
import statistics
from pathlib import Path

OPS = ("A", "B", "C")


def make_graph(M):
    def succ(op, v):
        if op == "A":
            return (v + 1) % M
        if op == "B":
            return (v + 7) % M
        return (2 * v) % M
    return succ


def all_edges(succ, M):
    for u in range(M):
        for op in OPS:
            yield u, succ(op, u)


def build_reverse_index(succ, M):
    rev = [[] for _ in range(M)]
    offline = 0
    for u, v in all_edges(succ, M):
        rev[v].append(u)
        offline += 1
    return rev, offline, sum(map(len, rev))


def build_policy_table(succ, M):
    table = [[None] * M for _ in range(M)]
    offline = 0
    stored = 0
    for s in range(M):
        q = deque([s])
        seen = {s: None}
        first = {s: None}
        while q:
            u = q.popleft()
            for op in OPS:
                v = succ(op, u)
                offline += 1
                if v in seen:
                    continue
                seen[v] = u
                first[v] = op if u == s else first[u]
                q.append(v)
        for t in range(M):
            if t != s and t in first:
                table[s][t] = first[t]
                stored += 1
    return table, offline, stored


def queries(M, n=80, seed=17):
    rng = random.Random(seed + M)
    out = []
    while len(out) < n:
        s, t = rng.randrange(M), rng.randrange(M)
        if s != t:
            out.append((s, t))
    return out


def forward(succ, s, t, M, cap):
    if s == t:
        return True, 0
    q = deque([s])
    seen = {s}
    ticks = 0
    while q:
        u = q.popleft()
        for op in OPS:
            ticks += 1
            if ticks > cap:
                return False, ticks
            v = succ(op, u)
            if v == t:
                return True, ticks
            if v not in seen:
                seen.add(v)
                q.append(v)
    return False, ticks


def native_bidi(succ, s, t, M, cap):
    # Direct predecessor access for the declared graph family.
    if s == t:
        return True, 0
    rev = [[] for _ in range(M)]
    for u, v in all_edges(succ, M):
        rev[v].append(u)

    fq, bq = deque([s]), deque([t])
    fs, bs = {s}, {t}
    ticks = 0
    while fq and bq:
        if len(fq) <= len(bq):
            u = fq.popleft()
            for op in OPS:
                ticks += 1
                if ticks > cap:
                    return False, ticks
                v = succ(op, u)
                if v in bs:
                    return True, ticks
                if v not in fs:
                    fs.add(v)
                    fq.append(v)
        else:
            u = bq.popleft()
            for v in rev[u]:
                ticks += 1
                if ticks > cap:
                    return False, ticks
                if v in fs:
                    return True, ticks
                if v not in bs:
                    bs.add(v)
                    bq.append(v)
    return False, ticks


def reverse_index_bidi(succ, rev, s, t, M, cap):
    if s == t:
        return True, 0
    fq, bq = deque([s]), deque([t])
    fs, bs = {s}, {t}
    ticks = 0
    while fq and bq:
        if len(fq) <= len(bq):
            u = fq.popleft()
            for op in OPS:
                ticks += 1
                if ticks > cap:
                    return False, ticks
                v = succ(op, u)
                if v in bs:
                    return True, ticks
                if v not in fs:
                    fs.add(v)
                    fq.append(v)
        else:
            u = bq.popleft()
            for v in rev[u]:
                ticks += 1
                if ticks > cap:
                    return False, ticks
                if v in fs:
                    return True, ticks
                if v not in bs:
                    bs.add(v)
                    bq.append(v)
    return False, ticks


def policy_lookup(succ, table, s, t, M, cap):
    if s == t:
        return True, 0
    ticks = 1  # target-oblivious table lookup
    u = s
    for _ in range(M + 1):
        if ticks > cap:
            return False, ticks
        op = table[u][t]
        if op is None:
            return False, ticks
        u = succ(op, u)
        ticks += 2  # lookup + successor execution
        if u == t:
            return True, ticks - 1
    return False, ticks


def min_required_cap(solver, query, M, upper=20000):
    s, t = query
    lo, hi = 0, upper
    if not solver(s, t, M, hi)[0]:
        return float("inf")
    while lo < hi:
        mid = (lo + hi) // 2
        if solver(s, t, M, mid)[0]:
            hi = mid
        else:
            lo = mid + 1
    return lo


def run():
    out = Path("experiments/pareto-representation-closure-v0")
    out.mkdir(parents=True, exist_ok=True)

    caps = [10, 20, 40, 80, 160, 320, 640]
    seeds = [17, 23, 41]
    Ms = [30, 100, 300]

    summary = []
    samples = []
    resource_meta = []

    for M in Ms:
        succ = make_graph(M)
        rev, reverse_B_off, reverse_R = build_reverse_index(succ, M)
        table, policy_B_off, policy_R = build_policy_table(succ, M)

        resource_meta.append({
            "M": M,
            "reverse_index": {"B_off": reverse_B_off, "R": reverse_R},
            "all_pairs_policy": {"B_off": policy_B_off, "R": policy_R},
        })

        for seed in seeds:
            qs = queries(M, seed=seed)
            for cap in caps:
                counts = {k: 0 for k in
                          ("forward", "native_bidi", "reverse_index", "policy")}
                for i, (s, t) in enumerate(qs):
                    f, ft = forward(succ, s, t, M, cap)
                    n, nt = native_bidi(succ, s, t, M, cap)
                    r, rt = reverse_index_bidi(succ, rev, s, t, M, cap)
                    p, pt = policy_lookup(succ, table, s, t, M, cap)

                    counts["forward"] += int(f)
                    counts["native_bidi"] += int(n)
                    counts["reverse_index"] += int(r)
                    counts["policy"] += int(p)

                    if seed == 17 and i in (0, 20, 40, 60) and cap in (10, 40, 80):
                        samples.append({
                            "M": M, "seed": seed, "query_index": i,
                            "start": s, "target": t, "B_on": cap,
                            "forward": int(f), "forward_ticks": ft,
                            "native_bidi": int(n), "native_bidi_ticks": nt,
                            "reverse_index": int(r),
                            "reverse_index_ticks": rt,
                            "policy": int(p), "policy_ticks": pt,
                            "reverse_B_off": reverse_B_off,
                            "reverse_R": reverse_R,
                            "policy_B_off": policy_B_off,
                            "policy_R": policy_R,
                        })

                summary.append({
                    "M": M, "seed": seed, "B_on": cap, "n": len(qs),
                    **counts
                })

    frontier = []
    for M in Ms:
        succ = make_graph(M)
        rev, reverse_B_off, reverse_R = build_reverse_index(succ, M)
        table, policy_B_off, policy_R = build_policy_table(succ, M)
        all_qs = [q for seed in seeds for q in queries(M, seed=seed)]

        solvers = {
            "forward": lambda s, t, c, succ=succ, M=M: forward(succ, s, t, M, c)[0],
            "native_bidi": lambda s, t, c, succ=succ, M=M: native_bidi(succ, s, t, M, c)[0],
            "reverse_index": lambda s, t, c, succ=succ, rev=rev, M=M:
                reverse_index_bidi(succ, rev, s, t, M, c)[0],
            "policy": lambda s, t, c, succ=succ, table=table, M=M:
                policy_lookup(succ, table, s, t, M, c)[0],
        }

        for name, solver in solvers.items():
            costs = [min_required_cap(solver, q, M) for q in all_qs]
            frontier.append({
                "M": M,
                "method": name,
                "B_off": 0 if name in ("forward", "native_bidi") else
                         (reverse_B_off if name == "reverse_index" else policy_B_off),
                "R": 0 if name in ("forward", "native_bidi") else
                    (reverse_R if name == "reverse_index" else policy_R),
                "B_on_max_all_sampled": max(costs),
                "B_on_median": statistics.median(costs),
                "B_on_p90": sorted(costs)[int(0.9 * len(costs)) - 1],
            })

    with open(out / "SUMMARY-V0.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=summary[0].keys())
        w.writeheader(); w.writerows(summary)

    with open(out / "REPRESENTATIVE-SAMPLES-V0.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=samples[0].keys())
        w.writeheader(); w.writerows(samples)

    with open(out / "PARETO-FRONTIER-V0.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=frontier[0].keys())
        w.writeheader(); w.writerows(frontier)

    with open(out / "RESOURCE-METADATA-V0.json", "w") as f:
        json.dump({
            "M_values": Ms, "seeds": seeds, "caps": caps,
            "resource_meta": resource_meta,
            "tick_definition": "one candidate-edge examination; policy lookup counts separately",
        }, f, indent=2)

    print(json.dumps(frontier, indent=2))


if __name__ == "__main__":
    run()
