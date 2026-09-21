import json, time, numpy as np, pandas as pd
from bidir_v2 import generate_clustered_bottleneck_graph, BETAS, ALPHAS, INF
import bidir_v3 as V3
POL = ["alternate", "min_key", "cardinality_true", "equal_work_edge"]
SIZES = [75, 150, 300, 600, 1200]; SEEDS = [41, 42, 43]
rows = []; t0 = time.time()
for npc in SIZES:
    for sd in SEEDS:
        ss = np.random.SeedSequence([sd, npc]).spawn(90); gid = 0
        for b in BETAS:
            for a in ALPHAS:
                for rep in range(10):
                    g_ss, q_ss = ss[gid].spawn(2); gid += 1
                    adj, N, _ = generate_clustered_bottleneck_graph(npc, b, a, g_ss); q = np.random.default_rng(q_ss)
                    for _ in range(3):
                        s, t = int(q.integers(0, npc)), int(q.integers(npc, N)); fr = V3.forward_dijkstra(adj, s, t)
                        if fr["cost"] == INF: continue
                        for pol in POL:
                            r = V3.run_policy(adj, adj, s, t, fr["cost"], pol); assert abs(r["cost"] - fr["cost"]) < 1e-9
                            rows.append(dict(npc=npc, seed=sd, graph=gid, policy=pol, exp=r["total_exp"], scan=r["total_scan"], fwd_scan=fr["scans"], fwd_exp=fr["exp"],
                                             pre=r.get("pre_exp", np.nan), res=r.get("res_exp", np.nan), cert=r.get("cert_exp", np.nan)))
    print("size", npc, round(time.time() - t0, 1), "s", flush=True)
df = pd.DataFrame(rows); df.to_pickle("scaling.pkl")
out = {}
for pol in POL:
    d = df[df.policy == pol]; out[pol] = {}
    for m in ["exp", "scan", "pre", "res", "cert", "fwd_scan", "fwd_exp"]:
        if d[m].isna().all(): continue
        sl = []
        for sd in SEEDS:
            g = d[d.seed == sd].groupby("npc")[m].mean(); sl.append(np.polyfit(np.log(g.index.values), np.log(g.values), 1)[0])
        out[pol][m] = dict(slope_mean=float(np.mean(sl)), slope_sd=float(np.std(sl, ddof=1)), means_by_size={int(k): round(float(v), 1) for k, v in d.groupby("npc")[m].mean().items()})
    print(pol, {m: (round(v["slope_mean"], 2), round(v["slope_sd"], 2)) for m, v in out[pol].items()})
# ratios vs cardinality across sizes
ratio = {}
for m in ["scan", "exp"]:
    for pol in ["alternate", "min_key", "equal_work_edge"]:
        ratio[f"{pol}/cardinality_true ({m})"] = {int(n): round(float(df[(df.policy == pol) & (df.npc == n)][m].mean() / df[(df.policy == "cardinality_true") & (df.npc == n)][m].mean()), 3) for n in SIZES}
for k, v in ratio.items(): print(k, v)
json.dump(dict(slopes=out, ratios=ratio), open("scaling_results.json", "w"), indent=1)
