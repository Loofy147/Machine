"""
bidir_v3.py -- bidirectional Dijkstra scheduling policies on directed multigraphs (forward + predecessor-fiber adjacency).

Policies (names follow the literature as characterised by Haeupler et al., arXiv:2410.14638v4, Sec. 2):
  alternate          Dantzig 1963: alternate whole-vertex expansions
  min_key            Nicholson 1966: expand the side whose next vertex has the smaller key
  cardinality_true   Pohl 1969: expand the side with fewer open vertices (exact count)
  cardinality_proxy  as above, using heap length (includes stale entries)
  open_work          expand the side whose open set has the smaller total degree (own addition)
  equal_work_vertex  expand the side that has scanned fewer edges so far (vertex-granular equal-work rule)
  equal_work_edge    Haeupler et al. Algorithm 2 (corrected per their errata): alternate single EDGE relaxations
Stopping rule: Pohl's  top_f + top_b >= mu  (for equal_work_edge also the paper's last-closed-key variant).
mu is updated on every relaxation whose target has a finite tentative distance from the other side (no 'closed' guard --
the guard was the bug fixed in the errata).
"""
import heapq
import numpy as np
from bidir_v2 import clean_top, INF

VERTEX_POLICIES = ["alternate", "min_key", "cardinality_true", "cardinality_proxy", "open_work", "equal_work_vertex"]
ALL_POLICIES = VERTEX_POLICIES + ["equal_work_edge"]


def forward_dijkstra(adj_f, s, t):
    c = 0
    pq = [(0.0, c, s)]
    dist = {s: 0.0}
    exp = scans = 0
    while pq:
        d, _, u = heapq.heappop(pq)
        if d > dist.get(u, INF):
            continue
        exp += 1
        if u == t:
            return dict(cost=d, exp=exp, scans=scans)
        scans += len(adj_f[u])
        for v, w in adj_f[u]:
            if d + w < dist.get(v, INF):
                dist[v] = d + w; c += 1
                heapq.heappush(pq, (d + w, c, v))
    return dict(cost=INF, exp=exp, scans=scans)


def bidir_vertex(adj_f, adj_b, s, t, opt_cost, policy):
    adj = (adj_f, adj_b)
    pq = [[(0.0, 0, s)], [(0.0, 0, t)]]
    dist = [{s: 0.0}, {t: 0.0}]
    opn = [{s}, {t}]
    wopen = [len(adj_f[s]), len(adj_b[t])]
    cnt = [0, 0]; exp = [0, 0]; scan = [0, 0]; push = [0, 0]
    stale = 0; mu = INF
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
        elif policy == "equal_work_vertex":
            ef = scan[0] <= scan[1]
        else:
            raise ValueError(policy)
        sd = 0 if ef else 1
        d, _, u = heapq.heappop(pq[sd])
        opn[sd].discard(u); wopen[sd] -= len(adj[sd][u])
        exp[sd] += 1; scan[sd] += len(adj[sd][u])
        flag_c = flag_o = False
        for v, w in adj[sd][u]:
            nd = d + w
            if nd < dist[sd].get(v, INF):
                dist[sd][v] = nd; cnt[sd] += 1
                heapq.heappush(pq[sd], (nd, cnt[sd], v)); push[sd] += 1
                if v not in opn[sd]:
                    opn[sd].add(v); wopen[sd] += len(adj[sd][v])
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
               total_stale=stale, exp_f=exp[0], exp_b=exp[1], scan_f=scan[0], scan_b=scan[1])
    for name, S in (("pre", S1), ("res", S2), ("cert", S3)):
        out[f"{name}_exp"] = S[0] + S[1]; out[f"{name}_scan"] = S[2] + S[3]
    return out


def bidir_edge(adj_f, adj_b, s, t, opt_cost, stop="top"):
    """Haeupler-Hladik-Rozhon-Tarjan-Tetek Algorithm 2 (errata version): strictly alternate ONE edge relaxation per side."""
    adj = (adj_f, adj_b)
    dist = [{s: 0.0}, {t: 0.0}]
    pq = [[(0.0, 0, s)], [(0.0, 0, t)]]
    cnt = [0, 0]; closed = [set(), set()]
    cur = [None, None]; it = [0, 0]
    dlast = [0.0, 0.0]
    exp = [0, 0]; scan = [0, 0]; push = [0, 0]
    mu = INF
    side = 0; done = False
    while not done:
        performed = False
        while not performed:
            if cur[side] is None:
                if stop == "top":
                    tf, _ = clean_top(pq[0], dist[0]); tb, _ = clean_top(pq[1], dist[1])
                    # a side that is mid-vertex still has unrelaxed edges: its lower bound must include that vertex's key
                    lb0 = min(tf, dist[0][cur[0]]) if cur[0] is not None else tf
                    lb1 = min(tb, dist[1][cur[1]]) if cur[1] is not None else tb
                    if lb0 + lb1 >= mu or not pq[side]:
                        done = True; break
                    d, _, u = heapq.heappop(pq[side])
                else:                                   # paper rule: last closed keys, lazy deletion
                    u = None
                    while pq[side]:
                        d, _, x = heapq.heappop(pq[side])
                        if x in closed[side] or d > dist[side][x]:
                            continue
                        u = x; break
                    if u is None:
                        done = True; break
                closed[side].add(u); exp[side] += 1
                dlast[side] = dist[side][u]
                if stop != "top" and dlast[0] + dlast[1] >= mu:
                    done = True; break
                if not adj[side][u]:
                    continue
                cur[side] = u; it[side] = 0
            u = cur[side]
            v, w = adj[side][u][it[side]]
            it[side] += 1
            if it[side] >= len(adj[side][u]):
                cur[side] = None
            scan[side] += 1; performed = True
            nd = dist[side][u] + w
            if v not in closed[side] and nd < dist[side].get(v, INF):
                dist[side][v] = nd; cnt[side] += 1
                heapq.heappush(pq[side], (nd, cnt[side], v)); push[side] += 1
            o = dist[1 - side].get(v)
            if o is not None and nd + o < mu:
                mu = nd + o
        side = 1 - side
    return dict(cost=mu, total_exp=exp[0] + exp[1], total_scan=scan[0] + scan[1], total_push=push[0] + push[1],
                exp_f=exp[0], exp_b=exp[1], scan_f=scan[0], scan_b=scan[1])


def run_policy(adj_f, adj_b, s, t, opt_cost, policy):
    if policy == "equal_work_edge":
        return bidir_edge(adj_f, adj_b, s, t, opt_cost, "top")
    if policy == "equal_work_edge_paperstop":
        return bidir_edge(adj_f, adj_b, s, t, opt_cost, "paper")
    return bidir_vertex(adj_f, adj_b, s, t, opt_cost, policy)


# ------------------------------------------------------------------------------------------ graph builders
def directed_hub_graph(n=20000, k=4, seed=1, hubs=50, p_hub=0.3, wmax=9):
    """Directed multigraph from the substrate generator: out-degree k, hubs receive p_hub of all arcs; weights 1..wmax."""
    from substrate_lib import gen_system
    delta = gen_system(n, k, seed, hubs, p_hub)
    rng = np.random.default_rng(seed + 10_000)
    W = rng.integers(1, wmax + 1, size=(n, k)).astype(float)
    adj_f = [[(int(delta[s, a]), float(W[s, a])) for a in range(k)] for s in range(n)]
    adj_b = [[] for _ in range(n)]
    for s in range(n):
        for a in range(k):
            adj_b[int(delta[s, a])].append((s, float(W[s, a])))
    return adj_f, adj_b


def load_metis(path, seed=0, wmax=9):
    """Undirected METIS graph (unweighted) -> adjacency with symmetric random integer weights 1..wmax."""
    with open(path) as f:
        lines = [l for l in f if not l.startswith("%")]
    n, m = map(int, lines[0].split()[:2])
    rng = np.random.default_rng(seed)
    wts = {}
    adj = [[] for _ in range(n)]
    for u in range(n):
        for tok in lines[1 + u].split():
            v = int(tok) - 1
            if v == u:
                continue
            key = (u, v) if u < v else (v, u)
            if key not in wts:
                wts[key] = float(rng.integers(1, wmax + 1))
            adj[u].append((v, wts[key]))
    return adj


def largest_component(adj):
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components
    n = len(adj)
    rows = np.repeat(np.arange(n), [len(a) for a in adj]); cols = np.array([v for a in adj for v, _ in a])
    ncomp, lab = connected_components(csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n)), directed=False)
    big = np.bincount(lab).argmax()
    return np.flatnonzero(lab == big)
