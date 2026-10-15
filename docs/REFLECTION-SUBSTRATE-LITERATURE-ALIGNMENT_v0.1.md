
# Reflection Substrate & Literature Alignment Audit v0.1

Status: RESEARCH AUDIT / OPEN
Date: 2026-09-18
Branch: research/machine-native-primitives-v0

## 1. Scope

This audit reconciles the Machine reflection frontier with the first reflective-interpreter candidate supplied during research and with external work on CEK-style machines and computational reflection.

The candidate is treated as a USER-SUPPLIED / UNVERIFIED research attempt unless executable evidence is committed to the repository.

## 2. Repository boundary

The distinctive candidate identifiers searched in the inspected Machine surfaces included:

- *applier*
- snapshot->list
- reify
- reflective
- CEK

They were not found in the inspected Machine repository surfaces. Therefore the candidate is not currently a repository-established implementation.

This does not prove absence from every branch or unindexed artifact.

## 3. Existing Machine frontier

Machine already defines the reflection target as:

reified/exposed execution machinery -> modify -> modified representation participates in later transitions -> observable behavior changes

The broader experimental state is:

Q = <R, S, K, rho, H>

The existing prime-stream work establishes same-process executable replacement but explicitly leaves causal evaluator reflection open because its live representation is external.

The new candidate potentially addresses that exact boundary by placing reflective state inside the interpreter.

## 4. External alignment

### CEK

The candidate state:

(C, E, K)

matches the standard CEK decomposition of control, environment, and continuation.

This is a valid structural substrate for small-step interpreter semantics.

### Friedman & Wand 1984

The closest direct architectural precedent identified is:

Daniel P. Friedman and Mitchell Wand,
"Reification: Reflection without Metaphysics" (1984).

Its stated concern is making interpreter data structures available to the program being executed and allowing the program to alter those structures. The described reification includes expression/form, environment, and continuation, and does not require an infinite reflective tower.

This maps directly onto the intended Snapshot/reify/install construction.

### Smith / des Rivières

Procedural reflection emphasizes that a reflective account must be causally connected to the running process and must have an appropriate vantage point.

The candidate's nested reflective execution can be viewed as a possible meta-level vantage point, but equivalence to the historical model is not established.

### Wand & Friedman 1986

"The Mystery of the Tower Revealed" is best treated as a semantic/reference framework for reflective towers rather than as the closest implementation recipe for the candidate.

Therefore:

1984 -> closest direct reification/reflection precedent

1986 -> reflective-tower semantic/reference framework

### Later reflective-tower work

Later work distinguishes issues including metacontinuation structure, proper tail reflection, and single-threadedness.

Therefore the relevant invariant is not literally "the same host-language while loop". The stronger requirement is causal continuity with correct continuation/meta-level semantics.

## 5. Candidate architecture

The candidate introduces an ordinary object-language closure:

*applier*

Compound application is conceptually:

compound procedure
-> lookup *applier*
-> execute its object-language body
-> produce Snapshot
-> install/resume

This is a promising narrow reflective seam.

A precise name for the reflected mechanism is:

rho_dispatch = compound-procedure dispatch semantics

It should not yet be called the whole evaluator.

## 6. Direct gaps

### G1 — incorrect current control

The shown reify path creates:

Snapshot(control=0, env=E, kont=K)

Therefore it does not currently capture the actual control expression.

### G2 — partial object-language representation

snapshot->list wraps control, environment, and continuation in an object-language list, but Env and continuation remain host-language objects.

The wrapper is not yet a fully inspectable/mutable object-language machine-state representation.

### G3 — host-recognized applier role

The value of *applier* is a Closure, but the Python evaluator still recognizes the role explicitly, constructs the invocation environment, runs the applier body through a special ABI, and requires a Snapshot result.

Thus "no Python special case for the default applier" is stronger than the current implementation.

A more defensible target is:

one fixed bootstrap/dispatch hook
+
object-language-defined dispatch semantics.

### G4 — reflective mutation does not yet reach rho_dispatch

The object language has set!, but the reified environment is not generally inspectable/mutable as object-language data.

Therefore the experiment has not yet shown:

modify(reified state)
-> change *applier*
-> future dispatch uses modified rho_dispatch.

Ordinary set! rebinding is a necessary control, not reflection proof.

### G5 — continuation transport vs continuation reification

Continuation objects can be carried and reinstalled, but their internal structure is opaque to the object language.

This leaves open whether the system has genuine continuation reification or merely continuation transport.

### G6 — install semantics are jump-style unless explicitly defined otherwise

install discards the current continuation and restores the snapshot continuation.

This can be a valid reflective semantics, but its jump/push/tail behavior must be explicit because it affects causal continuity and nested reflection.

### G7 — clone isolation is not established

clone_env_chain copies frame dictionaries but not arbitrary reachable object graphs.

Closures may retain references to original environments, and mutable values can remain shared.

Therefore the helper is not yet a general clone-fidelity proof.

### G8 — probe/rollback is not integrated

The shown clone helper is not yet a complete candidate -> isolated probe -> commit/reject contract.

## 7. Underlying gaps

1. Define whether rho means dispatch-only, evaluator-level, or whole transition semantics.
2. Define the fixed bootstrap boundary explicitly.
3. Define reflective versus reflected execution context and any meta-continuation.
4. Define ownership, identity, aliasing, copying, and installation semantics for reified state.
5. Define continuation semantics precisely.
6. Define which machine state is native, object-language data, opaque runtime capability, or replay artifact.
7. Establish whether the reflected seam is portable to another execution substrate.

## 8. Indirect gaps

Still open:

- whether dispatch reflection generalizes beyond compound calls;
- whether changing rho_dispatch changes reachable operation space or only routing;
- whether modified dispatch yields reusable executable structure;
- whether the modifier can modify itself;
- whether reflection adds capability beyond ordinary rebinding;
- whether continuity matters beyond retained state;
- whether the candidate is minimal;
- whether the candidate's mechanism is necessary rather than merely convenient.

## 9. Correct minimal-pair test

Initial and control executions must match on:

- program;
- environment;
- inputs;
- current control;
- continuation;
- budget;
- substrate.

Only the reified dispatch representation may differ.

The required result is:

rho_dispatch_pre != rho_dispatch_post

and:

future_transition_pre != future_transition_post

inside one uninterrupted execution.

The result must not be explainable by:

- ordinary set!;
- different data;
- extra compute;
- restart;
- fixed candidate enumeration;
- hidden Python dispatch;
- unrelated continuation changes.

## 10. Relationship map

CEK-style machine
-> control/environment/continuation substrate
-> Friedman/Wand 1984 tower-independent reification/reflection
-> Smith/des Rivières procedural reflection and causal vantage point
-> Wand/Friedman 1986 reflective-tower semantics
-> Machine Q=<R,S,K,rho,H>
-> candidate narrow seam rho_dispatch=*applier*

Log-Os remains a historical implementation reference and is not evidence of direct Machine lineage.

## 11. Current status

ESTABLISHED:
- Machine's reflection target and current online-hot-swap boundary.
- CEK's relevance to (C,E,K).
- External literature's direct treatment of interpreter-state reification/reflection.

USER_SUPPLIED / UNVERIFIED:
- the candidate interpreter and its tier-3 behavior.

INFERENCE:
- *applier* is a promising narrow causal reflection seam.
- the candidate is closer to the 1984 tower-independent line than to a literal 1986 tower implementation.

OPEN:
- causal installation of modified rho_dispatch;
- full object-language state representation;
- continuation transformation;
- clone/rollback fidelity;
- minimality;
- substrate independence.
