"""Emit vector-valued predecessor access costs and symbolic break-even rules."""
from __future__ import annotations
import json
from pathlib import Path
from cost_model import (
    GENERIC_REVERSE_INDEX, OPAQUE_FORWARD, SPECIALIZED_FIBER_LOOKUP,
    break_even_conditions, csr_resource_footprint, query_events,
)


def main() -> None:
    profiles = (OPAQUE_FORWARD, GENERIC_REVERSE_INDEX, SPECIALIZED_FIBER_LOOKUP)
    rows = []
    for edge_count in (10, 100, 1000):
        degrees = sorted({0, 1, min(10, edge_count), edge_count})
        for degree in degrees:
            vectors = {profile: query_events(profile, edge_count, degree) for profile in profiles}
            assert {vector["output_entries"] for vector in vectors.values()} == {degree}
            assert vectors[GENERIC_REVERSE_INDEX]["generic_state_reads"] == 2 + 2 * degree
            assert vectors[SPECIALIZED_FIBER_LOOKUP]["fiber_lookup_calls"] == 1
            assert vectors[OPAQUE_FORWARD]["transition_probes"] == edge_count
            rows.append({
                "transition_count_E": edge_count,
                "indegree_d": degree,
                "events": vectors,
                "break_even_conditions": break_even_conditions(edge_count, degree),
            })

    footprints = []
    for n, edge_count in ((10, 10), (100, 100), (100, 1000)):
        footprints.append({
            "state_count_n": n,
            "edge_count_E": edge_count,
            **csr_resource_footprint(n, edge_count),
        })

    result = {
        "schema": "machine.predecessor-access-cost-normalization.v0.1",
        "status": "PASS",
        "method": "vector-valued event accounting plus symbolic break-even conditions",
        "no_default_scalar_costs": True,
        "output_cardinality_equal_across_profiles": True,
        "online_profiles": [
            {
                "profile": OPAQUE_FORWARD,
                "definition": "opaque forward scan; charges E transition probes and d returned entries",
                "preprocessing": "none in this query model",
                "storage": "no inverse CSR",
            },
            {
                "profile": GENERIC_REVERSE_INDEX,
                "definition": "generic indexed reads over prebuilt CSR; charges two offsets and two payload reads per predecessor",
                "preprocessing": "count + prefix + scatter abstraction, B_off=2E+n",
                "storage": "int32 offsets + int32 source + uint8 action, R=4(n+1)+5E bytes",
            },
            {
                "profile": SPECIALIZED_FIBER_LOOKUP,
                "definition": "specialized fiber lookup over the same prebuilt CSR; charges one explicit lookup event and d returned entries",
                "preprocessing": "same as generic reverse-index profile",
                "storage": "same as generic reverse-index profile",
                "physical_internal_access_cost": "UNKNOWN; represented by caller-supplied c_fiber_lookup",
            },
        ],
        "break_even_rule": {
            "specialized_beats_generic": "c_fiber_lookup < c_state_read * (2 + 2d)",
            "specialized_beats_opaque": "c_fiber_lookup < c_transition_probe * E",
            "generic_beats_opaque": "c_state_read * (2 + 2d) < c_transition_probe * E",
            "conditions": "same output cost; generic and specialized profiles share the same prebuilt CSR representation",
        },
        "query_sweep": rows,
        "representation_footprint_sweep": footprints,
        "conclusion": {
            "direct_predecessor_computability_advantage": "NOT_ESTABLISHED",
            "resource_advantage": "CONDITIONAL_ON_DECLARED_EVENT_WEIGHTS_AND_OFFLINE_STORAGE_BUDGETS",
            "universal_scalar_winner": "NOT_IDENTIFIABLE_WITHOUT_A_DECLARED_COST_MODEL",
        },
        "limits": [
            "Cost weights are symbolic parameters, not empirical latency estimates.",
            "The specialized lookup internal cost is not assumed to be one operation or free.",
            "The CSR footprint assumes int32 offsets, int32 source payloads, and uint8 action payloads.",
            "Finite structural accounting is not an asymptotic lower-bound proof.",
        ],
    }
    output_path = Path(__file__).with_name("COST-NORMALIZATION-V0.1.json")
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
