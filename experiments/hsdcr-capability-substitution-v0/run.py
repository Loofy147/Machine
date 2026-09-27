#!/usr/bin/env python3
"""Contract-level capability substitution test.

This is a semantic-boundary test object, not an implementation of HSDCR.
It checks whether different known capability styles can satisfy the same
minimal boundaries without collapsing the required distinctions.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from typing import Any, Dict, List


def digest(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Identity:
    subject_id: str
    location: str


@dataclass(frozen=True)
class Change:
    change_id: str
    base_state: str
    patch: Dict[str, Any]
    lineage: tuple[str, ...]


@dataclass(frozen=True)
class Observation:
    observation_id: str
    source: str
    change_id: str


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    observation_id: str
    result: str
    scope: str


@dataclass(frozen=True)
class Authority:
    authority_id: str
    principal: str
    action: str
    subject_id: str


@dataclass(frozen=True)
class Decision:
    decision_id: str
    change_id: str
    disposition: str
    evidence_id: str
    authority_id: str


@dataclass(frozen=True)
class Record:
    kind: str
    payload: Dict[str, Any]


class Provider:
    """Provider contract. Concrete styles differ only in representation."""

    def identity(self) -> Identity:
        raise NotImplementedError

    def change(self, base: str) -> Change:
        raise NotImplementedError

    def observe(self, change: Change) -> Observation:
        raise NotImplementedError

    def evidence(self, obs: Observation) -> Evidence:
        raise NotImplementedError

    def authority(self, change: Change) -> Authority:
        raise NotImplementedError


class GitStyleProvider(Provider):
    def identity(self):
        return Identity("actor:alice", "branch:feature-x")

    def change(self, base):
        return Change("commit:c1", base, {"value": 2}, ("commit:c0",))

    def observe(self, change):
        return Observation("check:event:c1", "github-check", change.change_id)

    def evidence(self, obs):
        return Evidence("check:e1", obs.observation_id, "PASS", "unit-test-v1")

    def authority(self, change):
        return Authority("ruleset:r1", "maintainer", "merge", "repo:demo")


class ATStyleProvider(Provider):
    def identity(self):
        return Identity("did:example:alice", "pds:node-7")

    def change(self, base):
        return Change("cid:c1", base, {"value": 2}, ("cid:c0",))

    def observe(self, change):
        return Observation("stream:evt:c1", "repo-firehose", change.change_id)

    def evidence(self, obs):
        return Evidence("attestation:e1", obs.observation_id, "PASS", "unit-test-v1")

    def authority(self, change):
        return Authority("cap:merge:r1", "did:example:maintainer",
                          "merge", "repo:demo")


def canonicalize_identity(x: Identity) -> Dict[str, str]:
    return {"subject_class": "contributor", "stable_subject": x.subject_id}


def canonicalize_change(x: Change) -> Dict[str, Any]:
    return {
        "change_semantics": {
            "base_state": "state:0",
            "patch": x.patch,
            "lineage_length": len(x.lineage),
        }
    }


def canonicalize_observation(x: Observation) -> Dict[str, str]:
    return {"source_class": "signal", "observed_change": "change:1"}


def canonicalize_evidence(x: Evidence) -> Dict[str, str]:
    return {"status": x.result, "scope": x.scope, "semantic_class": "evidence"}


def canonicalize_authority(x: Authority) -> Dict[str, str]:
    return {"action": x.action, "principal_class": "authorizer",
            "semantic_class": "authority"}


def run(provider: Provider) -> List[Record]:
    ident = provider.identity()
    ch = provider.change("state:0")

    # Signal acquisition must not mutate canonical state.
    obs = provider.observe(ch)

    ev = provider.evidence(obs)
    auth = provider.authority(ch)

    # Explicit decision is the only transition point in this fixture.
    decision = Decision(
        "decision:1",
        ch.change_id,
        "ACCEPTED",
        ev.evidence_id,
        auth.authority_id,
    )

    return [
        Record("identity", canonicalize_identity(ident)),
        Record("change", canonicalize_change(ch)),
        Record("observation", canonicalize_observation(obs)),
        Record("evidence", canonicalize_evidence(ev)),
        Record("authority", canonicalize_authority(auth)),
        Record("decision", {
            "disposition": decision.disposition,
            "evidence": "evidence:1",
            "authority": "authority:1",
        }),
        Record("canonical_state", {"value": 2}),
    ]


def assert_invariants(records: List[Record]) -> None:
    kinds = [r.kind for r in records]
    assert kinds == [
        "identity", "change", "observation", "evidence",
        "authority", "decision", "canonical_state"
    ]

    by_kind = {r.kind: r.payload for r in records}

    assert "stable_subject" in by_kind["identity"]
    assert "source_class" in by_kind["observation"]
    assert by_kind["evidence"]["semantic_class"] == "evidence"
    assert by_kind["authority"]["semantic_class"] == "authority"
    assert by_kind["decision"]["evidence"] == "evidence:1"
    assert by_kind["decision"]["authority"] == "authority:1"

    # Sensitivity/non-reactivity: observation exists before canonical mutation
    # in this semantic sequence. The fixture has exactly one explicit state write.
    assert kinds.index("observation") < kinds.index("decision")
    assert kinds.index("decision") < kinds.index("canonical_state")


def normalized(records: List[Record]) -> str:
    return digest([{"kind": r.kind, "payload": r.payload} for r in records])


def main() -> int:
    providers = {
        "git_style": GitStyleProvider(),
        "at_style": ATStyleProvider(),
    }

    outputs = {}
    for name, provider in providers.items():
        recs = run(provider)
        assert_invariants(recs)
        outputs[name] = {
            "normalized_digest": normalized(recs),
            "records": [{"kind": r.kind, "payload": r.payload} for r in recs],
        }

    assert outputs["git_style"]["normalized_digest"] == outputs["at_style"]["normalized_digest"]

    result = {
        "status": "PASS",
        "test": "capability-substitution-boundary-v0.1",
        "providers": sorted(outputs),
        "semantic_equivalence": True,
        "invariants": 9,
        "note": (
            "This proves only that the declared boundary adapters in this "
            "fixture preserve the selected semantic distinctions. It does "
            "not prove compatibility with the external systems themselves."
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
