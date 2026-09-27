# HSDCR Capability Substitution Boundary v0.1

Status: **EXPERIMENT / STRUCTURAL TEST ONLY**

This experiment tests the minimal capability boundaries defined in:

`docs/research/HSDCR-MINIMAL-CAPABILITY-BOUNDARIES-v0.1.md`

It intentionally uses small adapters that emulate two known styles:

- Git-like contribution/history/review semantics;
- AT Protocol-like authenticated repository/event semantics.

The adapters are not the external systems themselves.

## Question

Can the same candidate-level semantic object be produced from different known capability styles without collapsing:

```
identity
contribution
observation
evidence
authority
decision
canonical state
```

## Test

Run:

```sh
python3 run.py
```

The test should produce:

```text
PASS
semantic_equivalence = true
```

## Interpretation

A passing result means the selected boundary interfaces are sufficiently abstract for this fixture.

It does **not** establish:
- compatibility with GitHub or AT Protocol implementations;
- architectural novelty;
- decentralization;
- production suitability;
- security;
- performance equivalence.

A failure is more informative: it identifies a boundary that is too tied to one source system or a semantic distinction that was lost during normalization.

## Next expansion

Replace one emulated provider at a time with:
- a real Git-derived record source;
- an AT Protocol repository export;
- a CRDT/change source;
- a provenance source;
- a capability authorization source;
- a transparency log source.

Run the same semantic collision suite without changing the candidate-level interface.
