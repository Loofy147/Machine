# Typed Contract Closure v0.2

A conservative, offline verifier for typed API contracts and prerequisite closure. This is a stricter layer beside the v0.1 context-pair planner; it does not replace or silently change the v0.1 existential pair-admission rule.

## What it verifies

Given a target operation, a registry of operations, and externally established anchor facts, the planner attempts to construct a low-cost acyclic order in which **every required input of every selected operation** is supplied by a typed anchor value or by a guaranteed output of an earlier operation.

A candidate dependency must pass all three gates:

1. **Semantic identity:** the input and output refer to the same stable semantic ID. Explicit `x-semantic-id` metadata is strongest. A resource `$ref` (such as `#/components/schemas/customer` exposing a required `id`) and a direct API description such as “the ID of the customer” are accepted as *documented inference*, not as explicit identity. A field name alone (`customer_id`) is not enough to close a dependency.
2. **Type assignability:** the producer's whole declared value domain must fit the consumer's accepted domain. The implemented subset checks JSON types, null, enum/const domains, formats, patterns, numeric and size bounds, arrays, and directly declared object properties/required fields. Incompatible or unresolved schemas do not count as matches.
3. **Prerequisite and security closure:** all required inputs of candidate providers must themselves be closed. Cycles, unresolved required contract fragments, and missing security-scheme preconditions block a plan.

The planner is a verifier only. It does not execute HTTP requests, store tokens, verify that credentials are valid, or assert that an API call will succeed at runtime. The `auth_schemes` anchor records a declared external precondition only.

## Result states

| Status | Meaning |
|---|---|
| `COMPLETE_EXPLICIT` | Full closure; semantic links use explicit IDs; bounded search was exhausted, so the configured cost optimum is proven within the registered operation set. |
| `COMPLETE_INFERRED` | Full closure; at least one link relies on documented inference; search was exhausted. This is not equivalent to explicit semantic proof. |
| `FEASIBLE_SEARCH_LIMIT` | A feasible plan was found, but the search limit prevented proving that it is minimum-cost. |
| `SEARCH_LIMIT` | The limit was reached before a feasible plan was established. |
| `INCOMPLETE` | At least one required input, type check, contract fragment, cycle, or external precondition prevents closure. |

The default expansion budget is 2,000. The planner must not report optimality when alternatives were pruned by that budget.

## Real source benchmark

`run_openapi_corpus.py` fetches a **pinned** Stripe OpenAPI document and verifies the canonical Git blob SHA-1 before parsing it:

- Repository: [`stripe/openapi`](https://github.com/stripe/openapi)
- Commit: `51610f5f061c9723730582a7638b8cc0e646640d`
- File: `latest/openapi.spec3.json`
- Git blob SHA-1: `9270d090ab4961efd0eb1a751410d210af929e99`
- Upstream repository license: MIT

The benchmark uses two real operations from that pinned specification: `POST /v1/customers` and `GET /v1/customers/{customer}`. It checks whether the create response's required customer `id` can satisfy the retrieve operation's required path input, which is described as the ID of the customer. The source does not carry an explicit shared `x-semantic-id`; the expected result is therefore `COMPLETE_INFERRED`, not `COMPLETE_EXPLICIT`.

The same run executes four negative controls: strict explicit-ID-only mode, a consumer type mutation, a missing auth-scheme precondition, and removal of the path description leaving only a field name. All must be rejected. The runner downloads a public specification only; it does not call Stripe endpoints or use credentials.

```bash
python -m unittest -v
python run_openapi_corpus.py --output OPENAPI-CORPUS-RESULTS.json
```

The runner uses only the Python standard library. GitHub Actions downloads the pinned specification, verifies its blob identity and uploads the machine-readable result as an artifact.

## Deliberate limits

This is not a complete JSON Schema or OpenAPI implementation. It deliberately blocks or leaves unresolved constructs it does not prove, including external `$ref` targets, composed required request-body objects (`allOf`/`anyOf`/`oneOf` at the body root), conditional/dependent schemas, full regular-expression implication, discriminator semantics, and some advanced array/object constraints. Required-body extraction currently supports directly declared object bodies and top-level required properties; outputs are only fields guaranteed across all declared successful 2xx JSON responses. Non-JSON response representations are outside this benchmark's scope.

Descriptions are narrow semantic evidence, not a substitute for domain-specific ontology validation. A documented description can be stale, ambiguous or wrong. The verifier reports the evidence class so downstream policy can demand explicit IDs where inference risk is unacceptable.

The Stripe source validates interface-contract behavior in one API. It does **not** establish cross-provider composition, legal or commercial obligation compatibility, production runtime success, or business value. CUAD/MAUD/ACORD are separate legal-contract research candidates; no legal obligation extraction or clause-composition claim is made in this version.

See [`docs/research/TYPED-CONTRACT-CLOSURE-OPENAPI-v0.2.md`](../../docs/research/TYPED-CONTRACT-CLOSURE-OPENAPI-v0.2.md) for the research record, provenance, findings and next gates.
