#!/usr/bin/env python3
"""Verify typed dependency closure against a pinned, real Stripe OpenAPI spec.

This runner downloads only the public specification document. It never calls
Stripe API operations and never uses credentials. The exact Git commit and
canonical Git blob SHA-1 are pinned below for reproducibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.request
from dataclasses import replace
from pathlib import Path
from typing import Any

from typed_contract_closure import (
    ALGORITHM_VERSION,
    SCHEMA_VERSION,
    Operation,
    Slot,
    contract_from_openapi,
    parse_openapi_json,
    plan_closure,
)

SOURCE_REPOSITORY = "stripe/openapi"
SOURCE_COMMIT = "51610f5f061c9723730582a7638b8cc0e646640d"
SOURCE_PATH = "latest/openapi.spec3.json"
SOURCE_GIT_BLOB_SHA1 = "9270d090ab4961efd0eb1a751410d210af929e99"
SOURCE_LICENSE = "MIT"
SOURCE_URL = (
    "https://raw.githubusercontent.com/stripe/openapi/"
    f"{SOURCE_COMMIT}/{SOURCE_PATH}"
)
MAX_SPEC_BYTES = 20 * 1024 * 1024


def fetch_pinned_spec(timeout: int = 60) -> bytes:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Machine-Typed-Contract-Closure/0.2", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(MAX_SPEC_BYTES + 1)
    if len(raw) > MAX_SPEC_BYTES:
        raise ValueError(f"OpenAPI spec exceeds {MAX_SPEC_BYTES} byte safety limit")
    return raw


def _operation(document: dict[str, Any], path: str, method: str) -> Operation:
    return contract_from_openapi(
        document, path, method,
        source=f"{SOURCE_REPOSITORY}@{SOURCE_COMMIT}:{SOURCE_PATH}",
    )


def _required_customer_id_slot(operation: Operation, *, output: bool) -> Slot:
    slots = operation.outputs if output else operation.required_inputs
    matches = [slot for slot in slots if slot.semantic_id == "customer.id"]
    if len(matches) != 1:
        kind = "guaranteed output" if output else "required input"
        raise AssertionError(
            f"expected exactly one customer.id {kind} in {operation.operation_id}; "
            f"found {[slot.semantic_id for slot in slots]}"
        )
    return matches[0]


def evaluate(raw: bytes) -> dict[str, Any]:
    document = parse_openapi_json(raw, expected_git_blob_sha1=SOURCE_GIT_BLOB_SHA1)
    source_sha256 = hashlib.sha256(raw).hexdigest()
    created = _operation(document, "/v1/customers", "post")
    retrieved = _operation(document, "/v1/customers/{customer}", "get")

    produced_customer_id = _required_customer_id_slot(created, output=True)
    consumed_customer_id = _required_customer_id_slot(retrieved, output=False)
    if produced_customer_id.schema.get("type") != "string":
        raise AssertionError("Stripe customer resource ID is not declared as a string output")
    if consumed_customer_id.schema.get("type") != "string":
        raise AssertionError("Stripe retrieve-customer path parameter is not declared as a string")
    if consumed_customer_id.evidence != "description":
        raise AssertionError(
            "expected documented description evidence for the customer path parameter; "
            f"got {consumed_customer_id.evidence!r}"
        )
    if produced_customer_id.evidence != "resource_ref":
        raise AssertionError(
            "expected a response-schema resource reference for customer.id; "
            f"got {produced_customer_id.evidence!r}"
        )
    if not created.security_alternatives or not retrieved.security_alternatives:
        raise AssertionError("expected both real Stripe operations to declare security requirements")

    operations = {created.operation_id: created, retrieved.operation_id: retrieved}
    authenticated_anchor = {"auth_schemes": ["bearerAuth"]}
    complete = plan_closure(retrieved.operation_id, operations, authenticated_anchor)
    if complete.status != "COMPLETE_INFERRED":
        raise AssertionError(f"expected COMPLETE_INFERRED; got {complete.to_dict()}")
    if complete.operation_order != (created.operation_id, retrieved.operation_id):
        raise AssertionError(f"unexpected provider/consumer order: {complete.operation_order}")
    if len(complete.dependencies) != 1:
        raise AssertionError(f"expected one documented customer ID dependency: {complete.dependencies}")

    # A stricter mode refuses documented inference where the upstream spec has
    # no explicit x-semantic-id guarantee.
    strict = plan_closure(
        retrieved.operation_id, operations, authenticated_anchor, require_explicit=True
    )
    if strict.status != "INCOMPLETE":
        raise AssertionError(f"strict semantic-ID mode must not accept inferred links: {strict.to_dict()}")

    # Mutate only the consumer type: same semantic ID must not hide a mismatch.
    wrong_input = replace(consumed_customer_id, schema={"type": "integer"})
    wrong_retrieval = replace(
        retrieved,
        required_inputs=tuple(
            wrong_input if item is consumed_customer_id else item
            for item in retrieved.required_inputs
        ),
    )
    type_mismatch = plan_closure(
        wrong_retrieval.operation_id,
        {created.operation_id: created, wrong_retrieval.operation_id: wrong_retrieval},
        authenticated_anchor,
    )
    if type_mismatch.status != "INCOMPLETE" or not any(
        issue.get("kind") == "type_incompatible" for issue in type_mismatch.issues
    ):
        raise AssertionError(f"type mismatch mutation was not rejected: {type_mismatch.to_dict()}")

    # Missing credentials/auth schemes is a blocking external precondition.
    unauthenticated = plan_closure(retrieved.operation_id, operations, {})
    if unauthenticated.status != "INCOMPLETE" or not any(
        issue.get("kind") == "security_precondition_missing" for issue in unauthenticated.issues
    ):
        raise AssertionError(f"security precondition was not enforced: {unauthenticated.to_dict()}")

    # The name 'customer' itself is not enough: remove its descriptive evidence.
    no_description_input = replace(consumed_customer_id, semantic_id=None, evidence="unknown", description="")
    undocumented_retrieval = replace(
        retrieved,
        required_inputs=tuple(
            no_description_input if item is consumed_customer_id else item
            for item in retrieved.required_inputs
        ),
    )
    name_only = plan_closure(
        undocumented_retrieval.operation_id,
        {created.operation_id: created, undocumented_retrieval.operation_id: undocumented_retrieval},
        authenticated_anchor,
    )
    if name_only.status != "INCOMPLETE":
        raise AssertionError(f"name-only semantic link was accepted: {name_only.to_dict()}")

    return {
        "schema": SCHEMA_VERSION,
        "algorithm": ALGORITHM_VERSION,
        "source": {
            "repository": SOURCE_REPOSITORY,
            "commit": SOURCE_COMMIT,
            "path": SOURCE_PATH,
            "url": SOURCE_URL,
            "git_blob_sha1_expected_and_verified": SOURCE_GIT_BLOB_SHA1,
            "sha256": source_sha256,
            "bytes": len(raw),
            "license": SOURCE_LICENSE,
            "license_url": f"https://github.com/{SOURCE_REPOSITORY}/blob/{SOURCE_COMMIT}/LICENSE",
        },
        "operations": [
            {
                "operation_id": operation.operation_id,
                "method": operation.method,
                "path": operation.path,
                "security_alternatives": [list(value) for value in operation.security_alternatives],
                "required_inputs": [
                    {
                        "name": slot.name,
                        "semantic_id": slot.semantic_id,
                        "evidence": slot.evidence,
                        "schema": dict(slot.schema),
                        "description": slot.description,
                    }
                    for slot in operation.required_inputs
                ],
                "guaranteed_outputs": [
                    {
                        "name": slot.name,
                        "semantic_id": slot.semantic_id,
                        "evidence": slot.evidence,
                        "schema": dict(slot.schema),
                    }
                    for slot in operation.outputs
                ],
            }
            for operation in (created, retrieved)
        ],
        "checks": {
            "pinned_git_blob_integrity": "PASS",
            "documented_customer_id_link": "PASS",
            "all_required_inputs_closed": "PASS",
            "provider_before_consumer_order": "PASS",
            "strict_explicit_semantic_id_gate": "PASS_REJECTED_INFERENCE",
            "same_id_type_mismatch_mutation": "PASS_REJECTED",
            "missing_auth_precondition": "PASS_REJECTED",
            "name_only_similarity_mutation": "PASS_REJECTED",
        },
        "documented_inference_plan": complete.to_dict(),
        "strict_explicit_plan": strict.to_dict(),
        "type_mismatch_mutation": type_mismatch.to_dict(),
        "missing_auth_mutation": unauthenticated.to_dict(),
        "name_only_mutation": name_only.to_dict(),
        "claim_boundary": {
            "result": "EXPERIMENTALLY_SUPPORTED",
            "scope": "one real, pinned OpenAPI provider-consumer path in one API",
            "meaning": "The API documents a customer identifier output and describes a required path input as the ID of that customer; this is inferred semantic evidence, not an explicit machine-readable equivalence assertion.",
            "not_established": [
                "cross-provider compatibility",
                "successful live API execution",
                "commercial or legal obligation semantics",
                "authorization or credential validity",
                "complete OpenAPI/JSON Schema semantic interpretation",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("OPENAPI-CORPUS-RESULTS.json"))
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    started = time.perf_counter()
    raw = fetch_pinned_spec(args.timeout)
    result = evaluate(raw)
    result["runtime_seconds"] = round(time.perf_counter() - started, 6)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(args.output), "checks": result["checks"], "source_sha256": result["source"]["sha256"], "bytes": result["source"]["bytes"], "runtime_seconds": result["runtime_seconds"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
