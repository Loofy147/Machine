"""Adversarial black-box test for the current-space-insufficiency frontier.

Detector inputs are only residual(x), [lo, hi], and search budgets. It does not
receive fixture names, structural labels, or ground truth. Verdicts:
SUFFICIENT_FOUND; INSUFFICIENT_CERTIFIED_AT_RESOLUTION; INCONCLUSIVE_AT_RESOLUTION.
"""
import math


def sufficient_funnel(x0=413.7, width=0.4, levels=40):
    def f(x):
        d = abs(x - x0)
        return 0.0 if d < width else float(min(levels, math.floor(d / width)))
    return f, 0.0, 1000.0, True


def sufficient_needle(x0=777.2, width=0.05):
    def f(x):
        return 0.0 if abs(x - x0) < width else 1.0
    return f, 0.0, 1000.0, True


def insufficient_easy(x0=250.0, basin=300.0):
    def f(x):
        return 1.0 + min(1.0, abs(x - x0) / basin)
    return f, 0.0, 1000.0, False


def insufficient_dense(period=9.0):
    def f(x):
        return 1.0 + 0.5 * (1.0 + math.sin(2.0 * math.pi * x / period))
    return f, 0.0, 1000.0, False


def pathological_multiscale():
    # Infimum approaches zero through ever narrower positive basins; zero is
    # never attained.
    def f(x):
        if x <= 0.0:
            return 1.0
        n = max(1, int(round(1.0 / x)))
        c = 1.0 / n
        w = 1.0 / (100.0 * n * n)
        return 1.0 / n if abs(x - c) <= w else 1.0
    return f, 0.0, 1.0, False


def uniform_search(f, lo, hi, n):
    xs = [lo + i * (hi - lo) / (n - 1) for i in range(n)]
    vals = [(x, f(x)) for x in xs]
    return min(vals, key=lambda p: (p[1], p[0])), (hi - lo) / (n - 1)


def stratified_zoom(f, lo, hi, delta, levels=3, points=9, top_k=3):
    cells = max(1, math.ceil((hi - lo) / delta))
    cell_w = (hi - lo) / cells
    obs = [(lo + (i + 0.5) * cell_w, f(lo + (i + 0.5) * cell_w))
           for i in range(cells)]
    radius = cell_w
    for _ in range(levels):
        ranked = sorted(obs, key=lambda p: (p[1], p[0]))
        seeds = []
        for x, y in ranked:
            if all(abs(x - s) >= radius / 2 for s in seeds):
                seeds.append(x)
            if len(seeds) == top_k:
                break
        for s in seeds:
            for j in range(points):
                t = -1.0 + 2.0 * j / (points - 1)
                x = min(hi, max(lo, s + t * radius))
                obs.append((x, f(x)))
        radius *= 0.5
    return min(obs, key=lambda p: (p[1], p[0])), cell_w


def stable(a, b, atol=1e-12, rtol=1e-12):
    scale = max(abs(a), abs(b), 1.0)
    return abs(a - b) <= max(atol, rtol * scale)


def detect(f, lo, hi, *, lipschitz=None):
    uniform_ns = (7, 61, 241)
    deltas = (100.0, 20.0, 5.0)
    ub, sb = [], []
    for n, d in zip(uniform_ns, deltas):
        (ux, uy), _ = uniform_search(f, lo, hi, n)
        (sx, sy), sd = stratified_zoom(f, lo, hi, d)
        ub.append((ux, uy)); sb.append((sx, sy))
        if uy <= 0.0:
            return "SUFFICIENT_FOUND", min(d, sd), uy, ux, True, False
        if sy <= 0.0:
            return "SUFFICIENT_FOUND", sd, sy, sx, True, False

    u, s = ub[-1], sb[-1]
    stable_floor = stable(ub[-2][1], ub[-1][1]) and stable(sb[-2][1], sb[-1][1])
    agree = abs(u[1] - s[1]) <= 1e-12 * max(abs(u[1]), abs(s[1]), 1.0)

    if lipschitz is not None:
        lower = s[1] - lipschitz * (5.0 / 2.0)
        if lower > 0.0:
            return "INSUFFICIENT_CERTIFIED_AT_RESOLUTION", 5.0, min(u[1], s[1]), (u[0] if u[1] <= s[1] else s[0]), stable_floor, agree
    return "INCONCLUSIVE_AT_RESOLUTION", 5.0, min(u[1], s[1]), (u[0] if u[1] <= s[1] else s[0]), stable_floor, agree


FIXTURES = {
    "A_sufficient_hard_funnel": sufficient_funnel,
    "A2_sufficient_hard_NO_GRADIENT": sufficient_needle,
    "B_insufficient_easy": insufficient_easy,
    "D_insufficient_dense_near_misses": insufficient_dense,
    "E_pathological_multiscale": pathological_multiscale,
}

CERTIFIED = {
    "B_insufficient_easy": 1.0 / 300.0,
    "D_insufficient_dense_near_misses": math.pi / 9.0,
}

if __name__ == "__main__":
    print("BLIND BENCHMARK")
    for name, maker in FIXTURES.items():
        f, lo, hi, gt = maker()
        v, d, y, x, st, ag = detect(f, lo, hi)
        print(f"{name}: gt={gt} verdict={v} delta={d:g} best={y:g} stable={st} cross={ag}")

    print("\nCERTIFIED MODE")
    for name, L in CERTIFIED.items():
        f, lo, hi, gt = FIXTURES[name]()
        v, d, y, x, st, ag = detect(f, lo, hi, lipschitz=L)
        print(f"{name}: L={L:g} verdict={v} delta={d:g} best={y:g}")
