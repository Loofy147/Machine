from __future__ import annotations

import heapq
import random
from dataclasses import dataclass
from typing import Callable, Dict, Hashable, Iterable, List, Optional, Sequence, Set, Tuple

Node = int
Edge = Tuple[Node, int]
Adj = Dict[Node, List[Edge]]
Policy = Callable[[int, int, int, int], str]

INF = float("inf")


def random_weighted_digraph(
    n: int,
    out_deg: int,
    seed: int,
    wmin: int = 1,
    wmax: int = 10,
    multigraph: bool = False,
    ensure_path: bool = True,
    s: int = 0,
    t: Optional[int] = None,
) -> Tuple[Adj, Adj]:
    """Generate a directed positive-weight graph and its reverse.

    multigraph=False gives a simple directed graph (at most one u->v).
    multigraph=True allows repeated directed transitions.
    If ensure_path=True, a positive-weight s->t backbone is inserted.
    """
    if n < 2:
        raise ValueError("n must be >= 2")
    if out_deg < 0:
        raise ValueError("out_deg must be >= 0")
    if not (1 <= wmin <= wmax):
        raise ValueError("invalid weight range")
    if t is None:
        t = n - 1
    if not (0 <= s < n and 0 <= t < n and s != t):
        raise ValueError("invalid s/t")

    rng = random.Random(seed)
    adj: Adj = {i: [] for i in range(n)}
    rev: Adj = {i: [] for i in range(n)}

    if multigraph:
        for u in range(n):
            for _ in range(out_deg):
                v = rng.randrange(n - 1)
                if v >= u:
                    v += 1
                w = rng.randint(wmin, wmax)
                adj[u].append((v, w))
                rev[v].append((u, w))
    else:
        for u in range(n):
            candidates = [v for v in range(n) if v != u]
            targets = rng.sample(candidates, min(out_deg, len(candidates)))
            for v in targets:
                w = rng.randint(wmin, wmax)
                adj[u].append((v, w))
                rev[v].append((u, w))

    if ensure_path:
        # Deterministic backbone makes the generated instance solvable.
        if n == 2:
            backbone = [s, t]
        else:
            middle = list(range(n))
            middle.remove(s)
            middle.remove(t)
            rng.shuffle(middle)
            backbone = [s] + middle[: max(1, min(3, n - 2))] + [t]

        for u, v in zip(backbone, backbone[1:]):
            if multigraph or all(x != v for x, _ in adj[u]):
                w = rng.randint(wmin, wmax)
                adj[u].append((v, w))
                rev[v].append((u, w))

    return adj, rev


def dijkstra(adj: Adj, source: Node) -> Dict[Node, int]:
    dist: Dict[Node, int] = {source: 0}
    pq: List[Tuple[int, Node]] = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist.get(u, INF):
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


def clean_heap(heap: List[Tuple[int, Node]], g: Dict[Node, int], closed: Set[Node]) -> None:
    """Remove stale/closed heap roots."""
    while heap:
        d, u = heap[0]
        if u in closed or d != g.get(u, INF):
            heapq.heappop(heap)
            continue
        break


def top_value(heap: List[Tuple[int, Node]], g: Dict[Node, int], closed: Set[Node]) -> int:
    clean_heap(heap, g, closed)
    return heap[0][0] if heap else INF


def active_frontier_size(g: Dict[Node, int], closed: Set[Node], active: Optional[Node]) -> int:
    """Exact discovered-not-closed frontier cardinality between edge scans.

    During an interruptible active expansion, the active node is removed from
    the frontier; it is therefore added back for a logical active-inclusive
    cardinality only when explicitly needed by a caller.
    """
    return len(g) - len(closed) - (1 if active is not None else 0)


def build_must_expand_graph(
    n: int,
    dist_s: Dict[Node, int],
    dist_t: Dict[Node, int],
    C_star: int,
) -> Dict[Node, Set[Node]]:
    """Blind-search/Dijkstra specialization:
       (u,v) in E_MX iff d(s,u) + d(v,t) < C*.
    """
    if C_star == INF:
        raise ValueError("C* must be finite for a solvable instance")

    right = [(v, d) for v, d in dist_t.items() if d < C_star]
    edges: Dict[Node, Set[Node]] = {}
    for u, du in dist_s.items():
        if du >= C_star:
            continue
        limit = C_star - du
        for v, dv in right:
            if du + dv < C_star:
                edges.setdefault(u, set()).add(v)
    return edges


def max_bipartite_matching(
    left_nodes: Iterable[Node],
    adj_bipartite: Dict[Node, Set[Node]],
) -> Tuple[int, Dict[Node, Node]]:
    """Kuhn maximum-cardinality matching: left -> right."""
    match_right: Dict[Node, Node] = {}

    def try_augment(u: Node, seen: Set[Node]) -> bool:
        for v in adj_bipartite.get(u, ()):
            if v in seen:
                continue
            seen.add(v)
            if v not in match_right or try_augment(match_right[v], seen):
                match_right[v] = u
                return True
        return False

    size = 0
    for u in left_nodes:
        if try_augment(u, set()):
            size += 1
    return size, match_right


def minimum_vertex_cover_from_matching(
    left_nodes: Iterable[Node],
    adj_bipartite: Dict[Node, Set[Node]],
    match_right: Dict[Node, Node],
) -> Tuple[Set[Tuple[str, Node]], Set[Tuple[str, Node]]]:
    """Return the min vertex cover as (side,node) pairs via alternating paths."""
    left = set(left_nodes)
    match_left = {u: v for v, u in match_right.items()}
    matched_right = set(match_right)

    z_left: Set[Node] = set()
    z_right: Set[Node] = set()
    stack = [u for u in left if u not in match_left]

    while stack:
        u = stack.pop()
        if u in z_left:
            continue
        z_left.add(u)
        for v in adj_bipartite.get(u, ()):
            # Traverse unmatched edges L -> R.
            if match_left.get(u) == v:
                continue
            if v in z_right:
                continue
            z_right.add(v)
            # Traverse matched edge R -> L.
            if v in match_right:
                mu = match_right[v]
                if mu not in z_left:
                    stack.append(mu)

    cover_left = {u for u in left if u not in z_left}
    cover_right = z_right
    return ({("F", u) for u in cover_left}, {("B", v) for v in cover_right})


@dataclass
class SearchResult:
    mu: int | float
    N_pi: int
    W_pi: int
    expanded_F: Set[Node]
    expanded_B: Set[Node]
    terminated: bool
    termination_reason: str
    trace: List[dict]


def bidirectional_dijkstra(
    adj: Adj,
    rev: Adj,
    s: Node,
    t: Node,
    policy: Policy,
) -> SearchResult:
    """Completed-expansion bidirectional Dijkstra with exact frontier metadata."""
    gF: Dict[Node, int] = {s: 0}
    gB: Dict[Node, int] = {t: 0}
    openF: List[Tuple[int, Node]] = [(0, s)]
    openB: List[Tuple[int, Node]] = [(0, t)]
    closedF: Set[Node] = set()
    closedB: Set[Node] = set()
    expandedF: Set[Node] = set()
    expandedB: Set[Node] = set()
    mu: int | float = INF
    N = 0
    W = 0
    trace: List[dict] = []

    def frontier_cardinality(g: Dict[Node, int], closed: Set[Node]) -> int:
        return len(g) - len(closed)

    while True:
        topF = top_value(openF, gF, closedF)
        topB = top_value(openB, gB, closedB)
        trace.append({"N_pi": N, "top_F": topF, "top_B": topB, "mu": mu})

        if topF == INF or topB == INF:
            return SearchResult(mu, N, W, expandedF, expandedB, False, "frontier_exhausted", trace)
        if topF + topB >= mu:
            return SearchResult(mu, N, W, expandedF, expandedB, True, "lower_bound", trace)

        side = policy(
            frontier_cardinality(gF, closedF),
            frontier_cardinality(gB, closedB),
            topF,
            topB,
        )
        if side == "F":
            clean_heap(openF, gF, closedF)
            d, u = heapq.heappop(openF)
            if u in closedF or d != gF[u]:
                continue
            closedF.add(u)
            expandedF.add(u)
            N += 1
            if u in gB:
                mu = min(mu, d + gB[u])
            for v, w in adj[u]:
                W += 1
                nd = d + w
                if nd < gF.get(v, INF):
                    gF[v] = nd
                    heapq.heappush(openF, (nd, v))
                    if v in gB:
                        mu = min(mu, nd + gB[v])
        elif side == "B":
            clean_heap(openB, gB, closedB)
            d, u = heapq.heappop(openB)
            if u in closedB or d != gB[u]:
                continue
            closedB.add(u)
            expandedB.add(u)
            N += 1
            if u in gF:
                mu = min(mu, d + gF[u])
            for v, w in rev[u]:
                W += 1
                nd = d + w
                if nd < gB.get(v, INF):
                    gB[v] = nd
                    heapq.heappush(openB, (nd, v))
                    if v in gF:
                        mu = min(mu, nd + gF[v])
        else:
            raise ValueError(f"invalid side: {side!r}")


def interruptible_bidirectional_dijkstra(
    adj: Adj,
    rev: Adj,
    s: Node,
    t: Node,
    policy: Policy,
    active_guard: bool = True,
    check_before_first_edge: bool = True,
) -> SearchResult:
    """Edge-interruptible bidirectional Dijkstra.

    At each edge boundary, one direction may contain an ACTIVE vertex whose
    outgoing/incoming edges have not all been scanned.  active_guard=True uses
        min(topF, g(activeF)) + min(topB, g(activeB)) >= mu.
    active_guard=False intentionally reproduces the naive topF+topB guard.
    """
    gF: Dict[Node, int] = {s: 0}
    gB: Dict[Node, int] = {t: 0}
    openF: List[Tuple[int, Node]] = [(0, s)]
    openB: List[Tuple[int, Node]] = [(0, t)]
    closedF: Set[Node] = set()
    closedB: Set[Node] = set()
    expandedF: Set[Node] = set()
    expandedB: Set[Node] = set()
    mu: int | float = INF
    N = 0
    W = 0
    trace: List[dict] = []
    activeF: Optional[Tuple[Node, int, int]] = None
    activeB: Optional[Tuple[Node, int, int]] = None

    def logical_lb():
        topF = top_value(openF, gF, closedF)
        topB = top_value(openB, gB, closedB)
        active_gF = activeF[1] if activeF is not None else INF
        active_gB = activeB[1] if activeB is not None else INF
        if active_guard:
            LF = min(topF, active_gF)
            LB = min(topB, active_gB)
        else:
            LF, LB = topF, topB
        return LF, LB, topF, topB

    def should_stop() -> bool:
        LF, LB, topF, topB = logical_lb()
        trace.append({
            "N_pi": N,
            "W_pi": W,
            "L_F": LF,
            "L_B": LB,
            "top_F": topF,
            "top_B": topB,
            "active_F": None if activeF is None else activeF[0],
            "active_B": None if activeB is None else activeB[0],
            "mu": mu,
        })
        return LF + LB >= mu

    while True:
        # Continue an existing active expansion one edge at a time.
        if activeF is not None:
            u, gu, i = activeF
            edges = adj[u]
            if i == 0 and check_before_first_edge and should_stop():
                return SearchResult(mu, N, W, expandedF, expandedB, True, "interrupt_guard", trace)
            if i >= len(edges):
                closedF.add(u)
                activeF = None
                continue
            v, w = edges[i]
            activeF = (u, gu, i + 1)
            W += 1
            nd = gu + w
            if nd < gF.get(v, INF):
                gF[v] = nd
                heapq.heappush(openF, (nd, v))
                if v in gB:
                    mu = min(mu, nd + gB[v])
            if should_stop():
                return SearchResult(mu, N, W, expandedF, expandedB, True, "interrupt_guard", trace)
            continue

        if activeB is not None:
            u, gu, i = activeB
            edges = rev[u]
            if i == 0 and check_before_first_edge and should_stop():
                return SearchResult(mu, N, W, expandedF, expandedB, True, "interrupt_guard", trace)
            if i >= len(edges):
                closedB.add(u)
                activeB = None
                continue
            v, w = edges[i]
            activeB = (u, gu, i + 1)
            W += 1
            nd = gu + w
            if nd < gB.get(v, INF):
                gB[v] = nd
                heapq.heappush(openB, (nd, v))
                if v in gF:
                    mu = min(mu, nd + gF[v])
            if should_stop():
                return SearchResult(mu, N, W, expandedF, expandedB, True, "interrupt_guard", trace)
            continue

        # No active expansion: ordinary global stopping decision.
        if should_stop():
            return SearchResult(mu, N, W, expandedF, expandedB, True, "lower_bound", trace)

        topF = top_value(openF, gF, closedF)
        topB = top_value(openB, gB, closedB)
        if topF == INF or topB == INF:
            return SearchResult(mu, N, W, expandedF, expandedB, False, "frontier_exhausted", trace)

        fcard = len(gF) - len(closedF)
        bcard = len(gB) - len(closedB)
        side = policy(fcard, bcard, topF, topB)
        if side == "F":
            clean_heap(openF, gF, closedF)
            gu, u = heapq.heappop(openF)
            if u in closedF or gu != gF[u]:
                continue
            N += 1
            expandedF.add(u)
            activeF = (u, gu, 0)
        elif side == "B":
            clean_heap(openB, gB, closedB)
            gu, u = heapq.heappop(openB)
            if u in closedB or gu != gB[u]:
                continue
            N += 1
            expandedB.add(u)
            activeB = (u, gu, 0)
        else:
            raise ValueError(f"invalid side: {side!r}")


# Policy factories: no hidden mutable default state.
def make_alternate() -> Policy:
    state = {"turn": 0}

    def policy(nF: int, nB: int, topF: int, topB: int) -> str:
        state["turn"] += 1
        return "F" if state["turn"] % 2 else "B"

    return policy


def make_smaller_frontier() -> Policy:
    def policy(nF: int, nB: int, topF: int, topB: int) -> str:
        return "F" if nF <= nB else "B"

    return policy


def make_smaller_top() -> Policy:
    def policy(nF: int, nB: int, topF: int, topB: int) -> str:
        return "F" if topF <= topB else "B"

    return policy


def make_forward_biased() -> Policy:
    state = {"turn": 0}

    def policy(nF: int, nB: int, topF: int, topB: int) -> str:
        state["turn"] += 1
        return "F" if state["turn"] % 4 else "B"

    return policy


def all_policies() -> Dict[str, Callable[[], Policy]]:
    return {
        "alternate": make_alternate,
        "smaller_frontier": make_smaller_frontier,
        "smaller_top": make_smaller_top,
        "forward_biased": make_forward_biased,
    }
