# S2 Substrate Properties v0.1 — Superseded Interpretation

Status: SUPERSEDED / PROVENANCE CORRECTION

This file previously described the experimental S2 implementation as if its property set could serve as the specification of S2.

That interpretation was too strong.

The current evidence supports the second, narrower interpretation:

    experimental S2 implementation
            ↓
    evidence-backed substrate profile

not:

    evidence-backed profile
            ↓
    canonical S2 specification

The durable artifacts are now separated as follows:

- docs/S2-EXPERIMENTAL-SUBSTRATE-PROFILE-v0.1.md
  Evidence-backed profile of the concrete implementation currently labeled S2.

- docs/S2-SPECIFICATION-DEBT-v0.1.md
  Open specification problem: define S2 independently of the implementation and then test that definition.

The original property evidence remains valid as evidence about the experimental implementation, but its provenance must not be upgraded into a canonical S2 definition.

Important boundary:

    S2-P1 ... S2-P12

are properties of the implementation/profile under the recorded experimental contract. They are not, by themselves, semantic axioms of S2.

Next discriminating action:

Define a candidate S2 specification independently, derive the implementation tests from it, and determine which current profile properties are necessary, accidental, or missing.