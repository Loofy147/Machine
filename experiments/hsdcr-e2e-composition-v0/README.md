# HSDCR End-to-End Composition v0

Status: **RESEARCH / NON-NORMATIVE / OPEN**

This experiment tests the surviving semantic junction after the HSDCR reassessment.

It uses two real source fixtures at the contribution boundary:
- GitHub Machine PR #10;
- a real public AT Protocol repository record.

The test first attempts direct substitution and then adds an explicit application-level proposal record to the AT record. The proposal wrapper uses an already-declared domain semantic (proposal/contribution); it is not treated as a new primitive.

The acceptance path is deliberately provider-neutral:

`typed records -> evidence -> authority -> explicit decision -> canonical transition -> replay`

The current evidence and authority objects are normalized fixtures. This version therefore does not claim live security, authority, durability, or performance equivalence between external providers.

## Kill target

If the complete junction is representable with ordinary typed data, explicit transition/policy rules, and known provider capabilities, the "new primitive" hypothesis remains unfalsified only at the composition level.

A future residual must survive provider replacement and cannot be dismissed as an adapter or ordinary data relation.

## Current result

- direct GitHub PR -> native AT record: **DIRECT_COLLISION**
- GitHub PR -> AT record + explicit application proposal wrapper: **SEMANTIC_BOUNDARY_PRESERVED**
- new execution primitive detected: **NO**
- new repository primitive detected: **NO**
- architectural novelty: **OPEN**

## Limit

This is a contract composition experiment, not a proof of architectural novelty.
