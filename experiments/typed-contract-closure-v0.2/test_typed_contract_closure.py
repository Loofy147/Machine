import hashlib
import json
import unittest

from typed_contract_closure import (
    Operation,
    Slot,
    contract_from_openapi,
    infer_semantic_id,
    parse_openapi_json,
    plan_closure,
    schema_compatibility,
)


class SchemaCompatibilityTests(unittest.TestCase):
    def test_integer_output_is_assignable_to_number_input_but_not_reverse(self):
        self.assertEqual(
            schema_compatibility({"type": "integer"}, {"type": "number"}).status,
            "SUPPORTED",
        )
        self.assertEqual(
            schema_compatibility({"type": "number"}, {"type": "integer"}).status,
            "INCOMPATIBLE",
        )

    def test_nullable_output_cannot_guarantee_non_nullable_input(self):
        result = schema_compatibility(
            {"type": "string", "nullable": True}, {"type": "string"}
        )
        self.assertEqual(result.status, "INCOMPATIBLE")

    def test_provider_enum_must_be_subset_of_consumer_enum(self):
        accepted = schema_compatibility(
            {"type": "string", "enum": ["draft"]},
            {"type": "string", "enum": ["draft", "final"]},
        )
        rejected = schema_compatibility(
            {"type": "string", "enum": ["draft", "void"]},
            {"type": "string", "enum": ["draft", "final"]},
        )
        unknown = schema_compatibility(
            {"type": "string"}, {"type": "string", "enum": ["draft", "final"]}
        )
        self.assertEqual(accepted.status, "SUPPORTED")
        self.assertEqual(rejected.status, "INCOMPATIBLE")
        self.assertEqual(unknown.status, "UNKNOWN")

    def test_enum_without_explicit_type_infers_json_value_type(self):
        compatible = schema_compatibility(
            {"enum": ["draft", "final"]},
            {"type": "string", "enum": ["draft", "final", "void"]},
        )
        incompatible = schema_compatibility(
            {"enum": ["draft", 1]},
            {"type": "string"},
        )
        self.assertEqual(compatible.status, "SUPPORTED")
        self.assertEqual(incompatible.status, "INCOMPATIBLE")

    def test_anyof_union_is_type_checked_without_erasing_nullable_branch(self):
        optional_string = {"anyOf": [{"type": "string"}, {"type": "string", "enum": [""]}]}
        self.assertEqual(
            schema_compatibility(optional_string, {"type": "string"}).status,
            "SUPPORTED",
        )
        mixed_union = {"anyOf": [{"type": "string"}, {"type": "integer"}]}
        self.assertEqual(
            schema_compatibility(mixed_union, {"type": "string"}).status,
            "INCOMPATIBLE",
        )
        nullable_union = {"anyOf": [{"type": "string"}, {"type": "null"}]}
        self.assertEqual(
            schema_compatibility(nullable_union, {"type": "string"}).status,
            "INCOMPATIBLE",
        )
        self.assertEqual(
            schema_compatibility(nullable_union, {"type": "string", "nullable": True}).status,
            "SUPPORTED",
        )

    def test_exclusive_numeric_bounds_preserve_open_and_closed_interval_rules(self):
        provider_open = {"type": "integer", "minimum": 1, "exclusiveMinimum": True}
        consumer_closed = {"type": "integer", "minimum": 1}
        provider_closed = {"type": "integer", "minimum": 1}
        consumer_open = {"type": "integer", "minimum": 1, "exclusiveMinimum": True}
        self.assertEqual(schema_compatibility(provider_open, consumer_closed).status, "SUPPORTED")
        self.assertEqual(schema_compatibility(provider_closed, consumer_open).status, "INCOMPATIBLE")
        invalid = {"type": "integer", "exclusiveMinimum": True}
        self.assertEqual(schema_compatibility(invalid, consumer_closed).status, "UNKNOWN")

    def test_object_compatibility_checks_required_fields_and_nested_types(self):
        provider = {
            "type": "object", "required": ["id"],
            "properties": {"id": {"type": "string"}, "count": {"type": "integer"}},
            "additionalProperties": False,
        }
        consumer = {
            "type": "object", "required": ["id"],
            "properties": {"id": {"type": "string"}, "count": {"type": "number"}},
            "additionalProperties": False,
        }
        self.assertEqual(schema_compatibility(provider, consumer).status, "SUPPORTED")
        missing_required = {**provider, "required": []}
        self.assertEqual(schema_compatibility(missing_required, consumer).status, "INCOMPATIBLE")
        bad_field = {**provider, "properties": {"id": {"type": "integer"}, "count": {"type": "integer"}}}
        self.assertEqual(schema_compatibility(bad_field, consumer).status, "INCOMPATIBLE")
        unbounded_optional = {
            "type": "object", "properties": {},
            "additionalProperties": {"type": "integer"},
        }
        consumer_optional = {
            "type": "object", "properties": {"metadata": {"type": "string"}},
        }
        self.assertEqual(schema_compatibility(unbounded_optional, consumer_optional).status, "INCOMPATIBLE")

    def test_array_item_schema_must_be_checked_when_consumer_constrains_items(self):
        safe = schema_compatibility(
            {"type": "array", "items": {"type": "integer"}},
            {"type": "array", "items": {"type": "number"}},
        )
        unsafe = schema_compatibility(
            {"type": "array"},
            {"type": "array", "items": {"type": "string"}},
        )
        self.assertEqual(safe.status, "SUPPORTED")
        self.assertEqual(unsafe.status, "UNKNOWN")

    def test_consumer_numeric_bounds_must_cover_provider_guarantees(self):
        safe = schema_compatibility(
            {"type": "integer", "minimum": 1, "maximum": 10},
            {"type": "integer", "minimum": 0, "maximum": 20},
        )
        unsafe = schema_compatibility(
            {"type": "integer", "minimum": -1, "maximum": 10},
            {"type": "integer", "minimum": 0, "maximum": 20},
        )
        self.assertEqual(safe.status, "SUPPORTED")
        self.assertEqual(unsafe.status, "INCOMPATIBLE")


class ClosurePlannerTests(unittest.TestCase):
    def test_multi_hop_closure_resolves_every_required_dependency(self):
        create_customer = Operation(
            operation_id="create_customer",
            method="POST",
            path="/customers",
            outputs=(Slot("customer_id", "customer.id", {"type": "string"}, evidence="explicit"),),
        )
        create_invoice = Operation(
            operation_id="create_invoice",
            method="POST",
            path="/invoices",
            required_inputs=(Slot("customer", "customer.id", {"type": "string"}, evidence="explicit"),),
            outputs=(Slot("invoice_id", "invoice.id", {"type": "string"}, evidence="explicit"),),
        )
        retrieve_invoice = Operation(
            operation_id="retrieve_invoice",
            method="GET",
            path="/invoices/{invoice}",
            required_inputs=(Slot("invoice", "invoice.id", {"type": "string"}, evidence="explicit"),),
        )
        result = plan_closure(
            "retrieve_invoice",
            {op.operation_id: op for op in (create_customer, create_invoice, retrieve_invoice)},
            anchor={},
        )
        self.assertEqual(result.status, "COMPLETE_EXPLICIT")
        self.assertEqual(result.operation_order, ("create_customer", "create_invoice", "retrieve_invoice"))
        self.assertEqual(result.missing_inputs, ())
        self.assertEqual(len(result.dependencies), 2)

    def test_documented_inference_is_not_reported_as_explicit(self):
        provider = Operation(
            "create_customer", "POST", "/customers",
            outputs=(Slot("id", "customer.id", {"type": "string"}, evidence="resource_ref"),),
        )
        consumer = Operation(
            "get_customer", "GET", "/customers/{customer}",
            required_inputs=(Slot("customer", "customer.id", {"type": "string"}, evidence="description"),),
        )
        operations = {provider.operation_id: provider, consumer.operation_id: consumer}
        inferred = plan_closure("get_customer", operations, anchor={})
        strict = plan_closure("get_customer", operations, anchor={}, require_explicit=True)
        self.assertEqual(inferred.status, "COMPLETE_INFERRED")
        self.assertEqual(strict.status, "INCOMPLETE")
        self.assertTrue(strict.missing_inputs)

    def test_incomplete_closure_rejects_existential_partial_coverage(self):
        provider = Operation(
            "provider", "POST", "/provider",
            outputs=(Slot("customer", "customer.id", {"type": "string"}, evidence="explicit"),),
        )
        target = Operation(
            "target", "POST", "/target",
            required_inputs=(
                Slot("customer", "customer.id", {"type": "string"}, evidence="explicit"),
                Slot("invoice", "invoice.id", {"type": "string"}, evidence="explicit"),
            ),
        )
        result = plan_closure("target", {"provider": provider, "target": target}, anchor={})
        self.assertEqual(result.status, "INCOMPLETE")
        self.assertEqual({item.semantic_id for item in result.missing_inputs}, {"invoice.id"})

    def test_input_digest_changes_when_documented_semantic_evidence_changes(self):
        provider = Operation(
            "provider", "POST", "/customers",
            outputs=(Slot("id", "customer.id", {"type": "string"}, evidence="resource_ref"),),
        )
        consumer_a = Operation(
            "consumer", "GET", "/customers/{customer}",
            required_inputs=(Slot("customer", "customer.id", {"type": "string"}, evidence="description", description="ID of customer"),),
        )
        consumer_b = Operation(
            "consumer", "GET", "/customers/{customer}",
            required_inputs=(Slot("customer", "customer.id", {"type": "string"}, evidence="description", description="ID of a different entity"),),
        )
        first = plan_closure("consumer", {"provider": provider, "consumer": consumer_a}, anchor={})
        second = plan_closure("consumer", {"provider": provider, "consumer": consumer_b}, anchor={})
        self.assertNotEqual(first.input_digest_sha256, second.input_digest_sha256)

    def test_name_only_field_name_is_not_accepted_as_semantic_evidence(self):
        provider = Operation(
            "provider", "POST", "/customers",
            outputs=(Slot("customer_id", "customer.id", {"type": "string"}, evidence="name_only"),),
        )
        consumer = Operation(
            "consumer", "GET", "/customers/{customer_id}",
            required_inputs=(Slot("customer_id", "customer.id", {"type": "string"}, evidence="name_only"),),
        )
        result = plan_closure("consumer", {"provider": provider, "consumer": consumer}, anchor={})
        self.assertEqual(result.status, "INCOMPLETE")
        self.assertEqual(result.operation_order, ())
        self.assertTrue(any(issue["kind"] == "semantic_evidence_insufficient" for issue in result.issues))

    def test_dependency_cycle_is_not_treated_as_a_closed_workflow(self):
        first = Operation(
            "first", "POST", "/first",
            required_inputs=(Slot("b", "b.id", {"type": "string"}, evidence="explicit"),),
            outputs=(Slot("a", "a.id", {"type": "string"}, evidence="explicit"),),
        )
        second = Operation(
            "second", "POST", "/second",
            required_inputs=(Slot("a", "a.id", {"type": "string"}, evidence="explicit"),),
            outputs=(Slot("b", "b.id", {"type": "string"}, evidence="explicit"),),
        )
        result = plan_closure("first", {"first": first, "second": second}, anchor={})
        self.assertEqual(result.status, "INCOMPLETE")
        self.assertTrue(any(issue["kind"] == "cycle" for issue in result.issues))

    def test_type_mismatch_cannot_be_hidden_by_matching_semantic_id(self):
        provider = Operation(
            "producer", "POST", "/producer",
            outputs=(Slot("amount", "payment.amount", {"type": "string"}, evidence="explicit"),),
        )
        consumer = Operation(
            "consumer", "POST", "/consumer",
            required_inputs=(Slot("amount", "payment.amount", {"type": "integer"}, evidence="explicit"),),
        )
        result = plan_closure("consumer", {"producer": provider, "consumer": consumer}, anchor={})
        self.assertEqual(result.status, "INCOMPLETE")
        self.assertTrue(any(issue["kind"] == "type_incompatible" for issue in result.issues))

    def test_search_limit_does_not_claim_minimum_cost_optimality(self):
        expensive = Operation(
            "expensive", "POST", "/expensive",
            outputs=(Slot("id", "customer.id", {"type": "string"}, evidence="explicit"),),
            cost=10,
        )
        cheap = Operation(
            "cheap", "POST", "/cheap",
            outputs=(Slot("id", "customer.id", {"type": "string"}, evidence="explicit"),),
            cost=1,
        )
        target = Operation(
            "target", "GET", "/customers/{customer}",
            required_inputs=(Slot("customer", "customer.id", {"type": "string"}, evidence="explicit"),),
        )
        result = plan_closure(
            "target", {"expensive": expensive, "cheap": cheap, "target": target},
            anchor={}, max_expansions=2,
        )
        self.assertEqual(result.status, "FEASIBLE_SEARCH_LIMIT")
        self.assertIn(result.operation_order[0], {"cheap", "expensive"})
        self.assertFalse(result.to_dict()["optimality_proven"])

    def test_planner_selects_lowest_cost_provider_when_search_is_exhaustive(self):
        expensive = Operation(
            "expensive", "POST", "/expensive",
            outputs=(Slot("id", "customer.id", {"type": "string"}, evidence="explicit"),),
            cost=10,
        )
        cheap = Operation(
            "cheap", "POST", "/cheap",
            outputs=(Slot("id", "customer.id", {"type": "string"}, evidence="explicit"),),
            cost=1,
        )
        target = Operation(
            "target", "GET", "/customers/{customer}",
            required_inputs=(Slot("customer", "customer.id", {"type": "string"}, evidence="explicit"),),
        )
        result = plan_closure(
            "target", {"expensive": expensive, "cheap": cheap, "target": target}, anchor={}
        )
        self.assertEqual(result.status, "COMPLETE_EXPLICIT")
        self.assertEqual(result.operation_order, ("cheap", "target"))
        self.assertEqual(result.total_cost, 2)
        self.assertTrue(result.to_dict()["optimality_proven"])

    def test_security_is_an_external_precondition(self):
        operation = Operation(
            "secured", "GET", "/secured",
            security_alternatives=(("bearerAuth",), ("apiKey",)),
        )
        without = plan_closure("secured", {"secured": operation}, anchor={})
        with_auth = plan_closure(
            "secured", {"secured": operation}, anchor={"auth_schemes": ["bearerAuth"]}
        )
        self.assertEqual(without.status, "INCOMPLETE")
        self.assertEqual(with_auth.status, "COMPLETE_EXPLICIT")


class OpenApiAdapterTests(unittest.TestCase):
    def test_openapi_adapter_extracts_guaranteed_outputs_and_required_inputs(self):
        document = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1"},
            "components": {
                "schemas": {
                    "customer": {
                        "type": "object",
                        "required": ["id", "object"],
                        "properties": {
                            "id": {"type": "string", "description": "Unique customer identifier"},
                            "object": {"type": "string", "enum": ["customer"]},
                            "email": {"type": "string"},
                        },
                    }
                }
            },
            "paths": {
                "/customers": {
                    "post": {
                        "operationId": "createCustomer",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["email"],
                                        "properties": {
                                            "email": {"type": "string", "x-semantic-id": "customer.email"},
                                            "description": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        },
                        "responses": {
                            "201": {
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/customer"}
                                    }
                                }
                            }
                        },
                    }
                },
                "/customers/{customer}": {
                    "get": {
                        "operationId": "getCustomer",
                        "parameters": [
                            {
                                "name": "customer",
                                "in": "path",
                                "required": True,
                                "description": "The ID of the customer to retrieve.",
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"200": {"description": "ok"}},
                    }
                },
            },
        }
        create = contract_from_openapi(document, "/customers", "post")
        retrieve = contract_from_openapi(document, "/customers/{customer}", "get")
        self.assertEqual([slot.name for slot in create.required_inputs], ["email"])
        self.assertIn("customer.id", {slot.semantic_id for slot in create.outputs})
        self.assertEqual(retrieve.required_inputs[0].semantic_id, "customer.id")
        plan = plan_closure(
            "getCustomer", {"createCustomer": create, "getCustomer": retrieve},
            anchor={"values": {"customer.email": {"type": "string"}}},
        )
        self.assertEqual(plan.status, "COMPLETE_INFERRED")
        self.assertEqual(plan.operation_order, ("createCustomer", "getCustomer"))

    def test_required_path_parameter_without_schema_blocks_closure(self):
        document = {
            "openapi": "3.0.3", "info": {"title": "Missing path schema", "version": "1"},
            "paths": {"/customers/{customer}": {"get": {
                "operationId": "getCustomer",
                "parameters": [{"name": "customer", "in": "path", "required": True}],
                "responses": {"200": {"description": "ok"}}
            }}}
        }
        operation = contract_from_openapi(document, "/customers/{customer}", "get")
        result = plan_closure("getCustomer", {"getCustomer": operation}, anchor={})
        self.assertEqual(result.status, "INCOMPLETE")
        self.assertTrue(any(issue["kind"] == "contract_schema_unsupported" for issue in result.issues))

    def test_unresolved_path_parameter_reference_blocks_closure(self):
        document = {
            "openapi": "3.0.3", "info": {"title": "Unresolved parameter", "version": "1"},
            "paths": {"/customers/{customer}": {"get": {
                "operationId": "getCustomer",
                "parameters": [{"$ref": "#/components/parameters/Missing"}],
                "responses": {"200": {"description": "ok"}}
            }}}
        }
        operation = contract_from_openapi(document, "/customers/{customer}", "get")
        result = plan_closure("getCustomer", {"getCustomer": operation}, anchor={})
        self.assertEqual(result.status, "INCOMPLETE")
        self.assertTrue(any(issue["kind"] == "contract_schema_unsupported" for issue in result.issues))

    def test_required_body_with_unsupported_composition_blocks_closure(self):
        document = {
            "openapi": "3.0.3", "info": {"title": "Unsupported body", "version": "1"},
            "paths": {"/compose": {"post": {
                "operationId": "composedBody",
                "requestBody": {"required": True, "content": {"application/json": {
                    "schema": {"anyOf": [
                        {"type": "object", "required": ["customer"], "properties": {"customer": {"type": "string"}}},
                        {"type": "object", "required": ["account"], "properties": {"account": {"type": "string"}}},
                    ]}
                }}},
                "responses": {"204": {"description": "done"}}
            }}}
        }
        operation = contract_from_openapi(document, "/compose", "post")
        result = plan_closure("composedBody", {"composedBody": operation}, anchor={})
        self.assertEqual(result.status, "INCOMPLETE")
        self.assertTrue(any(issue["kind"] == "contract_schema_unsupported" for issue in result.issues))

    def test_only_guaranteed_outputs_across_all_success_responses_are_exposed(self):
        document = {
            "openapi": "3.0.3", "info": {"title": "Multi success", "version": "1"},
            "paths": {"/create": {"post": {
                "operationId": "createResource",
                "responses": {
                    "200": {"content": {"application/json": {"schema": {
                        "type": "object", "required": ["id"], "properties": {
                            "id": {"type": "string", "x-semantic-id": "resource.id"}
                        }
                    }}}},
                    "202": {"description": "accepted without a response body"}
                }
            }}}
        }
        operation = contract_from_openapi(document, "/create", "post")
        self.assertEqual(operation.outputs, ())

    def test_allof_unconstrained_branch_does_not_erase_a_declared_type(self):
        result = schema_compatibility(
            {"allOf": [{"type": "string"}, {"description": "constrained elsewhere"}]},
            {"type": "string"},
        )
        self.assertEqual(result.status, "SUPPORTED")

    def test_required_fields_inside_optional_request_body_are_not_operation_gates(self):
        document = {
            "openapi": "3.0.3",
            "info": {"title": "Optional body", "version": "1"},
            "paths": {"/optional": {"post": {
                "operationId": "optionalBody",
                "requestBody": {"required": False, "content": {"application/json": {
                    "schema": {"type": "object", "required": ["payload"], "properties": {
                        "payload": {"type": "string"}
                    }}
                }}},
                "responses": {"204": {"description": "done"}}
            }}}
        }
        operation = contract_from_openapi(document, "/optional", "post")
        self.assertEqual(operation.required_inputs, ())

    def test_required_request_body_reference_that_cannot_resolve_blocks_closure(self):
        document = {
            "openapi": "3.0.3", "info": {"title": "Unresolved body", "version": "1"},
            "paths": {"/create": {"post": {
                "operationId": "create", "requestBody": {"$ref": "#/components/requestBodies/Missing"},
                "responses": {"201": {"description": "created"}}
            }}}
        }
        operation = contract_from_openapi(document, "/create", "post")
        result = plan_closure("create", {"create": operation}, anchor={})
        self.assertEqual(result.status, "INCOMPLETE")
        self.assertEqual(result.operation_order, ())
        self.assertTrue(any(issue["kind"] == "contract_schema_unsupported" for issue in result.issues))

    def test_resource_reference_closes_a_documented_required_path_identifier(self):
        document = {
            "openapi": "3.0.3", "info": {"title": "Resource-reference flow", "version": "1"},
            "components": {"schemas": {"customer": {
                "type": "object", "required": ["id"],
                "properties": {"id": {"type": "string"}},
            }}},
            "paths": {
                "/customers": {"post": {
                    "operationId": "createCustomer",
                    "responses": {"201": {"content": {"application/json": {
                        "schema": {"$ref": "#/components/schemas/customer"}
                    }}}},
                    "security": [{"bearerAuth": []}, {"basicAuth": []}],
                }},
                "/customers/{customer}": {"get": {
                    "operationId": "getCustomer",
                    "parameters": [{
                        "name": "customer", "in": "path", "required": True,
                        "description": "The ID of the customer to retrieve.",
                        "schema": {"type": "string"},
                    }],
                    "responses": {"200": {"description": "ok"}},
                    "security": [{"bearerAuth": []}, {"basicAuth": []}],
                }},
            },
        }
        create = contract_from_openapi(document, "/customers", "post")
        retrieve = contract_from_openapi(document, "/customers/{customer}", "get")
        result = plan_closure(
            "getCustomer", {"createCustomer": create, "getCustomer": retrieve},
            anchor={"auth_schemes": ["bearerAuth"]},
        )
        self.assertEqual(result.status, "COMPLETE_INFERRED")
        self.assertEqual(result.operation_order, ("createCustomer", "getCustomer"))
        self.assertEqual(result.dependencies[0]["semantic_id"], "customer.id")

    def test_generic_path_identifier_is_bound_by_matching_collection_and_response_resources(self):
        customer = {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}}}
        deleted_customer = {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}}}
        path_parameter = {
            "name": "customer", "in": "path", "required": True,
            "description": "Unique identifier for the object.", "schema": {"type": "string"},
        }
        response_schema = {"anyOf": [
            {"$ref": "#/components/schemas/customer"},
            {"$ref": "#/components/schemas/deleted_customer"},
        ]}
        operation = {
            "operationId": "retrieveCustomer",
            "parameters": [path_parameter],
            "responses": {"200": {"content": {"application/json": {"schema": response_schema}}}},
        }
        document = {
            "openapi": "3.0.3", "info": {"title": "Path-to-resource binding", "version": "1"},
            "components": {"schemas": {"customer": customer, "deleted_customer": deleted_customer}},
            "paths": {"/v1/customers/{customer}": {"get": operation}},
        }
        compiled = contract_from_openapi(document, "/v1/customers/{customer}", "get")
        slot = compiled.required_inputs[0]
        self.assertEqual(slot.semantic_id, "customer.id")
        self.assertEqual(slot.evidence, "operation_response_resource")

    def test_generic_identifier_does_not_bind_when_path_and_response_resource_disagree(self):
        account = {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}}}
        operation = {
            "operationId": "retrieveCustomer",
            "parameters": [{
                "name": "customer", "in": "path", "required": True,
                "description": "Unique identifier for the object.", "schema": {"type": "string"},
            }],
            "responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/account"}}}}},
        }
        document = {
            "openapi": "3.0.3", "info": {"title": "Mismatched response resource", "version": "1"},
            "components": {"schemas": {"account": account}},
            "paths": {"/v1/customers/{customer}": {"get": operation}},
        }
        compiled = contract_from_openapi(document, "/v1/customers/{customer}", "get")
        self.assertIsNone(compiled.required_inputs[0].semantic_id)

    def test_generic_identifier_without_collection_context_is_not_semantic_identity(self):
        customer = {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}}}
        operation = {
            "operationId": "lookup",
            "parameters": [{
                "name": "customer", "in": "path", "required": True,
                "description": "Unique identifier for the object.", "schema": {"type": "string"},
            }],
            "responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/customer"}}}}},
        }
        document = {
            "openapi": "3.0.3", "info": {"title": "No resource path context", "version": "1"},
            "components": {"schemas": {"customer": customer}},
            "paths": {"/v1/lookup/{customer}": {"get": operation}},
        }
        compiled = contract_from_openapi(document, "/v1/lookup/{customer}", "get")
        self.assertIsNone(compiled.required_inputs[0].semantic_id)

    def test_path_response_join_requires_identifier_prose(self):
        customer = {"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}}}
        operation = {
            "operationId": "retrieveCustomer",
            "parameters": [{
                "name": "customer", "in": "path", "required": True,
                "description": "The object to retrieve.", "schema": {"type": "string"},
            }],
            "responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/customer"}}}}},
        }
        document = {
            "openapi": "3.0.3", "info": {"title": "Missing identifier prose", "version": "1"},
            "components": {"schemas": {"customer": customer}},
            "paths": {"/v1/customers/{customer}": {"get": operation}},
        }
        compiled = contract_from_openapi(document, "/v1/customers/{customer}", "get")
        self.assertIsNone(compiled.required_inputs[0].semantic_id)

    def test_name_only_identifier_pattern_is_not_promoted_by_an_unrelated_description(self):
        semantic_id, evidence = infer_semantic_id("customer_id", "Used when linking the record.")
        self.assertEqual(semantic_id, "customer.id")
        self.assertEqual(evidence, "name_only")
        documented_id, documented_evidence = infer_semantic_id(
            "customer_id", "Identifier for the customer to retrieve."
        )
        self.assertEqual(documented_id, "customer.id")
        self.assertEqual(documented_evidence, "description")

    def test_pinned_git_blob_digest_is_verified_when_parsing(self):
        raw = json.dumps({"openapi": "3.0.3", "paths": {}}, separators=(",", ":")).encode()
        digest = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        parse_openapi_json(raw, expected_git_blob_sha1=digest)
        with self.assertRaisesRegex(ValueError, "SHA-1 mismatch"):
            parse_openapi_json(raw, expected_git_blob_sha1="0" * 40)

    def test_name_only_similarity_does_not_create_semantic_identity(self):
        document = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1"},
            "paths": {
                "/a": {"post": {"operationId": "create", "responses": {"200": {"description": "ok"}}}},
                "/b": {
                    "get": {
                        "operationId": "read",
                        "parameters": [{"name": "customer", "in": "path", "required": True, "schema": {"type": "string"}}],
                        "responses": {"200": {"description": "ok"}},
                    }
                },
            },
        }
        create = contract_from_openapi(document, "/a", "post")
        read = contract_from_openapi(document, "/b", "get")
        self.assertFalse(create.outputs)
        self.assertIsNone(read.required_inputs[0].semantic_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
