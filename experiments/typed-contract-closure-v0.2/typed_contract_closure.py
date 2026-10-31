#!/usr/bin/env python3
"""Typed OpenAPI contract compatibility and dependency-closure planner.

This module is an offline verifier. It does not invoke operations, hold
credentials, or treat inferred semantic links as execution authorization.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Mapping


SCHEMA_VERSION = "typed-contract-closure.v0.2"
ALGORITHM_VERSION = "bounded-min-cost-depth-first-closure.v0.2.2"
_METHODS = {"get", "put", "post", "delete", "patch", "options", "head", "trace"}
_ENTITY_NAMES = (
    "payment_intent", "invoice_item", "customer", "invoice", "subscription",
    "payment_method", "product", "price", "account", "charge", "transfer",
    "refund", "balance_transaction", "file", "order", "shipment", "contract",
)


@dataclass(frozen=True)
class Slot:
    name: str
    semantic_id: str | None
    schema: Mapping[str, Any]
    required: bool = True
    evidence: str = "unknown"
    source_path: str = ""
    description: str = ""


@dataclass(frozen=True)
class Operation:
    operation_id: str
    method: str
    path: str
    required_inputs: tuple[Slot, ...] = ()
    outputs: tuple[Slot, ...] = ()
    security_alternatives: tuple[tuple[str, ...], ...] = ()
    cost: int = 1
    source: str = ""
    contract_issues: tuple[Mapping[str, Any], ...] = ()

    def __post_init__(self) -> None:
        if not self.operation_id:
            raise ValueError("operation_id must not be empty")
        if self.method.lower() not in _METHODS:
            raise ValueError(f"unsupported HTTP method: {self.method}")
        if type(self.cost) is not int or self.cost < 0:
            raise ValueError("cost must be a non-negative integer")


@dataclass(frozen=True)
class Compatibility:
    status: str
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ClosureResult:
    status: str
    target: str
    operation_order: tuple[str, ...]
    dependencies: tuple[Mapping[str, Any], ...]
    anchored_inputs: tuple[Mapping[str, Any], ...]
    missing_inputs: tuple[Slot, ...]
    issues: tuple[Mapping[str, Any], ...]
    total_cost: int
    input_digest_sha256: str
    expansions: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA_VERSION,
            "algorithm": ALGORITHM_VERSION,
            "status": self.status,
            "feasible": self.status in {"COMPLETE_EXPLICIT", "COMPLETE_INFERRED", "FEASIBLE_SEARCH_LIMIT"},
            "optimality_proven": self.status in {"COMPLETE_EXPLICIT", "COMPLETE_INFERRED"},
            "target": self.target,
            "operation_order": list(self.operation_order),
            "dependencies": [dict(item) for item in self.dependencies],
            "anchored_inputs": [dict(item) for item in self.anchored_inputs],
            "missing_inputs": [
                {"name": s.name, "semantic_id": s.semantic_id, "schema": dict(s.schema),
                 "source_path": s.source_path, "description": s.description}
                for s in self.missing_inputs
            ],
            "issues": [dict(item) for item in self.issues],
            "total_cost": self.total_cost,
            "input_digest_sha256": self.input_digest_sha256,
            "search_expansions": self.expansions,
        }


def _resolve_ref(document: Mapping[str, Any], schema: Mapping[str, Any], seen: frozenset[str] = frozenset()) -> Mapping[str, Any]:
    ref = schema.get("$ref") if isinstance(schema, Mapping) else None
    if not isinstance(ref, str):
        return schema
    if not ref.startswith("#/") or ref in seen:
        return {"x-unresolved-ref": ref}
    current: Any = document
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, Mapping) or part not in current:
            return {"x-unresolved-ref": ref}
        current = current[part]
    if not isinstance(current, Mapping):
        return {"x-unresolved-ref": ref}
    resolved = _resolve_ref(document, current, seen | {ref})
    if len(schema) > 1:
        merged = dict(resolved)
        merged.update({key: value for key, value in schema.items() if key != "$ref"})
        return merged
    return resolved



def _json_value_type(value: Any) -> str:
    if value is None:
        return "null"
    if type(value) is bool:
        return "boolean"
    if type(value) is int:
        return "integer"
    if type(value) is float:
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, Mapping):
        return "object"
    if isinstance(value, list):
        return "array"
    return "unknown"


def _types(schema: Mapping[str, Any]) -> frozenset[str]:
    """Return a conservative set of JSON value types admitted by a schema.

    anyOf/oneOf contribute a union, allOf contributes an intersection, and a
    sibling ``type`` constraint intersects with the union. Null is first-class
    so nullable values cannot accidentally satisfy non-null consumers.
    """
    if not isinstance(schema, Mapping):
        return frozenset()
    value = schema.get("type")
    if isinstance(value, str):
        declared = frozenset((value,))
    elif isinstance(value, list):
        declared = frozenset(item for item in value if isinstance(item, str))
    elif "properties" in schema or "required" in schema:
        declared = frozenset(("object",))
    elif "items" in schema:
        declared = frozenset(("array",))
    elif isinstance(schema.get("enum"), list):
        declared = frozenset(_json_value_type(item) for item in schema["enum"] if _json_value_type(item) != "unknown")
    elif "const" in schema:
        inferred = _json_value_type(schema["const"])
        declared = frozenset((inferred,)) if inferred != "unknown" else frozenset()
    else:
        declared = frozenset()

    branches = schema.get("anyOf") or schema.get("oneOf")
    if isinstance(branches, list):
        branch_types = [_types(branch) for branch in branches if isinstance(branch, Mapping)]
        if len(branch_types) != len(branches) or not branch_types:
            return frozenset()
        union = frozenset().union(*branch_types)
        result = union if not declared else union & declared
    else:
        result = declared

    all_of = schema.get("allOf")
    if isinstance(all_of, list):
        branch_types = [_types(branch) for branch in all_of if isinstance(branch, Mapping)]
        if len(branch_types) != len(all_of) or not branch_types:
            return frozenset()
        constrained = [types for types in branch_types if types]
        intersection = set(constrained[0]) if constrained else set(result)
        for types in constrained[1:]:
            intersection.intersection_update(types)
        if result:
            intersection.intersection_update(result)
        result = frozenset(intersection)

    if schema.get("nullable") is True or (isinstance(schema.get("enum"), list) and None in schema["enum"]):
        result = result | frozenset(("null",))
    return frozenset(result)


def _json_value_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _enum_values(schema: Mapping[str, Any]) -> tuple[Any, ...] | None:
    if isinstance(schema.get("enum"), list):
        return tuple(schema["enum"])
    if "const" in schema:
        return (schema["const"],)
    branches = schema.get("anyOf") or schema.get("oneOf")
    if isinstance(branches, list) and branches:
        values: list[Any] = []
        for branch in branches:
            if not isinstance(branch, Mapping):
                return None
            enum = _enum_values(branch)
            if enum is None:
                return None
            values.extend(enum)
        unique = {_json_value_key(value): value for value in values}
        return tuple(unique[key] for key in sorted(unique))
    all_of = schema.get("allOf")
    if isinstance(all_of, list) and all_of:
        enum_sets = [_enum_values(branch) for branch in all_of if isinstance(branch, Mapping)]
        if any(enum is not None for enum in enum_sets):
            known_sets = [enum for enum in enum_sets if enum is not None]
            smallest = min(known_sets, key=len)
            common = {_json_value_key(value): value for value in smallest}
            for enum in known_sets:
                allowed = {_json_value_key(value) for value in enum}
                common = {key: value for key, value in common.items() if key in allowed}
            return tuple(common[key] for key in sorted(common))
    return None



def _shape_unknown(schema: Mapping[str, Any]) -> bool:
    return bool(schema.get("x-unresolved-ref")) or not _types(schema)


def _type_accepts(consumer_type: str, producer_type: str) -> bool:
    if consumer_type == producer_type:
        return True
    return consumer_type == "number" and producer_type == "integer"


def _numeric_bound(schema: Mapping[str, Any], side: str) -> tuple[float | int | None, bool] | None:
    """Return (value, exclusive); None means unbounded, invalid means None tuple."""
    inclusive_key = "minimum" if side == "lower" else "maximum"
    exclusive_key = "exclusiveMinimum" if side == "lower" else "exclusiveMaximum"
    inclusive = schema.get(inclusive_key)
    exclusive = schema.get(exclusive_key)
    if isinstance(exclusive, bool):
        if exclusive and inclusive is None:
            return None
        if inclusive is not None and (isinstance(inclusive, bool) or not isinstance(inclusive, (int, float))):
            return None
        return (inclusive, exclusive) if inclusive is not None else (None, False)
    if exclusive is not None and (isinstance(exclusive, bool) or not isinstance(exclusive, (int, float))):
        return None
    if inclusive is not None and (isinstance(inclusive, bool) or not isinstance(inclusive, (int, float))):
        return None
    candidates: list[tuple[float | int, bool]] = []
    if inclusive is not None:
        candidates.append((inclusive, False))
    if exclusive is not None:
        candidates.append((exclusive, True))
    if not candidates:
        return (None, False)
    return max(candidates, key=lambda item: (item[0], item[1])) if side == "lower" else min(candidates, key=lambda item: (item[0], not item[1]))


def _numeric_bounds_compatible(producer: Mapping[str, Any], consumer: Mapping[str, Any]) -> Compatibility:
    for side in ("lower", "upper"):
        consumer_bound = _numeric_bound(consumer, side)
        producer_bound = _numeric_bound(producer, side)
        if consumer_bound is None or producer_bound is None:
            return Compatibility("UNKNOWN", (f"invalid_{side}_numeric_bound",))
        c_value, c_exclusive = consumer_bound
        p_value, p_exclusive = producer_bound
        if c_value is None:
            continue
        if p_value is None:
            return Compatibility("UNKNOWN", (f"producer_{side}_numeric_bound_unspecified",))
        if side == "lower":
            if p_value < c_value or (p_value == c_value and c_exclusive and not p_exclusive):
                return Compatibility("INCOMPATIBLE", ("producer_numeric_lower_bound_too_weak",))
        else:
            if p_value > c_value or (p_value == c_value and c_exclusive and not p_exclusive):
                return Compatibility("INCOMPATIBLE", ("producer_numeric_upper_bound_too_weak",))
    return Compatibility("SUPPORTED", ("numeric_bounds_compatible",))


def _object_compatibility(producer: Mapping[str, Any], consumer: Mapping[str, Any]) -> Compatibility:
    if any(key in producer or key in consumer for key in ("allOf", "anyOf", "oneOf")):
        return Compatibility("UNKNOWN", ("composed_object_schema_not_fully_interpreted",))
    producer_properties = producer.get("properties", {})
    consumer_properties = consumer.get("properties", {})
    if not isinstance(producer_properties, Mapping) or not isinstance(consumer_properties, Mapping):
        return Compatibility("UNKNOWN", ("object_properties_not_mapping",))
    producer_required = producer.get("required", [])
    consumer_required = consumer.get("required", [])
    if not isinstance(producer_required, list) or not isinstance(consumer_required, list):
        return Compatibility("UNKNOWN", ("object_required_not_list",))
    if not set(consumer_required).issubset(set(producer_required)):
        return Compatibility("INCOMPATIBLE", ("producer_does_not_guarantee_consumer_required_properties",))

    provider_additional = producer.get("additionalProperties", True)
    consumer_additional = consumer.get("additionalProperties", True)

    # For each property understood by the consumer, prove that any value the
    # producer could emit at that key is accepted. Optional does not mean
    # unconstrained when a producer may still include the property.
    for name, accepted_schema in consumer_properties.items():
        if not isinstance(accepted_schema, Mapping):
            return Compatibility("UNKNOWN", (f"consumer_property_schema_unknown:{name}",))
        provider_schema = producer_properties.get(name)
        if isinstance(provider_schema, Mapping):
            result = schema_compatibility(provider_schema, accepted_schema)
            if result.status != "SUPPORTED":
                return Compatibility(result.status, (f"property:{name}", *result.reasons))
        elif provider_additional is False:
            if name in consumer_required:
                return Compatibility("INCOMPATIBLE", (f"provider_cannot_supply_required_property:{name}",))
        elif isinstance(provider_additional, Mapping):
            result = schema_compatibility(provider_additional, accepted_schema)
            if result.status != "SUPPORTED":
                return Compatibility(result.status, (f"additional_property:{name}", *result.reasons))
        else:
            return Compatibility("UNKNOWN", (f"provider_property_domain_unbounded:{name}",))

    # Producer-defined properties not declared by the consumer must be
    # accepted by the consumer's additionalProperties contract.
    for name, provider_schema in producer_properties.items():
        if name in consumer_properties:
            continue
        if not isinstance(provider_schema, Mapping):
            return Compatibility("UNKNOWN", (f"producer_property_schema_unknown:{name}",))
        if consumer_additional is False:
            return Compatibility("INCOMPATIBLE", (f"consumer_rejects_provider_property:{name}",))
        if isinstance(consumer_additional, Mapping):
            result = schema_compatibility(provider_schema, consumer_additional)
            if result.status != "SUPPORTED":
                return Compatibility(result.status, (f"additional_property:{name}", *result.reasons))

    if consumer_additional is False and provider_additional is not False:
        return Compatibility("INCOMPATIBLE", ("producer_may_emit_properties_rejected_by_consumer",))
    if isinstance(consumer_additional, Mapping):
        if provider_additional is False:
            pass
        elif isinstance(provider_additional, Mapping):
            result = schema_compatibility(provider_additional, consumer_additional)
            if result.status != "SUPPORTED":
                return Compatibility(result.status, ("additional_properties_schema", *result.reasons))
        else:
            return Compatibility("UNKNOWN", ("producer_additional_properties_unbounded",))
    return Compatibility("SUPPORTED", ("object_required_and_property_constraints_compatible",))


def schema_compatibility(producer_schema: Mapping[str, Any], consumer_schema: Mapping[str, Any]) -> Compatibility:
    """Check whether every value promised by a producer fits a consumer input.

    UNKNOWN is not accepted as a verified dependency. Only supported schema
    fragments are proved; constructs not fully interpreted remain blocked.
    """
    if not isinstance(producer_schema, Mapping) or not isinstance(consumer_schema, Mapping):
        return Compatibility("UNKNOWN", ("schema_not_object",))
    if dict(producer_schema) == dict(consumer_schema):
        return Compatibility("SUPPORTED", ("identical_schema",))
    producer_types = _types(producer_schema)
    consumer_types = _types(consumer_schema)
    if _shape_unknown(producer_schema) or _shape_unknown(consumer_schema):
        return Compatibility("UNKNOWN", ("type_or_reference_unresolved",))
    if not producer_types or not consumer_types:
        return Compatibility("UNKNOWN", ("type_not_declared",))
    if any(not any(_type_accepts(c, p) for c in consumer_types) for p in producer_types):
        return Compatibility("INCOMPATIBLE", ("json_type_mismatch",))

    producer_enum = _enum_values(producer_schema)
    consumer_enum = _enum_values(consumer_schema)
    if consumer_enum is not None:
        if producer_enum is None:
            return Compatibility("UNKNOWN", ("producer_enum_unbounded_for_restricted_consumer",))
        if not {_json_value_key(value) for value in producer_enum}.issubset({_json_value_key(value) for value in consumer_enum}):
            return Compatibility("INCOMPATIBLE", ("producer_enum_not_subset_of_consumer_enum",))

    consumer_format = consumer_schema.get("format")
    producer_format = producer_schema.get("format")
    if consumer_format and producer_format != consumer_format:
        if not producer_format:
            return Compatibility("UNKNOWN", ("producer_format_unspecified",))
        return Compatibility("INCOMPATIBLE", ("format_mismatch",))

    consumer_pattern = consumer_schema.get("pattern")
    producer_pattern = producer_schema.get("pattern")
    if consumer_pattern and producer_pattern != consumer_pattern:
        return Compatibility("UNKNOWN", ("pattern_implication_not_proven",))

    numeric_types = {"integer", "number"}
    if producer_types & numeric_types and consumer_types & numeric_types:
        numeric_result = _numeric_bounds_compatible(producer_schema, consumer_schema)
        if numeric_result.status != "SUPPORTED":
            return numeric_result

    for minimum, maximum in (("minLength", "maxLength"), ("minItems", "maxItems"), ("minProperties", "maxProperties")):
        if minimum in consumer_schema:
            provider_minimum = producer_schema.get(minimum)
            if provider_minimum is None:
                return Compatibility("UNKNOWN", (f"producer_{minimum}_unspecified",))
            if provider_minimum < consumer_schema[minimum]:
                return Compatibility("INCOMPATIBLE", (f"producer_{minimum}_below_consumer_bound",))
        if maximum in consumer_schema:
            provider_maximum = producer_schema.get(maximum)
            if provider_maximum is None:
                return Compatibility("UNKNOWN", (f"producer_{maximum}_unspecified",))
            if provider_maximum > consumer_schema[maximum]:
                return Compatibility("INCOMPATIBLE", (f"producer_{maximum}_above_consumer_bound",))

    if producer_types == frozenset(("array",)) and consumer_types == frozenset(("array",)):
        producer_items = producer_schema.get("items")
        consumer_items = consumer_schema.get("items")
        if isinstance(consumer_items, Mapping):
            if not isinstance(producer_items, Mapping):
                return Compatibility("UNKNOWN", ("producer_array_items_schema_unspecified",))
            item_result = schema_compatibility(producer_items, consumer_items)
            if item_result.status != "SUPPORTED":
                return item_result
        elif consumer_items is False:
            if producer_items is not False and producer_schema.get("maxItems") != 0:
                return Compatibility("INCOMPATIBLE", ("consumer_rejects_array_items",))
        elif consumer_items not in (None, True):
            return Compatibility("UNKNOWN", ("consumer_array_items_schema_unsupported",))

    if producer_types == frozenset(("object",)) and consumer_types == frozenset(("object",)):
        return _object_compatibility(producer_schema, consumer_schema)

    return Compatibility("SUPPORTED", ("producer_value_domain_within_consumer_domain",))


def _snake(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()


def _canonical_entity(value: str) -> str | None:
    candidate = _snake(value).rstrip("s")
    aliases = {"payment_intents": "payment_intent", "invoiceitems": "invoice_item", "paymentmethods": "payment_method"}
    candidate = aliases.get(_snake(value), candidate)
    if candidate in _ENTITY_NAMES:
        return candidate
    return None


def _canonical_resource_entity(value: str) -> str | None:
    normalized = _snake(value)
    if normalized.startswith("deleted_"):
        normalized = normalized[len("deleted_"):]
    return _canonical_entity(normalized)


def _response_resource_entities(
    document: Mapping[str, Any], operation: Mapping[str, Any]
) -> set[str] | None:
    """Return one unambiguous entity only when every 2xx JSON response names it.

    Response unions are supported when every branch resolves to the same
    canonical entity (e.g. customer | deleted_customer). Missing or mixed
    response contracts deliberately produce no inference.
    """
    responses = operation.get("responses")
    if not isinstance(responses, Mapping):
        return None
    success_schemas: list[Mapping[str, Any]] = []
    for code, raw_response in responses.items():
        if not re.fullmatch(r"2(?:\d\d|XX)", str(code), flags=re.IGNORECASE):
            continue
        if not isinstance(raw_response, Mapping):
            return None
        response = _resolve_ref(document, raw_response)
        if response.get("x-unresolved-ref"):
            return None
        schema = _content_schema(response.get("content"))
        if not isinstance(schema, Mapping):
            return None
        success_schemas.append(schema)
    if not success_schemas:
        return None

    def collect(schema: Mapping[str, Any], seen: frozenset[str] = frozenset()) -> set[str] | None:
        ref = schema.get("$ref")
        if isinstance(ref, str):
            prefix = "#/components/schemas/"
            if not ref.startswith(prefix) or ref in seen:
                return None
            name = ref[len(prefix):].replace("~1", "/").replace("~0", "~")
            entity = _canonical_resource_entity(name)
            if entity is None:
                return None
            resolved = _resolve_ref(document, schema, seen)
            if resolved.get("x-unresolved-ref"):
                return None
            return {entity}

        branches = [schema[key] for key in ("anyOf", "oneOf", "allOf") if isinstance(schema.get(key), list)]
        if branches:
            entities: set[str] = set()
            for branch_list in branches:
                for branch in branch_list:
                    if not isinstance(branch, Mapping):
                        return None
                    branch_entities = collect(branch, seen)
                    if branch_entities is None:
                        return None
                    entities.update(branch_entities)
            return entities if entities else None
        return None

    per_response: list[set[str]] = []
    for schema in success_schemas:
        entities = collect(schema)
        if not entities or len(entities) != 1:
            return None
        per_response.append(entities)
    common = set.intersection(*per_response)
    return common if len(common) == 1 else None


def _path_collection_entity(path: str, parameter_name: str) -> str | None:
    """Bind only a final path placeholder beneath a matching plural resource path."""
    if not path.endswith("{" + parameter_name + "}"):
        return None
    prefix = path[: -(len(parameter_name) + 2)].rstrip("/")
    collection = prefix.rsplit("/", 1)[-1] if prefix else ""
    entity = _canonical_entity(collection)
    placeholder_entity = _canonical_entity(parameter_name)
    if entity and entity == placeholder_entity:
        return entity
    return None


def _is_generic_object_identifier(description: str) -> bool:
    text = re.sub(r"\s+", " ", description.lower()).strip()
    return bool(re.search(r"\b(?:unique\s+)?(?:id|identifier)\s+(?:for|of)\s+(?:the\s+)?object\b", text))


def _infer_path_parameter_from_response(
    document: Mapping[str, Any], path: str, operation: Mapping[str, Any], parameter: Mapping[str, Any]
) -> tuple[str | None, str]:
    """Infer a resource ID only when path, prose and success schema agree."""
    name = parameter.get("name")
    description = parameter.get("description", "")
    if not isinstance(name, str) or not isinstance(description, str):
        return None, "unknown"
    if parameter.get("in") != "path" or parameter.get("required") is not True:
        return None, "unknown"
    if not _is_generic_object_identifier(description):
        return None, "unknown"
    path_entity = _path_collection_entity(path, name)
    response_entities = _response_resource_entities(document, operation)
    if path_entity and response_entities == {path_entity}:
        return f"{path_entity}.id", "operation_response_resource"
    return None, "unknown"


def infer_semantic_id(
    name: str, description: str = "", *, scope: str | None = None,
    extensions: Mapping[str, Any] | None = None,
) -> tuple[str | None, str]:
    """Derive only narrow, auditable semantic IDs; never use fuzzy similarity."""
    if isinstance(extensions, Mapping):
        explicit = extensions.get("x-semantic-id")
        if isinstance(explicit, str) and explicit.strip():
            return explicit.strip(), "explicit"
    normalized = _snake(name)
    if normalized == "id" and scope:
        entity = _canonical_entity(scope)
        if entity:
            return f"{entity}.id", "resource_ref"

    text = description.lower().replace("_", " ")
    match = re.search(
        r"\b(?:id|identifier)\s+(?:of|for)\s+(?:the\s+|an?\s+)?([a-z][a-z _-]{0,32})",
        text,
    )
    if match:
        phrase = match.group(1)
        phrase = re.split(r"\b(?:to|that|which|used|attached|representing|being|billed|bill)\b", phrase)[0]
        entity = _canonical_entity(phrase.strip(" .,:;-/"))
        if entity:
            return f"{entity}.id", "description"

    # "customer ID" / "invoice identifier" appears in some provider docs.
    match = re.search(r"\b(customer|invoice|payment intent|subscription|product|price|account)\s+(?:id|identifier)\b", text)
    if match:
        entity = _canonical_entity(match.group(1))
        if entity:
            return f"{entity}.id", "description"

    direct = re.fullmatch(r"([a-z0-9_]+)_id", normalized)
    if direct:
        entity = _canonical_entity(direct.group(1))
        if entity:
            return f"{entity}.id", "name_only"
    return None, "unknown"


def _ref_scope(schema: Mapping[str, Any]) -> str | None:
    ref = schema.get("$ref") if isinstance(schema, Mapping) else None
    if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
        return ref.rsplit("/", 1)[-1]
    return None


def _guaranteed_properties(schema: Mapping[str, Any], document: Mapping[str, Any], seen: frozenset[str] = frozenset()) -> tuple[str, Mapping[str, Any]]:
    resolved = _resolve_ref(document, schema, seen)
    scope = _ref_scope(schema) or _ref_scope(resolved)
    if "allOf" in resolved and isinstance(resolved["allOf"], list):
        combined: dict[str, Any] = {}
        for child in resolved["allOf"]:
            _, props = _guaranteed_properties(child, document, seen)
            combined.update(props)
        return scope or "", combined
    branches = resolved.get("anyOf") or resolved.get("oneOf")
    if isinstance(branches, list):
        branch_props = [_guaranteed_properties(branch, document, seen)[1] for branch in branches if isinstance(branch, Mapping)]
        if not branch_props:
            return scope or "", {}
        common = set(branch_props[0])
        for props in branch_props[1:]:
            common.intersection_update(props)
        combined = {}
        for key in sorted(common):
            candidates = [props[key] for props in branch_props]
            if all(_schema_signature(c) == _schema_signature(candidates[0]) for c in candidates[1:]):
                combined[key] = candidates[0]
        return scope or "", combined
    properties = resolved.get("properties")
    required = resolved.get("required", [])
    if not isinstance(properties, Mapping) or not isinstance(required, list):
        return scope or "", {}
    return scope or "", {
        key: properties[key] for key in sorted(set(required))
        if key in properties and isinstance(properties[key], Mapping)
    }


def _schema_signature(schema: Mapping[str, Any]) -> str:
    return json.dumps(schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _content_schema(content: Any) -> Mapping[str, Any] | None:
    if not isinstance(content, Mapping):
        return None
    media_types = sorted(content, key=lambda item: (0 if item == "application/json" else 1 if item.endswith("+json") else 2 if item == "application/x-www-form-urlencoded" else 3, item))
    for media in media_types:
        entry = content.get(media)
        if isinstance(entry, Mapping) and isinstance(entry.get("schema"), Mapping):
            return entry["schema"]
    return None


def _make_slot(name: str, schema: Mapping[str, Any], *, description: str = "", scope: str | None = None, source_path: str = "", required: bool = True) -> Slot:
    semantic_id, evidence = infer_semantic_id(name, description, scope=scope, extensions=schema)
    return Slot(name, semantic_id, dict(schema), required, evidence, source_path, description)


def contract_from_openapi(document: Mapping[str, Any], path: str, method: str, *, source: str = "") -> Operation:
    """Compile one OpenAPI operation into required input and guaranteed output slots."""
    method = method.lower()
    if method not in _METHODS:
        raise ValueError(f"unsupported HTTP method: {method}")
    paths = document.get("paths")
    if not isinstance(paths, Mapping) or path not in paths or not isinstance(paths[path], Mapping):
        raise ValueError(f"OpenAPI path not found: {path}")
    path_item = paths[path]
    operation = path_item.get(method)
    if not isinstance(operation, Mapping):
        raise ValueError(f"OpenAPI operation not found: {method.upper()} {path}")
    operation_id = operation.get("operationId")
    if not isinstance(operation_id, str) or not operation_id:
        operation_id = f"{method.upper()} {path}"

    required_inputs: list[Slot] = []
    contract_issues: list[Mapping[str, Any]] = []
    path_parameters = path_item.get("parameters", [])
    operation_parameters = operation.get("parameters", [])
    if not isinstance(path_parameters, list):
        contract_issues.append({"kind": "contract_schema_unsupported", "location": "path_parameters", "reason": "path-level parameters are not a list"})
        path_parameters = []
    if not isinstance(operation_parameters, list):
        contract_issues.append({"kind": "contract_schema_unsupported", "location": "operation_parameters", "reason": "operation-level parameters are not a list"})
        operation_parameters = []

    # OpenAPI operation parameters override same-name/in path-level parameters.
    parameters_by_key: dict[tuple[str, str], tuple[int, Mapping[str, Any]]] = {}
    for index, raw_parameter in enumerate(path_parameters + operation_parameters):
        if not isinstance(raw_parameter, Mapping):
            contract_issues.append({"kind": "contract_schema_unsupported", "location": "parameter", "index": index, "reason": "parameter is not an object"})
            continue
        parameter = _resolve_ref(document, raw_parameter)
        if parameter.get("x-unresolved-ref"):
            contract_issues.append({"kind": "contract_schema_unsupported", "location": "parameter", "index": index, "reference": parameter.get("x-unresolved-ref")})
            continue
        name = parameter.get("name")
        location = parameter.get("in")
        if isinstance(name, str) and isinstance(location, str):
            parameters_by_key[(name, location)] = (index, parameter)

    path_parameter_names = set(re.findall(r"\{([^{}]+)\}", path))
    for name in sorted(path_parameter_names):
        if (name, "path") not in parameters_by_key:
            contract_issues.append({
                "kind": "contract_schema_unsupported", "location": "path_parameter",
                "parameter": name, "reason": "path template parameter has no declared parameter schema",
            })

    for (name, location), (index, parameter) in sorted(parameters_by_key.items()):
        is_required = parameter.get("required") is True
        if location == "path" and not is_required:
            contract_issues.append({
                "kind": "contract_schema_unsupported", "location": "path_parameter",
                "parameter": name, "reason": "OpenAPI path parameters must be required",
            })
            continue
        if not is_required:
            continue
        schema = parameter.get("schema")
        if isinstance(schema, Mapping):
            resolved_schema = _resolve_ref(document, schema)
            if resolved_schema.get("x-unresolved-ref"):
                contract_issues.append({
                    "kind": "contract_schema_unsupported", "location": "required_parameter",
                    "parameter": name, "reference": resolved_schema.get("x-unresolved-ref"),
                })
            else:
                slot = _make_slot(
                    name, resolved_schema,
                    description=str(parameter.get("description", "")),
                    source_path=f"paths.{path}.{method}.parameters[{index}]",
                )
                if slot.semantic_id is None:
                    inferred_id, inferred_evidence = _infer_path_parameter_from_response(
                        document, path, operation, parameter
                    )
                    if inferred_id is not None:
                        slot = Slot(
                            slot.name, inferred_id, slot.schema, slot.required,
                            inferred_evidence, slot.source_path, slot.description,
                        )
                required_inputs.append(slot)
        else:
            contract_issues.append({
                "kind": "contract_schema_unsupported", "location": "required_parameter",
                "parameter": name, "reason": "required parameter has no supported schema",
            })

    request_body = operation.get("requestBody")
    if "requestBody" in operation and not isinstance(request_body, Mapping):
        contract_issues.append({
            "kind": "contract_schema_unsupported", "location": "required_request_body",
            "reason": "request body declaration is not an object",
        })
    if isinstance(request_body, Mapping):
        request_body = _resolve_ref(document, request_body)
        if request_body.get("x-unresolved-ref"):
            contract_issues.append({
                "kind": "contract_schema_unsupported", "location": "request_body",
                "reference": request_body.get("x-unresolved-ref"),
            })
        else:
            # In OpenAPI 3, requestBody.required defaults to false. A field marked
            # required inside an optional body is conditional on sending that body.
            body_is_required = request_body.get("required", False) is True
            if body_is_required:
                body_schema = _content_schema(request_body.get("content"))
                if not isinstance(body_schema, Mapping):
                    contract_issues.append({
                        "kind": "contract_schema_unsupported", "location": "required_request_body",
                        "reason": "required request body has no supported content schema",
                    })
                else:
                    body_schema = _resolve_ref(document, body_schema)
                    properties = body_schema.get("properties")
                    required_names = body_schema.get("required", [])
                    has_object_shape = body_schema.get("type") == "object" or isinstance(properties, Mapping)
                    has_composition = any(key in body_schema for key in ("allOf", "anyOf", "oneOf"))
                    if not has_object_shape or has_composition or not isinstance(properties, Mapping) or not isinstance(required_names, list):
                        contract_issues.append({
                            "kind": "contract_schema_unsupported", "location": "required_request_body",
                            "reason": "required body is not a directly declared object schema",
                        })
                    else:
                        for name in sorted(set(required_names)):
                            child_schema = properties.get(name)
                            if not isinstance(name, str) or not isinstance(child_schema, Mapping):
                                contract_issues.append({
                                    "kind": "contract_schema_unsupported", "location": "required_request_body",
                                    "field": str(name), "reason": "required body field lacks a supported property schema",
                                })
                                continue
                            child_schema = _resolve_ref(document, child_schema)
                            if child_schema.get("x-unresolved-ref"):
                                contract_issues.append({
                                    "kind": "contract_schema_unsupported", "location": "required_request_body",
                                    "field": name, "reason": "required body field reference cannot be resolved",
                                })
                                continue
                            required_inputs.append(_make_slot(
                                name, child_schema,
                                description=str(child_schema.get("description", "")),
                                source_path=f"paths.{path}.{method}.requestBody.{name}",
                            ))

    responses = operation.get("responses", {})
    success_schema_sets: list[tuple[str, Mapping[str, Any]]] = []
    success_response_without_schema = False
    if isinstance(responses, Mapping):
        for code in sorted(responses, key=lambda item: (int(item) if str(item).isdigit() else 999, str(item))):
            if not re.fullmatch(r"2(?:\d\d|XX)", str(code), flags=re.IGNORECASE):
                continue
            response = responses[code]
            if isinstance(response, Mapping):
                response = _resolve_ref(document, response)
                schema = _content_schema(response.get("content"))
                if isinstance(schema, Mapping):
                    success_schema_sets.append((str(code), schema))
                else:
                    success_response_without_schema = True
    outputs: list[Slot] = []
    # An output is guaranteed only if every declared 2xx response has a schema
    # and declares the same required semantic field with the same schema.
    if success_schema_sets and not success_response_without_schema:
        response_slots: list[dict[str, Slot]] = []
        for code, response_schema in success_schema_sets:
            scope, properties = _guaranteed_properties(response_schema, document)
            slots: dict[str, Slot] = {}
            for name, child_schema in sorted(properties.items()):
                resolved_child = _resolve_ref(document, child_schema)
                slots[name] = _make_slot(
                    name, resolved_child,
                    description=str(child_schema.get("description", "")),
                    scope=scope,
                    source_path=f"paths.{path}.{method}.responses.{code}.{scope}.{name}",
                )
            response_slots.append(slots)
        common_names = set(response_slots[0])
        for slots in response_slots[1:]:
            common_names.intersection_update(slots)
        for name in sorted(common_names):
            candidates = [slots[name] for slots in response_slots]
            first = candidates[0]
            if all(
                slot.semantic_id == first.semantic_id
                and _schema_signature(slot.schema) == _schema_signature(first.schema)
                and slot.semantic_id is not None
                for slot in candidates[1:]
            ):
                outputs.append(first)

    security = operation.get("security", document.get("security", []))
    security_alternatives: list[tuple[str, ...]] = []
    if isinstance(security, list):
        for alternative in security:
            if isinstance(alternative, Mapping):
                security_alternatives.append(tuple(sorted(str(key) for key in alternative)))

    return Operation(
        operation_id=operation_id,
        method=method.upper(),
        path=path,
        required_inputs=tuple(sorted(required_inputs, key=lambda slot: (slot.semantic_id or "", slot.name))),
        outputs=tuple(sorted(outputs, key=lambda slot: (slot.semantic_id or "", slot.name))),
        security_alternatives=tuple(security_alternatives),
        source=source,
        contract_issues=tuple(contract_issues),
    )


def _compatible_semantic_slots(provider: Slot, consumer: Slot) -> Compatibility:
    if not provider.semantic_id or not consumer.semantic_id:
        return Compatibility("UNKNOWN", ("semantic_identity_missing",))
    if provider.semantic_id != consumer.semantic_id:
        return Compatibility("INCOMPATIBLE", ("semantic_identity_mismatch",))
    accepted_evidence = {"explicit", "description", "resource_ref", "operation_response_resource"}
    if provider.evidence not in accepted_evidence or consumer.evidence not in accepted_evidence:
        return Compatibility("UNKNOWN", ("semantic_evidence_insufficient",))
    return schema_compatibility(provider.schema, consumer.schema)


def _anchor_schema(anchor: Mapping[str, Any], semantic_id: str) -> Mapping[str, Any] | None:
    values = anchor.get("values", anchor)
    if not isinstance(values, Mapping):
        return None
    candidate = values.get(semantic_id)
    if isinstance(candidate, Mapping):
        return candidate
    return None


def _anchor_auth(anchor: Mapping[str, Any]) -> set[str]:
    values = anchor.get("auth_schemes", [])
    return {value for value in values if isinstance(value, str)} if isinstance(values, list) else set()


def _operation_security_satisfied(operation: Operation, anchor: Mapping[str, Any]) -> bool:
    if not operation.security_alternatives:
        return True
    available = _anchor_auth(anchor)
    return any(all(scheme in available for scheme in alternative) for alternative in operation.security_alternatives)


def _provider_candidates(
    consumer: Slot, operations: Mapping[str, Operation], current_id: str,
    *, require_explicit: bool,
) -> tuple[list[tuple[str, Slot]], list[Mapping[str, Any]]]:
    candidates: list[tuple[str, Slot]] = []
    rejected: list[Mapping[str, Any]] = []
    for operation_id, operation in sorted(operations.items()):
        if operation_id == current_id:
            continue
        for output in operation.outputs:
            if consumer.semantic_id is None or output.semantic_id != consumer.semantic_id:
                continue
            if require_explicit and (output.evidence != "explicit" or consumer.evidence != "explicit"):
                rejected.append({
                    "kind": "explicit_evidence_required", "provider": operation_id,
                    "input": consumer.semantic_id, "provider_evidence": output.evidence,
                    "consumer_evidence": consumer.evidence,
                })
                continue
            compatibility = _compatible_semantic_slots(output, consumer)
            if compatibility.status == "SUPPORTED":
                candidates.append((operation_id, output))
            else:
                rejected.append({
                    "kind": (
                        "semantic_evidence_insufficient" if "semantic_evidence_insufficient" in compatibility.reasons
                        else "type_incompatible" if compatibility.status == "INCOMPATIBLE"
                        else "type_unknown"
                    ),
                    "provider": operation_id, "input": consumer.semantic_id,
                    "reasons": list(compatibility.reasons),
                })
    candidates.sort(key=lambda item: (operations[item[0]].cost, item[0]))
    return candidates, rejected


def _digest_input(target: str, operations: Mapping[str, Operation], anchor: Mapping[str, Any], require_explicit: bool) -> str:
    canonical_operations = []
    for op_id, op in sorted(operations.items()):
        canonical_operations.append({
            "id": op_id, "method": op.method, "path": op.path, "cost": op.cost, "source": op.source,
            "required_inputs": [
                {"semantic_id": slot.semantic_id, "name": slot.name, "schema": dict(slot.schema), "evidence": slot.evidence, "description": slot.description, "source_path": slot.source_path}
                for slot in op.required_inputs
            ],
            "outputs": [
                {"semantic_id": slot.semantic_id, "name": slot.name, "schema": dict(slot.schema), "evidence": slot.evidence, "description": slot.description, "source_path": slot.source_path}
                for slot in op.outputs
            ],
            "security": [list(x) for x in op.security_alternatives],
            "contract_issues": [dict(issue) for issue in op.contract_issues],
        })
    payload = {
        "schema": SCHEMA_VERSION, "algorithm": ALGORITHM_VERSION, "target": target,
        "operations": canonical_operations, "anchor": anchor,
        "require_explicit": require_explicit,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def plan_closure(
    target: str,
    operations: Mapping[str, Operation],
    anchor: Mapping[str, Any],
    *,
    require_explicit: bool = False,
    max_expansions: int = 2000,
) -> ClosureResult:
    """Find a low-cost acyclic prerequisite closure for one target operation.

    All required inputs of every selected operation must be provided by the
    anchor or by a previously ordered provider. Optional fields are not gates.
    The bounded DFS selects the lowest total operation cost, then fewest calls,
    then lexical operation order. A complete inferred plan is clearly
    distinguished from one grounded in explicit semantic IDs.
    """
    if target not in operations:
        raise ValueError(f"target operation not registered: {target}")
    if type(max_expansions) is not int or max_expansions < 1:
        raise ValueError("max_expansions must be a positive integer")

    expansions = 0
    limit_hit = False

    def clone(state: dict[str, Any]) -> dict[str, Any]:
        return {
            "order": list(state["order"]),
            "dependencies": list(state["dependencies"]),
            "anchored": list(state["anchored"]),
            "missing": list(state["missing"]),
            "issues": list(state["issues"]),
            "used_inferred": state["used_inferred"],
            "cost": state["cost"],
        }

    initial = {"order": [], "dependencies": [], "anchored": [], "missing": [], "issues": [], "used_inferred": False, "cost": 0}

    def is_completed(state: dict[str, Any], op_id: str) -> bool:
        return op_id in state["order"]

    def visit(op_id: str, state: dict[str, Any], stack: tuple[str, ...]) -> list[dict[str, Any]]:
        nonlocal expansions, limit_hit
        expansions += 1
        if expansions > max_expansions:
            limit_hit = True
            return []
        if op_id in stack:
            state = clone(state)
            state["issues"].append({"kind": "cycle", "cycle": list(stack) + [op_id]})
            return [state]
        if is_completed(state, op_id):
            return [state]

        operation = operations[op_id]
        state = clone(state)
        before_missing = len(state["missing"])
        before_issues = len(state["issues"])
        for contract_issue in operation.contract_issues:
            state["issues"].append({"operation": op_id, **dict(contract_issue)})
        if not _operation_security_satisfied(operation, anchor):
            state["issues"].append({
                "kind": "security_precondition_missing", "operation": op_id,
                "alternatives": [list(value) for value in operation.security_alternatives],
            })
            return [state]

        states = [state]
        for required_input in operation.required_inputs:
            next_states: list[dict[str, Any]] = []
            for current in states:
                # A typed anchor value is an external precondition and can satisfy an input.
                if required_input.semantic_id:
                    anchored_schema = _anchor_schema(anchor, required_input.semantic_id)
                else:
                    anchored_schema = None
                if anchored_schema is not None:
                    compatibility = schema_compatibility(anchored_schema, required_input.schema)
                    if compatibility.status == "SUPPORTED":
                        updated = clone(current)
                        updated["anchored"].append({
                            "operation": op_id, "input": required_input.semantic_id,
                            "source": "anchor", "compatibility": list(compatibility.reasons),
                        })
                        next_states.append(updated)
                        continue
                    current = clone(current)
                    current["issues"].append({
                        "kind": "anchor_type_incompatible" if compatibility.status == "INCOMPATIBLE" else "anchor_type_unknown",
                        "operation": op_id, "input": required_input.semantic_id,
                        "reasons": list(compatibility.reasons),
                    })

                # Only outputs from operations already placed before this consumer are available.
                existing: list[tuple[str, Slot, Compatibility]] = []
                for previous_id in current["order"]:
                    previous = operations[previous_id]
                    for output in previous.outputs:
                        result = _compatible_semantic_slots(output, required_input)
                        if result.status == "SUPPORTED":
                            existing.append((previous_id, output, result))
                if existing:
                    provider_id, output, compatibility = sorted(existing, key=lambda item: (operations[item[0]].cost, item[0]))[0]
                    updated = clone(current)
                    updated["dependencies"].append({
                        "provider": provider_id, "consumer": op_id,
                        "semantic_id": required_input.semantic_id,
                        "provider_evidence": output.evidence,
                        "consumer_evidence": required_input.evidence,
                        "compatibility": list(compatibility.reasons),
                    })
                    if output.evidence != "explicit" or required_input.evidence != "explicit":
                        updated["used_inferred"] = True
                    next_states.append(updated)
                    continue

                candidates, rejected = _provider_candidates(
                    required_input, operations, op_id, require_explicit=require_explicit
                )
                viable = [candidate for candidate in candidates if candidate[0] not in stack and candidate[0] != op_id]
                cyclic = [candidate[0] for candidate in candidates if candidate[0] in stack]
                if cyclic:
                    current = clone(current)
                    current["issues"].append({"kind": "cycle", "operation": op_id, "input": required_input.semantic_id, "providers_in_dependency_stack": cyclic})
                if not viable:
                    updated = clone(current)
                    updated["missing"].append(required_input)
                    updated["issues"].extend(rejected)
                    if not candidates and not rejected and not cyclic:
                        updated["issues"].append({"kind": "unprovided_input", "operation": op_id, "input": required_input.semantic_id, "name": required_input.name})
                    next_states.append(updated)
                    continue

                successful_branches: list[dict[str, Any]] = []
                failed_branches: list[dict[str, Any]] = []
                for provider_id, output in viable:
                    branch_states = visit(provider_id, current, stack + (op_id,))
                    for branch in branch_states:
                        if is_completed(branch, provider_id):
                            compatibility = _compatible_semantic_slots(output, required_input)
                            branch["dependencies"].append({
                                "provider": provider_id, "consumer": op_id,
                                "semantic_id": required_input.semantic_id,
                                "provider_evidence": output.evidence,
                                "consumer_evidence": required_input.evidence,
                                "compatibility": list(compatibility.reasons),
                            })
                            if output.evidence != "explicit" or required_input.evidence != "explicit":
                                branch["used_inferred"] = True
                            successful_branches.append(branch)
                        else:
                            failed_branches.append(branch)
                next_states.extend(successful_branches if successful_branches else failed_branches)
            remaining = max(1, max_expansions - expansions + 1)
            if len(next_states) > remaining:
                # Never silently prune branches: doing so would make the
                # minimum-cost claim unsubstantiated.
                limit_hit = True
                next_states = next_states[:remaining]
            states = next_states
            if not states:
                break

        finished: list[dict[str, Any]] = []
        for final_state in states:
            local_missing = len(final_state["missing"]) > before_missing
            local_blocking = any(
                issue.get("kind") in {"security_precondition_missing", "contract_schema_unsupported", "cycle", "type_incompatible", "type_unknown", "semantic_evidence_insufficient", "explicit_evidence_required", "anchor_type_incompatible", "anchor_type_unknown"}
                for issue in final_state["issues"][before_issues:]
            )
            if not local_missing and not local_blocking:
                if op_id not in final_state["order"]:
                    final_state["order"].append(op_id)
                    final_state["cost"] += operation.cost
            finished.append(final_state)
        return finished

    candidates = visit(target, initial, ())
    if not candidates:
        chosen = initial
    else:
        def rank(state: dict[str, Any]) -> tuple[Any, ...]:
            return (
                0 if not state["missing"] and not state["issues"] and target in state["order"] else 1,
                state["cost"], len(state["order"]), tuple(state["order"]),
                len(state["missing"]), len(state["issues"]),
            )
        chosen = min(candidates, key=rank)

    feasible = not chosen["missing"] and not chosen["issues"] and target in chosen["order"]
    if limit_hit and feasible:
        # A plan was found, but unexplored branches mean minimum-cost
        # optimality has not been established.
        status = "FEASIBLE_SEARCH_LIMIT"
    elif feasible:
        status = "COMPLETE_INFERRED" if chosen["used_inferred"] else "COMPLETE_EXPLICIT"
    elif limit_hit:
        status = "SEARCH_LIMIT"
    else:
        status = "INCOMPLETE"
    digest = _digest_input(target, operations, anchor, require_explicit)
    missing_unique: dict[tuple[str | None, str, str], Slot] = {}
    for slot in chosen["missing"]:
        missing_unique[(slot.semantic_id, slot.name, slot.source_path)] = slot
    return ClosureResult(
        status=status,
        target=target,
        operation_order=tuple(chosen["order"]),
        dependencies=tuple(chosen["dependencies"]),
        anchored_inputs=tuple(chosen["anchored"]),
        missing_inputs=tuple(missing_unique[key] for key in sorted(missing_unique, key=str)),
        issues=tuple(chosen["issues"]),
        total_cost=chosen["cost"],
        input_digest_sha256=digest,
        expansions=expansions,
    )


def parse_openapi_json(raw: bytes, *, expected_git_blob_sha1: str | None = None) -> Mapping[str, Any]:
    """Parse JSON OpenAPI and optionally verify Git's canonical blob SHA-1."""
    if expected_git_blob_sha1:
        header = f"blob {len(raw)}\0".encode("ascii")
        actual = hashlib.sha1(header + raw).hexdigest()
        if actual != expected_git_blob_sha1:
            raise ValueError(f"Git blob SHA-1 mismatch: expected {expected_git_blob_sha1}, got {actual}")
    document = json.loads(raw)
    if not isinstance(document, Mapping) or not str(document.get("openapi", "")).startswith("3."):
        raise ValueError("expected an OpenAPI 3.x JSON document")
    if not isinstance(document.get("paths"), Mapping):
        raise ValueError("OpenAPI document has no paths mapping")
    return document
