#!/usr/bin/env python3
"""Fixed-seed stress tests against scikit-learn's bundled datasets.

Covers the user's H1-H5 real-dataset battery plus B1-B3 scarce-supply follow-up.
This exercises the production-shaped planner API, not the original greedy selector.
All feature keys are strings to satisfy the JSON contract schema; needs are presence-only.
Results are finite experimental evidence, not a theorem or production workload claim.
"""
from __future__ import annotations

import json
import platform
import random
import sys
import time
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import numpy as np
import networkx as nx
import sklearn
from sklearn.datasets import load_wine, load_diabetes, load_breast_cancer, load_digits

from context_contract_distribution import ContractContext, build_compatibility_graph, plan_distribution

SEED = 2026
rng = random.Random(SEED)
results = []
case_results = []


def log(*args):
    print(*args, flush=True)


def check(name, ok, detail):
    record = {"name": name, "passed": bool(ok), "details": detail}
    results.append(record)
    log(f"[{'PASS' if ok else 'FAIL'}] {name}\n       {detail}")


def discretize(X):
    return np.stack([
        np.digitize(X[:, j], np.quantile(X[:, j], [1 / 3, 2 / 3]))
        for j in range(X.shape[1])
    ], axis=1)


def _contexts(name, facts_needs, utility=None):
    contexts = []
    for i, (facts, needs) in enumerate(facts_needs):
        v = len(facts) if utility is None else utility[i]
        contexts.append(ContractContext(
            context_id=f"{name}-{i:03d}",
            facts={f"f{k}": int(value) for k, value in facts.items()},
            needs={f"f{k}": None for k in needs},
            utility=int(v),
        ))
    return contexts


def make_pool(X, name, n, k_lo, k_hi, skew=False):
    bins = discretize(X)
    rows = rng.sample(range(len(X)), min(n, len(X)))
    F = X.shape[1]
    order = list(range(F))
    rng.shuffle(order)
    w = {f: 1.0 / (rank + 1) for rank, f in enumerate(order)}
    pool = []
    for r in rows:
        k = rng.randint(k_lo, k_hi)
        if skew:
            ks = sorted(range(F), key=lambda f: -(rng.random() ** (1.0 / w[f])))[:k]
        else:
            ks = rng.sample(range(F), k)
        facts = {f: int(bins[r, f]) for f in ks}
        pool_needs = [f for f in range(F) if f not in facts]
        needs = set(rng.sample(pool_needs, rng.randint(2, 3) if skew else rng.randint(1, 2)))
        pool.append((facts, needs))
    return _contexts(name, pool), bins


def make_bottleneck_pool(X, name, n, k_lo, k_hi, expo=2.5, need_lo=3, need_hi=4):
    bins = discretize(X)
    rows = rng.sample(range(len(X)), min(n, len(X)))
    F = X.shape[1]
    order = list(range(F))
    rng.shuffle(order)
    w = {f: 1.0 / (rank + 1) ** expo for rank, f in enumerate(order)}
    pool = []
    for r in rows:
        ks = sorted(range(F), key=lambda f: -(rng.random() ** (1.0 / w[f])))[:rng.randint(k_lo, k_hi)]
        facts = {f: int(bins[r, f]) for f in ks}
        needs = set(rng.sample([f for f in range(F) if f not in facts], rng.randint(need_lo, need_hi)))
        pool.append((facts, needs))
    return _contexts(name, pool), bins


def make_anchor(bins, k):
    if k == 0:
        return {}
    row = rng.randrange(len(bins))
    return {f"f{j}": int(bins[row, j]) for j in rng.sample(range(bins.shape[1]), k)}


def graph_for(contexts, anchor):
    return build_compatibility_graph(contexts, anchor)


def ref_value(graph, value):
    G = nx.Graph(graph)
    for u, v in G.edges:
        G[u][v]["weight"] = value[u] + value[v]
    return sum(value[x] for edge in nx.max_weight_matching(G, weight="weight") for x in edge)


def naive_value(graph, value):
    used, total = set(), 0
    for u, v in sorted(graph.edges, key=lambda edge: (-(value[edge[0]] + value[edge[1]]), str(edge[0]), str(edge[1]))):
        if u not in used and v not in used:
            used |= {u, v}
            total += value[u] + value[v]
    return total


def independent_valid(context_by_id, anchor, selected):
    selected = sorted(selected)
    graph = nx.Graph()
    graph.add_nodes_from(selected)
    for left, right in combinations(selected, 2):
        a, b = context_by_id[left], context_by_id[right]
        consistent = all(a.facts[k] == b.facts[k] and type(a.facts[k]) is type(b.facts[k])
                         for k in a.facts.keys() & b.facts.keys())
        anchor_ok_a = all(k not in anchor or (type(v) is type(anchor[k]) and v == anchor[k])
                          for k, v in a.facts.items())
        anchor_ok_b = all(k not in anchor or (type(v) is type(anchor[k]) and v == anchor[k])
                          for k, v in b.facts.items())
        serves = any(k in b.facts for k in a.needs) or any(k in a.facts for k in b.needs)
        if consistent and anchor_ok_a and anchor_ok_b and serves:
            graph.add_edge(left, right)
    return len(selected) % 2 == 0 and 2 * len(nx.max_weight_matching(graph, maxcardinality=True)) == len(selected) and all(
        all(k not in anchor or (type(v) is type(anchor[k]) and v == anchor[k]) for k, v in context_by_id[i].facts.items())
        for i in selected
    )


def perfectly_pairable(graph, selected):
    selected = set(selected)
    if len(selected) % 2:
        return False
    return 2 * len(nx.max_weight_matching(graph.subgraph(selected), maxcardinality=True)) == len(selected)


def select(contexts, anchor, utilities=None):
    if utilities is not None:
        contexts = [ContractContext(c.context_id, c.facts, c.needs, utilities[c.context_id]) for c in contexts]
    plan = plan_distribution(contexts, anchor)
    return plan, graph_for(contexts, anchor)


def det_q(M):
    n = len(M)
    M = [[Fraction(x) for x in row] for row in M]
    d = Fraction(1)
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None:
            return Fraction(0)
        if p != c:
            M[c], M[p] = M[p], M[c]
            d = -d
        d *= M[c][c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            for k in range(c, n):
                M[r][k] -= f * M[c][k]
    return d


def det_mod(M, p):
    n = len(M)
    M = [[x % p for x in row] for row in M]
    d = 1
    for c in range(n):
        pivot = next((r for r in range(c, n) if M[r][c]), None)
        if pivot is None:
            return 0
        if pivot != c:
            M[c], M[pivot] = M[pivot], M[c]
            d = -d
        d = d * M[c][c] % p
        inv = pow(M[c][c], -1, p)
        for r in range(c + 1, n):
            f = M[r][c] * inv % p
            for k in range(c, n):
                M[r][k] = (M[r][k] - f * M[c][k]) % p
    return d % p


def run_h1_h5():
    log("== H1: real-data pools, anchor strengths, exact planner vs independent matching reference ==")
    data = [
        ("wine", load_wine(return_X_y=True)[0], 178, 4, 7),
        ("diabetes", load_diabetes(return_X_y=True)[0], 160, 3, 5),
        ("breast_cancer", load_breast_cancer(return_X_y=True)[0], 160, 5, 9),
        ("digits", load_digits(return_X_y=True)[0], 160, 8, 14),
    ]
    pools = {}
    bad = invalid = cases = 0
    uplift = []
    for name, X, n, klo, khi in data:
        for skew in (False, True):
            contexts, bins = make_pool(X, name + ("-skew" if skew else "-uniform"), n, klo, khi, skew)
            if not skew:
                pools[name] = (contexts, bins)
            for label, k in (("no anchor", 0), ("tight anchor (3 facts)", 3)):
                anchor = make_anchor(bins, k)
                started = time.time()
                plan, graph = select(contexts, anchor)
                values = {c.context_id: c.value for c in contexts}
                got = plan.total_utility
                ref = ref_value(graph, values)
                nv = naive_value(graph, values)
                bad += got != ref
                independent_ok = independent_valid({c.context_id: c for c in contexts}, anchor, plan.selected_contexts)
                invalid += not independent_ok
                cases += 1
                elapsed = time.time() - started
                uplift.append((got - nv) / max(nv, 1))
                case_results.append({
                    "suite": "H1", "dataset": name, "feature_sampling": "skewed" if skew else "uniform",
                    "anchor": label, "eligible_contexts": graph.number_of_nodes(), "edges": graph.number_of_edges(),
                    "selected_contexts": len(plan.selected_contexts), "selected_fraction": len(plan.selected_contexts) / max(graph.number_of_nodes(), 1),
                    "utility": got, "independent_matching_reference": ref, "greedy_edge_baseline": nv,
                    "independent_validity": independent_ok, "elapsed_seconds": round(elapsed, 6),
                })
                log(f"   {name:13s} {'skewed' if skew else 'uniform':7s} {label:22s} valid {graph.number_of_nodes():3d}, edges {graph.number_of_edges():5d}, selected {len(plan.selected_contexts):3d}, value {got:4d} (blossom {ref:4d}, greedy-edge {nv:4d}), {elapsed:5.2f}s")
    check("H1 exact utility and independently revalidated selected swarm", bad == 0 and invalid == 0,
          f"{cases} cases, {bad} objective mismatches, {invalid} invalid swarms; mean uplift over naive edge pairing {100*np.mean(uplift):.1f}%")

    log("\n== H2: adversarial anchors on wine ==")
    contexts, bins = pools["wine"]
    failures, notes = 0, []
    full_anchor = {f"f{j}": 99 for j in range(bins.shape[1])}
    row_anchor = {f"f{j}": int(bins[5, j]) for j in range(bins.shape[1])}
    for label, anchor in (("impossible", full_anchor), ("one context full fact set", dict(contexts[0].facts)), ("contradiction-prone full row", row_anchor)):
        plan, graph = select(contexts, anchor)
        values = {c.context_id: c.value for c in contexts}
        ok = len(plan.selected_contexts) % 2 == 0 and plan.total_utility == ref_value(graph, values) and independent_valid({c.context_id: c for c in contexts}, anchor, plan.selected_contexts)
        failures += not ok
        notes.append(f"{label}: valid {graph.number_of_nodes()}, edges {graph.number_of_edges()}, selected {len(plan.selected_contexts)}")
        case_results.append({"suite": "H2", "anchor_case": label, "eligible_contexts": graph.number_of_nodes(), "edges": graph.number_of_edges(), "selected_contexts": len(plan.selected_contexts), "passed": bool(ok)})
    check("H2 exact plan under adversarial anchors", failures == 0, "; ".join(notes))

    log("\n== H3: two-context walk between differently weighted real-data swarms ==")
    contexts, bins = pools["breast_cancer"]
    stuck = nonpair = badlen = nontrivial = checks = walks = 0
    for _ in range(12):
        pool = rng.sample(contexts, 40)
        anchor = make_anchor(bins, 1)
        utilities1 = {c.context_id: c.value for c in pool}
        utilities2 = {c.context_id: rng.randint(1, 20) for c in pool}
        plan1, graph = select(pool, anchor, utilities1)
        plan2, _ = select(pool, anchor, utilities2)
        first, target = set(plan1.selected_contexts), set(plan2.selected_contexts)
        family_cache = {}
        def feasible(S):
            key = frozenset(S)
            if key not in family_cache:
                family_cache[key] = perfectly_pairable(graph, key)
            return family_cache[key]
        current, path, ok = set(first), [], True
        while current != target:
            diff = sorted(current ^ target)
            moved = False
            for x in diff:
                for y in diff:
                    step = {x} if x == y else {x, y}
                    candidate = current ^ step
                    if feasible(candidate):
                        path.append(step)
                        current = candidate
                        moved = True
                        break
                if moved:
                    break
            if not moved:
                ok = False
                break
        walks += 1
        checks += len(family_cache)
        if not ok:
            stuck += 1
            continue
        nontrivial += bool(path)
        nonpair += any(len(s) != 2 for s in path)
        badlen += len(path) != len(first ^ target) // 2
    h3_ok = stuck == 0 and nonpair == 0 and badlen == 0
    check("H3 feasible-family continuity between selected sets", h3_ok,
          f"{walks} walks, {nontrivial} non-trivial; stuck {stuck}, non-pair moves {nonpair}, wrong lengths {badlen}, mean feasibility checks {checks/max(walks,1):.0f}")
    case_results.append({"suite": "H3", "walks": walks, "nontrivial_walks": nontrivial, "stuck": stuck, "non_pair_moves": nonpair, "wrong_lengths": badlen, "mean_feasibility_checks": checks/max(walks,1), "passed": h3_ok})

    log("\n== H4: sequential anchor drift ==")
    contexts, bins = pools["wine"]
    contexts = contexts[:120]
    anchor = make_anchor(bins, 1)
    plan, graph = select(contexts, anchor)
    old_selected = set(plan.selected_contexts)
    infeasible = violations = restored = 0
    churn_repair, churn_full, regrets = [], [], []
    values = {c.context_id: c.value for c in contexts}
    for _ in range(40):
        k = rng.randrange(bins.shape[1])
        anchor2 = dict(anchor)
        anchor2[f"f{k}"] = int(bins[rng.randrange(len(bins)), k])
        new_graph = graph_for(contexts, anchor2)
        broken = old_selected - set(new_graph.nodes)
        restored += len(set(new_graph.nodes) - set(graph.nodes))
        old_pairs = [(p.left, p.right) for p in plan.pairs]
        repaired = {v for pair in old_pairs if not (set(pair) & broken) for v in pair}
        infeasible += not (repaired <= set(new_graph.nodes) and perfectly_pairable(new_graph, repaired))
        violations += len(old_selected ^ repaired) > 2 * len(broken)
        new_plan, _ = select(contexts, anchor2)
        new_selected = set(new_plan.selected_contexts)
        regrets.append(sum(values[x] for x in new_selected) - sum(values[x] for x in repaired))
        churn_repair.append(len(old_selected ^ repaired))
        churn_full.append(len(old_selected ^ new_selected))
        anchor, graph, plan, old_selected = anchor2, new_graph, new_plan, new_selected
    h4_ok = infeasible == 0 and violations == 0
    check("H4 constructive repair feasibility and 2-per-broken-context bound", h4_ok,
          f"40 updates; infeasible {infeasible}; bound violations {violations}; newly eligible after anchor changes {restored}; mean churn repair {np.mean(churn_repair):.1f} vs full reoptimize {np.mean(churn_full):.1f}; mean utility regret {np.mean(regrets):.1f}")
    case_results.append({"suite": "H4", "updates": 40, "infeasible_repairs": infeasible, "bound_violations": violations, "newly_eligible_total": restored, "mean_repair_churn": float(np.mean(churn_repair)), "mean_reoptimization_churn": float(np.mean(churn_full)), "mean_utility_regret": float(np.mean(regrets)), "passed": h4_ok})

    log("\n== H5: fixed +/-1 matrix encoding hazard on real graph submatrices ==")
    contexts, _ = pools["wine"]
    graph = graph_for(contexts, {})
    maximum_matching = sorted(tuple(sorted(edge)) for edge in nx.max_weight_matching(graph, maxcardinality=True))
    p = 1_000_003
    rows, total_fixed, total_random = [], 0, 0
    for size in (4, 8, 12, 16, 20, 24):
        fixed_zero = random_zero = 0
        if len(maximum_matching) < size // 2:
            rows.append(f"size {size}: not enough disjoint matching edges ({len(maximum_matching)})")
            continue
        for _ in range(25):
            picked_pairs = rng.sample(maximum_matching, size // 2)
            selected = sorted(x for edge in picked_pairs for x in edge)
            idx = {node: i for i, node in enumerate(selected)}
            fixed = [[0] * size for _ in range(size)]
            weighted = [[0] * size for _ in range(size)]
            for u, v in combinations(selected, 2):
                if not graph.has_edge(u, v):
                    continue
                cu = next(c for c in contexts if c.context_id == u)
                cv = next(c for c in contexts if c.context_id == v)
                u_served = any(k in cv.facts for k in cu.needs)
                a, b = (u, v) if u_served else (v, u)
                fixed[idx[a]][idx[b]], fixed[idx[b]][idx[a]] = 1, -1
                weight = rng.randrange(1, p)
                weighted[idx[a]][idx[b]], weighted[idx[b]][idx[a]] = weight, (-weight) % p
            fixed_zero += det_q(fixed) == 0
            random_zero += det_mod(weighted, p) == 0
        rows.append(f"size {size}: fixed +/-1 singular {fixed_zero}/25, random modular singular {random_zero}/25")
        total_fixed += fixed_zero
        total_random += random_zero
    h5_ok = total_fixed > 0 and total_random == 0
    check("H5 fixed-sign singularity hazard is observed; random encoding has no observed zero here", h5_ok,
          "; ".join(rows) + f"; random singular total {total_random}")
    case_results.append({"suite": "H5", "matrix_sizes": [4, 8, 12, 16, 20, 24], "fixed_sign_singular": total_fixed, "random_modular_singular": total_random, "trials_per_size": 25, "prime": p, "passed": h5_ok})
    return pools


def run_b1_b3():
    log("\n== B1: scarce-supply regime ==")
    sets = [("breast_cancer", load_breast_cancer(return_X_y=True)[0]),
            ("digits", load_digits(return_X_y=True)[0]),
            ("diabetes", load_diabetes(return_X_y=True)[0])]
    pools = {}
    mismatch = invalid = 0
    fractions = []
    uplifts = []
    cases = 0
    for name, X in sets:
        contexts, bins = make_bottleneck_pool(X, "bottleneck-" + name, 160, 3, 5)
        pools[name] = (contexts, bins)
        for label, k in (("no anchor", 0), ("loose anchor (1 fact)", 1)):
            anchor = make_anchor(bins, k)
            plan, graph = select(contexts, anchor)
            values = {c.context_id: c.value for c in contexts}
            ref, naive = ref_value(graph, values), naive_value(graph, values)
            mismatch += plan.total_utility != ref
            independent_ok = independent_valid({c.context_id: c for c in contexts}, anchor, plan.selected_contexts)
            invalid += not independent_ok
            fractions.append(len(plan.selected_contexts) / max(graph.number_of_nodes(), 1))
            uplifts.append((plan.total_utility - naive) / max(naive, 1))
            cases += 1
            case_results.append({
                "suite": "B1", "dataset": name, "anchor": label, "eligible_contexts": graph.number_of_nodes(),
                "edges": graph.number_of_edges(), "selected_contexts": len(plan.selected_contexts),
                "selected_fraction": fractions[-1], "utility": plan.total_utility,
                "independent_matching_reference": ref, "greedy_edge_baseline": naive,
                "independent_validity": independent_ok,
            })
            log(f"   {name:13s} {label:22s} eligible {graph.number_of_nodes():3d}, edges {graph.number_of_edges():4d}, selected {len(plan.selected_contexts):3d} ({100*fractions[-1]:4.1f}%), value {plan.total_utility:4d} (ref {ref:4d}, naive {naive:4d})")
    b1_ok = mismatch == 0 and invalid == 0 and min(fractions) < .9
    check("B1 exact selection and independent validity under scarce supply", b1_ok,
          f"{cases} cases; objective mismatches {mismatch}, invalid {invalid}; selected fraction {100*min(fractions):.0f}-{100*max(fractions):.0f}%; mean uplift over greedy edge pairing {100*np.mean(uplifts):.1f}%")
    case_results.append({"suite": "B1", "cases": cases, "objective_mismatches": mismatch, "invalid_swarms": invalid, "min_selected_fraction": min(fractions), "max_selected_fraction": max(fractions), "mean_uplift_over_greedy_edge_pairing": float(np.mean(uplifts)), "passed": b1_ok})

    log("\n== B2: non-trivial continuity under different utility weightings ==")
    stuck = odd = wrong_len = nontrivial = steps_sum = max_steps = walks = 0
    for name in ("breast_cancer", "digits", "diabetes"):
        contexts, bins = pools[name]
        for _ in range(6):
            pool = rng.sample(contexts, 60)
            utils1 = {c.context_id: c.value for c in pool}
            utils2 = {c.context_id: rng.randint(1, 30) for c in pool}
            anchor = make_anchor(bins, 1)
            first_plan, graph = select(pool, anchor, utils1)
            target_plan, _ = select(pool, anchor, utils2)
            first, target = set(first_plan.selected_contexts), set(target_plan.selected_contexts)
            cache = {}
            def feasible(S):
                key = frozenset(S)
                if key not in cache:
                    cache[key] = perfectly_pairable(graph, key)
                return cache[key]
            current, path, ok = set(first), [], True
            while current != target:
                diff = sorted(current ^ target)
                moved = False
                for x in diff:
                    for y in diff:
                        step = {x} if x == y else {x, y}
                        candidate = current ^ step
                        if feasible(candidate):
                            path.append(step)
                            current = candidate
                            moved = True
                            break
                    if moved:
                        break
                if not moved:
                    ok = False
                    break
            walks += 1
            if not ok:
                stuck += 1
                continue
            nontrivial += bool(path)
            steps_sum += len(path)
            max_steps = max(max_steps, len(path))
            odd += any(len(step) != 2 for step in path)
            wrong_len += len(path) != len(first ^ target) // 2
    b2_ok = stuck == 0 and odd == 0 and wrong_len == 0 and nontrivial > walks // 2
    check("B2 non-trivial feasible-family continuity", b2_ok,
          f"{walks} walks; non-trivial {nontrivial}; stuck {stuck}, non-pair moves {odd}, wrong lengths {wrong_len}; mean steps {steps_sum/max(nontrivial,1):.1f}; max {max_steps}")
    case_results.append({"suite": "B2", "walks": walks, "nontrivial_walks": nontrivial, "stuck": stuck, "non_pair_moves": odd, "wrong_lengths": wrong_len, "mean_steps_nontrivial": steps_sum/max(nontrivial,1), "max_steps": max_steps, "passed": b2_ok})

    log("\n== B3: sequential anchors in scarce regime ==")
    contexts, bins = pools["digits"]
    contexts = contexts[:120]
    anchor = make_anchor(bins, 1)
    plan, graph = select(contexts, anchor)
    old_selected = set(plan.selected_contexts)
    values = {c.context_id: c.value for c in contexts}
    infeasible = violations = hits = 0
    churn_repair, churn_reopt, regrets = [], [], []
    for _ in range(30):
        key = f"f{rng.randrange(bins.shape[1])}"
        anchor2 = dict(anchor)
        feature = int(key[1:])
        anchor2[key] = int(bins[rng.randrange(len(bins)), feature])
        new_graph = graph_for(contexts, anchor2)
        broken = old_selected - set(new_graph.nodes)
        hits += bool(broken)
        repaired = {v for pair in [(p.left, p.right) for p in plan.pairs] if not (set(pair) & broken) for v in pair}
        infeasible += not (repaired <= set(new_graph.nodes) and perfectly_pairable(new_graph, repaired))
        violations += len(old_selected ^ repaired) > 2 * len(broken)
        new_plan, _ = select(contexts, anchor2)
        new_selected = set(new_plan.selected_contexts)
        regrets.append(sum(values[x] for x in new_selected) - sum(values[x] for x in repaired))
        churn_repair.append(len(old_selected ^ repaired))
        churn_reopt.append(len(old_selected ^ new_selected))
        anchor, graph, plan, old_selected = anchor2, new_graph, new_plan, new_selected
    b3_ok = infeasible == 0 and violations == 0 and hits > 0
    check("B3 bounded, feasible repair under anchor drift", b3_ok,
          f"30 updates ({hits} broke selected contexts); infeasible {infeasible}, bound violations {violations}; mean churn repair {np.mean(churn_repair):.1f} vs reoptimize {np.mean(churn_reopt):.1f}; mean utility regret {np.mean(regrets):.1f}")
    case_results.append({"suite": "B3", "updates": 30, "updates_breaking_selected_contexts": hits, "infeasible_repairs": infeasible, "bound_violations": violations, "mean_repair_churn": float(np.mean(churn_repair)), "mean_reoptimization_churn": float(np.mean(churn_reopt)), "mean_utility_regret": float(np.mean(regrets)), "passed": b3_ok})


def main():
    started = time.time()
    run_h1_h5()
    run_b1_b3()
    checks_passed = sum(record["passed"] for record in results)
    summary = {
        "schema": "context-contract-real-dataset-stress-results.v0.1",
        "seed": SEED,
        "source_script": Path(__file__).name,
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "networkx": nx.__version__,
        "scikit_learn": sklearn.__version__,
        "datasets": {
            "wine": {"rows": 178, "features": 13},
            "diabetes": {"rows": 442, "features": 10},
            "breast_cancer": {"rows": 569, "features": 30},
            "digits": {"rows": 1797, "features": 64},
        },
        "checks_passed": checks_passed,
        "checks_total": len(results),
        "all_passed": checks_passed == len(results),
        "runtime_seconds": round(time.time()-started, 3),
        "check_results": results,
        "case_results": case_results,
        "interpretation_boundary": "Feature distributions are bundled public datasets; generated contexts/anchors are synthetic. This is finite fixed-seed evidence, not production workload validation or a universal proof.",
    }
    log("\nSUMMARY: " + json.dumps({k: v for k, v in summary.items() if k not in ("check_results", "case_results")}, sort_keys=True))
    out = Path(__file__).with_name("REAL-DATASET-STRESS-RESULTS.json")
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not summary["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
