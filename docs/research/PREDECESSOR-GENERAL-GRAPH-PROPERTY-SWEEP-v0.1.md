# General-Graph Predecessor Property Sweep v0.1

**Status:** deterministic finite differential validation  
**Scope:** supplied predecessor-fiber provider contract for directed multigraphs  
**Not claimed:** universal native predecessor implementation, computability separation, physical-cost advantage

## Why this extends the fixed-fixture suite

The original general-graph gate used a handcrafted adversarial graph and three seeded examples. This sweep expands the finite test population and explicitly varies graph density while preserving edge identity and adversarial boundary cases.

For every generated graph, the generator fixes:
- two distinct labeled transitions with identical endpoints;
- at least one self-loop;
- a zero-indegree state that has an outgoing edge;
- a separate isolated state.

It then adds deterministic pseudo-random edges in three families: sparse, medium, and dense. The random generation never adds inbound edges to the designated zero-indegree state or any edge incident to the isolated state. Additional parallel transitions can be generated with unique labels.

## What is checked

For every target in every graph:
1. compare the full labeled predecessor multiset against an independently built reference reverse index;
2. compare backward reachability using the injected provider against a query over the reference index;
3. validate edge-label uniqueness and retained parallel multiplicity;
4. retain observable lookup and returned-entry counts;
5. preserve the fact that the query function does not receive a graph or index builder.

Default run: 40 seeds per family = 120 generated graphs. The exact seed scheme, per-graph sizes, edges, counts, source commit, Python version, and SHA-256 source fingerprints are persisted to GENERAL-GRAPH-PREDECESSOR-PROPERTY-SWEEP-V0.1.json.

## Reproduction

    python -m unittest discover -s experiments/pareto-representation-closure-v0 -p test_general_graph_predecessor.py -v
    python -m unittest discover -s experiments/pareto-representation-closure-v0 -p test_general_graph_property_sweep.py -v
    python experiments/pareto-representation-closure-v0/run_general_graph_property_sweep.py --seeds-per-family 40

CI: .github/workflows/general-graph-predecessor-property-sweep-v0.1.yml.

## Claim disposition

- **EXPERIMENTALLY_SUPPORTED:** for the finite deterministic generated set, the supplied provider returns the same labeled predecessor multiset and backward-reachable state set as the independently constructed reference index.
- **ESTABLISHED WITHIN THE TESTED CODE PATH:** target queries operate through the injected provider without building the validation reverse index during query execution.
- **OPEN:** the cost and implementation of constructing arbitrary-graph predecessor fibers under alternative substrate contracts.
- **NOT ESTABLISHED:** a universal direct-predecessor algorithm, absolute computational advantage, or physical-cost winner.

The test deliberately treats parallel transitions as distinct labeled edges. Collapsing them could preserve reachability while violating the edge-identity contract, so reachability alone is not a sufficient oracle.
