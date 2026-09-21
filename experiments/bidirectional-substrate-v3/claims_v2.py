import json, itertools, sys
import numpy as np, pandas as pd
from scipy import stats
from bidir_v2 import *

OUT = {}
df = pd.read_pickle("prov_v2.pkl")
P5 = POLICIES_ALL
df["sep_exp"] = df["fwd_exp"] / df["total_exp"]            # separation efficiency (expansions)
df["sep_scan"] = df["fwd_scan"] / df["total_scan"]          # separation efficiency (edge work)


def gl(d, metric):
    return d.pivot_table(index="graph_id", columns="policy", values=metric, aggfunc="mean")


def paired(a, b):
    d = (a - b).values
    t, p = stats.ttest_1samp(d, 0.0)
    w = stats.wilcoxon(a, b, method="approx")
    return dict(mean_diff=float(d.mean()), t=float(t), p_t=float(p), W=float(w.statistic), p_w_approx=float(w.pvalue),
                n_pos=int((d > 0).sum()), n_neg=int((d < 0).sum()), n=len(d))


def pct(d, metric, x, y, boot=4000, seed=0):
    """ratio of means x/y - 1 with graph-cluster bootstrap CI."""
    G = d.pivot_table(index="graph_id", columns="policy", values=metric, aggfunc="mean")
    rng = np.random.default_rng(seed)
    n = len(G); ax, ay = G[x].values, G[y].values
    pt = ax.mean() / ay.mean() - 1
    bs = []
    for _ in range(boot):
        i = rng.integers(0, n, n); bs.append(ax[i].mean() / ay[i].mean() - 1)
    return dict(point_pct=100 * pt, ci95=[100 * np.percentile(bs, 2.5), 100 * np.percentile(bs, 97.5)])


print("=" * 100); print("A. HEADLINE PERCENTAGES (ratio of means, graph-cluster bootstrap 95% CI)")
A = {}
A["minkey_pre_vs_card"] = pct(df, "pre_exp", "min_key", "cardinality_true")
A["alt_cert_vs_card"] = pct(df, "cert_exp", "alternate", "cardinality_true")
A["alt_pre_vs_card"] = pct(df, "pre_exp", "alternate", "cardinality_true")
A["minkey_cert_vs_card"] = pct(df, "cert_exp", "min_key", "cardinality_true")
A["alt_total_vs_card"] = pct(df, "total_exp", "alternate", "cardinality_true")
A["minkey_total_vs_card"] = pct(df, "total_exp", "min_key", "cardinality_true")
A["alt_scan_vs_card"] = pct(df, "total_scan", "alternate", "cardinality_true")
A["minkey_scan_vs_card"] = pct(df, "total_scan", "min_key", "cardinality_true")
for k, v in A.items():
    print(f"  {k:24s} {v['point_pct']:+7.2f}%   95% CI [{v['ci95'][0]:+.2f}, {v['ci95'][1]:+.2f}]")
OUT["A_percentages"] = A

print("=" * 100); print("B. WHERE DO t(89)=13.224, W=0, p=1.74e-16 COME FROM?  (all 10 policy pairs x 8 metrics, graph-clustered n=90)")
rows = []
for metric in ["total_exp", "total_scan", "pre_exp", "res_exp", "cert_exp", "sep_exp", "sep_scan", "total_push"]:
    G = gl(df, metric)
    for x, y in itertools.combinations(P5, 2):
        r = paired(G[x], G[y]); r.update(metric=metric, x=x, y=y); rows.append(r)
R = pd.DataFrame(rows)
R["dist_to_13.224"] = (R["t"].abs() - 13.224).abs()
print("  pairs with W==0 (unanimous):")
print(R[R.W == 0][["metric", "x", "y", "mean_diff", "t", "W", "p_w_approx"]].round(4).to_string(index=False) if (R.W == 0).any() else "   none")
print("  closest |t| to 13.224:")
print(R.sort_values("dist_to_13.224").head(5)[["metric", "x", "y", "mean_diff", "t", "W", "n_pos", "n_neg"]].round(3).to_string(index=False))
OUT["B_closest_to_claimed_t"] = R.sort_values("dist_to_13.224").head(5)[["metric", "x", "y", "t", "W"]].to_dict("records")
OUT["B_unanimous_pairs"] = R[R.W == 0][["metric", "x", "y", "t"]].to_dict("records")
n = 90; z = (0 - n * (n + 1) / 4) / np.sqrt(n * (n + 1) * (2 * n + 1) / 24)
OUT["B_wilcoxon_p_floor"] = dict(normal_approx=float(2 * stats.norm.cdf(z)), exact=float(2.0 ** (1 - n)))
print(f"  Wilcoxon unanimity floor at n=90: normal-approx p={2*stats.norm.cdf(z):.3g}, exact p={2.0**(1-n):.3g}")

print("=" * 100); print("C. IS PHASE 2 (E_res) INVARIANT?  paired graph-level diffs + TOST equivalence margin (90% CI)")
G = gl(df, "res_exp"); C = {}
for x, y in [("alternate", "cardinality_true"), ("min_key", "cardinality_true"), ("alternate", "min_key")]:
    d = (G[x] - G[y]).values; se = d.std(ddof=1) / np.sqrt(len(d)); tcrit = stats.t.ppf(0.95, len(d) - 1)
    lo, hi = d.mean() - tcrit * se, d.mean() + tcrit * se
    C[f"{x}-{y}"] = dict(mean=float(d.mean()), ci90=[float(lo), float(hi)], min_equiv_margin=float(max(abs(lo), abs(hi))), p_t=float(stats.ttest_1samp(d, 0).pvalue))
    print(f"  {x:>10s} - {y:16s} mean={d.mean():6.2f}  90% CI [{lo:6.2f},{hi:6.2f}]  smallest symmetric equivalence margin = {max(abs(lo),abs(hi)):.2f} expansions")
print("  Friedman:", stats.friedmanchisquare(G["alternate"], G["min_key"], G["cardinality_true"]))
print("  stage-2 means:", df.groupby("policy")["res_exp"].mean().round(2).to_dict(), "| pooled mean", round(df.res_exp.mean(), 2))
OUT["C_stage2_equivalence"] = C

print("=" * 100); print("D. MECHANISM TESTS")
# D1: min_key pre-contact dilation vs local degree density (dose-response)
Gp = gl(df, "pre_exp"); meta = df.drop_duplicates("graph_id").set_index("graph_id")[["beta", "alpha_nominal", "alpha_realized"]]
dil = (Gp["min_key"] - Gp["cardinality_true"]).rename("dil")
M = meta.join(dil)
rho, prho = stats.spearmanr(M["alpha_realized"], M["dil"])
sl = stats.linregress(M["alpha_realized"], M["dil"])
print(f"  D1 min_key pre-contact dilation vs alpha_realized: spearman rho={rho:.3f} (p={prho:.2g}); slope={sl.slope:.1f} expansions per unit alpha (R2={sl.rvalue**2:.3f})")
print("     mean dilation by nominal alpha:", M.groupby("alpha_nominal")["dil"].mean().round(1).to_dict(), " by beta:", M.groupby("beta")["dil"].mean().round(1).to_dict())
D1 = dict(spearman_rho=float(rho), p=float(prho), slope=float(sl.slope), R2=float(sl.rvalue ** 2),
          by_alpha=M.groupby("alpha_nominal")["dil"].mean().round(2).to_dict(), by_beta=M.groupby("beta")["dil"].mean().round(2).to_dict())
# D2: which side does min_key burn its pre-contact budget on?
side = df.groupby("policy")[["pre_exp_f", "pre_exp_b", "cert_exp_f", "cert_exp_b"]].mean()
side["pre_fwd_frac"] = side["pre_exp_f"] / (side["pre_exp_f"] + side["pre_exp_b"])
side["cert_fwd_frac"] = side["cert_exp_f"] / (side["cert_exp_f"] + side["cert_exp_b"])
print("  D2 side split of expansions (fwd = sparse cluster A, bwd = cluster B):")
print(side.round(3).to_string())
# D3: alternate cert tax vs 1:1 rigidity -- is the tax concentrated where the two sides differ in cost?
Gc = gl(df, "cert_exp"); tax = (Gc["alternate"] - Gc["cardinality_true"]).rename("tax")
M2 = meta.join(tax)
print("  D3 alternate cert tax by nominal alpha:", M2.groupby("alpha_nominal")["tax"].mean().round(1).to_dict(), "| by beta:", M2.groupby("beta")["tax"].mean().round(1).to_dict())
rho2, p2 = stats.spearmanr(M2["alpha_realized"], M2["tax"])
print(f"     spearman(tax, alpha_realized) = {rho2:.3f} (p={p2:.2g})")
D3 = dict(by_alpha=M2.groupby("alpha_nominal")["tax"].mean().round(2).to_dict(), spearman=float(rho2), p=float(p2))
OUT["D_mechanism"] = dict(D1=D1, side_split=side.round(4).to_dict(), D3=D3)

print("=" * 100); print("E. WORK (edge scans) instead of expansions")
E = df.groupby("policy")[["total_exp", "total_scan", "total_push"]].mean().round(1)
E["scan_vs_card_pct"] = (100 * (E["total_scan"] / E.loc["cardinality_true", "total_scan"] - 1)).round(1)
E["exp_vs_card_pct"] = (100 * (E["total_exp"] / E.loc["cardinality_true", "total_exp"] - 1)).round(1)
print(E.to_string())
OUT["E_work"] = E.to_dict()
Gs = gl(df, "total_scan")
OUT["E_scan_tests"] = {f"{x}-{y}": paired(Gs[x], Gs[y]) for x, y in [("min_key", "cardinality_true"), ("alternate", "cardinality_true"), ("open_work", "cardinality_true"), ("cardinality_proxy", "cardinality_true")]}
for k, v in OUT["E_scan_tests"].items():
    print(f"   {k:32s} t={v['t']:7.2f}  (+{v['n_pos']}/-{v['n_neg']})  W={v['W']:.0f}")

print("=" * 100); print("F. e7m2r1: how much of separation-ratio variance do (beta, alpha_nominal, alpha_realized, geodesic) explain?")
def ols_r2(X, y):
    X1 = np.column_stack([np.ones(len(X)), X]); b, *_ = np.linalg.lstsq(X1, y, rcond=None)
    res = y - X1 @ b; return 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum(), b
def grouped_cv_r2(X, y, groups, k=5, seed=0):
    ug = np.unique(groups); rng = np.random.default_rng(seed); rng.shuffle(ug); folds = np.array_split(ug, k)
    sse = 0.0
    for f in folds:
        te = np.isin(groups, f); Xtr = np.column_stack([np.ones((~te).sum()), X[~te]]); b, *_ = np.linalg.lstsq(Xtr, y[~te], rcond=None)
        pred = np.column_stack([np.ones(te.sum()), X[te]]) @ b; sse += ((y[te] - pred) ** 2).sum()
    return 1 - sse / ((y - y.mean()) ** 2).sum()
Fres = {}
for pol in P5:
    d = df[df.policy == pol]; y = d["sep_exp"].values; g = d["graph_id"].values
    XA = d[["beta", "alpha_nominal", "alpha_realized", "hop"]].values.astype(float)
    XB = d[["beta", "alpha_nominal", "alpha_realized", "hop", "opt_cost", "d_s_bridge", "d_t_bridge", "deg_s", "deg_t"]].values.astype(float)
    XA2 = d[["beta", "alpha_nominal", "alpha_realized", "opt_cost"]].values.astype(float)     # geodesic = weighted shortest-path cost
    cell = pd.get_dummies(d["beta"].astype(str) + "_" + d["alpha_nominal"].astype(str)).values.astype(float)
    # between-graph share of variance (one-way ANOVA eta^2 on graph id)
    gm = d.groupby("graph_id")["sep_exp"].transform("mean"); eta2 = 1 - ((y - gm) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    r2A, _ = ols_r2(XA, y); r2B, _ = ols_r2(XB, y); r2C, _ = ols_r2(cell[:, 1:], y)
    r2A2, _ = ols_r2(XA2, y)
    Fres[pol] = dict(R2_specified=r2A, R2_specified_weightedgeo=r2A2, cvR2_specified=grouped_cv_r2(XA, y, g), R2_cell_means=r2C, R2_plus_query_local=r2B,
                     cvR2_plus_query_local=grouped_cv_r2(XB, y, g), eta2_between_graph=eta2)
print(pd.DataFrame(Fres).T.round(3).to_string())
OUT["F_variance"] = Fres

print("=" * 100); print("G. BIDIRECTIONAL vs FORWARD-ONLY DIJKSTRA (graph-level, n=90)")
Gf = {}
for pol in P5:
    d = df[df.policy == pol].groupby("graph_id")[["fwd_exp", "total_exp", "fwd_scan", "total_scan"]].mean()
    r = {}
    for a, b, lab in [("fwd_exp", "total_exp", "exp"), ("fwd_scan", "total_scan", "scan")]:
        diff = d[a] - d[b]; w = stats.wilcoxon(d[a], d[b], method="approx")
        r[lab] = dict(saving_pct=float(100 * diff.mean() / d[a].mean()), t=float(stats.ttest_1samp(diff, 0).statistic), W=float(w.statistic), n_pos=int((diff > 0).sum()), n_neg=int((diff < 0).sum()))
    Gf[pol] = r
    print(f"  {pol:18s} expansions saved {r['exp']['saving_pct']:5.1f}% (t={r['exp']['t']:6.2f}, W={r['exp']['W']:.0f}, +{r['exp']['n_pos']}/-{r['exp']['n_neg']}) | edge scans saved {r['scan']['saving_pct']:6.1f}% (t={r['scan']['t']:6.2f}, W={r['scan']['W']:.0f}, +{r['scan']['n_pos']}/-{r['scan']['n_neg']})")
OUT["G_vs_forward_only"] = Gf
json.dump(OUT, open("claims_v2_results.json", "w"), indent=1, default=float)
print("saved claims_v2_results.json")
