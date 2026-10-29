"""General directed-multigraph predecessor contract validation.

This is a supplied fiber-table adapter, not a universal direct-predecessor
algorithm. The test contract deliberately separates setup from query execution.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
import random
from typing import Sequence


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    label: str


@dataclass(frozen=True)
class GraphFixture:
    name: str
    state_count: int
    edges: tuple[Edge, ...]
    family: str = "fixed"
    seed: int | None = None

    def __post_init__(self) -> None:
        if self.state_count < 1:
            raise ValueError("state_count must be positive")
        labels = [edge.label for edge in self.edges]
        if len(labels) != len(set(labels)):
            raise ValueError("edge labels must identify distinct transitions")
        for edge in self.edges:
            if not 0 <= edge.source < self.state_count:
                raise ValueError("edge source outside graph")
            if not 0 <= edge.target < self.state_count:
                raise ValueError("edge target outside graph")


def adversarial_fixture() -> GraphFixture:
    # 8 is isolated; 7 has zero indegree; 1 and 8 have zero outdegree.
    edges = (
        Edge(0, 0, "loop-at-0"),
        Edge(0, 1, "parallel-alpha"),
        Edge(0, 1, "parallel-beta"),
        Edge(0, 2, "branch-0-2"),
        Edge(2, 3, "chain-2-3"),
        Edge(3, 2, "back-edge-3-2"),
        Edge(4, 3, "merge-from-4"),
        Edge(5, 3, "merge-from-5"),
        Edge(6, 4, "component-link-6-4"),
        Edge(7, 6, "zero-indegree-source-7"),
        Edge(5, 9, "sink-edge-to-9"),
        Edge(9, 9, "loop-at-9"),
    )
    return GraphFixture("handcrafted-adversarial", 10, edges)


def generated_fixture(seed: int, state_count: int) -> GraphFixture:
    if state_count < 3:
        raise ValueError("generated graph needs at least three states")
    rng = random.Random(seed)
    edges: list[Edge] = [
        Edge(0, 1, f"seed-{seed}-forced-parallel-a"),
        Edge(0, 1, f"seed-{seed}-forced-parallel-b"),
        Edge(state_count - 1, state_count - 1, f"seed-{seed}-forced-loop"),
    ]
    for source in range(state_count):
        degree = rng.randrange(0, min(state_count, 5))
        for edge_index in range(degree):
            target = rng.randrange(state_count)
            edges.append(Edge(
                source, target, f"seed-{seed}-random-{source}-{edge_index}"
            ))
    return GraphFixture(
        f"generated-seed-{seed}-n-{state_count}", state_count, tuple(edges)
    )


def fixtures() -> tuple[GraphFixture, ...]:
    return (
        adversarial_fixture(),
        generated_fixture(11, 7),
        generated_fixture(29, 11),
        generated_fixture(101, 17),
    )


def build_reference_reverse_index(
    graph: GraphFixture,
) -> tuple[tuple[tuple[int, str], ...], ...]:
    buckets: list[list[tuple[int, str]]] = [
        [] for _ in range(graph.state_count)
    ]
    for edge in graph.edges:
        buckets[edge.target].append((edge.source, edge.label))
    return tuple(tuple(bucket) for bucket in buckets)


def build_declared_fiber_rows(
    graph: GraphFixture,
) -> tuple[tuple[tuple[int, str], ...], ...]:
    buckets: dict[int, list[tuple[int, str]]] = {}
    for edge in graph.edges:
        buckets.setdefault(edge.target, []).append((edge.source, edge.label))
    return tuple(
        tuple(sorted(buckets.get(target, ()), key=lambda item: (item[0], item[1])))
        for target in range(graph.state_count)
    )


class DeclaredFiberProvider:
    """Pre-supplied fiber rows plus observable lookup/output counters."""

    def __init__(self, fibers: Sequence[Sequence[tuple[int, str]]]) -> None:
        self._fibers = tuple(tuple(row) for row in fibers)
        self.lookup_calls = 0
        self.returned_entries = 0

    @property
    def state_count(self) -> int:
        return len(self._fibers)

    def predecessors(self, target: int) -> tuple[tuple[int, str], ...]:
        if isinstance(target, bool) or not isinstance(target, int):
            raise ValueError("target must be an integer state")
        if not 0 <= target < self.state_count:
            raise ValueError("target outside provider state range")
        self.lookup_calls += 1
        entries = self._fibers[target]
        self.returned_entries += len(entries)
        return entries


def backward_reachable(provider: DeclaredFiberProvider, target: int) -> set[int]:
    """Query through the injected provider; no graph or index builder is passed."""
    if isinstance(target, bool) or not isinstance(target, int):
        raise ValueError("target must be an integer state")
    if not 0 <= target < provider.state_count:
        raise ValueError("target outside provider state range")
    seen = {target}
    queue = deque([target])
    while queue:
        current = queue.popleft()
        for source, _label in provider.predecessors(current):
            if source not in seen:
                seen.add(source)
                queue.append(source)
    return seen


def backward_reachable_reference(
    reverse_index: Sequence[Sequence[tuple[int, str]]], target: int
) -> set[int]:
    seen = {target}
    queue = deque([target])
    while queue:
        current = queue.popleft()
        for source, _label in reverse_index[current]:
            if source not in seen:
                seen.add(source)
                queue.append(source)
    return seen


def weak_component_count(graph: GraphFixture) -> int:
    neighbors = [set() for _ in range(graph.state_count)]
    for edge in graph.edges:
        neighbors[edge.source].add(edge.target)
        neighbors[edge.target].add(edge.source)
    unseen = set(range(graph.state_count))
    count = 0
    while unseen:
        count += 1
        queue = deque([unseen.pop()])
        while queue:
            current = queue.popleft()
            for neighbor in neighbors[current] & unseen:
                unseen.remove(neighbor)
                queue.append(neighbor)
    return count


def validate_suite() -> dict:
    graph_rows = []
    total_states = total_edges = total_fibers = total_queries = 0
    total_parallel_pairs = total_parallel_excess = total_loops = 0
    total_zero_in = total_zero_out = 0

    for graph in fixtures():
        reference = build_reference_reverse_index(graph)
        provider = DeclaredFiberProvider(build_declared_fiber_rows(graph))
        outgoing = [[] for _ in range(graph.state_count)]
        for edge in graph.edges:
            outgoing[edge.source].append(edge.target)

        mismatches = 0
        for target in range(graph.state_count):
            if Counter(provider.predecessors(target)) != Counter(reference[target]):
                mismatches += 1
            if backward_reachable(provider, target) != backward_reachable_reference(
                reference, target
            ):
                mismatches += 1

        indegree = [len(row) for row in reference]
        outdegree = [len(row) for row in outgoing]
        endpoints = Counter((edge.source, edge.target) for edge in graph.edges)
        parallel_pairs = sum(count > 1 for count in endpoints.values())
        parallel_excess = sum(max(0, count - 1) for count in endpoints.values())
        zero_in = [i for i, count in enumerate(indegree) if count == 0]
        zero_out = [i for i, count in enumerate(outdegree) if count == 0]
        loops = sum(edge.source == edge.target for edge in graph.edges)

        if mismatches:
            raise AssertionError(f"{graph.name}: {mismatches} semantic mismatches")
        if provider.lookup_calls < graph.state_count * 2:
            raise AssertionError(f"{graph.name}: lookup counter undercounts queries")
        if provider.returned_entries < len(graph.edges):
            raise AssertionError(f"{graph.name}: output-entry counter undercounts edges")

        graph_rows.append({
            "name": graph.name,
            "state_count": graph.state_count,
            "edge_count": len(graph.edges),
            "target_fibers_checked": graph.state_count,
            "backward_reachability_queries_checked": graph.state_count,
            "semantic_mismatches": mismatches,
            "parallel_endpoint_pairs": parallel_pairs,
            "parallel_edge_excess": parallel_excess,
            "self_loop_edges": loops,
            "zero_indegree_states": zero_in,
            "zero_outdegree_states": zero_out,
            "weak_component_count": weak_component_count(graph),
            "provider_lookup_calls": provider.lookup_calls,
            "provider_returned_entries": provider.returned_entries,
        })
        total_states += graph.state_count
        total_edges += len(graph.edges)
        total_fibers += graph.state_count
        total_queries += graph.state_count
        total_parallel_pairs += parallel_pairs
        total_parallel_excess += parallel_excess
        total_loops += loops
        total_zero_in += len(zero_in)
        total_zero_out += len(zero_out)

    return {
        "schema": "machine.general-graph-predecessor-validation.v0.1",
        "status": "PASS",
        "fixture_count": len(graph_rows),
        "fixture_names": [row["name"] for row in graph_rows],
        "state_count_total": total_states,
        "edge_count_total": total_edges,
        "target_fibers_checked": total_fibers,
        "backward_reachability_queries_checked": total_queries,
        "total_semantic_mismatches": 0,
        "parallel_endpoint_pairs": total_parallel_pairs,
        "parallel_edge_excess": total_parallel_excess,
        "self_loop_edges": total_loops,
        "zero_indegree_state_count": total_zero_in,
        "zero_outdegree_state_count": total_zero_out,
        "disconnected_fixture_count": sum(
            row["weak_component_count"] > 1 for row in graph_rows
        ),
        "reference_index_builds_for_validation": len(graph_rows),
        "query_path_builds_reverse_index": False,
        "arbitrary_graph_native_fiber_implementation": "NOT CLAIMED",
        "generic_provider_cost": "SYMBOLIC; no physical lookup weight assigned",
        "interpretation_limit": (
            "Finite contract verification of a supplied fiber provider; not proof "
            "of a universal direct-predecessor algorithm or cost advantage."
        ),
        "fixtures": graph_rows,
    }


def generated_sweep_fixtures(seeds_per_family: int = 40) -> tuple[GraphFixture, ...]:
    """Generate deterministic sparse, medium, and dense directed multigraphs.

    Each graph deliberately includes a parallel labeled edge pair, a self-loop,
    a zero-indegree state with an outgoing edge, and a separate isolated state.
    Random edges never enter the zero-indegree state or touch the isolated state.
    The returned fixtures are inputs to a finite differential test, not evidence
    of a universal native predecessor implementation.
    """
    if isinstance(seeds_per_family, bool) or not isinstance(seeds_per_family, int):
        raise ValueError("seeds_per_family must be a positive integer")
    if seeds_per_family < 1 or seeds_per_family > 500:
        raise ValueError("seeds_per_family must be in [1, 500]")

    families = (("sparse", 0.04), ("medium", 0.22), ("dense", 0.62))
    graphs: list[GraphFixture] = []
    for family_index, (family, probability) in enumerate(families):
        for ordinal in range(seeds_per_family):
            seed = 20261029 + family_index * 100_000 + ordinal
            rng = random.Random(seed)
            state_count = 5 + ((seed * 7 + ordinal * 13) % 28)
            prefix = f"sweep-{family}-seed-{seed}-n-{state_count}"
            zero_indegree = state_count - 2
            isolated = state_count - 1
            edges: list[Edge] = [
                Edge(0, 0, f"{prefix}-forced-self-loop"),
                Edge(0, 1, f"{prefix}-forced-parallel-alpha"),
                Edge(0, 1, f"{prefix}-forced-parallel-beta"),
                Edge(zero_indegree, 1, f"{prefix}-forced-zero-indegree-source"),
            ]

            # The random subgraph ranges over [0, state_count-3]. This keeps
            # zero_indegree free of incoming edges and isolated completely unused.
            for source in range(state_count - 2):
                for target in range(state_count - 2):
                    if rng.random() < probability:
                        label = f"{prefix}-edge-{source}-{target}-{len(edges)}"
                        edges.append(Edge(source, target, label))
                        if rng.random() < 0.12:
                            edges.append(Edge(source, target, label + "-parallel"))

            graphs.append(GraphFixture(
                name=prefix,
                state_count=state_count,
                edges=tuple(edges),
                family=family,
                seed=seed,
            ))
    return tuple(graphs)


def validate_generated_sweep(seeds_per_family: int = 40) -> dict:
    """Differentially test every target fiber and reverse-reachability query."""
    graph_rows = []
    total_states = total_edges = total_fibers = total_queries = 0
    total_mismatches = total_parallel_pairs = total_parallel_excess = 0
    total_loops = total_zero_indegree = total_isolated = 0
    family_counts = {name: 0 for name in ("sparse", "medium", "dense")}

    for graph in generated_sweep_fixtures(seeds_per_family):
        reference = build_reference_reverse_index(graph)
        provider = DeclaredFiberProvider(build_declared_fiber_rows(graph))
        mismatches = 0

        for target in range(graph.state_count):
            if Counter(provider.predecessors(target)) != Counter(reference[target]):
                mismatches += 1
            if backward_reachable(provider, target) != backward_reachable_reference(
                reference, target
            ):
                mismatches += 1

        indegree = [len(row) for row in reference]
        outdegree = [0] * graph.state_count
        endpoint_counts = Counter((edge.source, edge.target) for edge in graph.edges)
        for edge in graph.edges:
            outdegree[edge.source] += 1
        parallel_pairs = sum(count > 1 for count in endpoint_counts.values())
        parallel_excess = sum(max(0, count - 1) for count in endpoint_counts.values())
        loops = sum(edge.source == edge.target for edge in graph.edges)
        zero_indegree = [state for state, degree in enumerate(indegree) if degree == 0]
        isolated_states = [
            state for state in range(graph.state_count)
            if indegree[state] == 0 and outdegree[state] == 0
        ]

        if len({edge.label for edge in graph.edges}) != len(graph.edges):
            mismatches += 1
        if not parallel_pairs or not loops or not zero_indegree or not isolated_states:
            mismatches += 1

        if mismatches:
            raise AssertionError(f"{graph.name}: {mismatches} property-sweep mismatches")
        if provider.lookup_calls < graph.state_count * 2:
            raise AssertionError(f"{graph.name}: provider lookup counter undercounts")
        if provider.returned_entries < len(graph.edges):
            raise AssertionError(f"{graph.name}: returned-edge counter undercounts")

        graph_rows.append({
            "name": graph.name,
            "family": graph.family,
            "seed": graph.seed,
            "state_count": graph.state_count,
            "edge_count": len(graph.edges),
            "target_fibers_checked": graph.state_count,
            "backward_reachability_queries_checked": graph.state_count,
            "semantic_mismatches": mismatches,
            "parallel_endpoint_pairs": parallel_pairs,
            "parallel_edge_excess": parallel_excess,
            "self_loop_edges": loops,
            "zero_indegree_states": zero_indegree,
            "isolated_states": isolated_states,
            "weak_component_count": weak_component_count(graph),
            "provider_lookup_calls": provider.lookup_calls,
            "provider_returned_entries": provider.returned_entries,
        })
        family_counts[graph.family] += 1
        total_states += graph.state_count
        total_edges += len(graph.edges)
        total_fibers += graph.state_count
        total_queries += graph.state_count
        total_mismatches += mismatches
        total_parallel_pairs += parallel_pairs
        total_parallel_excess += parallel_excess
        total_loops += loops
        total_zero_indegree += len(zero_indegree)
        total_isolated += len(isolated_states)

    return {
        "schema": "machine.general-graph-predecessor-property-sweep.v0.1",
        "status": "PASS",
        "seed_scheme": "seed=20261029+family_index*100000+ordinal",
        "seeds_per_family": seeds_per_family,
        "family_counts": family_counts,
        "fixture_count": len(graph_rows),
        "state_count_total": total_states,
        "edge_count_total": total_edges,
        "target_fibers_checked": total_fibers,
        "backward_reachability_queries_checked": total_queries,
        "total_semantic_mismatches": total_mismatches,
        "parallel_endpoint_pairs": total_parallel_pairs,
        "parallel_edge_excess": total_parallel_excess,
        "self_loop_edges": total_loops,
        "zero_indegree_state_count": total_zero_indegree,
        "isolated_state_count": total_isolated,
        "disconnected_fixture_count": sum(
            row["weak_component_count"] > 1 for row in graph_rows
        ),
        "reference_index_builds_for_validation": len(graph_rows),
        "query_path_builds_reverse_index": False,
        "arbitrary_graph_native_fiber_implementation": "NOT CLAIMED",
        "physical_access_cost": "SYMBOLIC / CALLER-SUPPLIED; no default scalar lookup cost",
        "interpretation_limit": (
            "Finite deterministic differential validation of a supplied fiber provider. "
            "It is not proof of a universal direct-predecessor algorithm, computational "
            "advantage, or physical-cost winner."
        ),
        "fixtures": graph_rows,
    }
