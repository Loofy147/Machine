"""Decisive control: emulate predecessor access inside the original successor-only substrate.

Contract:
- B_off = 0
- R = 0
- no persistent target-dependent state
- primary tick = one candidate-edge examination
- original substrate exposes only successor operations A/B/C
- emulated predecessor access must discover predecessors by scanning candidate
  source states and applying those same successor operations online

Compare:
1) forward BFS + visited
2) bidirectional BFS with explicit online predecessor access
3) forward-search-compatible bidirectional emulation: predecessor frontier expansion
   implemented by scanning the entire state domain and testing successor edges.
"""
from collections import deque
import math
import random


OPS = ("A", "B", "C")


def succ(op, v, M):
    if op == "A":
        return (v + 1) % M
    if op == "B":
        return (v + 7) % M
    if op == "C":
        return (v * 2) % M
    raise ValueError(op)


def reverse_neighbors_native(v, M):
    """Explicit predecessor access: this is the changed mechanism."""
    out = [(v - 1) % M, (v - 7) % M]
    if M % 2:
        out.append((v * pow(2, -1, M)) % M)
    elif v % 2 == 0:
        x = v // 2
        out.extend((x, (x + M // 2) % M))
    return out


def forward_bfs(start, target, M, cap):
    if start == target:
        return True, 0
    q = deque([start])
    seen = {start}
    ticks = 0
    while q:
        u = q.popleft()
        for op in OPS:
            v = succ(op, u, M)
            ticks += 1
            if ticks > cap:
                return False, ticks
            if v == target:
                return True, ticks
            if v not in seen:
                seen.add(v)
                q.append(v)
    return False, ticks


def bidi_native(start, target, M, cap):
    if start == target:
        return True, 0
    fq, bq = deque([start]), deque([target])
    fs, bs = {start}, {target}
    ticks = 0

    while fq and bq:
        if len(fq) <= len(bq):
            u = fq.popleft()
            for op in OPS:
                v = succ(op, u, M)
                ticks += 1
                if ticks > cap:
                    return False, ticks
                if v in bs:
                    return True, ticks
                if v not in fs:
                    fs.add(v)
                    fq.append(v)
        else:
            u = bq.popleft()
            for v in reverse_neighbors_native(u, M):
                ticks += 1
                if ticks > cap:
                    return False, ticks
                if v in fs:
                    return True, ticks
                if v not in bs:
                    bs.add(v)
                    bq.append(v)
    return False, ticks


def predecessor_scan(v, M, cap_remaining):
    """Discover predecessors using ONLY the original successor primitive.

    Cost: 1 tick for every tested candidate edge. The caller must charge all
    ticks against B_on. Returns predecessors, ticks, and whether cap survived.
    """
    preds = []
    ticks = 0
    for candidate in range(M):
        for op in OPS:
            w = succ(op, candidate, M)
            ticks += 1
            if ticks > cap_remaining:
                return preds, ticks, False
            if w == v:
                preds.append(candidate)
    return preds, ticks, True


def bidi_emulated_reverse(start, target, M, cap):
    """Same bidirectional organization, but reverse access is emulated using
    only the baseline successor primitive. No reverse index or inverse formula.
    """
    if start == target:
        return True, 0
    fq, bq = deque([start]), deque([target])
    fs, bs = {start}, {target}
    ticks = 0

    while fq and bq:
        if len(fq) <= len(bq):
            u = fq.popleft()
            for op in OPS:
                v = succ(op, u, M)
                ticks += 1
                if ticks > cap:
                    return False, ticks
                if v in bs:
                    return True, ticks
                if v not in fs:
                    fs.add(v)
                    fq.append(v)
        else:
            u = bq.popleft()
            preds, spent, ok = predecessor_scan(v=u, M=M, cap_remaining=cap - ticks)
            ticks += spent
            if not ok:
                return False, ticks
            for v in preds:
                if v in fs:
                    return True, ticks
                if v not in bs:
                    bs.add(v)
                    bq.append(v)
    return False, ticks


def queries(M, n=200, seed=7):
    rng = random.Random(seed)
    return [(s, t) for s, t in
            ((rng.randrange(M), rng.randrange(M)) for _ in range(n))
            if s != t]


def count(solver, qs, M, cap):
    return sum(solver(s, t, M, cap)[0] for s, t in qs)


def paired_gap(base, alt, qs, M, cap):
    return sum(
        (not base(s, t, M, cap)[0]) and alt(s, t, M, cap)[0]
        for s, t in qs
    )


def run():
    caps = (10, 20, 40, 80, 160, 320, 640)
    for M in (30, 300, 3000):
        qs = queries(M)
        print(f"M={M} n={len(qs)}")
        for cap in caps:
            f = count(forward_bfs, qs, M, cap)
            n = count(bidi_native, qs, M, cap)
            e = count(bidi_emulated_reverse, qs, M, cap)
            ngap = paired_gap(forward_bfs, bidi_native, qs, M, cap)
            egap = paired_gap(forward_bfs, bidi_emulated_reverse, qs, M, cap)
            print(
                f"  B_on={cap:<4} "
                f"forward={f:<4} native_bidi={n:<4} emulated_bidi={e:<4} "
                f"native_gap={ngap:<4} emulated_gap={egap:<4}"
            )
        print()


if __name__ == "__main__":
    run()
