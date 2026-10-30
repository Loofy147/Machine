# Typed Contract Closure over Real OpenAPI — v0.2

**Status:** EXPERIMENTAL IMPLEMENTATION  
**Scope:** typed API interface contracts and prerequisite closure  
**Code:** `experiments/typed-contract-closure-v0.2/`  
**Baseline:** `Loofy147/Machine` PR #31, branch `experiment/context-contract-distribution-center-v0.1`

## 1. Why this layer exists

The v0.1 planner tested context-pair compatibility, but its pair admission was existential: one satisfied need in one direction could admit a pair while other needs remained unsatisfied. That is a useful exploratory pairing primitive, not a proof that an entire workflow can execute in dependency order.

The v0.2 layer asks a stricter question:

> Can every mandatory input of a target operation, and every mandatory input of its prerequisite providers, be supplied by typed and semantically evidenced outputs or pre-existing anchor state?

This is an offline verification problem. It does not send requests, validate credentials, or treat a planned workflow as authorized execution.

## 2. Source choice and provenance

### Chosen source: Stripe OpenAPI

The `stripe/openapi` repository describes Stripe's API in OpenAPI 3 and documents that its `latest/` directory contains the current GA specification. Its repository README recommends the public `openapi.spec3.json`/YAML variant for API consumers; it distinguishes those public specs from SDK-specific variants.

The benchmark pins an immutable source identity:

| Field | Pinned value |
|---|---|
| Repository | `stripe/openapi` |
| Commit | `51610f5f061c9723730582a7638b8cc0e646640d` |
| Commit date | 2026-10-29T22:36:39Z |
| Path | `latest/openapi.spec3.json` |
| Git blob SHA-1 | `9270d090ab4961efd0eb1a751410d210af929e99` |
| File size in Git tree | 5,070,331 bytes |
| Repository license | MIT |

The workflow fetches the raw file at that commit, computes Git's canonical blob hash (`blob <length>\0<bytes>`), rejects any mismatch, and emits an SHA-256 checksum in its JSON artifact. The exact source is therefore not allowed to drift with the moving `master` branch.

The benchmark is intentionally small and interpretable:

- Provider: `POST /v1/customers`.
- Consumer: `GET /v1/customers/{customer}`.
- Provider guarantee: the customer resource response schema requires `id`; the component `$ref` scopes that identifier to the customer resource.
- Consumer requirement: the `customer` path parameter is required and its description identifies it as the ID of the customer to retrieve.
- Type: string on both sides.
- Security: both operations declare auth alternatives; the benchmark supplies `bearerAuth` as an external scheme precondition. No token or live request is used.

The link is inferred from a resource reference and a field description. It is **not** explicit machine-readable semantic identity (`x-semantic-id`). Thus the positive outcome is expected to be `COMPLETE_INFERRED`. Strict explicit-ID mode must reject the same link.

### Legal-contract datasets: separate future track

CUAD is a real commercial-contract corpus (510 contracts, 41 clause categories, and more than 13,000 expert labels) released under CC BY 4.0. The Atticus project also indexes MAUD and ACORD resources, which may be useful for deal-point and clause-retrieval tasks. These are appropriate sources for a separate obligation/term extraction benchmark, but their clause labels alone do not define actor, trigger, timing, state transition, exception, remedy, or dependency relations. This v0.2 API-spec experiment does not claim legal-contract validation.

Sources:
- APIs.guru OpenAPI directory and API catalogue: https://github.com/APIs-guru/openapi-directory and https://apis.guru/.
- Stripe OpenAPI repository and pinned source: https://github.com/stripe/openapi/tree/51610f5f061c9723730582a7638b8cc0e646640d/latest.
- CUAD: https://www.atticusprojectai.org/cuad and https://github.com/TheAtticusProject/cuad.
- Atticus project dataset directory (including MAUD and ACORD): https://www.atticusprojectai.org/.

## 3. Implemented architecture

### 3.1 Contract normalization

`contract_from_openapi` compiles an OpenAPI 3 operation into:
- required path/query/header/cookie parameter slots;
- required top-level properties of a directly declared required object request body;
- response slots that are required and schema-identical across every declared 2xx response, when every such response has a supported JSON schema;
- security alternatives and static unsupported-contract issues.

OpenAPI operation-level parameters override same-name/in parameters declared at path level. Path placeholders without matching required parameter schemas block closure. A `requestBody` is optional unless its `required` flag is true; required properties inside an optional body are not mistaken for operation-level mandatory inputs.

Internal component `$ref` references are resolved. An unresolved required parameter or body reference is a blocker, not an empty schema.

### 3.2 Semantic evidence

The adapter recognizes three usable evidence classes:

- `explicit`: a non-empty `x-semantic-id` extension;
- `resource_ref`: an `id` field scoped by a resource component `$ref`;
- `description`: a narrow phrase in the operation contract, such as “the ID of the customer”.

`name_only` and `unknown` are retained as diagnostics but are not accepted to close a dependency. There is no embedding similarity or fuzzy field-name matching.

### 3.3 Type assignability

A producer output is considered usable only if all values allowed by its supported schema are accepted by the consumer schema. The checker includes:

- JSON primitive types and `integer` → `number` widening (not the reverse);
- nullable values and `null` branches;
- finite `enum`/`const` domain inclusion;
- format agreement when the consumer requires a format;
- exact pattern agreement where required (otherwise implication remains UNKNOWN);
- numeric inclusive/exclusive bounds;
- string length and array/object size constraints;
- array-item schema compatibility;
- direct object required-property and nested-property checks;
- type unions in `anyOf`/`oneOf` and type intersections in `allOf` where the checker can prove them.

An unsupported or unresolved fragment is not silently promoted to SUPPORTED. The adapter blocks composed required body schemas rather than pretending to flatten them safely. This is a conservative subset checker, not a full JSON Schema validator.

### 3.4 Dependency closure and search

A bounded DFS recursively resolves provider prerequisites, prevents cycles, and requires every selected operation to pass its external security-scheme precondition. The objective is lowest declared cost, then fewest operations, then lexical order. Default operation cost is 1, so it is currently a deterministic planning cost, not a measured API cost.

All alternatives are explored until the expansion budget is exhausted. If a feasible plan is found after the search budget is hit, status is `FEASIBLE_SEARCH_LIMIT` and `optimality_proven=false`; it is not mislabeled complete/optimal. The digest includes operation provenance, slot descriptions/evidence/source paths, schema constraints, security, contract issues, anchor data and algorithm version.

## 4. Tests and mutation controls

The test suite covers:

- integer-to-number widening and reverse rejection;
- nullable producer to non-null consumer rejection;
- enum subset and unbounded producer behavior;
- `anyOf` union and nullable branches;
- exclusive numeric bound semantics;
- object required-property and nested type checks;
- array item schema checks;
- multi-hop closure and full required-input coverage;
- provider cost selection when search is exhaustive;
- search-limit feasible-but-not-optimal reporting;
- dependency cycles;
- same semantic ID with type mismatch;
- insufficient name-only evidence rejection;
- required inputs and guaranteed output extraction from OpenAPI;
- optional-body semantics;
- unsupported required-body composition, unresolved references and missing path schemas;
- all-2xx response output guarantees;
- security preconditions outside the execution layer;
- digest changes when descriptions/evidence change.

The pinned-source integration runner adds actual-data controls:

1. verify immutable Git blob identity;
2. accept the documented provider → consumer customer-ID link as `COMPLETE_INFERRED`;
3. reject the same link under explicit-ID-only mode;
4. reject a type mutation (string output to integer input);
5. reject a missing auth-scheme precondition;
6. reject removal of description evidence, leaving only a field name.

The Python-only local suite is deterministic and uses the standard library. The actual full specification download and its pinned hash check run in GitHub Actions; this offline environment could not independently fetch the full 5 MB source file. The integration result must be taken from the pinned-source CI artifact, not claimed from local unit tests.

## 5. Decision and claim boundary

**EXPERIMENTALLY_SUPPORTED:** a conservative, testable pipeline can derive one prerequisite edge from real OpenAPI response references and an explicitly documented required path parameter, enforce type compatibility, require full recursive closure, and refuse the same edge when evidence or type constraints are weakened.

**Not established:**
- broad semantic equivalence between independently designed APIs;
- cross-provider or multi-domain API composition;
- complete OpenAPI or JSON Schema semantics;
- runtime availability, side effects, idempotency, retries, rate limits, credential validity or authorization scope;
- legal/commercial obligation extraction, interpretation or clause compatibility;
- any measurable production efficiency or business value.

The implementation stays opt-in and experimental. It does not change v0.1 results, Rust cache promotion criteria, production systems or PR merge state.

## 6. Next discriminating tests

1. **Broader API corpus:** sample independent APIs from the APIs.guru directory, pin every source revision and license, and measure how often documented semantic links can be proved without name-only assumptions.
2. **Cross-provider semantic identities:** add explicit canonical semantic IDs and versioning, then test whether mappings remain correct when names, response shapes and API versions differ. Do not use embedding similarity as an execution gate.
3. **Legal-contract benchmark:** fetch CUAD/MAUD/ACORD from official sources, preserve clause-level citations and license terms, then build an obligation representation containing actor, modal force, action, subject, trigger, deadline, preconditions, exception, remedy and evidence. Test clause extraction separately from obligation composition; require expert-labeled relation checks before calling it verified.
4. **Execution contract:** only after offline closure holds, specify auth scope, idempotency, state effects, compensations, failure/retry behavior, rate limits, version compatibility and audit evidence. No dispatcher should run on the strength of inferred semantics alone.
