# Substrate Interpreter v0 — Results

Status: EXPERIMENTALLY_SUPPORTED / LOCAL REPLAY
Branch: research/substrate-interpreter-v0

## Implementation

A small CEK-style interpreter was built from the current Machine abstract model:

- State: explicit runtime store plus persistent machine data;
- Operation: AST expression/control forms;
- Transition: single `step()` transition;
- Control: explicit continuation frames;
- Closure: object-language value carrying lexical environment;
- Recursive computation: `LetRec`.

The substrate contract is explicit:

- S1 = generic readable state, comparison, branching, sequence traversal, no direct relation lookup;
- S2 = S1 plus direct indexed relation access.

## Executed verification

Local commands:

```
python -m pytest -q
python run_audit.py
```

Observed:

```
pytest: 5 passed
audit exit: 0
semantic_equivalence: true
```

For five queries over a five-entry relation:

```
queries = [k4, k0, k2, missing, k3]
results = [40, 0, 20, NIL, 30]
```

S1 object-language recursive scan:

```
transition_ticks = 600
access_ticks = 211
```

S2 direct indexed lookup:

```
transition_ticks = 35
access_ticks = 15
```

Offline index construction/storage:

```
construction_ticks = 5
stored_entries = 5
```

Thus the measured ratios were:

```
transition ticks: 17.14x
access ticks:     14.07x
```

while observed semantics were identical.

## What this establishes

1. A candidate S1 substrate can perform relation lookup by ordinary object-language computation over stored relation data.
2. The direct indexed primitive can occupy a materially better resource point in S2.
3. The offline/index construction cost can be explicitly separated from online lookup cost.
4. Therefore direct lookup is not automatically a new semantic capability even when it is a strong resource optimization.

## Critical boundary

This does NOT establish that the canonical Machine interpreter already implements S1.

It also does NOT establish that the canonical Machine substrate excludes S1.

The result is a concrete experimental substrate that makes the boundary testable.

## Threats to validity

- one interpreter implementation;
- one finite relation fixture;
- abstract tick accounting;
- no asymptotic closure claim;
- indexed representation construction is charged separately but remains a representation choice rather than a hardware-level access model.

## Current disposition

```
S1 derivability in this interpreter       EXPERIMENTALLY_SUPPORTED
S1/S2 semantic equivalence on fixture     EXPERIMENTALLY_SUPPORTED
S2 resource advantage on fixture          EXPERIMENTALLY_SUPPORTED
canonical Machine substrate classification OPEN
```

Next action: reconcile this interpreter with the canonical Machine interpreter source and run the same minimal pair on the actual substrate.
