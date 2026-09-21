Bidirectional scheduling harness v3 (Python 3.12; numpy, pandas, scipy). Run from this directory, in order:
  python3 bidir_pasted_original.py   # the pasted harness (+1 added optimality check)        -> orig_runs.pkl
  python3 run_prov.py                # v2 on frozen seeds; exact regression vs pasted harness -> prov_v2.pkl
  python3 verify_v3.py               # v3 == v2 (1350 runs); 8 policy variants optimal on random directed multigraphs
  sh fetch_real_graphs.sh            # real graphs (network needed)
  python3 exp_policies.py            # 3 graph families x 8 policy variants -> exp_policies.pkl
  python3 analyze_policies.py        # Holm-corrected contrasts, bootstrap CIs, regret -> policy_results.json
  python3 exp_scaling.py             # size sweep 75..1200 per cluster -> scaling_results.json
  python3 claims_v2.py ; python3 replicate.py   # frozen-ensemble claim tests and 9 fresh-seed replications
