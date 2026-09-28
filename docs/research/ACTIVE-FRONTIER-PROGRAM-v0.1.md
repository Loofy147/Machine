# Active Frontier / Interruptible Bidirectional Search — Program Plan v0.1

Status: ACTIVE RESEARCH PROGRAM
Repository: Loofy147/Machine
Program branch: research/active-frontier-program-v0
Base evidence line: research/bidirectional-grounded-verification-v0
Scope: positive-weight interruptible bidirectional Dijkstra/UCS and the currently implemented post-edge interruption semantics.

## 0. Current evidence baseline

CURRENT durable evidence:
- v0.4 exact n=3: 4,096 graph states × 64 F/B schedules; 233,472 scheduler runs.
- Active-guard failures: 0.
- Naive top-only finite-cost failures: 3,840.
- Canonical post-edge regression:
  0->1 (1), 0->2 (3), 1->2 (1); C*=2; schedule prefix FBFFFF; naive mu=3; active mu=2.
- v0.4 exact n=4: 531,441 graph states; 488,430 solvable; smaller_frontier policy; active failures 0; naive finite failures 4,374.
- Random n=4 all-schedule: 2,000 sampled graphs; 351,232 schedule runs; active failures 0; naive finite failures 4,736.
- Matched simple/multigraph construction: geometry, G_MX, VC and expansions matched; edge-level work increased; stronger Theta(m/n) gap remains OPEN.

Epistemic boundary:
- active guard = EXPERIMENTALLY_SUPPORTED only within the specified Dijkstra/UCS + interruption model.
- naive top-only guard = CONTRADICTED within that same model.
- arbitrary consistent-heuristic correctness = OPEN.
- global graph-theoretic minimality beyond enumerated finite spaces = OPEN.
- theoretical simple-graph instance-optimality separation = OPEN.

## 1. Workstream topology

### A — Proof / invariant
Branch target: research/active-frontier-proof-v0
Objective: derive a formal stopping certificate whose lower bound explicitly includes the actual active/in-progress frontier state.
Acceptance gate:
1. define exact state semantics;
2. define admissible interruption points;
3. prove lower-bound soundness;
4. prove termination implies optimality;
5. identify assumptions and countermodels;
6. attach theorem/proof artifact to a machine-verifiable claim record.

Kill test:
- produce a reachable state satisfying the proposed guard with an s-t path cost below mu.

### B — Adversarial boundary search
Branch target: research/active-frontier-adversarial-v0
Objective: close the minimality/scheduling frontier rather than merely increasing n.
Sequence:
1. exhaustive n=2 under canonical post-edge semantics;
2. exhaustive n=3 already durable, independently re-run for audit;
3. arbitrary admissible scheduling beyond fixed F/B sequences;
4. multigraph / parallel-edge variants;
5. minimize edges, weights, and schedule prefix of the canonical failure.
Acceptance gate:
- every negative claim tied to an explicit finite search space and completion status.

Kill test:
- discover a smaller-state canonical failure or an active-guard failure under the exact stated model.

### C — Heuristic generalization
Branch target: research/active-frontier-mep-v0
Objective: test the active-state principle against front-to-end consistent heuristics using the generalized MEP definition.
Sequence:
1. define heuristic state contract;
2. implement reference controller;
3. differential test against Dijkstra baseline;
4. adversarial interruption suites;
5. separate correctness from performance.
Acceptance gate:
- no unexplained optimality failures in the completed tested space;
- every positive result carries explicit heuristic assumptions.

### D — Cost / substrate economics
Branch target: research/active-frontier-cost-v0
Objective: measure when predecessor access and active-state handling are actually worth their preprocessing cost.
Measure separately:
- preprocessing;
- one predecessor query;
- repeated predecessor queries;
- forward scanning;
- total wall time;
- edge examinations;
- memory;
- cache behavior where available.
Acceptance gate:
- break-even curves by query multiplicity and graph regime.
No conclusion may use algorithmic work as a substitute for end-to-end cost.

### E — Native implementation
Branch target: research/active-frontier-native-c-v0
Objective: port the validated guard/engine to native C without changing semantics.
Required:
- semantic equivalence tests;
- canonical regression;
- exhaustive small-n differential tests;
- counters for expansions, edge work, and stop checks;
- reproducible build metadata.
Acceptance gate:
- native results exactly match the reference implementation over the frozen regression suite.

### F — Productization
Branch target: research/active-frontier-product-v0
Objective: package the verified primitive as an integrable component, not as a research slogan.
Potential surface:
- small library/API;
- explicit interrupt/resume state contract;
- correctness modes;
- instrumentation;
- benchmark harness;
- integration examples.
Commercial claims remain CLOSED until technical gates A–E provide supporting artifacts.
Acceptance gate:
- independent consumer can integrate the component and reproduce correctness/performance results from published fixtures.

## 2. Integration / release topology

Do not merge all workstreams into one mutable research branch.

Suggested sequence:
program
├── proof
├── adversarial
├── mep
├── cost
├── native-c
└── product

Only evidence-complete branches are promoted into an integration/release branch.

Integration gate:
- claim ledger updated;
- old/withdrawn claims preserved;
- exact refs and artifact hashes recorded;
- regression suite green;
- scope/limits written beside each claim.

## 3. What we do NOT freeze yet

- universal correctness for arbitrary bidirectional heuristics;
- arbitrary scheduler correctness outside the tested semantics;
- a theoretical minimum-state theorem for the canonical counterexample;
- Theta(m/n) simple-digraph separation;
- product superiority or market demand;
- any claim that direct predecessor access is inherently more powerful than a sufficiently expressive representation.

## 4. First execution slice

Start with three tightly coupled tasks:
1. close n=2 minimality;
2. formalize the active-state stopping invariant;
3. add an audit-grade regression manifest that binds:
   claim -> experiment -> runner -> exact ref -> artifact -> status -> limits.

The first deliverable should be evidence infrastructure, not marketing material.

## 5. Revalidation rule

No claim changes status because prose was edited or because the result was repeated informally.
A status change requires:
- new evidence;
- exact provenance;
- comparison against the previous canonical artifact;
- explicit disposition of contradictions and retired claims.


## 5. Execution record

2026-09-28:
- Program branch created from research/bidirectional-grounded-verification-v0.
- Program commit: 566aba464d0f47b22eb91de78a5cc97ca153bb3b.
- Proof branch created; formalization target added in commit a6182207aa236b8c093ebe47ca48d63dbc173e61.
- Adversarial branch created; n=2 post-edge audit script added in commit c8ab7a889395b47c559162b14e1837b397277a37.
- MEP, cost, native-C and product branches created from the program branch.
- Issues opened: #14 proof, #15 adversarial, #16 cost, #17 MEP, #18 native-C, #19 product.
- Draft PRs opened: #20 proof -> program, #21 adversarial -> program.
- The n=2 script has been added but its execution result is NOT YET EVIDENCE; no status upgrade is made until execution is observed and recorded.

## 6. Revalidation rule

No claim changes status because prose was edited or because the result was repeated informally.
A status change requires:
- new evidence;
- exact provenance;
- comparison against the previous canonical artifact;
- explicit disposition of contradictions and retired claims.
