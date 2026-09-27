# Canonical Execution-Substrate Gate v0.1

Recorded: 2026-09-27
Repository: `Loofy147/Machine`
Branch: `research/orchestration-benchmark-2026-09-27`
Parent research state: `research/evidence-disposition-v0@137f76bc7fb56138a40b3bc98ed2a3291fe7acf5`

## Purpose

Close the provenance gap exposed by the Machine-targeted orchestration benchmark:

> Which concrete executable substrate is authoritative for claims about the canonical Machine transition semantics?

This gate prevents an experimental interpreter from silently becoming the canonical Machine implementation.

## Observed repository state

### Default branch

`main@1626bac2f5c478294afa4b9463f694608c322117`

The verified root contains a minimal README and documentation surfaces. No canonical interpreter source corresponding to the experimental S1/S2 interpreter was found in the verified default-branch tree.

### Machine-native research branch

`research/machine-native-primitives-v0@f752aac015d9f837bc6a89d44eed50e0325b60a6`

The recursive source inventory found:
- `docs/ABSTRACT-MACHINE.md`
- reflection and operational research documentation;
- experiment documentation;
- only one Python executable source path: `experiments/error-source-localization/harness.py`.

No canonical interpreter implementation was found in that branch's executable-source inventory.

### Experimental substrate branch

`research/substrate-interpreter-v0@d935495355ac6b827a17d6147d7f38fbcaaeb15f`

Contains the explicit CEK-style experimental implementation:
`experiments/substrate-interpreter-v0/machine.py`

Its S1/S2 results are experimentally supported for the declared finite fixture and were replayed by CI.

## Current classification

| Question | Status |
|---|---|
| Experimental CEK substrate exists | ESTABLISHED |
| Experimental S1 derivability on that substrate | EXPERIMENTALLY_SUPPORTED |
| Experimental S2 finite semantic/resource result | EXPERIMENTALLY_SUPPORTED |
| Experimental S2 candidate conformance | EXPERIMENTALLY_SUPPORTED / PRE-FREEZE source |
| Experimental substrate = canonical Machine substrate | OPEN |
| Canonical executable interpreter currently identified | OPEN |
| Canonical S1/S2 classification | OPEN / SPECIFICATION-DEBT |

## Required closure

Before any claim about a Machine mechanism being a new primitive, an optimization, or a changed computation frontier can be promoted to canonical Machine status, record all of:

1. canonical repository/branch/commit;
2. executable substrate source path;
3. transition/state/control semantics implemented by that source;
4. allowed state-access operations;
5. relation representation and traversal semantics;
6. cost accounting;
7. replay command or CI workflow;
8. evidence/result artifact tied to the exact source commit.

## Decisive minimal pair after closure

Control:
`S1 = generic readable state + comparison + branching + iteration`

Treatment:
`S2 = S1 + direct indexed relation access`

Fixed:
- information;
- timing;
- persistent representation;
- correctness contract;
- offline budget;
- online budget;
- access-cost accounting.

Observed outputs:
- semantic equivalence;
- `(B_off,R,B_on,C_access)`;
- full feasible-set frontier where applicable.

## Promotion rules

**Resource primitive / optimization**

If relation traversal is derivable from the canonical substrate and the direct mechanism only changes cost.

**Substrate extension**

If the direct relation capability requires an access/interpretation operation absent from the canonical fixed substrate.

**Resource-bounded frontier advantage**

If traversal is semantically derivable but no matched representation reproduces the direct mechanism within the declared resource contract.

This classification remains relative to the frozen substrate/resource contract.

## Explicit non-goals

This gate does not:
- declare S2 frozen;
- declare a new computational-power separation;
- broaden the reflective substrate;
- infer implementation lineage from terminology;
- treat documentation as executable evidence.

## Current next action

Identify or implement the canonical Machine execution substrate, then run the minimal pair on that actual substrate.

Until that happens, the experimental substrate remains evidence about its own implementation only.
