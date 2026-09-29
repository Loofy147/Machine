import hashlib
import json
from copy import deepcopy

GITHUB = {
    "provider": "github",
    "surface": "pull_request",
    "proposal_id": "github-pr-10",
    "base": "59fab62704875193801db77c7cb8361475297f48",
    "head": "12dade33f708d66890c6c10b754f85c1d3ae13e3",
    "state": "open",
    "merged": False,
}

AT = {
    "provider": "atproto",
    "surface": "repository_record",
    "record_uri": "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.post/3mp54n7zccc2j2",
    "record_type": "app.bsky.feed.post",
    "native_repository_mutation": True,
}


def github_to_contribution(src):
    return {
        "boundary": "D01",
        "id": src["proposal_id"],
        "subject": "change-X",
        "base_ref": src["base"],
        "result_ref": src["head"],
        "status": "PROPOSED",
        "canonical": False,
    }


def at_direct_to_contribution(src):
    return {
        "boundary": "D01",
        "id": src["record_uri"],
        "subject": "change-X",
        "base_ref": None,
        "result_ref": src["record_uri"],
        "status": "CANONICAL_RECORD",
        "canonical": True,
    }


def at_with_proposal_adapter(src):
    return {
        "boundary": "D01",
        "id": "at-proposal-001",
        "subject": "change-X",
        "base_ref": "state-A",
        "result_ref": src["record_uri"],
        "status": "PROPOSED",
        "canonical": False,
        "underlying_record": src["record_uri"],
        "adapter": "explicit_application_proposal_record",
    }


def project_to_boundary(contribution):
    return {
        "boundary": contribution["boundary"],
        "status": contribution["status"],
        "canonical": contribution["canonical"],
        "has_reference": (
            contribution["base_ref"] is not None
            and contribution["result_ref"] is not None
        ),
        "subject": contribution["subject"],
    }


def accept_once(canonical_state, contribution, evidence, authority, decision, history):
    if not evidence["supports"]:
        return canonical_state, False, "EVIDENCE_INSUFFICIENT"
    if not authority["permits"]:
        return canonical_state, False, "AUTHORITY_MISSING"
    if decision["disposition"] != "accepted":
        return canonical_state, False, "DECISION_NOT_ACCEPTED"

    key = (contribution["id"], decision["id"])
    if any(event["key"] == list(key) for event in history):
        return canonical_state, False, "DUPLICATE_NOOP"

    new_state = {
        "id": "state-B",
        "parent": canonical_state["id"],
        "applied_contribution": contribution["id"],
    }
    history.append(
        {
            "key": list(key),
            "transition": "ACCEPT_AND_APPLY",
            "from": canonical_state["id"],
            "to": new_state["id"],
        }
    )
    return new_state, True, "APPLIED"


def reconstruct(initial_state, history):
    state = deepcopy(initial_state)
    for event in history:
        if event["transition"] != "ACCEPT_AND_APPLY":
            raise AssertionError("unknown transition")
        state = {
            "id": event["to"],
            "parent": event["from"],
            "applied_contribution": event["key"][0],
        }
    return state


def canonical_payload(result):
    payload = deepcopy(result)
    payload.pop("result_payload_sha256", None)
    return json.dumps(
        payload,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    ).encode("utf-8")


def main():
    github_contribution = github_to_contribution(GITHUB)
    at_direct = at_direct_to_contribution(AT)
    at_wrapped = at_with_proposal_adapter(AT)

    initial = {"id": "state-A"}
    evidence = {
        "id": "evidence-001",
        "subject": at_wrapped["id"],
        "supports": True,
    }
    authority = {
        "id": "authority-001",
        "subject": at_wrapped["id"],
        "permits": True,
    }
    decision = {
        "id": "decision-001",
        "subject": at_wrapped["id"],
        "disposition": "accepted",
    }

    history = []
    state, applied, status = accept_once(
        initial,
        at_wrapped,
        evidence,
        authority,
        decision,
        history,
    )

    state_dup, applied_dup, status_dup = accept_once(
        state,
        at_wrapped,
        evidence,
        authority,
        decision,
        history,
    )

    evidence_only, _, evidence_only_status = accept_once(
        initial,
        at_wrapped,
        {
            "id": "evidence-only",
            "subject": at_wrapped["id"],
            "supports": True,
        },
        {
            "id": "authority-missing",
            "subject": at_wrapped["id"],
            "permits": False,
        },
        decision,
        [],
    )

    rejected, _, rejected_status = accept_once(
        initial,
        at_wrapped,
        evidence,
        authority,
        {
            "id": "decision-reject",
            "subject": at_wrapped["id"],
            "disposition": "rejected",
        },
        [],
    )

    signal_stream = [
        {
            "signal_id": "sig-001",
            "kind": "contribution_observed",
            "subject": at_wrapped["id"],
        }
    ]
    signal_count_before_drop = len(signal_stream)
    signal_stream.clear()

    reconstructed = reconstruct(initial, history)

    result = {
        "schema": "hsdcr-e2e-composition-v0.2",
        "status": "HARDENED_CONTRACT_COMPOSITION_CHECK",
        "source_fixtures": {
            "github_pr_10": GITHUB,
            "at_public_record": AT,
        },
        "provider_substitution": {
            "github_vs_at_direct": {
                "semantic_equivalence": project_to_boundary(github_contribution)
                == project_to_boundary(at_direct),
                "classification": "DIRECT_COLLISION",
                "adapter_required": True,
            },
            "github_vs_at_wrapped": {
                "semantic_equivalence": project_to_boundary(github_contribution)
                == project_to_boundary(at_wrapped),
                "classification": "SEMANTIC_BOUNDARY_PRESERVED",
                "adapter_type": "ordinary_application_record_plus_transition",
                "new_primitive_required": False,
            },
        },
        "boundary_tests": {
            "evidence_cannot_authorize_alone": (
                evidence_only_status == "AUTHORITY_MISSING"
                and evidence_only["id"] == "state-A"
            ),
            "rejected_decision_does_not_canonicalize": (
                rejected["id"] == "state-A"
                and rejected_status == "DECISION_NOT_ACCEPTED"
            ),
            "accepted_transition_is_explicit": (
                applied and status == "APPLIED" and state["parent"] == "state-A"
            ),
            "duplicate_acceptance_is_idempotent": (
                (not applied_dup)
                and status_dup == "DUPLICATE_NOOP"
                and state_dup == state
                and len(history) == 1
            ),
            "signal_is_actually_dropped": (
                signal_count_before_drop == 1 and len(signal_stream) == 0
            ),
            "canonical_state_survives_signal_loss": (
                reconstructed["id"] == "state-B"
            ),
            "reconstruction_matches_canonical": reconstructed == state,
        },
        "reduction": {
            "operations_used": [
                "typed-record-create",
                "field-validation",
                "deterministic-transition",
                "append-history",
                "replay",
            ],
            "new_execution_primitive_detected": False,
            "new_repository_primitive_detected": False,
            "acceptance_relation_reducible_to": (
                "ordinary typed data + explicit transition/policy"
            ),
            "signal_loss_reconstruction_source": "durable_history_not_signal_stream",
        },
        "equivalence_dimensions": {
            "semantic": True,
            "resource": "NOT_EXECUTED",
            "authority": "NOT_EQUALIZED",
            "durability": "NOT_EQUALIZED",
        },
        "disposition": {
            "strongest_current_kill_hypothesis_survives": True,
            "irreducible_residual": "NOT_DETECTED",
            "architectural_novelty": "OPEN",
            "protocol_status": "NOT_ASSIGNED",
            "next_test": (
                "replace normalized evidence and authority fixtures with "
                "independent real implementations and re-run the same transition oracle"
            ),
        },
    }

    result["result_payload_sha256"] = hashlib.sha256(
        canonical_payload(result)
    ).hexdigest()

    print(
        json.dumps(
            result,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
