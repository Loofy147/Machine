"""Self-contained correctness smoke test for the imported bidirectional harness."""
from bidir_v3 import ALL_POLICIES, forward_dijkstra, run_policy


def main():
    adj_f = [[(1, 2.0), (2, 8.0)], [(2, 3.0)], []]
    adj_b = [[], [], []]
    for source, edges in enumerate(adj_f):
        for target, weight in edges:
            adj_b[target].append((source, weight))

    forward = forward_dijkstra(adj_f, 0, 2)
    assert forward["cost"] == 5.0, forward
    for policy in ALL_POLICIES:
        result = run_policy(adj_f, adj_b, 0, 2, forward["cost"], policy)
        assert result["cost"] == 5.0, (policy, result)
    print(f"smoke test passed: {len(ALL_POLICIES)} policies returned cost 5.0")


if __name__ == "__main__":
    main()
