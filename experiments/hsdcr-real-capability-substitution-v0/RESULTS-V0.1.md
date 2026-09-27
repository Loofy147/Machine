# HSDCR Real Capability Substitution v0.1 — Results

Status: **EXPERIMENTALLY_SUPPORTED / CONTRACT-BOUND**

Recorded: **2026-09-28**

Branch under test:

`research/hsdcr-neighborhood-crosswalk-v0`

Repository head at test setup:

`40296835152eb85d6623b46af34794918c583099`

## Question

Can a native AT Protocol repository record substitute directly for a GitHub Pull Request while preserving the candidate distinction:

```
Contribution != CanonicalState
```

More specifically:

> Can a contribution exist as a non-canonical proposal before an acceptance transition?

## Real source observations

### GitHub

Repository: `Loofy147/Machine`

Pull Request: #10

URL: https://github.com/Loofy147/Machine/pull/10

Observed:
- state = open
- merged = false
- base = `research/bidirectional-substrate-v3`
- base SHA = `59fab62704875193801db77c7cb8361475297f48`
- head = `research/machine-substrate-primitive-closure-v0`
- head SHA = `12dade33f708d66890c6c10b754f85c1d3ae13e3`
- commits = 127
- changed files = 75

This real PR provides an explicit proposal surface whose head remains distinct from the canonical base while the PR is open.

### AT Protocol

Repository identity:
- handle = `bsky.app`
- DID = `did:plc:z72i7hdynmk6r22z27h6tvur`

Real public record:
- URI = `at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.post/3mp54n7zccc2j2`
- type = `app.bsky.feed.post`
- published = `2026-06-25T19:03:39.565Z`

The AT Protocol repository specification defines records as contents of an account repository and states that mutations create new signed repository commits. The repository itself is the authoritative location for the account's data. See:
- https://atproto.com/specs/repository
- https://atproto.com/specs/sync
- https://atproto.com/guides/sync

## Local replay

The semantic collision test was executed against the real source fixture with result:

```text
status = PASS
classification = PARTIAL_SUBSTITUTION / ADAPTER_REQUIRED
semantic_equivalence = false
github_preserves_noncanonical_proposal = true
at_record_is_repository_mutation = true
proposal_before_canonical_acceptance_substitutable = false
```

## Interpretation

The result is **not**:

> AT Protocol cannot implement proposals.

The result is narrower:

> A native AT repository record cannot be substituted directly for the cited GitHub Pull Request as a proposal-before-canonical-acceptance object.

To preserve the GitHub distinction, an AT-based composition would need an additional application-level proposal/acceptance layer, for example by defining separate record types and an explicit transition semantics.

That adapter is therefore an architectural dependency to investigate, not an implementation detail to hide.

## Removal consequence

If the proposal/acceptance boundary is removed from the composition:

```
contribution
  -> canonical repository mutation
```

and the distinction

```
Contribution != CanonicalState
```

is no longer represented natively.

Therefore the proposal/acceptance component is **not yet proven globally irreducible**, but it is experimentally shown to be required for direct GitHub↔AT substitution under the declared boundary.

## Falsification boundary

This experiment does not establish:
- a general impossibility theorem for AT Protocol application designs;
- architectural novelty;
- decentralization of authority;
- security equivalence;
- performance equivalence;
- production suitability.

It establishes one real substitution collision under a stated semantic boundary.

## Provenance

GitHub PR metadata was fetched directly from the repository on 2026-09-28.

The AT Protocol identity and public record were verified against current public Bluesky/AT Protocol sources on 2026-09-28.

Current external specification basis:
- AT Protocol Repository specification.
- AT Protocol Sync specification.
- AT Protocol Sync guide.

## Disposition

```
real_source_fixture = PASS
direct_GitHub_to_AT_substitution = NOT_EQUIVALENT
adapter_required = TRUE
proposal_acceptance_boundary = MATERIAL
architectural_novelty = OPEN
```

Next test:

> Perform the same real-source substitution for **evidence/provenance** and **authority**, where the strongest known providers are W3C PROV/Rekor and UCAN/GitHub rulesets respectively.
