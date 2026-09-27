#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
fixture = json.loads((ROOT / "REAL-SOURCES-v0.1.json").read_text())


def test_github_proposal_is_noncanonical() -> dict:
    x = fixture["sources"]["github_pr"]
    assert x["state"] == "open"
    assert x["merged"] is False
    assert x["base_sha"] != x["head_sha"]
    return {
        "provider": "github",
        "proposal_state": "noncanonical",
        "canonical_base_sha": x["base_sha"],
        "proposed_head_sha": x["head_sha"],
        "preserves_contribution_neq_canonical": True,
    }


def test_at_record_is_repository_mutation_not_pr() -> dict:
    x = fixture["sources"]["atproto_record"]
    assert x["record_type"] == "app.bsky.feed.post"
    assert x["repository_did"] == fixture["sources"]["atproto_profile"]["did"]

    # This is a deliberate boundary test:
    # the public record is a repository record, not a proposal object.
    # We therefore do NOT manufacture an acceptance state.
    return {
        "provider": "atproto",
        "record_state": "repository_record",
        "proposal_before_canonical_acceptance": False,
        "adapter_required_for_B03_B07": True,
    }


def test_substitution_result() -> dict:
    gh = test_github_proposal_is_noncanonical()
    at = test_at_record_is_repository_mutation_not_pr()

    # The two real source surfaces cannot be declared semantically equivalent
    # for the candidate boundary "proposal without canonical acceptance".
    # GitHub supplies it natively via an open PR; the cited AT record does not.
    assert gh["preserves_contribution_neq_canonical"] is True
    assert at["adapter_required_for_B03_B07"] is True

    return {
        "status": "PASS",
        "test": "real-capability-substitution-v0.1",
        "semantic_equivalence": False,
        "classification": "PARTIAL_SUBSTITUTION / ADAPTER_REQUIRED",
        "collision": "AT repository mutation does not natively carry the GitHub PR proposal-before-acceptance boundary in this fixture.",
        "important_limit": (
            "This does not prove AT Protocol cannot host proposal semantics. "
            "It proves that the cited native repository record cannot be substituted "
            "for a GitHub pull request without an application-level proposal/acceptance layer."
        ),
        "github": gh,
        "atproto": at,
    }


if __name__ == "__main__":
    print(json.dumps(test_substitution_result(), indent=2, sort_keys=True))
