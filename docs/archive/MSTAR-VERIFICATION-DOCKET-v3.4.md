# M* Verification Docket v3.4 — Historical Archive

Source: Library artifact M_star_verification_docket_v3.4.md
Original status in source: TESTED, not formally verified
Archived on: 2026-09-21

This is a historical artifact. It is NOT the Rev 2.1 canonical substrate specification.

## Historical signature

M* = <S, Sigma, delta, R^-1_rev, R+_opt, Phi, Pi>

The historical docket explicitly recorded Phi, R+_opt, and Pi. Rev 2.1 reconciliation deliberately removes these from the normative signature.

## Historical findings retained

- Attractor / CPre implementation was tested against exhaustive positional-strategy oracles on 3,000 tiny games with 0 mismatches under both reachability deadlock conventions and both dual safety conventions.
- A larger suite of 150 games (200–3,000 states) matched naive fixpoint iteration with 0 mismatches.
- The historical instance contained stuck states, making deadlock convention material.
- Historical Phi interning tests: 20,000 intern calls over mixed structured states; 3,519 distinct interned values; round-trip and idempotence checks passed. The source itself documented Python-equality caveats.
- Historical Hopcroft/Moore checks included 489 partial DFAs with 0 brute-force mismatches.
- Historical R+_opt forward mirror matched raw-edge oracles in the declared medium/large tests.
- Historical memory and timing figures are retained as historical measurements only.
- The historical docket explicitly corrected earlier speed explanations and rejected the v3.3 explanation that the observed Python hub speed came from an asymptotic binary-search advantage.
- The historical docket rejected several broader claims, including an incorrect trap-completion linearity claim, an undefined operational Pi claim, and unsupported external analogies.

## Rev 2.1 disposition

The historical constructs remain available for provenance, but they are not silently carried into Rev 2.1.

- Phi: HISTORICAL / DROPPED FROM REV 2.1 SIGNATURE.
- R+_opt: HISTORICAL / ABSORBED BY DENSE FORWARD DELTA SEMANTICS.
- Pi: HISTORICAL / NOT PART OF REV 2.1 SIGNATURE.
- Player partition and CPre: RETAINED as explicit owner semantics.
- Fiber multiplicity: RETAINED as an implementation contract owned by Fiber.deduped.

See:
docs/SUBSTRATE-REV2.1-RECONCILIATION-v0.1.md
