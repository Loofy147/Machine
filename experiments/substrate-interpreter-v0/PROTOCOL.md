# Substrate Interpreter v0 — Protocol

Status: EXECUTED / LOCAL REPLAY / RESEARCH SUBSTRATE

Question:
Can the fixed Machine substrate express relation traversal through ordinary object-language state computation, and how does that compare with a direct indexed relation primitive?

Fixed S1 contract:
- generic state read/write;
- equality;
- branching;
- sequence traversal;
- object-language closures and recursive computation;
- no direct relation lookup.

S2 changes only the substrate contract by adding direct indexed relation lookup over a pre-indexed representation.

Controls:
- same relation entries;
- same query keys;
- same correctness criterion;
- target/query revealed only to online execution;
- direct-index construction is charged separately as offline representation work.

Required observations:
- semantic equivalence;
- online transition ticks;
- access ticks;
- offline index construction;
- stored index entries.

Interpretation boundary:
This is a minimal substrate audit, not a proof over all possible Machine implementations or relation representations.
