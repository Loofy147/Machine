# Machine Production Resource Envelope Frontier v0.1

Status: **PROPOSED / EXECUTED STRUCTURAL FRONTIER**

## Objective

Move the production-substrate question from profile naming to explicit resource
admissibility.

For M2:

- A1_RW query access is generic state addressing.
- A2 query access is specialized fiber access.
- A1_RW dynamic maintenance is charged using the exact contiguous-CSR operation model.
- A2 dynamic update cost is kept as an explicit parameter (c_2), because the
  current Rev 2.1 contract does not expose an equivalent structural unit count.

For a query/update workload ((Q,U)):

[
C_{A1}=Q,q_1+U,c_1
]

[
C_{A2}=Q,q_2+U,c_2
]

with:

[
q_1=2+2d,qquad q_2=1+d.
]

Therefore the aggregate break-even condition is:

[
c_2 le c_1 + rac{Q}{U}(q_1-q_2).
]

This is a **boundary condition**, not a selection rule.

## Interpretation

A2 cannot be declared superior or inferior from the existing evidence because
(c_2), dynamic storage policy, and consistency semantics are not normalized with
A1_RW.

Likewise, A1_RW cannot be accepted as a production substrate merely because it is
representationally closed.

## Storage

For live contiguous CSR:

[
R_{live}=4(S+1)+4E+E
]

using the Rev 2.1 int32/int32/uint8 logical layout.

For M2, the physical capacity policy is a separate resource question. A fully
reserved (SSigma)-entry representation has a different storage envelope from
live-E storage.

Therefore the production contract must explicitly declare:

- live representation;
- reserved capacity;
- growth/reallocation policy;
- compaction policy;
- consistency point after update.

## Current gate

The canonical production profile remains **OPEN**.

The next admissibility test requires a concrete (c_2) update-resource contract for
the Rev 2.1 structured dynamic path and a production (Q/U) workload envelope.
