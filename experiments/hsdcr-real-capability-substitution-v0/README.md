# HSDCR Real Capability Substitution v0.1

Status: **EXPERIMENT / CONTRACT-BOUND**

This test uses real source observations rather than simulated provider objects.

Sources:
- GitHub: `Loofy147/Machine`, open PR #10 and its actual branch/commit identity.
- AT Protocol: public `bsky.app` repository identity and a real public post record.

The purpose is narrow:

> Test whether a real GitHub contribution proposal can be replaced by a native AT Protocol repository record while preserving the candidate boundary "contribution exists without canonical acceptance".

## Expected result

**PARTIAL_SUBSTITUTION / ADAPTER_REQUIRED**

The GitHub PR is open and unmerged, so the proposed head and canonical base remain distinct.

The cited AT Protocol post is a repository record. AT Protocol's repository specification says repository mutations produce signed commits in the author's repository. The record itself is therefore not a native proposal-before-acceptance object. See:

- https://atproto.com/specs/repository
- https://atproto.com/specs/sync
- https://atproto.com/guides/sync

The test deliberately refuses to invent an AT proposal state.

## What this establishes

It establishes a concrete substitution boundary:

```
GitHub PR
  !=
AT repository record
```

for the specific candidate semantic:

```
proposal exists
AND
canonical acceptance has not occurred
```

An application can certainly build proposal semantics on top of AT Protocol. That would be an added application-level layer, which is exactly the architectural boundary this experiment is intended to expose.

## Run

```sh
python3 run.py
```

The expected terminal result is a PASS for the *collision test*, with semantic equivalence reported as false.

This is not a benchmark of GitHub versus AT Protocol and not a claim about the overall capabilities of either system.
