import numpy as np
from substrate import (
    Fiber,
    as_partition,
    attractor,
    attractor_counter_contract,
    attractor_naive,
    basin,
    basin_naive,
    build_action_fiber,
    build_fiber,
    dtype_for_max,
    gen_system,
    hopcroft,
    moore,
    preds_naive,
    retro_dijkstra,
    validate_csr,
)


def test_dtype_boundaries():
    assert dtype_for_max(255) is np.uint8
    assert dtype_for_max(256) is np.uint16
    assert dtype_for_max(65535) is np.uint16
    assert dtype_for_max(65536) is np.uint32
    assert dtype_for_max(2**32 - 1) is np.uint32
    assert dtype_for_max(2**32) is np.uint64


def test_labeled_csr_exactness_and_contract():
    delta = np.array(
        [
            [1, 2, 2],
            [2, 0, 2],
            [1, 2, 0],
            [2, 1, 2],
        ],
        dtype=np.int64,
    )
    f = build_fiber(delta, dedupe=False)

    assert validate_csr(delta, f)
    assert f.edge_count() == int((delta >= 0).sum())
    assert f.record_count() == f.edge_count()
    assert f.dtype_profile()["source"].startswith("uint")
    assert f.dtype_profile()["action"].startswith("uint")

    for u in range(delta.shape[0]):
        got = list(zip(*[x.tolist() for x in f.predecessors(u)]))
        assert sorted(got) == sorted(preds_naive(delta, u))


def test_deduped_fiber_changes_representation_not_basin_semantics():
    delta = np.array(
        [
            [1, 2, 2],
            [2, 0, 2],
            [1, 2, 0],
            [2, 1, 2],
        ],
        dtype=np.int64,
    )

    labeled = build_fiber(delta, dedupe=False)
    deduped = build_fiber(delta, dedupe=True)

    U = {2}
    expected = basin_naive(delta, U)
    assert np.array_equal(basin(labeled, U), expected)
    assert np.array_equal(basin(deduped, U), expected)

    assert deduped.act is None
    try:
        deduped.edge_count()
    except ValueError:
        pass
    else:
        raise AssertionError("deduped Fiber must not expose raw edge_count")


def test_attractor_labeled_deduped_and_dense_agree():
    # Parallel transitions 0->2 occur twice.
    delta = np.array(
        [
            [2, 2, 1],
            [2, 0, 2],
            [2, 2, 2],
            [1, 2, 0],
        ],
        dtype=np.int64,
    )
    owner = np.array([1, 0, 1, 0], dtype=np.int64)
    targets = {2}

    labeled = build_fiber(delta, dedupe=False)
    deduped = build_fiber(delta, dedupe=True)

    truth = attractor_naive(delta, owner, targets)
    got_labeled = attractor(labeled, delta, owner, targets)
    got_deduped = attractor(deduped, delta, owner, targets)

    assert np.array_equal(got_labeled, truth)
    assert np.array_equal(got_deduped, truth)

    counts_l, mode_l = attractor_counter_contract(labeled, delta)
    counts_d, mode_d = attractor_counter_contract(deduped, delta)

    assert mode_l == "edge-multiplicity"
    assert mode_d == "distinct-successor"
    assert counts_l[0] == 3
    assert counts_d[0] == 2


def test_hopcroft_matches_moore():
    delta = gen_system(24, 4, seed=20260921, hubs=4, p_hub=0.35)
    accept = np.array(
        [(i % 5) in (0, 2) for i in range(delta.shape[0])],
        dtype=bool,
    )

    af = build_action_fiber(delta)
    hop = as_partition(hopcroft(af, delta.shape[0], delta.shape[1], accept))
    moo = as_partition(moore(delta, accept))
    assert hop == moo


def test_retro_dijkstra_matches_forward_reference_on_reversed_costs():
    rng = np.random.default_rng(20260921)
    n, k = 12, 3
    delta = gen_system(n, k, seed=20260922, hubs=3, p_hub=0.4)
    cost = rng.integers(1, 8, size=(n, k), dtype=np.int64)

    fiber = build_fiber(delta, dedupe=False)
    V, relax = retro_dijkstra(fiber, cost, goal={0}, n=n)

    assert len(V) == n
    assert relax == int((delta >= 0).sum())

    # Independent dynamic-programming check over the explicit transition graph.
    inf = 10**12
    rev_dist = [inf] * n
    rev_dist[0] = 0
    changed = True
    while changed:
        changed = False
        for s in range(n):
            for a in range(k):
                u = int(delta[s, a])
                if u >= 0 and rev_dist[u] < inf:
                    nd = rev_dist[u] + int(cost[s, a])
                    if nd < rev_dist[s]:
                        rev_dist[s] = nd
                        changed = True

    assert V == rev_dist
