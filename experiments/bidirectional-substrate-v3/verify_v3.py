import numpy as np, pandas as pd, heapq
from bidir_v2 import *
import bidir_v3 as V3

# ---- (1) regression: v3 vertex policies == v2 on the frozen clustered instances (undirected: adj_f = adj_b)
prov = pd.read_pickle("prov_v2.pkl")
mism = 0; n_cmp = 0; nonopt = 0; edge_runs = 0
graph_id = 0
for b in BETAS:
    for a in ALPHAS:
        for rep in range(10):
            graph_id += 1
            g_seed = 1000 + rep * 17 + int(b * 100 + a * 10)
            adj, N, _ = generate_clustered_bottleneck_graph(300, b, a, g_seed)
            q_rng = np.random.default_rng(2000 + rep + graph_id)
            sub = prov[prov.graph_id == graph_id]
            for q in range(3):
                s = int(q_rng.integers(0, 300)); t = int(q_rng.integers(300, 600))
                fr = V3.forward_dijkstra(adj, s, t)
                if fr["cost"] == INF: continue
                for pol in ["alternate", "min_key", "cardinality_true", "cardinality_proxy", "open_work"]:
                    r = V3.run_policy(adj, adj, s, t, fr["cost"], pol)
                    row = sub[(sub.policy == pol)].iloc[q]      # queries appear in order within a graph
                    n_cmp += 1
                    mism += not (r["total_exp"] == row.total_exp and r["total_scan"] == row.total_scan and r["pre_exp"] == row.pre_exp
                                 and r["res_exp"] == row.res_exp and r["cert_exp"] == row.cert_exp and abs(r["cost"] - row.cost) < 1e-9)
                for pol in ["equal_work_vertex", "equal_work_edge", "equal_work_edge_paperstop"]:
                    r = V3.run_policy(adj, adj, s, t, fr["cost"], pol); edge_runs += 1
                    nonopt += abs(r["cost"] - fr["cost"]) > 1e-9
print(f"(1) v3 == v2 on {n_cmp} runs (5 shared policies): mismatches = {mism}")
print(f"    new policies optimal on {edge_runs} clustered-graph runs: non-optimal = {nonopt}")

# ---- (2) random small DIRECTED multigraphs (parallel edges, self loops, isolated vertices): all policies vs Dijkstra
rng = np.random.default_rng(5); bad = 0; total = 0; unreach = 0
for _ in range(1500):
    n = int(rng.integers(2, 30)); m = int(rng.integers(0, 4 * n))
    adj_f = [[] for _ in range(n)]; adj_b = [[] for _ in range(n)]
    for _ in range(m):
        u, v = int(rng.integers(0, n)), int(rng.integers(0, n)); w = float(rng.integers(1, 6))
        adj_f[u].append((v, w)); adj_b[v].append((u, w))
    s, t = int(rng.integers(0, n)), int(rng.integers(0, n))
    if s == t: continue
    fr = V3.forward_dijkstra(adj_f, s, t)
    if fr["cost"] == INF: unreach += 1; continue
    for pol in V3.ALL_POLICIES + ["equal_work_edge_paperstop"]:
        r = V3.run_policy(adj_f, adj_b, s, t, fr["cost"], pol); total += 1
        bad += abs(r["cost"] - fr["cost"]) > 1e-9
print(f"(2) random directed multigraphs: {total} runs over {len(V3.ALL_POLICIES)+1} policies, non-optimal = {bad} (unreachable pairs skipped: {unreach})")

# ---- (3) directed hub system optimality
adj_f, adj_b = V3.directed_hub_graph(5000, 4, 3)
rng = np.random.default_rng(9); bad = 0; total = 0
for _ in range(60):
    s, t = int(rng.integers(0, 5000)), int(rng.integers(0, 5000))
    fr = V3.forward_dijkstra(adj_f, s, t)
    if s == t or fr["cost"] == INF: continue
    for pol in V3.ALL_POLICIES:
        r = V3.run_policy(adj_f, adj_b, s, t, fr["cost"], pol); total += 1; bad += abs(r["cost"] - fr["cost"]) > 1e-9
print(f"(3) directed hub graph n=5000: {total} runs, non-optimal = {bad}")
