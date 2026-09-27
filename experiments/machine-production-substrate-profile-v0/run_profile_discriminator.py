"""Machine production-substrate profile discriminator v0.1.

This is a contract-selection experiment, not a performance shootout.

Profiles:
  A0: opaque forward access; inverse queries require delta scans.
  A1: generic random-access state reads; target-oblivious CSR is ordinary state.
  A2: dedicated fiber_lookup(u) access; same CSR representation.

Decision target:
  Identify the minimum access profile that closes the required inverse-dependent
  Machine workloads without adding semantic knowledge to the access API.

The experiment deliberately separates:
  1. semantic closure,
  2. access-contract strength,
  3. resource envelope.

It does not infer a "canonical" profile from wall-clock speed.
"""

import json
import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Profile:
    name: str
    semantic_specialization: bool
    state_read: bool
    fiber_lookup: bool


PROFILES = {
    "A0_OPAQUE": Profile("A0_OPAQUE", False, False, False),
    "A1_RANDOM_ACCESS": Profile("A1_RANDOM_ACCESS", False, True, False),
    "A2_SPECIALIZED_INDEX": Profile("A2_SPECIALIZED_INDEX", True, False, True),
}


def gen_delta(n, k, seed, partial=0.0, hub_fraction=0.0):
    rng = random.Random(seed)
    hub_count = max(2, min(16, n // 8))
    hubs = rng.sample(range(n), hub_count)
    d = [[-1] * k for _ in range(n)]
    for s in range(n):
        for a in range(k):
            if partial and rng.random() < partial:
                continue
            if hub_fraction and rng.random() < hub_fraction:
                d[s][a] = hubs[rng.randrange(hub_count)]
            else:
                d[s][a] = rng.randrange(n)
    return d


def edges(delta):
    return [
        (s, a, v)
        for s, row in enumerate(delta)
        for a, v in enumerate(row)
        if v >= 0
    ]


def build_csr(delta):
    n = len(delta)
    es = edges(delta)
    offs = [0] * (n + 1)
    for _, _, u in es:
        offs[u + 1] += 1
    for u in range(n):
        offs[u + 1] += offs[u]
    cur = offs[:-1].copy()
    src = [0] * len(es)
    act = [0] * len(es)
    for s, a, u in es:
        i = cur[u]
        src[i] = s
        act[i] = a
        cur[u] += 1
    return offs, src, act


def pred_scan(delta, u):
    n = len(delta)
    k = len(delta[0])
    out = []
    probes = 0
    for s in range(n):
        for a in range(k):
            probes += 1
            if delta[s][a] == u:
                out.append((s, a))
    return out, probes


def pred_a1(offs, src, act, u):
    lo = offs[u]
    hi = offs[u + 1]
    out = [(src[i], act[i]) for i in range(lo, hi)]
    return out, 2 + 2 * (hi - lo)


def pred_a2(offs, src, act, u):
    lo = offs[u]
    hi = offs[u + 1]
    out = [(src[i], act[i]) for i in range(lo, hi)]
    return out, 1 + (hi - lo)


def predecessor(delta, csr, profile, u):
    if profile == "A0_OPAQUE":
        return pred_scan(delta, u)
    if profile == "A1_RANDOM_ACCESS":
        return pred_a1(*csr, u)
    if profile == "A2_SPECIALIZED_INDEX":
        return pred_a2(*csr, u)
    raise ValueError(profile)


def basin(delta, csr, profile, targets):
    seen = set(targets)
    q = list(targets)
    access_cost = 0
    expansions = 0
    while q:
        u = q.pop()
        expansions += 1
        pred, c = predecessor(delta, csr, profile, u)
        access_cost += c
        for s, _a in pred:
            if s not in seen:
                seen.add(s)
                q.append(s)
    return seen, access_cost, expansions


def retro_value(delta, csr, profile, goal):
    # Unit-cost retrograde shortest path. Returning values provides a second
    # inverse-dependent semantic workload without changing the representation.
    n = len(delta)
    inf = n + 1
    dist = [inf] * n
    dist[goal] = 0
    changed = True
    rounds = 0
    access_cost = 0
    while changed:
        changed = False
        rounds += 1
        for u in range(n):
            if dist[u] == inf:
                continue
            pred, c = predecessor(delta, csr, profile, u)
            access_cost += c
            for s, _a in pred:
                if dist[s] > dist[u] + 1:
                    dist[s] = dist[u] + 1
                    changed = True
    return dist, access_cost, rounds


def bidirectional_reachability(delta, csr, profile, source, target):
    # We only need semantic agreement here. A compact state-space version
    # expands forward from source and backward through predecessor fibers.
    n = len(delta)
    seen_f = {source}
    seen_b = {target}
    fq = [source]
    bq = [target]
    access_cost = 0
    while fq and bq and not (seen_f & seen_b):
        if len(fq) <= len(bq):
            u = fq.pop()
            for v in delta[u]:
                if v >= 0 and v not in seen_f:
                    seen_f.add(v)
                    fq.append(v)
        else:
            u = bq.pop()
            pred, c = predecessor(delta, csr, profile, u)
            access_cost += c
            for s, _a in pred:
                if s not in seen_b:
                    seen_b.add(s)
                    bq.append(s)
    return bool(seen_f & seen_b), access_cost


def workload_once(delta, seed):
    n = len(delta)
    k = len(delta[0])
    csr = build_csr(delta)
    rng = random.Random(seed)
    queries = [(rng.randrange(n), rng.randrange(n)) for _ in range(12)]

    semantic = {}
    costs = {}

    # P = predecessor enumeration
    P_ref = {}
    for u in range(min(n, 16)):
        P_ref[u] = pred_scan(delta, u)[0]

    # B = backward basin
    B_ref = {}
    for u in range(2):
        B_ref[u] = basin(delta, csr, "A0_OPAQUE", [u])[0]

    # R = retrograde value
    R_ref = {}
    for goal in range(min(n, 2)):
        R_ref[goal] = retro_value(delta, csr, "A0_OPAQUE", goal)[0]

    # Q = reachability (mixed forward/backward search)
    Q_ref = {}
    for s, t in queries:
        Q_ref[(s, t)] = bidirectional_reachability(
            delta, csr, "A0_OPAQUE", s, t
        )[0]

    for pname in PROFILES:
        p_sem = True
        pcost = {"predecessor": 0, "basin": 0, "retro": 0, "bidir": 0}
        for u, ref in P_ref.items():
            got, c = predecessor(delta, csr, pname, u)
            p_sem &= sorted(got) == sorted(ref)
            pcost["predecessor"] += c

        for u, ref in B_ref.items():
            got, c, _ = basin(delta, csr, pname, [u])
            p_sem &= got == ref
            pcost["basin"] += c

        for goal, ref in R_ref.items():
            got, c, _ = retro_value(delta, csr, pname, goal)
            p_sem &= got == ref
            pcost["retro"] += c

        for s, t in queries:
            got, c = bidirectional_reachability(delta, csr, pname, s, t)
            p_sem &= got == Q_ref[(s, t)]
            pcost["bidir"] += c

        semantic[pname] = p_sem
        costs[pname] = pcost

    return semantic, costs


def run():
    configs = [
        (31, 3, 0.0, 0.0),
        (31, 5, 0.0, 0.4),
        (127, 4, 0.15, 0.0),
        (127, 6, 0.70, 0.05),
        (503, 4, 0.20, 0.0),
        (503, 6, 0.75, 0.10),
    ]

    semantic_failures = {p: 0 for p in PROFILES}
    totals = {p: {"predecessor": 0, "basin": 0, "retro": 0, "bidir": 0}
              for p in PROFILES}
    cases = 0

    for family, (n, k, hub, partial) in enumerate(configs):
        for rep in range(10):
            seed = 20260927 + family * 1000 + rep
            delta = gen_delta(n, k, seed, partial=partial, hub_fraction=hub)
            semantic, costs = workload_once(delta, seed + 99)
            cases += 1
            for p in PROFILES:
                semantic_failures[p] += int(not semantic[p])
                for w, v in costs[p].items():
                    totals[p][w] += v

    # Capability surface is a partial order, not a performance score.
    # A1 is the least semantically specialized profile that closes the inverse
    # workloads. A2 exposes stronger semantic knowledge in its access API.
    closure = {
        p: semantic_failures[p] == 0
        for p in PROFILES
    }

    # Ratios are evidence about resource displacement only.
    a0 = sum(totals["A0_OPAQUE"].values())
    a1 = sum(totals["A1_RANDOM_ACCESS"].values())
    a2 = sum(totals["A2_SPECIALIZED_INDEX"].values())

    result = {
        "schema": "machine.production-substrate-profile-discriminator.v0.1",
        "status": "EXECUTED",
        "workload": {
            "families": len(configs),
            "systems": cases,
            "inverse_workloads": [
                "predecessor_enumeration",
                "backward_basin",
                "retrograde_value",
                "mixed_bidirectional_reachability",
            ],
        },
        "semantic": {
            "failures": semantic_failures,
            "closure": closure,
        },
        "resource": {
            "aggregate_access_work": totals,
            "A0_total": a0,
            "A1_total": a1,
            "A2_total": a2,
            "A0_over_A1": a0 / a1,
            "A1_over_A2": a1 / a2,
        },
        "profile_order": {
            "A0": "least access capability; inverse access requires repeated forward probes",
            "A1": "generic state addressing; inverse fibers are representable and derivable",
            "A2": "specialized inverse-fiber access",
        },
        "decision_boundary": {
            "minimal_generic_profile_for_inverse_closure":
                "A1_RANDOM_ACCESS" if closure["A1_RANDOM_ACCESS"] else "UNRESOLVED",
            "A2_is_semantically_stronger_than_A1": True,
            "A2_is_necessary_for_semantic_closure": not closure["A1_RANDOM_ACCESS"],
            "canonical_production_profile":
                "OPEN_PENDING_FROZEN_PRODUCTION_RESOURCE_ENVELOPE",
        },
        "falsification_boundary": [
            "same delta per system across profiles",
            "same target queries",
            "same semantic references",
            "same target-oblivious CSR construction",
            "no wall-clock classification",
            "resource costs are explicit access-work counts",
        ],
    }

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    run()
