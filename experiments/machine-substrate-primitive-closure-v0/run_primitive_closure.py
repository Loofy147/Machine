"""Primitive-closure experiment for the Machine predecessor-fiber claim.

Question:
    Is Rev 2.1 predecessor-fiber access derivable from generic random-access
    state reads, or does it require a new substrate capability?

Three explicit access contracts are separated:

A. OPAQUE_FORWARD:
   The machine exposes only semantic forward probes delta(s,a). Extra inverse
   bytes, if physically present, are not addressable by the machine API.
   Exact predecessor enumeration therefore has the E-probe adversarial lower
   bound.

B. RANDOM_ACCESS_STATE:
   The machine state is a word-addressable representation. The same derived
   CSR arrays (offs, src, act) are part of ordinary state and can be reached
   through the generic state_read(array,index) primitive. No semantic
   fiber-specific primitive is added.

C. FIBER_PRIMITIVE:
   A dedicated fiber(u) operation exists. This is a substrate extension and
   serves as the explicit control for "new access capability".

The experiment uses identical delta, identical inverse representation, and
identical semantics. It does not use wall-clock time for classification.
"""

import json
import random
from pathlib import Path


def gen_system(n, k, seed, hub_fraction=0.0, partial=0.0):
    rng = random.Random(seed)
    hub_count = max(2, min(12, n // 16))
    hubs = rng.sample(range(n), hub_count)
    delta = [[-1] * k for _ in range(n)]
    for s in range(n):
        for a in range(k):
            if partial and rng.random() < partial:
                continue
            if hub_fraction and rng.random() < hub_fraction:
                delta[s][a] = hubs[rng.randrange(len(hubs))]
            else:
                delta[s][a] = rng.randrange(n)
    return delta


def defined_edges(delta):
    n = len(delta)
    k = len(delta[0])
    return [(s, a, delta[s][a]) for s in range(n) for a in range(k) if delta[s][a] >= 0]


def build_csr(delta):
    n = len(delta)
    edges = defined_edges(delta)
    offs = [0] * (n + 1)
    for _, _, u in edges:
        offs[u + 1] += 1
    for u in range(n):
        offs[u + 1] += offs[u]
    cur = offs[:-1].copy()
    src = [0] * len(edges)
    act = [0] * len(edges)
    for s, a, u in edges:
        i = cur[u]
        src[i] = s
        act[i] = a
        cur[u] += 1
    for u in range(n):
        lo, hi = offs[u], offs[u + 1]
        pairs = sorted(zip(src[lo:hi], act[lo:hi]))
        for j, (s, a) in enumerate(pairs, start=lo):
            src[j], act[j] = s, a
    return offs, src, act


def pred_scan(delta, u):
    out = []
    for s, row in enumerate(delta):
        for a, v in enumerate(row):
            if v == u:
                out.append((s, a))
    return out


def pred_random_state(offs, src, act, u):
    lo = offs[u]
    hi = offs[u + 1]
    out = [(src[i], act[i]) for i in range(lo, hi)]
    return out


def pred_fiber_primitive(offs, src, act, u):
    # Semantically identical to the indexed implementation; the difference
    # is that the call itself is a dedicated substrate operation.
    return pred_random_state(offs, src, act, u)


def basin_from_preds(n, targets, pred_fn):
    seen = set(targets)
    frontier = list(targets)
    while frontier:
        u = frontier.pop()
        for s, _a in pred_fn(u):
            if s not in seen:
                seen.add(s)
                frontier.append(s)
    return seen


def exact_state_bytes(n, E):
    # Rev 2.1 layout: int32 offs[n+1] + int32 src[E] + uint8 act[E].
    return 4 * (n + 1) + 4 * E + E


def state_read_cost(degree):
    # Generic random-access state contract:
    # read offs[u], offs[u+1], then one src + one act word per edge.
    return 2 + 2 * degree


def run():
    configs = [
        (31, 3, 0.0, 0.0),
        (31, 4, 0.5, 0.0),
        (127, 3, 0.0, 0.15),
        (127, 5, 0.7, 0.05),
        (503, 4, 0.2, 0.0),
        (503, 6, 0.75, 0.10),
    ]

    rows = []
    basin_rows = []
    builder_failures = 0
    semantic_failures = 0
    basin_failures = 0

    for family_id, (n, k, hub_fraction, partial) in enumerate(configs):
        for rep in range(12):
            seed = 20260927 + family_id * 1000 + rep
            delta = gen_system(n, k, seed, hub_fraction, partial)
            edges = defined_edges(delta)
            E = len(edges)

            offs, src, act = build_csr(delta)
            rebuilt = build_csr(delta)
            if (offs, src, act) != rebuilt:
                builder_failures += 1

            forward_bytes = n * k * 4
            inverse_bytes = exact_state_bytes(n, E)
            offline_work = 2 * E + n  # count + prefix + scatter accounting

            queries = [((seed + q * 17) % n) for q in range(10)]
            for u in queries:
                control = pred_scan(delta, u)
                random_state = pred_random_state(offs, src, act, u)
                fiber = pred_fiber_primitive(offs, src, act, u)
                ok_random = sorted(control) == sorted(random_state)
                ok_fiber = sorted(control) == sorted(fiber)
                semantic_failures += int(not ok_random or not ok_fiber)

                d = len(control)
                rows.append({
                    "family_id": family_id,
                    "rep": rep,
                    "n": n,
                    "k": k,
                    "E": E,
                    "u": u,
                    "degree_in": d,
                    "control_online_probes": n * k,
                    "random_state_online_reads": state_read_cost(d),
                    "fiber_primitive_online_ops": 1 + d,
                    "semantic_equal": ok_random and ok_fiber,
                    "random_state_extra_bytes": inverse_bytes,
                    "offline_build_units": offline_work,
                })

            # One exact fixpoint comparison per system for compositional closure.
            targets = [((seed * 7 + 3) % n), ((seed * 11 + 5) % n)]
            control_basin = basin_from_preds(
                n, targets, lambda u: pred_scan(delta, u)
            )
            random_basin = basin_from_preds(
                n, targets, lambda u: pred_random_state(offs, src, act, u)
            )
            fiber_basin = basin_from_preds(
                n, targets, lambda u: pred_fiber_primitive(offs, src, act, u)
            )
            ok_basin = control_basin == random_basin == fiber_basin
            basin_failures += int(not ok_basin)
            basin_rows.append({
                "family_id": family_id,
                "rep": rep,
                "n": n,
                "k": k,
                "E": E,
                "basin_size": len(control_basin),
                "random_state_equal": control_basin == random_basin,
                "fiber_primitive_equal": control_basin == fiber_basin,
            })

    total_queries = len(rows)
    improved = [
        r for r in rows
        if r["random_state_online_reads"] < r["control_online_probes"]
    ]

    # Feasible-set frontier: for every tested lookup, compare the minimum
    # online budget needed by each contract, while keeping preprocessing and
    # representation costs explicit.
    frontier = []
    for r in rows:
        frontier.append({
            "n": r["n"],
            "k": r["k"],
            "E": r["E"],
            "degree_in": r["degree_in"],
            "control": {
                "B_off": 0,
                "R_extra": 0,
                "B_on": r["control_online_probes"],
                "access": "delta_probe",
            },
            "random_access_state": {
                "B_off": r["offline_build_units"],
                "R_extra": r["random_state_extra_bytes"],
                "B_on": r["random_state_online_reads"],
                "access": "generic_state_read",
            },
            "fiber_primitive": {
                "B_off": r["offline_build_units"],
                "R_extra": r["random_state_extra_bytes"],
                "B_on": r["fiber_primitive_online_ops"],
                "access": "fiber_lookup",
            },
        })

    out = {
        "schema": "machine.substrate-primitive-closure.v0.1",
        "status": "EXECUTED / CI",
        "question": "Is Rev 2.1 fiber access derivable from generic random-access state reads, or does it require a new substrate capability?",
        "contracts": {
            "opaque_forward": {
                "allowed": ["delta_read(s,a)", "finite iteration", "comparison"],
                "inverse_storage_addressable": False,
                "exact_predecessor_lower_bound": "Omega(E) defined-transition probes in the adversarial query model",
            },
            "random_access_state": {
                "allowed": ["generic_state_read(array,index)", "arithmetic", "finite iteration"],
                "inverse_arrays_are_state": True,
                "fiber_semantics_primitive_added": False,
            },
            "fiber_primitive": {
                "allowed": ["fiber_lookup(u)"],
                "inverse_arrays_are_state": True,
                "fiber_semantics_primitive_added": True,
            },
        },
        "workload": {
            "systems": len(configs) * 12,
            "lookups": total_queries,
            "basin_queries": len(basin_rows),
        },
        "verification": {
            "builder_failures": builder_failures,
            "predecessor_semantic_failures": semantic_failures,
            "basin_semantic_failures": basin_failures,
            "all_equal": builder_failures == semantic_failures == basin_failures == 0,
        },
        "aggregate": {
            "queries_with_online_reduction": len(improved),
            "online_reduction_fraction": len(improved) / total_queries,
            "control_total_online_probes": sum(r["control_online_probes"] for r in rows),
            "random_state_total_reads": sum(r["random_state_online_reads"] for r in rows),
            "fiber_primitive_total_ops": sum(r["fiber_primitive_online_ops"] for r in rows),
            "random_state_ratio_control_over_treatment": (
                sum(r["control_online_probes"] for r in rows)
                / sum(r["random_state_online_reads"] for r in rows)
            ),
            "mean_inverse_extra_bytes": sum(r["random_state_extra_bytes"] for r in rows) / total_queries,
            "mean_offline_build_units": sum(r["offline_build_units"] for r in rows) / total_queries,
        },
        "classification": {
            "random_access_state": "DERIVABLE / REPRESENTATION-LEVEL CLOSURE",
            "opaque_forward": "NOT_DERIVABLE_WITHOUT_ACCESS_EXTENSION",
            "fiber_primitive": "EXPLICIT_SUBSTRATE_EXTENSION",
            "absolute_computational_power_claim": "NOT_SUPPORTED",
            "canonical_machine_closure": "OPEN — the current repository tip does not expose a frozen generic state-access primitive contract sufficient to identify which of the above abstract access models is canonical",
        },
        "falsification_boundary": {
            "same_information": True,
            "same_delta": True,
            "target_oblivious_preprocessing": True,
            "offline_work_charged": True,
            "extra_representation_charged": True,
            "semantic_equivalence_required": True,
            "wall_clock_used_for_classification": False,
        },
        "frontier_sample": frontier[:24],
        "sample_rows": rows[:24],
    }

    out_path = Path(__file__).with_name("RESULTS-V0.1.json")
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    run()
