import sys, time, json, math, platform, tracemalloc, statistics
from array import array
from collections import deque
import numpy as np
import scipy, scipy.sparse as sp
from scipy.sparse.csgraph import breadth_first_order
from substrate_lib import *

QUICK = "--quick" in sys.argv
RES = {}
pc = time.perf_counter


def stats(xs):
    xs = sorted(xs)
    n = len(xs)
    q = lambda p: xs[min(n - 1, int(p * (n - 1) + 0.5))]
    return dict(median=statistics.median(xs), q1=q(.25), q3=q(.75), min=xs[0], max=xs[-1], n=n)


def bench(fn, reps=5, warm=1):
    for _ in range(warm):
        fn()
    ts = []
    for _ in range(reps):
        t = pc(); fn(); ts.append(pc() - t)
    return stats(ts)


def ms(x):
    return round(x * 1e3, 4)



def naive_step_py(dlist, nn, kk, u):
    hits = 0
    for s in range(nn):
        row = dlist[s]
        for a in range(kk):
            if row[a] == u:
                hits += 1
    return hits


def naive_pernode_fast(dlist, nn, kk, U):
    """Counter-free per-node scan (what a naive implementation would actually run)."""
    seen = bytearray(nn); dq = deque()
    for u in U:
        seen[u] = 1; dq.append(u)
    c = len(U)
    while dq:
        u = dq.popleft()
        for s in range(nn):
            row = dlist[s]
            for a in range(kk):
                if row[a] == u and not seen[s]:
                    seen[s] = 1; dq.append(s); c += 1
    return c


def step_median(dlist, nn, kk, seed=5, warm=2, reps=9):
    r = np.random.default_rng(seed)
    for _ in range(warm):
        naive_step_py(dlist, nn, kk, int(r.integers(0, nn)))
    xs = []
    for _ in range(reps):
        u = int(r.integers(0, nn)); t = pc(); naive_step_py(dlist, nn, kk, u); xs.append(pc() - t)
    return stats(xs)


def pick_target(d, min_frac=0.9, seed=0):
    o, s_, a_ = build_csr_np(d)
    ol, sl = o.tolist(), s_.tolist()
    r = np.random.default_rng(seed)
    for _ in range(1000):
        u = int(r.integers(0, len(d)))
        if basin_csr(ol, sl, [u])[1] >= min_frac * len(d):
            return u
    raise RuntimeError("no large-basin target found")


SPEC = dict(n=50_000, k=4, seed=7, hubs=50, p_hub=0.3)
delta = gen_system(**SPEC)
n, k = delta.shape
flat_l = delta.ravel().tolist()
dl = delta.tolist()

# ---------------------------------------------------------------- environment
RES["env"] = dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                  cpu=[l.split(":")[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")][0],
                  cores=1, spec_system=SPEC)

# ---------------------------------------------------------------- B1 structure
offs, src, act = build_csr_np(delta)
E = int((delta >= 0).sum())
indeg = np.diff(offs)
tgt = np.repeat(np.arange(n), indeg)
uniq = len(np.unique(src.astype(np.int64) * n + tgt))
RES["B1_structure"] = dict(S=n, Sigma=k, E=E, fiber_sum_labeled=int(indeg.sum()), unlabeled_pred_pairs=int(uniq),
                           parallel_edges=E - int(uniq), indeg_mean=float(indeg.mean()), indeg_max=int(indeg.max()),
                           indeg_p99=float(np.percentile(indeg, 99)), indeg_zero=int((indeg == 0).sum()),
                           top_hub_share_of_E=float(indeg.max() / E), csr_valid=validate_csr(delta, offs, src, act))
print("B1", RES["B1_structure"])

# ---------------------------------------------------------------- B2 single-step cost vs fiber size (Theorem 1)
offs_a = array("i", offs.tolist()); src_a = array("i", src.tolist())
rng = np.random.default_rng(1)
us = rng.integers(0, n, 3000).tolist() + np.argsort(-indeg)[:60].tolist()
tp = time.perf_counter_ns
ov = statistics.median([(lambda a, b: b - a)(tp(), tp()) for _ in range(2000)])
fs, ts = [], []
for u in us:
    t0 = tp()
    lo = offs_a[u]; hi = offs_a[u + 1]
    out = [src_a[i] for i in range(lo, hi)]
    t1 = tp()
    fs.append(hi - lo); ts.append(t1 - t0 - ov)
fs = np.array(fs, float); ts = np.array(ts, float)
slope, icpt = np.polyfit(fs, ts, 1)
r2 = 1 - ((ts - (slope * fs + icpt)) ** 2).sum() / ((ts - ts.mean()) ** 2).sum()


def naive_py(u):
    out = []
    for s in range(n):
        row = dl[s]
        for a in range(k):
            if row[a] == u:
                out.append((s, a))
    return out


for u in rng.integers(0, n, 20).tolist():      # correctness of fiber vs scan on the spec system
    assert sorted(naive_py(u)) == sorted(zip(src[offs[u]:offs[u + 1]].tolist(), act[offs[u]:offs[u + 1]].tolist()))
st_py = step_median(dl, n, k)
t_naive_py = [st_py["median"]]
flat = delta.ravel()
t_naive_np = bench(lambda: np.flatnonzero(flat == 12345), reps=200)["median"]
hub = int(np.argmax(indeg)); med_u = int(np.argsort(indeg)[n // 2])
t_hub = bench(lambda: [src_a[i] for i in range(offs_a[hub], offs_a[hub + 1])], reps=50)["median"]
t_med = bench(lambda: [src_a[i] for i in range(offs_a[med_u], offs_a[med_u + 1])], reps=2000)["median"]
RES["B2_step_cost"] = dict(
    fit_ns_per_entry=float(slope), fit_intercept_ns=float(icpt), fit_R2=float(r2), n_points=len(fs),
    naive_py_step_ms={kk_: round(vv * 1e3, 4) if kk_ != "n" else vv for kk_, vv in st_py.items()}, naive_numpy_step_ms=ms(t_naive_np),
    fiber_step_ms_median_node=dict(fiber=int(indeg[med_u]), ms=ms(t_med)),
    fiber_step_ms_top_hub=dict(fiber=int(indeg[hub]), ms=ms(t_hub)),
    speedup_vs_naive_py_median_node=float(np.median(t_naive_py) / t_med),
    speedup_vs_naive_py_top_hub=float(np.median(t_naive_py) / t_hub),
    speedup_vs_naive_np_median_node=float(t_naive_np / t_med), speedup_vs_naive_np_top_hub=float(t_naive_np / t_hub),
    ops_ratio_E_over_fiber_median=float(E / max(1, indeg[med_u])), ops_ratio_E_over_fiber_hub=float(E / indeg[hub]))
print("B2", json.dumps(RES["B2_step_cost"], indent=1))

# ---------------------------------------------------------------- B3 full-basin scaling, several implementations
rows = []
sizes = [1000, 2000, 4000, 10000, 50000] if not QUICK else [1000, 2000, 10000]
c_naive_ns_per_inspection = None
for nn in sizes:
    d = gen_system(nn, 4, 7, 50, .3)
    o, s_, a_ = build_csr_np(d)
    ol, sl = o.tolist(), s_.tolist()
    dlist = d.tolist()
    U = [pick_target(d, 0.9, nn)]
    Zref, rounds = basin_naive_layered(d, U)
    Zn = int(Zref.sum())
    row = dict(S=nn, E=nn * 4, basin=Zn, layered_rounds=rounds)
    # exact operation counts
    _, cnt, insp = basin_csr(ol, sl, U)
    assert cnt == Zn
    row["ops_fiber_entries_touched"] = insp
    row["ops_naive_pernode_inspections"] = Zn * nn * 4
    row["ops_naive_layered_inspections"] = rounds * nn * 4
    # naive per-node, pure python: single-step median (9 samples after 2 warm-ups) and, when feasible, a full measured run
    st = step_median(dlist, nn, 4)
    row["naive_step_py_ms"] = ms(st["median"])
    if nn <= 4000:
        if nn == 1000:   # exact inspection-count check with the counting variant
            _, c_, i_ = basin_naive_pernode(dlist, nn, 4, U)
            assert c_ == Zn and i_ == Zn * nn * 4
        t = pc(); c2 = naive_pernode_fast(dlist, nn, 4, U); tfull = pc() - t
        assert c2 == Zn
        row["naive_pernode_py_ms"] = ms(tfull); row["naive_pernode_py_mode"] = "measured"
        row["projection_error_pct"] = round(100 * (st["median"] * Zn - tfull) / tfull, 1)
        c_naive_ns_per_inspection = tfull / (Zn * nn * 4) * 1e9
    else:
        row["naive_pernode_py_ms"] = ms(st["median"] * Zn); row["naive_pernode_py_mode"] = "projected=basin*step"
    # naive per-node numpy
    reps = 3 if nn <= 10000 else 1
    row["naive_pernode_np_ms"] = ms(bench(lambda: basin_naive_pernode_np(d, U), reps=reps, warm=0)["median"])
    row["naive_layered_np_ms"] = ms(bench(lambda: basin_naive_layered(d, U), reps=5)["median"])
    row["csr_loop_list_ms"] = ms(bench(lambda: basin_csr(ol, sl, U), reps=5)["median"])
    oa, sa = array("i", ol), array("i", sl)
    row["csr_loop_array_ms"] = ms(bench(lambda: basin_csr(oa, sa, U), reps=5)["median"])
    row["csr_numpy_ms"] = ms(bench(lambda: basin_csr_np(o, s_, U), reps=7)["median"])
    row["build_numpy_ms"] = ms(bench(lambda: build_csr_np(d), reps=5)["median"])
    fl = d.ravel().tolist()
    row["build_counting_py_ms"] = ms(bench(lambda: build_csr_count(fl, nn, 4), reps=3)["median"])
    rows.append(row)
    print("B3", nn, {kk: vv for kk, vv in row.items() if kk.endswith("_ms") or kk in ("basin", "layered_rounds")})
RES["B3_basin_scaling"] = rows
# naive per-node py model check: time per inspection roughly constant across measured sizes
RES["B3_naive_py_ns_per_inspection_last_measured"] = c_naive_ns_per_inspection

# ---------------------------------------------------------------- B4 build scaling (P-04 linear?) 
bs = []
for nn in ([6250, 12500, 25000, 50000, 100000] if not QUICK else [6250, 12500, 25000]):
    d = gen_system(nn, 4, 3, 50, .3)
    fl = d.ravel().tolist()
    tc = bench(lambda: build_csr_count(fl, nn, 4), reps=3)["median"]
    tn = bench(lambda: build_csr_np(d), reps=5)["median"]
    bs.append(dict(S=nn, E=nn * 4, counting_py_ms=ms(tc), numpy_sort_ms=ms(tn)))
x = np.log([b["E"] for b in bs])
RES["B4_build_scaling"] = dict(rows=bs,
                               loglog_slope_counting=float(np.polyfit(x, np.log([b["counting_py_ms"] for b in bs]), 1)[0]),
                               loglog_slope_numpy=float(np.polyfit(x, np.log([b["numpy_sort_ms"] for b in bs]), 1)[0]))
print("B4", RES["B4_build_scaling"])

# ---------------------------------------------------------------- B5 standards table on the spec system
U0 = [pick_target(delta, 0.9, 99)]
Zref, rounds0 = basin_naive_layered(delta, U0)
Z0 = int(Zref.sum())


def mem_of(builder):
    import gc
    gc.collect(); tracemalloc.start(); base = tracemalloc.get_traced_memory()[0]
    obj = builder()
    cur = tracemalloc.get_traced_memory()[0] - base
    tracemalloc.stop()
    return obj, cur / 2 ** 20


def mk_hash():
    H = {}
    for s in range(n):
        row = dl[s]
        for a in range(k):
            t = row[a]
            if t >= 0:
                H.setdefault(t, []).append((s, a))
    return H


def mk_adj():
    L = [[] for _ in range(n)]
    for s in range(n):
        row = dl[s]
        for a in range(k):
            t = row[a]
            if t >= 0:
                L[t].append(s * k + a)
    return L


def mk_scipy():
    idx = np.flatnonzero(flat >= 0); dst = flat[idx]
    return sp.csr_matrix(((1 << (idx % k)).astype(np.uint8), (dst, idx // k)), shape=(n, n))


def mk_csr_compact():
    o, s_, a_ = build_csr_np(delta)
    A = array("i"); A.frombytes(o.tobytes())
    B = array("i"); B.frombytes(s_.tobytes())
    C = array("B"); C.frombytes(a_.tobytes())
    return A, B, C


def mk_csr_numpy():
    return build_csr_np(delta)


def bfs_hash(H, U):
    seen = bytearray(n); dq = deque(U)
    for u in U: seen[u] = 1
    c = len(U)
    while dq:
        u = dq.popleft()
        for (v, a) in H.get(u, ()):
            if not seen[v]:
                seen[v] = 1; dq.append(v); c += 1
    return c


def bfs_adj(L, U):
    seen = bytearray(n); dq = deque(U)
    for u in U: seen[u] = 1
    c = len(U)
    while dq:
        u = dq.popleft()
        for x in L[u]:
            v = x // k
            if not seen[v]:
                seen[v] = 1; dq.append(v); c += 1
    return c


def bfs_scipy_loop(G, U):
    ind, ptr = G.indices, G.indptr
    seen = bytearray(n); dq = deque(U)
    for u in U: seen[u] = 1
    c = len(U)
    while dq:
        u = dq.popleft()
        for v in ind[ptr[u]:ptr[u + 1]].tolist():
            if not seen[v]:
                seen[v] = 1; dq.append(v); c += 1
    return c


table = []
def add(name, builder, basin_fn, lookup_fn, build_reps=3, basin_reps=5):
    obj, mem = mem_of(builder)
    tb = bench(builder, reps=build_reps, warm=0)
    got = basin_fn(obj)
    assert got == Z0, (name, got, Z0)
    tq = bench(lambda: basin_fn(obj), reps=basin_reps)
    rr = np.random.default_rng(5).integers(0, n, 100000).tolist()
    t = pc(); ent = lookup_fn(obj, rr); tl = pc() - t
    table.append(dict(paradigm=name, mem_MiB=round(mem, 3), build_ms=stats([x * 1e3 for x in [tb["median"]]])["median"],
                      build_ms_iqr=[ms(tb["q1"]), ms(tb["q3"])], basin_ms=ms(tq["median"]),
                      basin_ms_iqr=[ms(tq["q1"]), ms(tq["q3"])], lookups_per_s_M=round(len(rr) / tl / 1e6, 3),
                      entries_per_s_M=round(ent / tl / 1e6, 3)))
    print("B5", table[-1])


def lk_hash(H, rr):
    e = 0
    for u in rr:
        for x in H.get(u, ()): e += 1
    return e


def lk_adj(L, rr):
    e = 0
    for u in rr:
        for x in L[u]: e += 1
    return e


def lk_scipy(G, rr):
    ind, ptr = G.indices, G.indptr
    e = 0
    for u in rr:
        e += len(ind[ptr[u]:ptr[u + 1]].tolist())
    return e


def lk_compact(obj, rr):
    o, s_, a_ = obj
    e = 0
    for u in rr:
        for i in range(o[u], o[u + 1]): _ = s_[i]; e += 1
    return e


def lk_numpy(obj, rr):
    o, s_, a_ = obj
    e = 0
    for u in rr:
        e += len(s_[o[u]:o[u + 1]])
    return e


add("Dynamic hash (dict of lists of (s,a))", mk_hash, lambda H: bfs_hash(H, U0), lk_hash)
add("Adjacency list (list of lists of ints)", mk_adj, lambda L: bfs_adj(L, U0), lk_adj)
add("SciPy CSR, Python-loop BFS", mk_scipy, lambda G: bfs_scipy_loop(G, U0), lk_scipy)
add("SciPy CSR + csgraph BFS (C)", mk_scipy, lambda G: len(breadth_first_order(G, U0[0], directed=True, return_predecessors=False)), lk_scipy)
add("Compact CSR array('i'), Python-loop BFS", mk_csr_compact, lambda A: basin_csr(A[0], A[1], U0)[1], lk_compact)
add("Compact CSR numpy, vectorised layers", mk_csr_numpy, lambda A: int(basin_csr_np(A[0], A[1], U0).sum()), lk_numpy)
tn = bench(lambda: basin_naive_layered(delta, U0), reps=5)
table.append(dict(paradigm="Naive layered scan (numpy, no index)", mem_MiB=0.0, build_ms=0.0, basin_ms=ms(tn["median"]),
                  basin_ms_iqr=[ms(tn["q1"]), ms(tn["q3"])], lookups_per_s_M=None, entries_per_s_M=None))
tnn = bench(lambda: basin_naive_pernode_np(delta, U0), reps=1, warm=0)
table.append(dict(paradigm="Naive per-node scan (numpy)", mem_MiB=0.0, build_ms=0.0, basin_ms=ms(tnn["median"]),
                  lookups_per_s_M=round(1 / (t_naive_np * 1e6), 5), entries_per_s_M=None))
step_py = statistics.median(t_naive_py)
table.append(dict(paradigm="Naive per-node scan (pure Python)", mem_MiB=0.0, build_ms=0.0,
                  basin_ms=ms(step_py * Z0), note="projected = basin_size x measured single step",
                  lookups_per_s_M=round(1 / (step_py * 1e6), 6), entries_per_s_M=None))
RES["B5_standards"] = dict(basin_size=Z0, layered_rounds=rounds0, rows=table)

# memory model check (exact bytes)
o32 = 4 * (n + 1); s32 = 4 * E; a8 = 1 * E
RES["B5_memory_model_bytes"] = dict(offsets_int32=o32, sources_int32=s32, actions_uint8=a8, total=o32 + s32 + a8,
                                    total_MiB=(o32 + s32 + a8) / 2 ** 20, total_MB_decimal=(o32 + s32 + a8) / 1e6)

# ---------------------------------------------------------------- B6 amortisation
# (a) per-step (spec's definition): build / (naive step - fiber step)
build_np_ms = table[5]["build_ms"] if len(table) > 5 else None
bnp = bench(lambda: build_csr_np(delta), reps=5)["median"]
fl_full = flat_l
bcount = bench(lambda: build_csr_count(fl_full, n, k), reps=3, warm=0)["median"]
am = dict(build_numpy_ms=ms(bnp), build_counting_py_ms=ms(bcount),
          steps_to_amortise_vs_naive_py_step=float(bnp / (step_py - t_med)),
          steps_to_amortise_counting_vs_naive_py_step=float(bcount / (step_py - t_med)),
          steps_to_amortise_vs_naive_numpy_step=float(bnp / (t_naive_np - t_med)),
          steps_to_amortise_counting_vs_naive_numpy_step=float(bcount / (t_naive_np - t_med)))
# (b) multi-query: q independent basin queries, naive layered scan vs build + q fiber queries
qs = [pick_target(delta, 0.9, 1000 + i) for i in range(12)]
tl_ = stats([bench(lambda: basin_naive_layered(delta, [u]), reps=1, warm=0)["median"] for u in qs])["median"]
o_, s_, a_ = build_csr_np(delta)
ts_np = stats([bench(lambda: basin_csr_np(o_, s_, [u]), reps=1, warm=0)["median"] for u in qs])["median"]
ol_, sl_ = o_.tolist(), s_.tolist()
ts_loop = stats([bench(lambda: basin_csr(ol_, sl_, [u]), reps=1, warm=0)["median"] for u in qs])["median"]
am["per_query_ms"] = dict(naive_layered_numpy=ms(tl_), csr_numpy=ms(ts_np), csr_python_loop=ms(ts_loop))
am["queries_to_amortise_build_numpy_vs_layered_scan__numpy_substrate"] = (bnp / (tl_ - ts_np)) if tl_ > ts_np else None
am["queries_to_amortise_build_numpy_vs_layered_scan__python_loop_substrate"] = (bnp / (tl_ - ts_loop)) if tl_ > ts_loop else None
RES["B6_amortisation"] = am
print("B6", json.dumps(am, indent=1))

# ---------------------------------------------------------------- B7 retrograde at scale
rng = np.random.default_rng(21)
cost = rng.integers(1, 10, size=(n, k))
goal = [U0[0]]
ol, sl, al = offs.tolist(), src.tolist(), act.tolist()
cl = cost.tolist()
t = pc(); V, relax, pushes = retro_dijkstra(ol, sl, al, cl, goal, n); td = pc() - t
Vb, sweeps = retro_bellman(delta, cost, goal)
tb_ = bench(lambda: retro_bellman(delta, cost, goal), reps=3, warm=0)["median"]
reach = int(sum(v < INF for v in V))
RES["B7_retrograde"] = dict(equal_to_bellman=bool(list(Vb) == V), states_reaching_goal=reach, relaxations=relax,
                            E=E, relax_over_E=relax / E, heap_pushes=pushes, dijkstra_ms=ms(td),
                            bellman_numpy_sweeps=sweeps, bellman_numpy_ms=ms(tb_),
                            bellman_inspections=sweeps * E)
print("B7", RES["B7_retrograde"])

# ---------------------------------------------------------------- B8 Hopcroft: per-action index vs mixed fiber
hop = []
for kk in ([2, 4, 8, 16] if not QUICK else [2, 4]):
    rng = np.random.default_rng(100 + kk)
    for kind in ("redundant", "random"):
        if kind == "redundant":
            d, acc, base, acc0 = redundant_dfa(rng, 250, kk, 8)
        else:
            d = rng.integers(0, 2000, size=(2000, kk)); acc = rng.random(2000) < .5
        d, acc = reachable_sub(d, acc)
        nn = len(d)
        aoffs, asrc = build_csr_action(d); aol, asl = aoffs.tolist(), asrc.tolist()
        o, s_, a_ = build_csr_np(d); ol, sl, al = o.tolist(), s_.tolist(), a_.tolist()
        c1 = [0]; c2 = [0]

        def pa(s, a):
            lo, hi = aol[s * kk + a], aol[s * kk + a + 1]
            c1[0] += hi - lo + 1
            return asl[lo:hi]

        def pm(s, a):
            lo, hi = ol[s], ol[s + 1]
            c2[0] += hi - lo + 1
            return [sl[i] for i in range(lo, hi) if al[i] == a]
        t = pc(); b1 = hopcroft(nn, kk, pa, acc); t1 = pc() - t
        t = pc(); b2 = hopcroft(nn, kk, pm, acc); t2 = pc() - t
        assert as_partition(b1) == as_partition(b2) == as_partition(moore(d, acc))
        hop.append(dict(Sigma=kk, kind=kind, S=nn, classes=len(set(b1)), ops_per_action_index=c1[0],
                        ops_mixed_fiber=c2[0], ratio_mixed_over_action=c2[0] / c1[0],
                        ops_per_action_over_k_S_log2S=c1[0] / (kk * nn * math.log2(nn)),
                        ms_per_action=ms(t1), ms_mixed=ms(t2)))
        print("B8", hop[-1])
RES["B8_hopcroft"] = hop

# ---------------------------------------------------------------- B9 bidirectional search at scale
def bidir_experiment(dd, npairs, label):
    o, s_, a_ = build_csr_np(dd)
    ol, sl = o.tolist(), s_.tolist()
    dlist = dd.tolist(); od = (dd >= 0).sum(axis=1).tolist()
    rng = np.random.default_rng(31)
    out = {p: dict(exp=[], insp=[]) for p in ("uni", "alternate", "size", "work")}
    dists = []; tries = 0; wrong = 0; unreach = 0
    while len(dists) < npairs and tries < npairs * 6:
        tries += 1
        s, t = int(rng.integers(0, len(dd))), int(rng.integers(0, len(dd)))
        dref, e0, i0 = bfs_uni(dlist, s, t)
        if dref is None:
            unreach += 1
            continue
        dists.append(dref)
        out["uni"]["exp"].append(e0); out["uni"]["insp"].append(i0)
        for pol in ("alternate", "size", "work"):
            g, e1, i1 = bfs_bi(dlist, od, ol, sl, s, t, pol)
            wrong += g != dref
            out[pol]["exp"].append(e1); out[pol]["insp"].append(i1)
    res = dict(label=label, pairs=len(dists), unreachable_skipped=unreach, distance_mismatches=wrong,
               dist_median=float(np.median(dists)), dist_max=int(max(dists)))
    for p in out:
        res[p] = dict(expansions_median=float(np.median(out[p]["exp"])), inspections_median=float(np.median(out[p]["insp"])),
                      inspections_p90=float(np.percentile(out[p]["insp"], 90)))
    res["insp_ratio_uni_over_work"] = res["uni"]["inspections_median"] / res["work"]["inspections_median"]
    res["insp_ratio_uni_over_alternate"] = res["uni"]["inspections_median"] / res["alternate"]["inspections_median"]
    print("B9", json.dumps(res))
    return res


npairs = 150 if not QUICK else 40
RES["B9_bidirectional"] = [bidir_experiment(delta, npairs, "spec system (hubs, p_hub=0.3)"),
                           bidir_experiment(gen_system(50_000, 4, 8, hubs=0, p_hub=0.0), npairs, "uniform random (no hubs)")]


# ---------------------------------------------------------------- B10 dynamic arc updates (P-07)
class DynFibers:
    """Hash-indexed fibers: O(1) expected insert/delete of one arc."""
    def __init__(self, dl_, nn, kk):
        self.n, self.k = nn, kk
        self.d = [r[:] for r in dl_]
        self.fib = [set() for _ in range(nn)]
        for s_ in range(nn):
            for a_ in range(kk):
                t_ = self.d[s_][a_]
                if t_ >= 0:
                    self.fib[t_].add(s_ * kk + a_)

    def set_arc(self, s_, a_, t_):
        old = self.d[s_][a_]
        if old >= 0:
            self.fib[old].discard(s_ * self.k + a_)
        self.d[s_][a_] = t_
        if t_ >= 0:
            self.fib[t_].add(s_ * self.k + a_)

rngu = np.random.default_rng(77)
NU = 200_000
ups = list(zip(rngu.integers(0, n, NU).tolist(), rngu.integers(0, k, NU).tolist(),
               np.where(rngu.random(NU) < 0.1, -1, rngu.integers(0, n, NU)).tolist()))
dyn = DynFibers(dl, n, k)
t = pc()
for s_, a_, t_ in ups:
    dyn.set_arc(s_, a_, t_)
t_upd = pc() - t
dfinal = np.array(dyn.d, dtype=np.int64)
o2, s2, a2 = build_csr_np(dfinal)
ok = all(sorted(dyn.fib[u]) == sorted((s2[o2[u]:o2[u + 1]].astype(np.int64) * k + a2[o2[u]:o2[u + 1]]).tolist()) for u in range(n))
inv_ok = validate_csr(dfinal, o2, s2, a2)
# adversarial: deletes from the top hub fiber -- list-backed vs set-backed fibers
as_list = [int(src[i]) * k + int(act[i]) for i in range(offs[hub], offs[hub + 1])]
hub_keys = np.random.default_rng(3).choice(as_list, 1000, replace=False).tolist()
as_set = set(as_list)
t = pc()
for key in hub_keys: as_list.remove(key)
t_list_del = (pc() - t) / len(hub_keys)
t = pc()
for key in hub_keys: as_set.discard(key)
t_set_del = (pc() - t) / len(hub_keys)
RES["B10_dynamic"] = dict(updates=NU, us_per_update=t_upd / NU * 1e6, fibers_match_rebuild=bool(ok), csr_invariants_hold_after=bool(inv_ok),
                          rebuild_numpy_ms=ms(bnp), updates_equal_to_one_rebuild=float(bnp / (t_upd / NU)),
                          hub_fiber_size=int(indeg[hub]), hub_delete_us_list_backed=t_list_del * 1e6, hub_delete_us_set_backed=t_set_del * 1e6)
print("B10", RES["B10_dynamic"])

# ---------------------------------------------------------------- write
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "bench_results.json"
json.dump(RES, open(out, "w"), indent=1, default=float)
print("wrote", out)
