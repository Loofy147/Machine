
# Reflection Substrate Re-Audit v0.2

Status: RESEARCH RE-AUDIT / DECISION SUPPORT
Date: 2026-09-18
Primary branch: research/machine-native-primitives-v0

## 1. Purpose

This re-audit checks the first reflective-interpreter attempt against the current Machine research and external literature before implementation decisions are widened.

## 2. Repository state

Machine currently has multiple meaningful branches.

The documented machine-native research frontier is:

`research/machine-native-primitives-v0`

Current comparison with `main` reports:

- diverged;
- research branch ahead by 43 commits;
- main behind by 3 commits;
- merge base `641517a26790c40295606f12fd6e4a87fcab7186`.

The branch `research/confirmatory-freeze-order-v0.1` is a separate experimental-governance line covering confirmatory fault-transfer design, freeze ledgers, operational utility, and a contract pilot.

Decision:
Keep confirmatory-fault-transfer governance separate from reflective-substrate implementation.

## 3. Candidate status

The supplied reflective interpreter was not found in the inspected Machine surfaces under its distinctive identifiers.

Therefore:

- repository implementation status: UNKNOWN;
- execution/test status in Machine: UNVERIFIED;
- design status: CANDIDATE SUBSTRATE;
- tier-3 status: OPEN.

Do not promote it to a Machine result until tests and artifacts are committed.

## 4. External alignment

### CEK

The candidate state `(C,E,K)` aligns with the standard CEK structural state: control, environment, continuation.

CEK is therefore a suitable small operational substrate. Standard abstract-machine literature describes CEK states as `Exp × Env × Kont`. See: Felleisen-style CEK formulations; a representative modern exposition is Van Horn & Might, Abstracting Abstract Machines (2010), which defines CEK states as Exp × Env × Kont.

### Friedman & Wand 1984

The closest direct reflection precedent is Friedman & Wand, "Reification: Reflection without Metaphysics" (1984).

That work makes interpreter data structures available to the running program and allows the program to alter them. The reified material includes form/expression, environment, and continuation; the construction does not depend on a reflective tower. Friedman, D. P.; Wand, M. (1984), Reification: Reflection without Metaphysics, DOI: 10.1145/800055.802051.

### Wand & Friedman 1986/1988

"The Mystery of the Tower Revealed" provides a semantic account of reflective towers.

It explicitly models expression/control, environment, and continuation, then introduces a metacontinuation for the upper interpreter context. It also describes reification/reflection symmetry in terms of representations of environment and continuation being converted back into live machine components. Wand, M.; Friedman, D. P. (1986 conference version; 1988 journal version), The Mystery of the Tower Revealed: A Non-reflective Description of the Reflective Tower, DOI: 10.1007/BF01806174.

### des Rivières / Smith

Their implementation work describes a level-shifting processor for procedural reflection and 3-LISP. This supports treating reflective execution context as an explicit semantic level rather than making one host-language loop the invariant. des Rivières, J.; Smith, B. C. (1984), The Implementation of Procedurally Reflective Languages, DOI: 10.1145/800055.802050.

## 5. Candidate's strongest defensible claim

The candidate makes `*applier*` an object-language Closure that is consulted for compound-procedure dispatch.

Therefore the narrow mechanism can be defined as:

`rho_dispatch = compound-procedure dispatch semantics`

This is narrower and cleaner than calling it the whole evaluator.

Decision:
Use `rho_dispatch` as the first experimental reflection target.

## 6. Direct gaps

### G1 — control representation

The candidate constructs:

`Snapshot(control=0, env=E, kont=K)`

The `0` value cannot currently serve as a general reflected control register.

However, classical reflection can reify selected interpreter registers rather than expose an unrestricted generic state object.

Decision:
Define the exact reflected register set before changing implementation.

### G2 — environment and continuation representation

`snapshot->list` wraps environment and continuation inside object-language data, but the payloads remain host-language objects.

That gives transport, not yet symmetric reification/reflection of their structures.

Decision:
Define:

`reify_rep -> object-language representation`

and:

`install_rep -> live machine component`

with explicit round-trip or controlled non-round-trip semantics.

### G3 — bootstrap role

Python still knows the semantic role of `*applier*`, constructs its invocation environment, executes its body, and requires a Snapshot result.

Thus the literal claim "no Python special case" is stronger than the shown mechanism.

Defensible formulation:

`one fixed bootstrap/dispatch hook + object-language-defined dispatch semantics`

Decision:
Minimize and document the bootstrap hook; do not pretend it does not exist.

### G4 — reflection versus ordinary rebinding

`set! *applier*` is a necessary control condition, not reflection proof.

Reflection requires:

`reify -> modify reified representation -> install -> later dispatch consults modified representation`

### G5 — continuation

The candidate transports a continuation through Snapshot but does not expose its structure for ordinary object-language transformation.

Decision:
Treat continuation transformation as a separate capability. The first dispatch experiment need not solve arbitrary continuation editing, but install semantics must be explicit.

### G6 — install semantics

Install discards the current continuation and restores the snapshot continuation.

This is not automatically wrong. Classical reflection work explicitly discusses continuation choice/asymmetry, while reflective-tower semantics introduce metacontinuation to represent the surrounding reflective context. Friedman & Wand 1984, continuation-choice asymmetry in the towerless reification model. Wand & Friedman 1986/1988, metacontinuation model for reflective tower context.

Decision:
Do not force continuation preservation prematurely. First classify the semantics as jumpy, resumptive, tail-like, or level-shifting.

### G7 — clone fidelity

`clone_env_chain` copies frame dictionaries but does not prove graph-wide isolation for closures and mutable reachable values.

Decision:
Do not call it a general clone/rollback guarantee.

### G8 — probe/rollback

The shown clone helper is not yet a complete candidate -> isolated probe -> commit/reject contract.

Decision:
Keep safety/rollback separate until needed by the causal-reflection test.

## 7. Underlying gaps

Before a broader reflection claim, specify:

1. scope of `rho`;
2. fixed substrate/bootstrap boundary;
3. reflected versus reflecting execution context;
4. ownership and aliasing of reified state;
5. continuation semantics;
6. boundary between host data, object-language data, runtime capabilities, and replay artifacts;
7. installation semantics;
8. round-trip/replay conditions.

## 8. Indirect gaps

Still open:

- whether reflection changes reachable operation space or merely routing;
- whether dispatch reflection yields reusable executable structure;
- whether modifying the modifier adds capability;
- whether continuity matters independently of retained data;
- whether reflection adds capability beyond ordinary rebinding;
- whether the seam is minimal;
- whether the semantics port to another substrate.

These do not belong in the first proof obligation.

## 9. Narrow first claim

The immediate target should be:

> A running machine can causally replace an object-language-defined compound-procedure dispatch rule through reified state and same-run installation, such that a later compound call is governed by the modified rule.

Do not yet claim:

- evaluator self-modification;
- general reflection;
- self-improvement;
- reflective learning;
- intelligence.

## 10. Minimal-pair acceptance contract

Treatment and control match:

- initial program;
- initial bindings;
- ordinary inputs;
- continuation/level context;
- resource budget;
- substrate.

Only the reified dispatch representation differs.

Acceptance requires:

1. modification is generated by object-language computation;
2. installation occurs during the ongoing computation;
3. a later compound call consults the modified dispatch rule;
4. observable transition/result differs;
5. no restart occurs;
6. hidden Python dispatch cannot explain the difference;
7. ordinary `set!` is insufficient to explain the result;
8. extra compute/budget is matched;
9. the committed representation is replayable under declared conditions.

## 11. Decision table

| Decision | Status |
|---|---|
| Keep current Machine abstract model | ACCEPT |
| Keep `rho_dispatch` narrower than whole evaluator | ACCEPT |
| Treat candidate as unverified | ACCEPT |
| Keep confirmatory branch separate | ACCEPT |
| Use CEK `(C,E,K)` as structural substrate | ACCEPT |
| Treat 1984 reification as closest direct precedent | ACCEPT |
| Treat 1986/1988 tower semantics as meta-continuation/level reference | ACCEPT |
| Require literal single host loop | REJECT AS TOO STRONG |
| Claim full evaluator reflection now | REJECT |
| Claim tier-3 now | OPEN / NOT ESTABLISHED |
| Add reflective features before minimal pair | REJECT |
| First prove dispatch-only causal reflection | ACCEPT |

## 12. Recommended next boundary

Do not broaden the interpreter.

Implement only the smallest mechanism required for:

`object-language reified dispatch representation
-> object-language modification
-> installation
-> same-run later compound call
-> modified dispatch behavior`

Then add matched controls for:

- ordinary rebinding;
- static alternative dispatch;
- restart/hot-swap;
- extra-compute explanation;
- continuation-only change.

Only after this passes should full `(C,E,K,rho,H)` reflection be revisited.

## 13. Frontier after the re-audit

ESTABLISHED:
- Machine causal-reflection target;
- online hot-swap as a weaker capability;
- CEK relevance;
- classical interpreter-state reification/reflection precedent.

INFERENCE:
- `rho_dispatch` is a promising minimal seam;
- bootstrap should be minimized and explicit;
- continuation/level semantics are a first-class design issue.

UNKNOWN / OPEN:
- causal dispatch replacement;
- symmetric reification/install;
- continuation semantics;
- clone/rollback fidelity;
- minimality;
- portability;
- reflection beyond dispatch;
- capability gain beyond ordinary rebinding.

## 14. Governing decision

Keep the question narrow until the mechanism is proved.

Immediate target:

`narrow causal reflection`

Everything above it remains OPEN.
