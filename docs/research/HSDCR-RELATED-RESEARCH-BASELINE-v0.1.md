# HSDCR Related Research Baseline v0.1

Status: RESEARCH / LITERATURE-AND-SYSTEMS REVIEW / CURRENT BASELINE
Reviewed: 2026-09-29

## Purpose

This document records the external systems and research families that materially overlap the HSDCR candidate. The purpose is reduction and capability adoption, not a novelty claim.

The test is:

adopt(capability) != adopt(ontology)

A neighboring system is relevant when it already implements a capability that HSDCR might otherwise be tempted to invent.

## Primary systems and standards

| Family | Relevant capability already documented | HSDCR implication |
|---|---|---|
| GitHub pull requests + rulesets/branch protection | proposal surface, reviews, required checks, controlled merge, protected canonical branches | contribution-before-acceptance and gated canonicalization are existing mechanics |
| AT Protocol repository | signed self-certifying repository, content-addressed Merkle state, revisions, export/sync | decentralized repository state, verification and reconstruction mechanics already exist |
| Automerge | CRDT document history, local storage, peer synchronization, pluggable storage/network adapters | contribution/change history + decentralized sync is known composition |
| Pijul | first-class changes, dependency relations, commutation, conflict representation | change-oriented contribution semantics are established |
| W3C PROV | provenance model over entities, activities, agents, derivation and revision | evidence/provenance can be represented without inventing a new provenance ontology |
| OpenTelemetry | structured log/event model with event timestamp and observed timestamp | signal and observation can remain separate semantic fields |
| UCAN | delegable, verifiable capability authority and proof chains | authority/capability is an existing semantic class |
| Rekor / Sigstore | append-only, verifiable transparency log for signed metadata and existence | tamper-evident evidence publication is existing infrastructure |
| ForgeFed | federated forge objects and activities, including repository/project-management collaboration | decentralized forge contribution is a known application domain |
| lakeFS | branches, immutable commits, pull requests, review before merge, protected branches | contribution-before-canonical-state is not unique to source-code forges |
| Event Sourcing | event log as source from which application state can be reconstructed | replay/reconstruction is a mature pattern, not a new primitive |
| Object-capability research | compositional authority/concurrency reasoning | composition itself is a mature research subject |

## Academic / foundational references

- Auvolat & Taiani, Merkle Search Trees: Efficient State-Based CRDTs in Open Networks, SRDS 2019, DOI 10.1109/SRDS47363.2019.00032. The paper studies Merkle-tree representations for state-based CRDTs in open networks.
- Almeida, Shoker & Baquero, Delta State Replicated Data Types, Journal of Parallel and Distributed Computing 111 (2018), 162–173, DOI 10.1016/j.jpdc.2017.08.003. The paper formalizes delta-state CRDTs and anti-entropy/convergence mechanisms.
- Miller, Robust Composition: Towards a Unified Approach to Access Control and Concurrency Control (PhD dissertation, 2006). The work explicitly studies compositional access-control and concurrency-control concerns.
- Fowler, Event Sourcing (2005), as a foundational engineering description of reconstructing application state by replaying stored events.

## Primary references

- GitHub protected branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub pull-request merge requirements: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request
- AT Protocol repository specification: https://atproto.com/specs/repository
- Automerge repositories: https://automerge.org/docs/reference/repositories/
- Automerge storage: https://automerge.org/docs/reference/repositories/storage/
- Pijul manual: https://pijul.org/manual/why_pijul
- W3C PROV overview: https://www.w3.org/TR/prov-overview/
- W3C PROV primer: https://www.w3.org/TR/prov-primer/
- OpenTelemetry Logs Data Model: https://opentelemetry.io/docs/specs/otel/logs/data-model/
- UCAN specification: https://github.com/ucan-wg/spec
- UCAN Delegation: https://github.com/ucan-wg/delegation
- Sigstore Rekor overview: https://docs.sigstore.dev/logging/overview/
- Sigstore Rekor security model: https://docs.sigstore.dev/about/security/
- ForgeFed specification: https://forgefed.org/spec/
- lakeFS concepts: https://docs.lakefs.io/v1.83/understand/model/
- lakeFS pull requests: https://docs.lakefs.io/howto/pull-requests/
- Event Sourcing: https://martinfowler.com/eaaDev/EventSourcing.html
- Miller dissertation: https://www.erights.org/talks/thesis/

## Why these sources are sufficient for the current reduction stage

They cover the candidate's current semantic/mechanical neighborhood from independent directions:

- repository/change and canonicalization;
- distributed replication/reconciliation;
- provenance/evidence;
- observation/signal modeling;
- authority/delegation;
- tamper-evident publication;
- federated contribution;
- state reconstruction.

The combination is sufficient to justify reduction pressure: most candidate capabilities already have established implementations or formal models.

It is not sufficient to prove the absence of every possible novel composition or semantic relation. That question remains an experiment, not a literature-search conclusion.

## Current literature disposition

related-capability coverage = SUFFICIENT_FOR_REDUCTION

novelty-exclusion = NOT_PROVEN

composition-irreducibility = EXPERIMENTAL_QUESTION
