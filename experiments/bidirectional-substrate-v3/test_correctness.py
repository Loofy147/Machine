import numpy as np, sys, json
from substrate_lib import *

CHECKS = []


def check(id_, desc, ok, detail=""):
    CHECKS.append(dict(id=id_, desc=desc, passed=bool(ok), detail=detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {id_}: {desc}  {detail}")


def small_system(rng, total=False):
    n = int(rng.integers(1, 41))
    k = int(rng.integers(1, 5))
    d = rng.integers(0, n, size=(n, k))
    if not total and rng.random() < 0.5:
        d[rng.random((n, k)) < 0.25] = -1
    return d


def run_all(trials=400, seed=123):
    rng = np.random.default_rng(seed)

    # ---- C1: structure invariants I1-I4, fiber sum == |E| (not |S||Sigma| when delta is partial)
    bad = 0; par_seen = 0; part_seen = 0
    for _ in range(trials):
        d = small_system(rng)
        offs, src, act = build_csr_np(d)
        if not validate_csr(d, offs, src, act):
            bad += 1
        # counting-sort builder must agree with sort builder
        o2, s2, a2 = build_csr_count(d.ravel().tolist(), *d.shape)
        if not (o2 == offs.tolist() and s2 == src.tolist() and a2 == act.tolist()):
            bad += 1
        E = int((d >= 0).sum())
        part_seen += E < d.size
        tgt = np.repeat(np.arange(len(d)), np.diff(offs))
        par_seen += len(np.unique(src.astype(np.int64) * len(d) + tgt)) < E
    check("C1", "CSR invariants I1-I4 hold; counting-sort == sort-based build", bad == 0,
          f"trials={trials}, partial-delta cases={part_seen}, cases with parallel edges={par_seen}, failures={bad}")

    # ---- C2: fiber(u) == brute-force predecessor scan
    bad = 0
    for _ in range(trials):
        d = small_system(rng); n, k = d.shape
        offs, src, act = build_csr_np(d)
        dl = d.tolist()
        for u in range(n):
            f = sorted(zip(src[offs[u]:offs[u + 1]].tolist(), act[offs[u]:offs[u + 1]].tolist()))
            if f != sorted(preds_naive(dl, n, k, u)):
                bad += 1
    check("C2", "P-05 fiber lookup == brute-force predecessor scan for every state", bad == 0, f"failures={bad}")

    # ---- C3: backward reachability
    bad = 0
    for _ in range(trials):
        d = small_system(rng); n, k = d.shape
        U = rng.choice(n, size=int(rng.integers(1, min(n, 4) + 1)), replace=False).tolist()
        offs, src, act = build_csr_np(d)
        Zn, _ = basin_naive_layered(d, U)
        Zc, cnt, _ = basin_csr(offs.tolist(), src.tolist(), U)
        Zv = basin_csr_np(offs, src, U)
        Zp, cp, _ = basin_naive_pernode(d.tolist(), n, k, U)
        Zq = basin_naive_pernode_np(d, U)
        ref = Zn
        if not (np.array_equal(np.frombuffer(bytes(Zc), np.uint8).astype(bool), ref) and np.array_equal(Zv, ref)
                and np.array_equal(np.frombuffer(bytes(Zp), np.uint8).astype(bool), ref)
                and np.array_equal(Zq, ref) and cnt == int(ref.sum())):
            bad += 1
    check("C3", "Backward basin: fiber BFS (loop & vectorised) == per-node scan == layered fixpoint", bad == 0,
          f"trials={trials}, failures={bad}")

    # ---- C4: retrograde values
    bad = 0; ninf = 0
    for _ in range(trials):
        d = small_system(rng); n, k = d.shape
        cost = rng.integers(1, 10, size=(n, k))
        goal = rng.choice(n, size=int(rng.integers(1, min(n, 3) + 1)), replace=False).tolist()
        offs, src, act = build_csr_np(d)
        Vd, relax, pushes = retro_dijkstra(offs.tolist(), src.tolist(), act.tolist(), cost.tolist(), goal, n)
        Vb, _ = retro_bellman(d, cost, goal)
        if list(Vb) != Vd:
            bad += 1
        ninf += sum(v >= INF for v in Vd) > 0
        if relax > int((d >= 0).sum()):
            bad += 1   # each edge relaxed at most once
    check("C4", "Retrograde Dijkstra over fibers == Bellman value iteration; relaxations <= |E|", bad == 0,
          f"trials={trials}, cases with unreachable states={ninf}, failures={bad}")

    # ---- C5: Hopcroft (per-action index / mixed fiber) == Moore, and == minimal size of base DFA
    bad = 0; merged = 0
    for t in range(trials // 2):
        if t % 2 == 0:
            m = int(rng.integers(1, 9)); k = int(rng.integers(1, 4)); r = int(rng.integers(1, 7))
            d, acc, base, acc0 = redundant_dfa(rng, m, k, r)
            base_min = len(set(moore(*reachable_sub(base, acc0))))
        else:
            n0 = int(rng.integers(1, 41)); k = int(rng.integers(1, 4))
            d = rng.integers(0, n0, size=(n0, k)); acc = rng.random(n0) < 0.5; base_min = None
        d, acc = reachable_sub(d, acc)
        n, k = d.shape
        aoffs, asrc = build_csr_action(d)
        aol, asl = aoffs.tolist(), asrc.tolist()
        offs, src, act = build_csr_np(d)
        ol, sl, al = offs.tolist(), src.tolist(), act.tolist()
        pa = lambda s, a: asl[aol[s * k + a]:aol[s * k + a + 1]]
        pm = lambda s, a: [sl[i] for i in range(ol[s], ol[s + 1]) if al[i] == a]
        P1 = as_partition(hopcroft(n, k, pa, acc)); P2 = as_partition(hopcroft(n, k, pm, acc))
        P0 = as_partition(moore(d, acc))
        merged += len(P0) < n
        if not (P0 == P1 == P2):
            bad += 1
        if base_min is not None and len(P0) != base_min:
            bad += 1
    check("C5", "Hopcroft (both index layouts) == Moore; redundant DFAs shrink to the known minimal size",
          bad == 0, f"trials={trials // 2}, cases where minimisation merged states={merged}, failures={bad}")

    # ---- C6: bidirectional search
    bad = 0; pairs = 0; unreach = 0
    for _ in range(trials // 4):
        d = small_system(rng); n, k = d.shape
        offs, src, act = build_csr_np(d)
        dl = d.tolist(); ol, sl = offs.tolist(), src.tolist()
        outdeg = (d >= 0).sum(axis=1).tolist()
        for _ in range(20):
            s, t = int(rng.integers(0, n)), int(rng.integers(0, n))
            ref, _, _ = bfs_uni(dl, s, t)
            unreach += ref is None
            pairs += 1
            for pol in ("alternate", "size", "work"):
                got, _, _ = bfs_bi(dl, outdeg, ol, sl, s, t, pol)
                if got != ref:
                    bad += 1
    check("C6", "Bidirectional BFS distance == unidirectional BFS (3 balancing policies)", bad == 0,
          f"pairs={pairs}, unreachable pairs={unreach}, failures={bad}")

    # ---- C7: game attractor with predecessor counters
    bad = 0; mism_bug = 0; par = 0
    for _ in range(trials):
        d = small_system(rng, total=True); n, k = d.shape
        owner = rng.integers(0, 2, size=n)
        T = rng.choice(n, size=int(rng.integers(1, min(n, 3) + 1)), replace=False).tolist()
        offs, src, act = build_csr_np(d)
        ref = attractor_naive(d, owner, T)
        lab = attractor_fiber(offs.tolist(), src.tolist(), owner.tolist(), T, [k] * n)
        dof, dsf = dedup_fibers(offs.tolist(), src.tolist())
        ndist = [len(set(row)) for row in d.tolist()]
        par += any(nd < k for nd in ndist)
        unl_ok = attractor_fiber(dof, dsf, owner.tolist(), T, ndist)          # consistent multiplicity
        unl_bad = attractor_fiber(dof, dsf, owner.tolist(), T, [k] * n)      # mismatched multiplicity
        if not (np.array_equal(lab, ref) and np.array_equal(unl_ok, ref)):
            bad += 1
        mism_bug += not np.array_equal(unl_bad, ref)
    check("C7", "Attractor: labeled fibers+outdegree counters == deduped fibers+#distinct-successor counters == fixpoint",
          bad == 0, f"trials={trials}, games with parallel edges={par}, failures={bad}; "
                    f"mismatched-multiplicity variant wrong in {mism_bug} games")
    return CHECKS


if __name__ == "__main__":
    run_all(int(sys.argv[1]) if len(sys.argv) > 1 else 400)
    print(sum(c["passed"] for c in CHECKS), "/", len(CHECKS), "passed")
