"""Primary metric (declared before running): total edge scans. Primary contrasts (Holm-corrected within dataset):
   each of {alternate, min_key, open_work, equal_work_vertex, equal_work_edge} vs cardinality_true."""
import sys, json, time, numpy as np, pandas as pd
from scipy import stats
from bidir_v2 import generate_clustered_bottleneck_graph, BETAS, ALPHAS, INF
import bidir_v3 as V3

POL = V3.ALL_POLICIES + ["equal_work_edge_paperstop"]
rows = []

def run_instance(ds, cluster, pair, adj_f, adj_b, s, t, fr):
    for pol in POL:
        r = V3.run_policy(adj_f, adj_b, s, t, fr["cost"], pol)
        assert abs(r["cost"] - fr["cost"]) < 1e-9, (ds, pol)
        rows.append(dict(dataset=ds, cluster=cluster, pair=pair, policy=pol, exp=r["total_exp"], scan=r["total_scan"],
                         push=r["total_push"], fwd_exp=fr["exp"], fwd_scan=fr["scans"]))

t0 = time.time()
# ---- E1: frozen clustered bottleneck ensemble (undirected)
gid = 0; pid = 0
for b in BETAS:
    for a in ALPHAS:
        for rep in range(10):
            gid += 1
            adj, N, _ = generate_clustered_bottleneck_graph(300, b, a, 1000 + rep * 17 + int(b * 100 + a * 10))
            q = np.random.default_rng(2000 + rep + gid)
            for _ in range(3):
                s, t = int(q.integers(0, 300)), int(q.integers(300, 600)); fr = V3.forward_dijkstra(adj, s, t)
                if fr["cost"] < INF: pid += 1; run_instance("clustered_frozen", gid, pid, adj, adj, s, t, fr)
print("E1 done", round(time.time() - t0, 1), "s", flush=True)

# ---- E2: directed hub-heavy multigraphs from the substrate generator (predecessor fibers = adj_b)
pid = 0
for seed in (1, 2, 3):
    adj_f, adj_b = V3.directed_hub_graph(20000, 4, seed)
    q = np.random.default_rng(100 + seed); done = 0
    while done < 60:
        s, t = int(q.integers(0, 20000)), int(q.integers(0, 20000))
        if s == t: continue
        fr = V3.forward_dijkstra(adj_f, s, t)
        if fr["cost"] == INF: continue
        pid += 1; done += 1; run_instance("directed_hub_20k", seed, pid, adj_f, adj_b, s, t, fr)
print("E2 done", round(time.time() - t0, 1), "s", flush=True)

# ---- E3: real undirected graphs (networkit/input), random integer weights 1..9 (seed 0)
meta = {}
for name, npairs in (("PGPgiantcompo", 150), ("power", 150), ("polblogs", 150), ("caidaRouterLevel", 60)):
    adj = V3.load_metis(f"real_{name}.graph", seed=0)
    deg = np.array([len(a) for a in adj]); comp = V3.largest_component(adj)
    meta[name] = dict(n=len(adj), m=int(deg.sum() // 2), giant=int(len(comp)), max_deg=int(deg.max()), mean_deg=float(deg.mean()),
                      delta2_over_n=float(deg.max() ** 2 / len(adj)))
    q = np.random.default_rng(7); pid = 0
    while pid < npairs:
        s, t = int(q.choice(comp)), int(q.choice(comp))
        if s == t: continue
        fr = V3.forward_dijkstra(adj, s, t); pid += 1
        run_instance(name, 1, pid, adj, adj, s, t, fr)
    print("E3", name, meta[name], round(time.time() - t0, 1), "s", flush=True)

df = pd.DataFrame(rows); df.to_pickle("exp_policies.pkl"); json.dump(meta, open("real_graph_meta.json", "w"), indent=1)
print("saved", len(df), "rows")
