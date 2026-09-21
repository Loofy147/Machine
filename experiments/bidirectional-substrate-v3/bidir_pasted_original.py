import numpy as np
import heapq
import pandas as pd

def generate_clustered_bottleneck_graph(n_per_cluster=300, beta_bridge=2, alpha_nominal=3.0, seed=42):
    rng = np.random.default_rng(seed)
    total_nodes = 2 * n_per_cluster
    adj = {u: [] for u in range(total_nodes)}
    k_A = 6
    for i in range(n_per_cluster):
        for _ in range(k_A // 2):
            j = int(rng.integers(0, n_per_cluster))
            if i != j:
                w = float(rng.integers(1, 10))
                adj[i].append((j, w))
                adj[j].append((i, w))
    k_B = int(k_A * alpha_nominal)
    for i in range(n_per_cluster, total_nodes):
        for _ in range(k_B // 2):
            j = int(rng.integers(n_per_cluster, total_nodes))
            if i != j:
                w = float(rng.integers(1, 10))
                adj[i].append((j, w))
                adj[j].append((i, w))
    bridge_sources = rng.choice(n_per_cluster, size=beta_bridge, replace=False)
    bridge_targets = rng.choice(np.arange(n_per_cluster, total_nodes), size=beta_bridge, replace=False)
    for s_b, t_b in zip(bridge_sources, bridge_targets):
        w = float(rng.integers(1, 5))
        adj[int(s_b)].append((int(t_b), w))
        adj[int(t_b)].append((int(s_b), w))
    deg_A = np.mean([len(adj[u]) for u in range(n_per_cluster)])
    deg_B = np.mean([len(adj[u]) for u in range(n_per_cluster, total_nodes)])
    realized_deg_ratio = deg_B / deg_A if deg_A > 0 else float('nan')
    return adj, total_nodes, realized_deg_ratio

def clean_top(pq, dist):
    purged = 0
    while pq:
        top_k, _, top_u = pq[0]
        if top_k > dist.get(top_u, float('inf')):
            heapq.heappop(pq)
            purged += 1
        else:
            return top_k, purged
    return float('inf'), purged

def forward_dijkstra(adj, s, t):
    counter = 0
    pq = [(0.0, counter, s)]
    dist = {s: 0.0}
    expanded = 0
    while pq:
        d, _, u = heapq.heappop(pq)
        if d > dist.get(u, float('inf')):
            continue
        expanded += 1
        if u == t:
            return {"expanded": expanded, "cost": d}
        for v, w in adj[u]:
            if d + w < dist.get(v, float('inf')):
                dist[v] = d + w
                counter += 1
                heapq.heappush(pq, (d + w, counter, v))
    return {"expanded": expanded, "cost": float('inf')}

def bidirectional_unified(adj, s, t, opt_cost, policy="alternate"):
    c_f, c_b = 0, 0
    pq_f = [(0.0, c_f, s)]
    pq_b = [(0.0, c_b, t)]
    dist_f = {s: 0.0}
    dist_b = {t: 0.0}
    active_open_f = {s}
    active_open_b = {t}
    mu = float('inf')
    first_cross_exp = None
    opt_found_exp = None
    exp_f, exp_b = 0, 0
    stale_pops_cert = 0
    while True:
        top_f, p_f = clean_top(pq_f, dist_f)
        top_b, p_b = clean_top(pq_b, dist_b)
        stale_pops_cert += (p_f + p_b)
        if not pq_f or not pq_b or top_f + top_b >= mu:
            break
        if policy == "alternate":
            expand_f = (exp_f <= exp_b)
        elif policy == "min_key":
            expand_f = (top_f <= top_b)
        elif policy == "cardinality_true":
            expand_f = (len(active_open_f) <= len(active_open_b))
        else:
            raise ValueError(f"Unknown policy: {policy}")
        if expand_f:
            d, _, u = heapq.heappop(pq_f)
            active_open_f.discard(u)
            exp_f += 1
            for v, w in adj[u]:
                if d + w < dist_f.get(v, float('inf')):
                    dist_f[v] = d + w
                    c_f += 1
                    heapq.heappush(pq_f, (d + w, c_f, v))
                    active_open_f.add(v)
                    if v in dist_b:
                        if dist_f[v] + dist_b[v] < mu:
                            mu = dist_f[v] + dist_b[v]
                            if first_cross_exp is None:
                                first_cross_exp = exp_f + exp_b
                            if np.isclose(mu, opt_cost) and opt_found_exp is None:
                                opt_found_exp = exp_f + exp_b
        else:
            d, _, u = heapq.heappop(pq_b)
            active_open_b.discard(u)
            exp_b += 1
            for v, w in adj[u]:
                if d + w < dist_b.get(v, float('inf')):
                    dist_b[v] = d + w
                    c_b += 1
                    heapq.heappush(pq_b, (d + w, c_b, v))
                    active_open_b.add(v)
                    if v in dist_f:
                        if dist_b[v] + dist_f[v] < mu:
                            mu = dist_b[v] + dist_f[v]
                            if first_cross_exp is None:
                                first_cross_exp = exp_f + exp_b
                            if np.isclose(mu, opt_cost) and opt_found_exp is None:
                                opt_found_exp = exp_f + exp_b
    total_exp = exp_f + exp_b
    e_contact = first_cross_exp if first_cross_exp is not None else total_exp
    e_opt_found = opt_found_exp if opt_found_exp is not None else total_exp
    stage1_contact = e_contact
    stage2_discovery = e_opt_found - e_contact
    stage3_cert = total_exp - e_opt_found
    assert stage1_contact + stage2_discovery + stage3_cert == total_exp
    return {
        "total_exp": total_exp,
        "pre_contact": stage1_contact,
        "post_contact": stage2_discovery + stage3_cert,
        "stage1_contact": stage1_contact,
        "stage2_discovery": stage2_discovery,
        "stage3_cert": stage3_cert,
        "stale_pops_cert": stale_pops_cert,
        "cost": mu
    }

betas = [1, 3, 5]
alphas = [1.0, 2.5, 4.0]
policies = ["alternate", "min_key", "cardinality_true"]
unified_rows = []
graph_id = 0
instance_id = 0
for b in betas:
    for a in alphas:
        for rep in range(10):
            graph_id += 1
            g_seed = 1000 + rep * 17 + int(b * 100 + a * 10)
            adj, _, realized_deg_ratio = generate_clustered_bottleneck_graph(
                n_per_cluster=300, beta_bridge=b, alpha_nominal=a, seed=g_seed)
            q_rng = np.random.default_rng(2000 + rep + graph_id)
            for q_idx in range(3):
                s = int(q_rng.integers(0, 300))
                t = int(q_rng.integers(300, 600))
                q_seed = 2000 + rep + graph_id + q_idx * 100
                fwd_res = forward_dijkstra(adj, s, t)
                if fwd_res["cost"] == float('inf'):
                    continue
                instance_id += 1
                opt_cost = fwd_res["cost"]
                for pol in policies:
                    res = bidirectional_unified(adj, s, t, opt_cost, policy=pol)
                    unified_rows.append({
                        "graph_id": graph_id, "instance_id": instance_id, "beta": b,
                        "alpha_nominal": a, "alpha_realized": realized_deg_ratio,
                        "policy": pol, "fwd_exp": fwd_res["expanded"], "opt_cost": opt_cost, **res})

df_unified = pd.DataFrame(unified_rows)
if __name__ == "__main__":
    print("UNIFIED ACCOUNTING VERIFICATION:")
    print(f"Total instances: {instance_id} | Total runs: {len(df_unified)}")
    identity_check = (df_unified["stage1_contact"] + df_unified["stage2_discovery"] + df_unified["stage3_cert"] == df_unified["total_exp"]).all()
    two_stage_check = (df_unified["pre_contact"] + df_unified["post_contact"] == df_unified["total_exp"]).all()
    subset_check = (df_unified["stage2_discovery"] + df_unified["stage3_cert"] == df_unified["post_contact"]).all()
    print(f"Conservation identity holds in 100% of rows: {identity_check}")
    print(f"Two-stage identity holds in 100% of rows:    {two_stage_check}")
    print(f"Stage 2 + Stage 3 == Post-Contact check:    {subset_check}")
    print("\n--- RECONCILED CONSERVATION TABLE ---")
    means = df_unified.groupby("policy")[["pre_contact", "post_contact", "stage1_contact", "stage2_discovery", "stage3_cert", "total_exp"]].mean()
    print(means.to_string())
    # NEW: the pasted code never checks that the returned cost is optimal
    bad = (~np.isclose(df_unified["cost"], df_unified["opt_cost"])).sum()
    print(f"\n[added check] runs whose returned cost != forward-Dijkstra optimum: {bad} / {len(df_unified)}")
    df_unified.to_pickle("orig_runs.pkl")
