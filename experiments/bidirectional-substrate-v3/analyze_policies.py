import json, numpy as np, pandas as pd
from scipy import stats
df = pd.read_pickle("exp_policies.pkl")
MAIN = ["alternate", "min_key", "cardinality_true", "cardinality_proxy", "open_work", "equal_work_vertex", "equal_work_edge"]
PRIMARY = ["alternate", "min_key", "open_work", "equal_work_vertex", "equal_work_edge"]
OUT = {}

def holm(p):
    p = np.asarray(p); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for rank, i in enumerate(o):
        run = max(run, (m - rank) * p[i]); adj[i] = min(1.0, run)
    return adj

def boot_ratio(a, b, cl, B=3000, seed=0):
    rng = np.random.default_rng(seed); u = np.unique(cl); idx = {c: np.flatnonzero(cl == c) for c in u}
    pt = a.mean() / b.mean(); bs = []
    for _ in range(B):
        pick = rng.choice(u, len(u)); ii = np.concatenate([idx[c] for c in pick]); bs.append(a[ii].mean() / b[ii].mean())
    return pt, np.percentile(bs, 2.5), np.percentile(bs, 97.5)

for ds, d in df.groupby("dataset", sort=False):
    piv = d.pivot_table(index=["cluster", "pair"], columns="policy", values="scan"); pe = d.pivot_table(index=["cluster", "pair"], columns="policy", values="exp")
    fwd = d.drop_duplicates(["cluster", "pair"]).set_index(["cluster", "pair"])[["fwd_scan", "fwd_exp"]].loc[piv.index]
    cl = piv.index.get_level_values(0).values; n_units = len(np.unique(cl)) if ds in ("clustered_frozen",) else len(piv)
    # unit of analysis: graph for clustered_frozen (mean per graph), instance/pair otherwise
    if ds == "clustered_frozen":
        U = piv.groupby(level=0).mean(); F = fwd.groupby(level=0).mean(); unit_cl = U.index.values
    else:
        U = piv.reset_index(drop=True); F = fwd.reset_index(drop=True); unit_cl = np.arange(len(U))
    print("=" * 110); print(f"{ds}: {len(piv)} instances, analysis units = {len(U)}")
    res = {}
    best = U[MAIN].min(axis=1)
    tab = []
    for pol in MAIN:
        a = U[pol].values; ref = U["cardinality_true"].values
        r_card = boot_ratio(a, ref, unit_cl)
        r_fwd = boot_ratio(a, F["fwd_scan"].values, unit_cl)
        regret = (U[pol] / best)
        tab.append(dict(policy=pol, mean_scans=a.mean(), vs_forward=r_fwd[0], vs_card=r_card[0], vs_card_lo=r_card[1], vs_card_hi=r_card[2],
                        regret_mean=regret.mean(), regret_p95=np.percentile(regret, 95), regret_max=regret.max(), exp_mean=(pe[pol].groupby(level=0).mean() if ds == "clustered_frozen" else pe[pol]).mean()))
    T = pd.DataFrame(tab).set_index("policy")
    pv = []; tt = []
    for pol in PRIMARY:
        w = stats.wilcoxon(U[pol].values, U["cardinality_true"].values, method="approx"); pv.append(w.pvalue)
        tt.append(stats.ttest_rel(U[pol].values, U["cardinality_true"].values).statistic)
    T.loc[PRIMARY, "p_wilcoxon_holm"] = holm(pv); T.loc[PRIMARY, "t_paired"] = tt
    T.loc["forward_only", "mean_scans"] = F["fwd_scan"].mean()
    ps = d[d.policy == "equal_work_edge_paperstop"].pivot_table(index=["cluster", "pair"], columns="policy", values="scan")
    T.loc["equal_work_edge_paperstop", "mean_scans"] = (ps.groupby(level=0).mean() if ds == "clustered_frozen" else ps).values.mean()
    print(T.round(3).to_string())
    OUT[ds] = T.round(4).reset_index().to_dict("records")
json.dump(OUT, open("policy_results.json", "w"), indent=1, default=float)
