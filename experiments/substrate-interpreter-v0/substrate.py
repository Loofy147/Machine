"""
substrate.py -- unified Machine Substrate
M = (S, Sigma, delta, R, C), spec Rev 2.1.

This file is the unified executable substrate profile built from:
- adaptive per-scale CSR dtype selection;
- labeled and deduplicated predecessor fibers;
- basin / retrograde / Hopcroft / attractor algorithms.

Important: this is an implementation/profile artifact, not by itself the canonical
semantic specification of the Machine substrate.
"""
from __future__ import annotations

import heapq
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Optional, Sequence, Mapping, Any

import numpy as np

INF = 10 ** 12


def dtype_for_max(max_val: int):
    """Return the smallest unsigned NumPy dtype that can represent max_val."""
    if max_val < 0:
        raise ValueError("max_val must be non-negative")
    if max_val <= 0xFF:
        return np.uint8
    if max_val <= 0xFFFF:
        return np.uint16
    if max_val <= 0xFFFFFFFF:
        return np.uint32
    if max_val <= 0xFFFFFFFFFFFFFFFF:
        return np.uint64
    raise OverflowError("value exceeds uint64")


def validate_dtype_capacity(arr: np.ndarray, max_allowed: int) -> bool:
    """Check that an encoded array never exceeds the declared representable range."""
    if max_allowed < 0:
        raise ValueError("max_allowed must be non-negative")
    if arr.size == 0:
        return True
    return int(arr.max()) <= max_allowed


# -----------------------------------------------------------------------------
# generator
def gen_system(n, k, seed, hubs=50, p_hub=0.3, undefined=0.0):
    """Generate a deterministic transition table with optional undefined edges."""
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


# -----------------------------------------------------------------------------
# fibers
@dataclass
class Fiber:
    """Predecessor index over target state.

    deduped=False:
        labeled fiber F(u), one record per valid (source, action) transition.
        act is present and parallel transitions are preserved.

    deduped=True:
        unlabeled predecessor set Pred(u), one record per distinct predecessor.
        act is None.

    All multiplicity-dependent algorithms must inspect deduped rather than
    receiving a separate counter convention from the caller.
    """
    offs: np.ndarray
    src: np.ndarray
    act: Optional[np.ndarray]
    n: int
    deduped: bool

    def predecessors(self, u):
        lo, hi = int(self.offs[u]), int(self.offs[u + 1])
        if self.act is not None:
            return self.src[lo:hi], self.act[lo:hi]
        return self.src[lo:hi]

    def in_degree(self, u) -> int:
        """Backward-fiber cardinality under the current representation."""
        return int(self.offs[u + 1] - self.offs[u])

    def record_count(self) -> int:
        """Number of stored predecessor records, not necessarily raw edges."""
        return int(self.offs[-1])

    def edge_count(self) -> int:
        """Raw transition count. Undefined for a deduplicated fiber."""
        if self.deduped:
            raise ValueError("edge_count is undefined for a deduplicated Fiber")
        return self.record_count()

    def max_in_degree(self) -> int:
        counts = np.diff(self.offs.astype(np.int64))
        return int(counts.max()) if counts.size else 0

    def dtype_profile(self) -> dict:
        return {
            "offset": str(self.offs.dtype),
            "source": str(self.src.dtype),
            "action": None if self.act is None else str(self.act.dtype),
        }

    def memory_bytes(self) -> int:
        return (
            self.offs.nbytes
            + self.src.nbytes
            + (self.act.nbytes if self.act is not None else 0)
        )

    def contract(self) -> dict:
        return {
            "n": self.n,
            "deduped": self.deduped,
            "record_count": self.record_count(),
            "raw_edge_count": None if self.deduped else self.edge_count(),
            "max_fiber_cardinality": self.max_in_degree(),
            "memory_bytes": self.memory_bytes(),
            "dtype_profile": self.dtype_profile(),
            "query_complexity": (
                "Theta(1 + deg^-(u))"
                if not self.deduped
                else "Theta(1 + |Pred(u)|)"
            ),
        }


def build_fiber(delta: np.ndarray, dedupe: bool = False) -> Fiber:
    """CSR build sorted by (target, source, action). Adaptive dtypes."""
    if delta.ndim != 2:
        raise ValueError("delta must be a 2-D array")

    n, k = delta.shape
    flat = delta.ravel()
    idx = np.flatnonzero(flat >= 0)
    E = len(idx)

    dst = flat[idx]
    order = np.argsort(dst, kind="stable")

    src_all = (idx[order] // k).astype(np.int64)
    act_all = (idx[order] % k).astype(np.int64)

    counts = np.bincount(dst, minlength=n).astype(np.int64)
    offs64 = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(counts, out=offs64[1:])

    src_dt = dtype_for_max(max(n - 1, 0))
    act_dt = dtype_for_max(max(k - 1, 0))

    if not dedupe:
        idx_dt = dtype_for_max(E)
        fiber = Fiber(
            offs64.astype(idx_dt),
            src_all.astype(src_dt),
            act_all.astype(act_dt),
            n,
            deduped=False,
        )
        return fiber

    dsrc_parts = []
    doffs64 = np.zeros(n + 1, dtype=np.int64)

    for u in range(n):
        lo, hi = offs64[u], offs64[u + 1]
        uniq = np.unique(src_all[lo:hi])
        dsrc_parts.append(uniq)
        doffs64[u + 1] = doffs64[u] + len(uniq)

    dsrc = (
        np.concatenate(dsrc_parts)
        if dsrc_parts
        else np.empty(0, dtype=np.int64)
    )

    idx_dt = dtype_for_max(len(dsrc))
    return Fiber(
        doffs64.astype(idx_dt),
        dsrc.astype(src_dt),
        None,
        n,
        deduped=True,
    )


@dataclass
class ActionFiber:
    """Per-action predecessor index F_a(u), bucketed by (u, action)."""
    offs: np.ndarray
    src: np.ndarray
    n: int
    k: int

    def predecessors(self, u, a):
        b = u * self.k + a
        lo, hi = int(self.offs[b]), int(self.offs[b + 1])
        return self.src[lo:hi]


def build_action_fiber(delta: np.ndarray) -> ActionFiber:
    if delta.ndim != 2:
        raise ValueError("delta must be a 2-D array")

    n, k = delta.shape
    flat = delta.ravel()
    idx = np.flatnonzero(flat >= 0)
    E = len(idx)

    dst = flat[idx]
    key = dst * k + (idx % k)
    order = np.argsort(key, kind="stable")

    src_dt = dtype_for_max(max(n - 1, 0))
    asrc = (idx[order] // k).astype(src_dt)

    counts = np.bincount(key, minlength=n * k).astype(np.int64)
    aoffs64 = np.zeros(n * k + 1, dtype=np.int64)
    np.cumsum(counts, out=aoffs64[1:])

    idx_dt = dtype_for_max(E)
    return ActionFiber(aoffs64.astype(idx_dt), asrc, n, k)


def validate_csr(delta: np.ndarray, fiber: Fiber) -> bool:
    """Validate labeled-fiber invariants I1-I4."""
    if fiber.deduped:
        raise ValueError("validate_csr requires a non-deduped Fiber")

    n, k = delta.shape
    offs, src, act = fiber.offs, fiber.src, fiber.act

    E = int((delta >= 0).sum())
    offs64 = offs.astype(np.int64)
    src64 = src.astype(np.int64)
    act64 = act.astype(np.int64)

    if not (
        int(offs64[0]) == 0
        and int(offs64[-1]) == E
        and bool(np.all(np.diff(offs64) >= 0))
    ):
        return False

    tgt = np.repeat(np.arange(n), np.diff(offs64))
    if not bool(np.all(delta[src64, act64] == tgt)):
        return False

    keys = src64 * k + act64
    valid_keys = np.flatnonzero(delta.ravel() >= 0)

    if not np.array_equal(np.sort(keys), valid_keys):
        return False

    same = tgt[1:] == tgt[:-1]
    if not bool(np.all(keys[1:][same] > keys[:-1][same])):
        return False

    if not validate_dtype_capacity(offs, E):
        return False
    if not validate_dtype_capacity(src, max(n - 1, 0)):
        return False
    if not validate_dtype_capacity(act, max(k - 1, 0)):
        return False

    return True


# -----------------------------------------------------------------------------
# naive references
def preds_naive(delta, u):
    n, k = delta.shape
    return [
        (s, a)
        for s in range(n)
        for a in range(k)
        if delta[s, a] == u
    ]


def basin_naive(delta, U):
    n, k = delta.shape
    seen = np.zeros(n, dtype=bool)
    dq = deque()

    for u in U:
        if not seen[u]:
            seen[u] = True
            dq.append(u)

    while dq:
        u = dq.popleft()
        for s in range(n):
            for a in range(k):
                if delta[s, a] == u and not seen[s]:
                    seen[s] = True
                    dq.append(s)

    return seen


# -----------------------------------------------------------------------------
# basin
def basin(fiber: Fiber, U) -> np.ndarray:
    """Backward reachability. Multiplicity is irrelevant."""
    n = fiber.n
    seen = np.zeros(n, dtype=bool)
    dq = deque()

    for u in U:
        if not seen[u]:
            seen[u] = True
            dq.append(u)

    while dq:
        u = dq.popleft()
        lo, hi = int(fiber.offs[u]), int(fiber.offs[u + 1])
        for v in fiber.src[lo:hi].tolist():
            if not seen[v]:
                seen[v] = True
                dq.append(v)

    return seen


# -----------------------------------------------------------------------------
# retrograde shortest paths
def retro_dijkstra(fiber: Fiber, cost, goal, n):
    if fiber.deduped:
        raise ValueError("retro_dijkstra needs action labels")

    V = [INF] * n
    heap = [(0, g) for g in goal]

    for g in goal:
        V[g] = 0

    heapq.heapify(heap)
    settled = bytearray(n)
    relax = 0

    while heap:
        d, u = heapq.heappop(heap)
        if settled[u]:
            continue

        settled[u] = 1
        lo, hi = int(fiber.offs[u]), int(fiber.offs[u + 1])

        for v, a in zip(
            fiber.src[lo:hi].tolist(),
            fiber.act[lo:hi].tolist(),
        ):
            relax += 1
            nd = d + cost[v][a]

            if nd < V[v]:
                V[v] = nd
                heapq.heappush(heap, (nd, v))

    return V, relax


# -----------------------------------------------------------------------------
# Hopcroft / Moore
def moore(delta, accept):
    n, k = delta.shape
    cls = [1 if accept[s] else 0 for s in range(n)]
    nc = len(set(cls))

    while True:
        sig = {}
        new = [0] * n

        for s in range(n):
            key = (cls[s],) + tuple(
                cls[int(delta[s, a])] for a in range(k)
            )
            new[s] = sig.setdefault(key, len(sig))

        if len(sig) == nc:
            return new

        cls, nc = new, len(sig)


def hopcroft(af: ActionFiber, n, k, accept):
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
            X.update(af.predecessors(s, a).tolist())

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


# -----------------------------------------------------------------------------
# attractor
def _out_degree_counts(delta):
    return (delta >= 0).sum(axis=1).astype(np.int64)


def _distinct_successor_counts(delta):
    n, _ = delta.shape
    return np.array(
        [
            len(set(int(x) for x in delta[v] if x >= 0))
            for v in range(n)
        ],
        dtype=np.int64,
    )


def attractor_counter_contract(fiber: Fiber, delta: np.ndarray):
    """Return the counter convention implied by the Fiber representation."""
    if delta.ndim != 2 or delta.shape[0] != fiber.n:
        raise ValueError("delta/fiber shape mismatch")

    if fiber.deduped:
        return (
            _distinct_successor_counts(delta),
            "distinct-successor",
        )

    return (
        _out_degree_counts(delta),
        "edge-multiplicity",
    )


def attractor_naive(delta, owner, T):
    """Ground truth: dense forward check. delta must be total."""
    Z = np.zeros(len(owner), dtype=bool)
    Z[list(T)] = True

    while True:
        inZ = Z[delta]
        new = Z | np.where(
            owner == 0,
            inZ.any(axis=1),
            inZ.all(axis=1),
        )

        if new.sum() == Z.sum():
            return Z

        Z = new


def attractor(fiber: Fiber, delta, owner, T) -> np.ndarray:
    """Player-0 attractor to T.

    owner[s] = 0: exists-move
    owner[s] = 1: forall-move

    Counter semantics are derived from fiber.deduped by construction.
    There is no externally supplied (fiber, counter) pair that can disagree.
    """
    n = fiber.n
    cnt, _mode = attractor_counter_contract(fiber, delta)
    cnt = cnt.copy()

    inZ = bytearray(n)
    dq = deque()

    for t in T:
        if not inZ[t]:
            inZ[t] = 1
            dq.append(t)

    while dq:
        u = dq.popleft()
        lo, hi = int(fiber.offs[u]), int(fiber.offs[u + 1])

        for v in fiber.src[lo:hi].tolist():
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
