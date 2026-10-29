"""Explicit event-vector and symbolic cost model for predecessor access."""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Literal

OPAQUE_FORWARD = "opaque_forward"
GENERIC_REVERSE_INDEX = "generic_reverse_index"
SPECIALIZED_FIBER_LOOKUP = "specialized_fiber_lookup"
Profile = Literal["opaque_forward", "generic_reverse_index", "specialized_fiber_lookup"]


@dataclass(frozen=True)
class AccessWeights:
    """Caller-declared positive weights; no default scalar costs are provided."""
    transition_probe: float
    state_read: float
    fiber_lookup: float
    output_entry: float

    def __post_init__(self) -> None:
        for name in ("transition_probe", "state_read", "fiber_lookup", "output_entry"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} weight must be a finite positive number")


def _validate_dimensions(transition_count: int, indegree: int) -> None:
    if isinstance(transition_count, bool) or not isinstance(transition_count, int) or transition_count < 0:
        raise ValueError("transition_count must be a non-negative integer")
    if isinstance(indegree, bool) or not isinstance(indegree, int) or indegree < 0:
        raise ValueError("indegree must be a non-negative integer")
    if indegree > transition_count:
        raise ValueError("indegree cannot exceed transition_count")


def query_events(profile: str, transition_count: int, indegree: int) -> dict[str, int]:
    """Return event vector; output entries are charged identically for every profile."""
    _validate_dimensions(transition_count, indegree)
    events = {
        "transition_probes": 0,
        "generic_state_reads": 0,
        "fiber_lookup_calls": 0,
        "scan_entries": 0,
        "output_entries": indegree,
    }
    if profile == OPAQUE_FORWARD:
        events["transition_probes"] = transition_count
    elif profile == GENERIC_REVERSE_INDEX:
        events["generic_state_reads"] = 2 + 2 * indegree
    elif profile == SPECIALIZED_FIBER_LOOKUP:
        events["fiber_lookup_calls"] = 1
    else:
        raise ValueError(f"unknown access profile: {profile}")
    return events


def weighted_query_cost(profile: str, transition_count: int, indegree: int, weights: AccessWeights) -> float:
    """Evaluate cost only after the caller declares weights for unlike events."""
    events = query_events(profile, transition_count, indegree)
    return (
        events["transition_probes"] * weights.transition_probe
        + events["generic_state_reads"] * weights.state_read
        + events["fiber_lookup_calls"] * weights.fiber_lookup
        + events["output_entries"] * weights.output_entry
    )


def csr_resource_footprint(state_count: int, edge_count: int) -> dict[str, int]:
    """Declared CSR construction units and bytes, separate from baseline delta storage."""
    if isinstance(state_count, bool) or not isinstance(state_count, int) or state_count <= 0:
        raise ValueError("state_count must be a positive integer")
    if isinstance(edge_count, bool) or not isinstance(edge_count, int) or edge_count < 0:
        raise ValueError("edge_count must be a non-negative integer")
    return {
        "offline_build_work_units": 2 * edge_count + state_count,
        "persistent_bytes": 4 * (state_count + 1) + 5 * edge_count,
    }


def break_even_conditions(transition_count: int, indegree: int) -> dict[str, str]:
    """Return symbolic inequalities; do not assign empirical costs implicitly."""
    _validate_dimensions(transition_count, indegree)
    return {
        "specialized_vs_generic": f"c_fiber_lookup < c_state_read * {2 + 2 * indegree}",
        "specialized_vs_opaque": f"c_fiber_lookup < c_transition_probe * {transition_count}",
        "generic_vs_opaque": f"c_state_read * {2 + 2 * indegree} < c_transition_probe * {transition_count}",
        "assumption": "same output cost; generic and specialized profiles share the same prebuilt CSR representation",
    }
