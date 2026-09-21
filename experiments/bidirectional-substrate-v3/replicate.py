import json, time, numpy as np, pandas as pd
from scipy import stats
from bidir_v2 import *

def summarize(df):
    g = lambda m: df.pivot_table(index="graph_id", columns="policy", values=m, aggfunc="mean")
    pre, cert, res, scan, exp_, fx = g("pre_exp"), g("cert_exp"), g("res_exp"), g("total_scan"), g("total_exp"), g("fwd_scan")
    r = lambda a, b: 100 * (a.mean() / b.mean() - 1)
    t = lambda d: stats.ttest_1samp(d, 0).statistic
    dres = [res["alternate"] - res["cardinality_true"], res["min_key"] - res["cardinality_true"]]
    marg = []
    for d in dres:
        se = d.std(ddof=1) / np.sqrt(len(d)); tc = stats.t.ppf(.95, len(d) - 1); marg.append(max(abs(d.mean() - tc * se), abs(d.mean() + tc * se)))
    fs = fx["min_key"]  # forward-only scans (same for every policy column)
    mk_vs_fwd = (fs - scan["min_key"])
    return dict(
        minkey_pre_pct=r(pre["min_key"], pre["cardinality_true"]), minkey_pre_t=t(pre["min_key"] - pre["cardinality_true"]),
        alt_cert_pct=r(cert["alternate"], cert["cardinality_true"]), alt_cert_t=t(cert["alternate"] - cert["cardinality_true"]),
        stage2_means=[round(float(res[p].mean()), 1) for p in ["alternate", "min_key", "cardinality_true"]],
        stage2_friedman_p=float(stats.friedmanchisquare(res["alternate"], res["min_key"], res["cardinality_true"]).pvalue),
        stage2_equiv_margin=[round(float(m), 1) for m in marg], stage2_share_pct=100 * df.res_exp.sum() / df.total_exp.sum(),
        minkey_scan_pct=r(scan["min_key"], scan["cardinality_true"]), alt_scan_pct=r(scan["alternate"], scan["cardinality_true"]),
        minkey_vs_fwd_scan_t=t(mk_vs_fwd), minkey_vs_fwd_scan_savings_pct=100 * mk_vs_fwd.mean() / fs.mean(),
        card_vs_fwd_unanimous_exp=int(((g("fwd_exp")["cardinality_true"] - exp_["cardinality_true"]) > 0).sum()),
        proxy_vs_true_exp_pct=r(exp_["cardinality_proxy"], exp_["cardinality_true"]),
        n_graphs=int(len(pre)), n_instances=int(df.instance_id.nunique()))

configs = [(300, e) for e in (11, 12, 13, 14, 15)] + [(150, e) for e in (21, 22)] + [(600, e) for e in (31, 32)]
rows = []
for npc, ent in configs:
    t0 = time.time(); d = run_experiment(npc, provenance=False, entropy=ent)
    s = summarize(d); s.update(n_per_cluster=npc, entropy=ent); rows.append(s)
    print(f"n={npc:4d} seed={ent:3d} ({time.time()-t0:4.1f}s) min_key pre {s['minkey_pre_pct']:+6.1f}% (t={s['minkey_pre_t']:5.1f}) | alt cert {s['alt_cert_pct']:+6.1f}% (t={s['alt_cert_t']:5.1f}) | "
          f"stage2 means {s['stage2_means']} Fried p={s['stage2_friedman_p']:.2f} margin {s['stage2_equiv_margin']} | scans: min_key {s['minkey_scan_pct']:+.0f}% alt {s['alt_scan_pct']:+.0f}% | min_key vs fwd scans t={s['minkey_vs_fwd_scan_t']:.1f} | proxy~true {s['proxy_vs_true_exp_pct']:+.1f}%", flush=True)
R = pd.DataFrame(rows)
R.to_pickle("replication.pkl"); json.dump(rows, open("replication.json", "w"), indent=1, default=float)
print("\nsummary over 9 replications:")
for c in ["minkey_pre_pct", "alt_cert_pct", "minkey_scan_pct", "alt_scan_pct", "stage2_share_pct", "minkey_vs_fwd_scan_savings_pct"]:
    print(f"  {c:32s} min {R[c].min():7.1f}  median {R[c].median():7.1f}  max {R[c].max():7.1f}")
print("  stage2 Friedman p<0.05 in", int((R.stage2_friedman_p < .05).sum()), "of", len(R), "replications")
print("  min_key sig. worse than card in pre stage (t>2):", int((R.minkey_pre_t > 2).sum()), "/", len(R), "; alt cert tax t>2:", int((R.alt_cert_t > 2).sum()), "/", len(R))
