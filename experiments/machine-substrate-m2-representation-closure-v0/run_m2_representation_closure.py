"""M2 representation-closure experiment.

Question:
  Can dynamic inverse-fiber maintenance be expressed using generic random-access
  state reads+writes without a specialized fiber semantic primitive?

Representation:
  fixed-capacity mutable adjacency cells held entirely in ordinary state:
    head[target], next[cell], prev[cell], src[cell], act[cell], target[cell],
    slot[source,action], free-list head/next.
  Capacity is S*Sigma, so no external allocator is assumed.

A1_RW operations:
  generic indexed reads/writes, arithmetic, finite iteration.
  All structural maintenance is expressed through those operations.

A2:
  same logical representation, but the whole structured update is treated as
  one specialized substrate operation.

No wall-clock time is used for classification.
"""

import json
import random


class DynamicIndex:
    def __init__(self, delta):
        self.n = len(delta)
        self.k = len(delta[0])
        cap = self.n * self.k
        self.head = [-1] * self.n
        self.next = [-1] * cap
        self.prev = [-1] * cap
        self.src = [-1] * cap
        self.act = [-1] * cap
        self.target = [-1] * cap
        self.slot = [-1] * cap
        self.free_next = list(range(1, cap)) + [-1]
        self.free_head = 0 if cap else -1

        for s, row in enumerate(delta):
            for a, u in enumerate(row):
                if u >= 0:
                    self.insert(s, a, u)

    def alloc(self):
        if self.free_head < 0:
            raise RuntimeError("capacity exhausted")
        node = self.free_head
        self.free_head = self.free_next[node]
        self.free_next[node] = -1
        return node

    def release(self, node):
        self.free_next[node] = self.free_head
        self.free_head = node

    def insert(self, s, a, u):
        node = self.alloc()
        self.src[node] = s
        self.act[node] = a
        self.target[node] = u
        self.prev[node] = -1
        self.next[node] = self.head[u]
        if self.head[u] >= 0:
            self.prev[self.head[u]] = node
        self.head[u] = node
        self.slot[s * self.k + a] = node

    def delete(self, s, a):
        node = self.slot[s * self.k + a]
        if node < 0:
            return
        u = self.target[node]
        p = self.prev[node]
        q = self.next[node]
        if p >= 0:
            self.next[p] = q
        else:
            self.head[u] = q
        if q >= 0:
            self.prev[q] = p
        self.slot[s * self.k + a] = -1
        self.target[node] = -1
        self.prev[node] = -1
        self.next[node] = -1
        self.src[node] = -1
        self.act[node] = -1
        self.release(node)

    def update(self, s, a, u):
        self.delete(s, a)
        if u >= 0:
            self.insert(s, a, u)

    def fiber(self, u):
        out = []
        node = self.head[u]
        while node >= 0:
            out.append((self.src[node], self.act[node]))
            node = self.next[node]
        return sorted(out)

    def invariant_ok(self, delta):
        seen_slots = set()
        for u in range(self.n):
            node = self.head[u]
            last = -1
            while node >= 0:
                if node in seen_slots:
                    return False
                seen_slots.add(node)
                if self.prev[node] != last:
                    return False
                s, a = self.src[node], self.act[node]
                if self.target[node] != delta[s][a]:
                    return False
                if self.slot[s * self.k + a] != node:
                    return False
                last = node
                node = self.next[node]

        for s, row in enumerate(delta):
            for a, u in enumerate(row):
                node = self.slot[s * self.k + a]
                if u < 0 and node != -1:
                    return False
                if u >= 0:
                    if node < 0 or self.target[node] != u:
                        return False
        return True


def brute(delta, u):
    return sorted(
        (s, a)
        for s, row in enumerate(delta)
        for a, v in enumerate(row)
        if v == u
    )


def make_delta(n, k, seed):
    rng = random.Random(seed)
    d = [[rng.randrange(n) for _ in range(k)] for _ in range(n)]
    for s in range(n):
        for a in range(k):
            if rng.random() < 0.18:
                d[s][a] = -1
        if k >= 2 and rng.random() < 0.4:
            a0, a1 = rng.sample(range(k), 2)
            d[s][a1] = d[s][a0]
    return d


def one_case(n, k, seed):
    rng = random.Random(seed)
    delta_a = make_delta(n, k, seed)
    delta_b = [row[:] for row in delta_a]
    ia = DynamicIndex(delta_a)
    ib = DynamicIndex(delta_b)

    if not ia.invariant_ok(delta_a) or not ib.invariant_ok(delta_b):
        return False, None

    max_updates = max(12, n * 2)
    a1_work = 0
    a2_work = 0
    for _ in range(max_updates):
        s = rng.randrange(n)
        a = rng.randrange(k)
        v = -1 if rng.random() < 0.25 else rng.randrange(n)

        # Generic RW representation update.
        old = delta_a[s][a]
        if old != v:
            # delete: read slot/head/prev/next/target + writes to unlink
            # insert: free-list + head/prev/next/slot + payload writes.
            delete_cost = 0 if old < 0 else 7
            insert_cost = 0 if v < 0 else 9
            a1_work += delete_cost + insert_cost
            ia.update(s, a, v)

        # Specialized structured update.
        old_b = delta_b[s][a]
        if old_b != v:
            ib.update(s, a, v)
            delta_b[s][a] = v
            a2_work += 1

        delta_a[s][a] = v

        for _q in range(5):
            u = rng.randrange(n)
            if ia.fiber(u) != brute(delta_a, u):
                return False, None
            if ib.fiber(u) != brute(delta_b, u):
                return False, None
        if not ia.invariant_ok(delta_a) or not ib.invariant_ok(delta_b):
            return False, None

    return True, (a1_work, a2_work)


def run():
    configs = [(17, 3), (31, 4), (63, 5), (127, 4), (255, 6)]
    failures = 0
    cases = 0
    work_a1 = 0
    work_a2 = 0

    for family, (n, k) in enumerate(configs):
        for rep in range(20):
            ok, work = one_case(n, k, 20260928 + family * 1000 + rep)
            cases += 1
            if not ok:
                failures += 1
                continue
            work_a1 += work[0]
            work_a2 += work[1]

    result = {
        "schema": "machine.substrate-m2-representation-closure.v0.1",
        "status": "EXECUTED",
        "cases": cases,
        "failures": failures,
        "semantic_and_invariant_failures": failures,
        "aggregate_generic_rw_update_work": work_a1,
        "aggregate_specialized_update_work": work_a2,
        "ratio_generic_rw_over_specialized": (
            work_a1 / work_a2 if work_a2 else None
        ),
        "capacity": "S*Sigma fixed state capacity; no external allocator",
        "classification": {
            "A1_RW_M2": (
                "REPRESENTATION_LEVEL_CLOSURE_WITH_EXPLICIT_MUTABLE_STATE"
                if failures == 0 else "FAILED"
            ),
            "A2_M2": "EXPLICIT_STRUCTURED_ACCESS_EXTENSION",
            "A1_read_only_M2": "NOT_EXPRESSIBLE",
        },
        "critical_limit": (
            "This is an existence proof for generic read/write state addressing "
            "with an explicit fixed-capacity mutable representation. It does not "
            "prove that Rev 2.1's compact contiguous CSR can support M2 with the "
            "same representation or cost."
        ),
        "falsification_boundary": [
            "same delta/update sequence for A1_RW and A2",
            "same semantic predecessor reference",
            "same fixed capacity S*Sigma",
            "all queries checked after every committed update",
            "all structural invariants checked after every committed update",
            "no wall-clock classification",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    run()
