# General-Graph Predecessor Contract: Adversarial Validation v0.1

**Status:** FINITE CONTRACT VALIDATION / COST UNRESOLVED  
**Scope:** Directed multigraph semantics and the boundary between a query algorithm and a supplied predecessor-fiber provider.

## Motivation

The algebraic predecessor routine in the Pareto experiment is specific to the declared A/B/C graph family. It must not be generalized to arbitrary directed graphs. This follow-up exercises the predecessor-consumer contract on independent graph instances without claiming that an arbitrary graph has a cheap direct-predecessor primitive.

## Fixtures and checks

The deterministic suite includes one handcrafted adversarial multigraph and three seeded generated directed graphs (seeds 11, 29, and 101). It checks every target fiber and every target's backward-reachable state set.

The handcrafted graph includes self-loops, two differently labeled parallel transitions with identical endpoints, a disconnected isolated state, a zero-indegree source, zero-outdegree states, and a merge/cycle structure. Generated fixtures force labeled parallel transitions and a self-loop, then add seeded edges that may include further loops and parallel transitions.

Checks cover exact predecessor edge-identity multiplicity, backward reachability against a separately constructed reference reverse index, termination with cycles and self-loops, invalid target rejection, observable lookup/output counters, and a patched test proving the query function does not invoke the reference index builder after its provider has been supplied.

## Deliberate boundary

DeclaredFiberProvider is a supplied fiber-table adapter. Its fibers are prepared before query execution; the query receives only the provider, not the graph or an index builder. The reference reverse index is permitted during validation. This tests the consumer/provider contract and its edge cases, not an implementation that can derive arbitrary predecessor fibers without preprocessing.

No default scalar price is assigned to a provider lookup. Physical access cost, preprocessing cost for any real implementation, update cost, and storage must be measured or explicitly modeled before comparing implementations. The report records arbitrary_graph_native_fiber_implementation = NOT CLAIMED.

## Reproduction and evidence

Run:

    python -m unittest discover -s experiments/pareto-representation-closure-v0 -p test_general_graph_predecessor.py -v
    python experiments/pareto-representation-closure-v0/run_general_graph_validation.py

The runner writes GENERAL-GRAPH-PREDECESSOR-VALIDATION-V0.json. CI binds this evidence into the aggregate integration result and uploads it as an artifact.

## Claim ledger

- **EXPERIMENTALLY_SUPPORTED:** On these four finite fixtures, the supplied fiber-table contract returns the same labeled predecessor multiset and backward reachability as the reference relation.
- **ESTABLISHED WITHIN THE TESTED CODE PATH:** The backward query uses only its injected provider and does not build the validation reverse index.
- **UNKNOWN / OPEN:** Whether a new arbitrary-graph implementation can provide direct predecessor fibers more cheaply than indexed or scanned representations.
- **NOT ESTABLISHED:** A universal direct-predecessor algorithm, a general computational advantage, or a physical-cost winner.
