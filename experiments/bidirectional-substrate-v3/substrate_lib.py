"""
substrate_lib.py -- reference implementation of the Machine Substrate contract (spec Rev 2).

State ids are dense integers 0..|S|-1. delta is an (|S|, |Sigma|) int64 array; -1 = undefined (partial delta).
Fiber (labeled)    F(s)  = [(s', a) : delta(s', a) = s]        -> CSR arrays (offs, src, act)
Fiber (per-action) F_a(s) = [s' : delta(s', a) = s]            -> CSR arrays (aoffs, asrc), bucket = s*|Sigma| + a
"""
import heapq
from collections import deque, defaultdict
import numpy as np

INF = 10 ** 12


# ----------------------------------------------------------------------------- generators
def gen_system(n, k, seed, hubs=50, p_hub=0.3, undefined=0.0):
    """Random non-bijective system. With prob p_hub an edge is redirected to one of `hubs`
    attractor states drawn with Zipf(1) weights (dense hubs + convergence)."""
    rng = np.random.default_rng(seed)
    d = rng.integers(0, n, size=(n, k), dtype=np.int64)
    if hubs and n > hubs:
        h = rng.choice(n, size=hubs, replace=False)
        w = 1.0 / np.arange(1, hubs + 1)
        w /= w.sum()
        m = rng.random((n, k)) < p_hub
        d[m] = rng.choice(h, size=int(m.sum()), p=w)
    if undefined:
        d[rng.random((n, k)) < undefined] = -1
    return d


# ----------------------------------------------------------------------------- builders (P-04)
def build_csr_np(delta):
    """Sort-based build (numpy). Fibers come out sorted by (s, a)."""
    n, k = delta.shape
    flat = delta.ravel()
    idx = np.flatnonzero(flat >= 0)
    dst = flat[idx]
    order = np.argsort(dst, kind="stable")
    src = (idx[order] // k).astype(np.int32)
    act = (idx[order] % k).astype(np.uint8)
    offs = np.zeros(n + 1, dtype=np.int32)
    np.cumsum(np.bincount(dst, minlength=n), out=offs[1:])
    return offs, src, act


def build_csr_count(flat, n, k):
    """Counting-sort build in pure Python: Theta(|S| + |E|) time, no comparison sort.
    flat: list of length n*k (row-major delta)."""
    cnt = [0] * (n + 1)
    for t in flat:
        if t >= 0:
            cnt[t + 1] += 1
    for i in range(n):
        cnt[i + 1] += cnt[i]
    offs = cnt
    E = offs[n]
    src = [0] * E
    act = [0] * E
    pos = offs[:n]
    i = 0
    for s in range(n):
        for a in range(k):
            t = flat[i]
            i += 1
            if t >= 0:
                p = pos[t]
                src[p] = s
                act[p] = a
                pos[t] = p + 1
    return offs, src, act


def build_csr_action(delta):
    """Action-partitioned inverse index: bucket (s, a) holds {s' : delta(s', a) = s}."""
    n, k = delta.shape
    flat = delta.ravel()
    idx = np.flatnonzero(flat >= 0)
    dst = flat[idx]
    key = dst * k + (idx % k)
    order = np.argsort(key, kind="stable")
    asrc = (idx[order] // k).astype(np.int32)
    aoffs = np.zeros(n * k + 1, dtype=np.int32)
    np.cumsum(np.bincount(key, minlength=n * k), out=aoffs[1:])
    return aoffs, asrc


def validate_csr(delta, offs, src, act):
    """Invariants I1-I4 of the spec."""
    n, k = delta.shape
    E = int((delta >= 0).sum())
    ok = offs[0] == 0 and int(offs[-1]) == E and bool(np.all(np.diff(offs) >= 0))          # I1
    tgt = np.repeat(np.arange(n), np.diff(offs))
    ok = ok and bool(np.all(delta[src, act] == tgt))                                        # I2 soundness
    keys = src.astype(np.int64) * k + act
    ok = ok and bool(np.array_equal(np.sort(keys), np.flatnonzero(delta.ravel() >= 0)))    # I3 completeness, once each
    same = tgt[1:] == tgt[:-1]
    ok = ok and bool(np.all(keys[1:][same] > keys[:-1][same]))                              # I4 sorted within fiber
    return bool(ok)


# ----------------------------------------------------------------------------- naive references
def preds_naive(delta_l, n, k, u):
    out = []
    for s in range(n):
        row = delta_l[s]
        for a in range(k):
            if row[a] == u:
                out.append((s, a))
    return out


def basin_naive_pernode(delta_l, n, k, U):
    """Per-node full scan (the O(|Z| |S| |Sigma|) baseline). Returns (seen, |Z|, inspections)."""
    seen = bytearray(n)
    dq = deque()
    for u in U:
        if not seen[u]:
            seen[u] = 1
            dq.append(u)
    cnt = len(dq)
    insp = 0
    while dq:
        u = dq.popleft()
        for s in range(n):
            row = delta_l[s]
            for a in range(k):
                insp += 1
                if row[a] == u and not seen[s]:
                    seen[s] = 1
                    dq.append(s)
                    cnt += 1
    return seen, cnt, insp


def basin_naive_pernode_np(delta, U):
    """Vectorised per-node scan (numpy): still O(|E|) per popped node."""
    n, k = delta.shape
    flat = delta.ravel()
    seen = np.zeros(n, dtype=bool)
    dq = deque()
    for u in U:
        if not seen[u]:
            seen[u] = True
            dq.append(u)
    while dq:
        u = dq.popleft()
        pre = np.flatnonzero(flat == u) // k
        new = pre[~seen[pre]]
        new = np.unique(new)
        seen[new] = True
        dq.extend(new.tolist())
    return seen


def basin_naive_layered(delta, U):
    """Layer-synchronous full-edge scan: O(diameter * |E|)."""
    n, k = delta.shape
    valid = delta >= 0
    safe = np.where(valid, delta, 0)
    Z = np.zeros(n, dtype=bool)
    Z[list(U)] = True
    rounds = 0
    while True:
        hit = (Z[safe] & valid).any(axis=1)
        new = Z | hit
        rounds += 1
        if new.sum() == Z.sum():
            return Z, rounds
        Z = new


# ----------------------------------------------------------------------------- substrate algorithms
def basin_csr(offs, src, U):
    """Backward reachability  mu Z.(U u Pre(Z))  via fibers. Returns (seen, |Z|, fiber entries touched)."""
    n = len(offs) - 1
    seen = bytearray(n)
    dq = deque()
    for u in U:
        if not seen[u]:
            seen[u] = 1
            dq.append(u)
    cnt = len(dq)
    insp = 0
    while dq:
        u = dq.popleft()
        lo, hi = offs[u], offs[u + 1]
        insp += hi - lo
        for i in range(lo, hi):
            v = src[i]
            if not seen[v]:
                seen[v] = 1
                dq.append(v)
                cnt += 1
    return seen, cnt, insp


def basin_csr_np(offs, src, U):
    """Vectorised layer expansion on CSR arrays."""
    n = len(offs) - 1
    seen = np.zeros(n, dtype=bool)
    front = np.unique(np.asarray(list(U), dtype=np.int64))
    seen[front] = True
    o = offs.astype(np.int64)
    while front.size:
        lens = o[front + 1] - o[front]
        tot = int(lens.sum())
        if tot == 0:
            break
        starts = np.repeat(o[front] - (np.cumsum(lens) - lens), lens)
        cand = src[starts + np.arange(tot)]
        cand = np.unique(cand[~seen[cand]])
        seen[cand] = True
        front = cand
    return seen


def retro_dijkstra(offs, src, act, cost, goal, n):
    """Retrograde value propagation: settled u pushes c(v,a)+V(u) to (v,a) in F(u).
    cost: list of lists (nonnegative ints). Returns V, relaxations, heap pushes."""
    V = [INF] * n
    heap = []
    for g in goal:
        V[g] = 0
        heap.append((0, g))
    heapq.heapify(heap)
    settled = bytearray(n)
    relax = 0
    pushes = len(heap)
    while heap:
        d, u = heapq.heappop(heap)
        if settled[u]:
            continue
        settled[u] = 1
        for i in range(offs[u], offs[u + 1]):
            v = src[i]
            relax += 1
            nd = d + cost[v][act[i]]
            if nd < V[v]:
                V[v] = nd
                heapq.heappush(heap, (nd, v))
                pushes += 1
    return V, relax, pushes


def retro_bellman(delta, cost, goal):
    n, k = delta.shape
    V = np.full(n, INF, dtype=np.int64)
    V[list(goal)] = 0
    valid = delta >= 0
    safe = np.where(valid, delta, 0)
    sweeps = 0
    while True:
        Q = np.where(valid, cost + V[safe], INF)
        nv = np.minimum(np.minimum(V, Q.min(axis=1)), INF)
        sweeps += 1
        if np.array_equal(nv, V):
            return V, sweeps
        V = nv


def moore(delta, accept):
    """Moore partition refinement (reference), complete DFA."""
    n, k = delta.shape
    cls = [1 if accept[s] else 0 for s in range(n)]
    nc = len(set(cls))
    while True:
        sig = {}
        new = [0] * n
        for s in range(n):
            key = (cls[s],) + tuple(cls[int(delta[s, a])] for a in range(k))
            new[s] = sig.setdefault(key, len(sig))
        if len(sig) == nc:
            return new
        cls, nc = new, len(sig)


def hopcroft(n, k, preds, accept):
    """Hopcroft DFA minimisation. preds(s, a) -> iterable of v with delta(v, a) = s."""
    A = [s for s in range(n) if accept[s]]
    B = [s for s in range(n) if not accept[s]]
    blocks = [set(x) for x in (A, B) if x]
    blk = [0] * n
    for i, b in enumerate(blocks):
        for s in b:
            blk[s] = i
    W = set()
    if len(blocks) == 2:
        small = 0 if len(blocks[0]) <= len(blocks[1]) else 1
        for a in range(k):
            W.add((small, a))
    while W:
        bi, a = W.pop()
        X = set()
        for s in blocks[bi]:
            X.update(preds(s, a))
        touched = defaultdict(list)
        for v in X:
            touched[blk[v]].append(v)
        for yi, inter in touched.items():
            Y = blocks[yi]
            if len(inter) == len(Y):
                continue
            new = set(inter)
            Y.difference_update(new)
            ni = len(blocks)
            blocks.append(new)
            for v in new:
                blk[v] = ni
            for b in range(k):
                if (yi, b) in W:
                    W.add((ni, b))
                else:
                    W.add((yi if len(Y) <= len(new) else ni, b))
    return blk


def as_partition(blk):
    g = defaultdict(list)
    for s, b in enumerate(blk):
        g[b].append(s)
    return frozenset(frozenset(x) for x in g.values())


def redundant_dfa(rng, m, k, r):
    base = rng.integers(0, m, size=(m, k))
    acc0 = rng.random(m) < 0.5
    d = np.empty((m * r, k), dtype=np.int64)
    for i in range(m):
        for c in range(r):
            for a in range(k):
                d[i * r + c, a] = base[i, a] * r + rng.integers(0, r)
    return d, np.repeat(acc0, r), base, acc0


def reachable_sub(d, acc, start=0):
    order = [start]
    seen = {start: 0}
    for u in order:
        for v in d[u]:
            v = int(v)
            if v not in seen:
                seen[v] = len(order)
                order.append(v)
    nd = np.array([[seen[int(v)] for v in d[s]] for s in order], dtype=np.int64)
    na = np.array([bool(acc[s]) for s in order])
    return nd, na


def bfs_uni(delta_l, s, t):
    if s == t:
        return 0, 1, 0
    dist = {s: 0}
    dq = deque([s])
    exp = insp = 0
    while dq:
        u = dq.popleft()
        exp += 1
        for v in delta_l[u]:
            insp += 1
            if v >= 0 and v not in dist:
                dist[v] = dist[u] + 1
                if v == t:
                    return dist[v], exp, insp
                dq.append(v)
    return None, exp, insp


def bfs_bi(delta_l, outdeg, offs, src, s, t, policy="work"):
    """Layer-synchronous bidirectional BFS with optimal termination.
    policy: 'alternate' | 'size' | 'work' (expand the side whose next layer is cheaper)."""
    if s == t:
        return 0, 1, 0
    df, db = {s: 0}, {t: 0}
    ff, fb = [s], [t]
    wf, wb = outdeg[s], offs[t + 1] - offs[t]
    exp = insp = 0
    turn = 0
    while ff and fb:
        if policy == "alternate":
            fwd = (turn % 2 == 0)
        elif policy == "size":
            fwd = len(ff) <= len(fb)
        else:
            fwd = wf <= wb
        turn += 1
        best = None
        nxt = []
        nw = 0
        if fwd:
            for u in ff:
                exp += 1
                du = df[u]
                for v in delta_l[u]:
                    insp += 1
                    if v >= 0 and v not in df:
                        df[v] = du + 1
                        nxt.append(v)
                        nw += outdeg[v]
                        if v in db:
                            c = df[v] + db[v]
                            if best is None or c < best:
                                best = c
            ff, wf = nxt, nw
        else:
            for u in fb:
                exp += 1
                du = db[u]
                lo, hi = offs[u], offs[u + 1]
                insp += hi - lo
                for i in range(lo, hi):
                    v = src[i]
                    if v not in db:
                        db[v] = du + 1
                        nxt.append(v)
                        nw += offs[v + 1] - offs[v]
                        if v in df:
                            c = df[v] + db[v]
                            if best is None or c < best:
                                best = c
            fb, wb = nxt, nw
        if best is not None:
            return best, exp, insp
    return None, exp, insp


def attractor_naive(delta, owner, T):
    """Player-0 attractor to T in a turn-based game (total delta). owner[s]=0: exists-move, 1: forall-move."""
    Z = np.zeros(len(owner), dtype=bool)
    Z[list(T)] = True
    while True:
        inZ = Z[delta]
        new = Z | np.where(owner == 0, inZ.any(axis=1), inZ.all(axis=1))
        if new.sum() == Z.sum():
            return Z
        Z = new


def attractor_fiber(offs, src, owner, T, cnt0):
    """Attractor with predecessor counters. cnt0[v] = number of fiber entries v contributes
    (out-degree for labeled fibers; #distinct successors for deduplicated fibers)."""
    n = len(offs) - 1
    cnt = list(cnt0)
    inZ = bytearray(n)
    dq = deque()
    for t in T:
        if not inZ[t]:
            inZ[t] = 1
            dq.append(t)
    while dq:
        u = dq.popleft()
        for i in range(offs[u], offs[u + 1]):
            v = src[i]
            if inZ[v]:
                continue
            if owner[v] == 0:
                inZ[v] = 1
                dq.append(v)
            else:
                cnt[v] -= 1
                if cnt[v] == 0:
                    inZ[v] = 1
                    dq.append(v)
    return np.frombuffer(bytes(inZ), dtype=np.uint8).astype(bool)


def dedup_fibers(offs, src):
    """Unlabeled predecessor SETS Pred(s) (parallel edges collapsed)."""
    n = len(offs) - 1
    no = [0]
    ns = []
    for s in range(n):
        u = sorted(set(int(x) for x in src[offs[s]:offs[s + 1]]))
        ns.extend(u)
        no.append(len(ns))
    return no, ns
