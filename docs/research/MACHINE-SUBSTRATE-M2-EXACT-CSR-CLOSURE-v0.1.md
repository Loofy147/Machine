# M2 Exact Contiguous CSR Closure v0.1

Status: **EXPERIMENT / DECISION SUPPORT**

This is the stronger M2 test requested by the A↔M gap.

The maintained representation is the same logical contiguous CSR layout used by the
inverse-fiber substrate:

`offs[n+1], src[E], act[E]`

A1_RW is restricted to generic indexed reads/writes, arithmetic, and finite iteration.
No fiber-specific mutation operation is used.

A fixed capacity of (S\Sigma) reserves enough cells for all possible transition
entries. Insert/delete is implemented logically through generic shifts and offset
updates.

## Decision target

If semantic and structural validation passes after every update, then:

> exact contiguous inverse CSR does not require a specialized inverse semantic mutation
> primitive for representability under A1_RW.

This is an existence result. It says nothing about efficiency.

## Resource meaning

The update cost counts logical word shifts plus payload/offset writes. Therefore the
experiment makes the potentially large M2 maintenance cost explicit rather than hiding
it behind a host-language list operation.

The expected architectural split is consequently:

- **A1_RW:** representational closure, potentially expensive dynamic maintenance.
- **A2:** specialized structured update, potentially lower maintenance cost.
- production choice: resource-frontier question after workload/update-rate limits are frozen.

## Non-claim

Passing this test does not establish that A1_RW is the production substrate, nor that
A2 should be removed from Rev 2.1. It only closes the representability question for the
exact contiguous CSR logical representation.
