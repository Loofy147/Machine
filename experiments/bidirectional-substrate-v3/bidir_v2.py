"""
bidir_v2.py -- instrumented, self-verifying harness for bidirectional Dijkstra scheduling policies.

Changes vs the pasted harness (semantics of expansions are unchanged; verified by exact regression, see verify_regression):
  * every returned cost is checked against forward Dijkstra (optimality)               [was unchecked]
  * stage boundaries are snapshots of cumulative counters (expansions, edge scans, heap pushes, stale pops), per side
  * stages renamed:  E_pre (start -> first contact), E_res (contact -> optimum first held), E_cert (optimum held -> proof)
  * 'stale_pops_cert' in the original is the WHOLE-run stale count; here stale pops are attributed per stage
  * extra policies: cardinality_proxy (heap length incl. stale entries), open_work (sum of degrees of open nodes)
  * seeds: provenance mode reproduces the frozen seeds exactly; fresh mode derives all seeds from a SeedSequence
"""
import heapq
import numpy as np
import pandas as pd
from collections import deque

INF = float("inf")


# ------------------------------------------------------------------------------------------- generator (RNG order unchanged)
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
                adj[i].append((j, w)); adj[j].append((i, w))
    k_B = int(k_A * alpha_nominal)
    for i in range(n_per_cluster, total_nodes):
        for _ in range(k_B // 2):
            j = int(rng.integers(n_per_cluster, total_nodes))
            if i != j:
                w = float(rng.integers(1, 10))
                adj[i].append((j, w)); adj[j].append((i, w))
    bridge_sources = rng.choice(n_per_cluster, size=beta_bridge, replace=False)
    bridge_targets = rng.choice(np.arange(n_per_cluster, total_nodes), size=beta_bridge, replace=False)
    for s_b, t_b in zip(bridge_sources, bridge_targets):
        w = float(rng.integers(1, 5))
        adj[int(s_b)].append((int(t_b), w)); adj[int(t_b)].append((int(s_b), w))
    deg_A = np.mean([len(adj[u]) for u in range(n_per_cluster)])
    deg_B = np.mean([len(adj[u]) for u in range(n_per_cluster, total_nodes)])
    return adj, total_nodes, (deg_B / deg_A if deg_A > 0 else float("nan"))


def clean_top(pq, dist):
    purged = 0
    while pq:
        k, _, u = pq[0]
        if k > dist.get(u, INF):
            heapq.heappop(pq); purged += 1
        else:
            return k, purged
    return INF, purged


def forward_dijkstra(adj, s, t):
    c = 0
    pq = [(0.0, c, s)]
    dist = {s: 0.0}
    expanded = 0; scans = 0
    while pq:
        d, _, u = heapq.heappop(pq)
        if d > dist.get(u, INF):
            continue
        expanded += 1
        if u == t:
            return {"expanded": expanded, "cost": d, "scans": scans}
        scans += len(adj[u])
        for v, w in adj[u]:
            if d + w < dist.get(v, INF):
                dist[v] = d + w; c += 1
                heapq.heappush(pq, (d + w, c, v))
    return {"expanded": expanded, "cost": INF, "scans": scans}


def all_dijkstra(adj, s):
    dist = {s: 0.0}; pq = [(0.0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, INF):
            continue
        for v, w in adj[u]:
            if d + w < dist.get(v, INF):
                dist[v] = d + w; heapq.heappush(pq, (d + w, v))
    return dist


def hop_distance(adj, s, t):
    seen = {s: 0}; dq = deque([s])
    while dq:
        u = dq.popleft()
        if u == t:
            return seen[u]
        for v, _ in adj[u]:
            if v not in seen:
                seen[v] = seen[u] + 1; dq.append(v)
    return -1


POLICIES_ORIG = ["alternate", "min_key", "cardinality_true"]
POLICIES_ALL = POLICIES_ORIG + ["cardinality_proxy", "open_work"]


# ------------------------------------------------------------------------------------------- instrumented search
def bidirectional_v2(adj, deg, s, t, opt_cost, policy):
    pq = [[(0.0, 0, s)], [(0.0, 0, t)]]
    dist = [{s: 0.0}, {t: 0.0}]
    opn = [{s}, {t}]
    wopen = [deg[s], deg[t]]
    cnt = [0, 0]
    exp = [0, 0]; scan = [0, 0]; push = [0, 0]
    stale = 0
    mu = INF
    snap_c = snap_o = None
    while True:
        top_f, p_f = clean_top(pq[0], dist[0]); top_b, p_b = clean_top(pq[1], dist[1])
        stale += p_f + p_b
        if not pq[0] or not pq[1] or top_f + top_b >= mu:
            break
        if policy == "alternate":
            ef = exp[0] <= exp[1]
        elif policy == "min_key":
            ef = top_f <= top_b
        elif policy == "cardinality_true":
            ef = len(opn[0]) <= len(opn[1])
        elif policy == "cardinality_proxy":
            ef = len(pq[0]) <= len(pq[1])
        elif policy == "open_work":
            ef = wopen[0] <= wopen[1]
        else:
            raise ValueError(policy)
        sd = 0 if ef else 1
        d, _, u = heapq.heappop(pq[sd])
        opn[sd].discard(u); wopen[sd] -= deg[u]
        exp[sd] += 1; scan[sd] += deg[u]
        flag_c = flag_o = False
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[sd].get(v, INF):
                dist[sd][v] = nd; cnt[sd] += 1
                heapq.heappush(pq[sd], (nd, cnt[sd], v)); push[sd] += 1
                if v not in opn[sd]:
                    opn[sd].add(v); wopen[sd] += deg[v]
                o = dist[1 - sd].get(v)
                if o is not None and nd + o < mu:
                    mu = nd + o
                    if snap_c is None: flag_c = True
                    if snap_o is None and abs(mu - opt_cost) < 1e-9: flag_o = True
        cur = (exp[0], exp[1], scan[0], scan[1], push[0], push[1], stale)
        if flag_c and snap_c is None: snap_c = cur
        if flag_o and snap_o is None: snap_o = cur
    final = (exp[0], exp[1], scan[0], scan[1], push[0], push[1], stale)
    snap_c = snap_c or final; snap_o = snap_o or final
    zero = (0,) * 7
    dif = lambda a, b: tuple(x - y for x, y in zip(a, b))
    S1, S2, S3 = dif(snap_c, zero), dif(snap_o, snap_c), dif(final, snap_o)
    out = dict(cost=mu, total_exp=exp[0] + exp[1], total_scan=scan[0] + scan[1], total_push=push[0] + push[1],
               total_stale=stale, exp_f=exp[0], exp_b=exp[1])
    for name, S in (("pre", S1), ("res", S2), ("cert", S3)):
        out[f"{name}_exp"] = S[0] + S[1]; out[f"{name}_exp_f"] = S[0]; out[f"{name}_exp_b"] = S[1]
        out[f"{name}_scan"] = S[2] + S[3]; out[f"{name}_push"] = S[4] + S[5]; out[f"{name}_stale"] = S[6]
    return out


# ------------------------------------------------------------------------------------------- experiment driver
BETAS = [1, 3, 5]
ALPHAS = [1.0, 2.5, 4.0]


def run_experiment(n_per_cluster=300, provenance=True, entropy=0, policies=POLICIES_ALL, reps=10, queries=3, verbose=False):
    rows = []; graph_id = 0; instance_id = 0; qseeds = []; gseeds = []
    ss_root = None if provenance else np.random.SeedSequence(entropy).spawn(len(BETAS) * len(ALPHAS) * reps)
    for b in BETAS:
        for a in ALPHAS:
            for rep in range(reps):
                graph_id += 1
                if provenance:
                    g_seed = 1000 + rep * 17 + int(b * 100 + a * 10)
                    q_rng = np.random.default_rng(2000 + rep + graph_id)
                    gseeds.append(g_seed); qseeds.append(2000 + rep + graph_id)
                else:
                    g_ss, q_ss = ss_root[graph_id - 1].spawn(2)
                    g_seed = g_ss; q_rng = np.random.default_rng(q_ss)
                adj, N, ratio = generate_clustered_bottleneck_graph(n_per_cluster, b, a, g_seed)
                deg = [len(adj[u]) for u in range(N)]
                cross = [(u, v, w) for u in range(n_per_cluster) for v, w in adj[u] if v >= n_per_cluster]
                for q in range(queries):
                    s = int(q_rng.integers(0, n_per_cluster)); t = int(q_rng.integers(n_per_cluster, N))
                    fr = forward_dijkstra(adj, s, t)
                    if fr["cost"] == INF:
                        continue
                    instance_id += 1
                    ds, dt = all_dijkstra(adj, s), all_dijkstra(adj, t)
                    feat = dict(hop=hop_distance(adj, s, t), deg_s=deg[s], deg_t=deg[t],
                                d_s_bridge=min(ds[u] for u, v, w in cross), d_t_bridge=min(dt[v] for u, v, w in cross))
                    for pol in policies:
                        r = bidirectional_v2(adj, deg, s, t, fr["cost"], pol)
                        assert abs(r["cost"] - fr["cost"]) < 1e-9, ("NON-OPTIMAL", graph_id, s, t, pol)   # optimality check
                        assert r["pre_exp"] + r["res_exp"] + r["cert_exp"] == r["total_exp"]
                        rows.append(dict(graph_id=graph_id, instance_id=instance_id, beta=b, alpha_nominal=a, alpha_realized=ratio,
                                         policy=pol, fwd_exp=fr["expanded"], fwd_scan=fr["scans"], opt_cost=fr["cost"], **feat, **r))
    df = pd.DataFrame(rows)
    df.attrs["graph_seeds"] = gseeds; df.attrs["query_seeds"] = qseeds
    return df


def verify_regression(df_v2, df_orig):
    """v2 must reproduce the pasted harness exactly: same expansions per stage and same cost, on all 810 runs."""
    m = df_orig.merge(df_v2, on=["graph_id", "instance_id", "policy"], suffixes=("_o", "_n"))
    assert len(m) == len(df_orig) == 810
    ok = ((m["stage1_contact"] == m["pre_exp"]) & (m["stage2_discovery"] == m["res_exp"]) &
          (m["stage3_cert"] == m["cert_exp"]) & (m["total_exp_o"] == m["total_exp_n"]) &
          (m["stale_pops_cert"] == m["total_stale"]) & np.isclose(m["cost_o"], m["cost_n"]))
    return bool(ok.all()), int(len(m))
