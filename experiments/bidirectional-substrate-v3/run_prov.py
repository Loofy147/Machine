import time, pandas as pd, numpy as np
from bidir_v2 import *
t=time.time()
df = run_experiment(300, provenance=True)
print("runs", len(df), "instances", df.instance_id.nunique(), "graphs", df.graph_id.nunique(), f"{time.time()-t:.1f}s")
orig = pd.read_pickle("orig_runs.pkl")
ok, n = verify_regression(df[df.policy.isin(POLICIES_ORIG)], orig)
print("regression: v2 reproduces the pasted harness exactly on", n, "runs ->", ok)
print("graph seeds unique:", len(set(df.attrs["graph_seeds"])), "/ 90 ; query seeds unique:", len(set(df.attrs["query_seeds"])), "/ 90")
df.to_pickle("prov_v2.pkl")
print(df.groupby("policy")[["pre_exp","res_exp","cert_exp","total_exp","total_scan","total_push"]].mean().round(2).to_string())
