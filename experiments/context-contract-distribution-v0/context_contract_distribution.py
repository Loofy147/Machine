#!/usr/bin/env python3
"""Auditable, offline contract-context distribution planner.

A fixed anchor filters contexts by fact consistency. Eligible contexts are
connected when their facts are mutually consistent and at least one context
satisfies a declared need of the other. A distribution is a matching: every
selected context belongs to exactly one serving pair.

No model calls, network access, persistence, or external side effects occur.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from itertools import combinations
from types import MappingProxyType
from typing import Any, Iterable, Mapping, TypeAlias

import networkx as nx


SCHEMA = "context-contract-distribution-plan.v0.1"
ALGORITHM = "max-weight-matching.lexicographic-utility-then-count.v0.1"
JsonScalar: TypeAlias = str | int | float | bool | None
NeedInput: TypeAlias = Mapping[str, JsonScalar | None] | Iterable[str]


def _validate_scalar(value: Any, *, where: str) -> JsonScalar:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise ValueError(f"{where} must be a finite JSON scalar (string, number, boolean, or null)")


def _same_value(left: JsonScalar, right: JsonScalar) -> bool:
    """Strict JSON-value equality; notably, bool is not treated as int."""
    return type(left) is type(right) and left == right


def consistent(left: Mapping[str, JsonScalar], right: Mapping[str, JsonScalar]) -> bool:
    """Return whether shared fact keys have exactly equal typed values."""
    return all(_same_value(left[key], right[key]) for key in left.keys() & right.keys())


@dataclass(frozen=True)
class ContractContext:
    """One candidate contract/context in the distribution ground set.

    needs may be a mapping of key -> expected value. Use None as the
    expected value to mean "the provider must contain this key, value agnostic".
    For compatibility with the original sketch, an iterable of strings also
    works and means presence-only needs.

    utility is a non-negative integer optimization value. If omitted,
    len(facts) is used as an explicitly weak demonstration proxy.
    """

    context_id: str
    facts: Mapping[str, JsonScalar]
    needs: NeedInput = field(default_factory=dict)
    utility: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.context_id, str) or not self.context_id.strip():
            raise ValueError("context_id must be a non-empty string")
        if not isinstance(self.facts, Mapping):
            raise ValueError(f"facts for {self.context_id!r} must be a mapping")

        normalized_facts: dict[str, JsonScalar] = {}
        for key, value in self.facts.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"fact keys for {self.context_id!r} must be non-empty strings")
            normalized_facts[key] = _validate_scalar(value, where=f"facts[{key!r}]")

        normalized_needs: dict[str, JsonScalar | None] = {}
        if isinstance(self.needs, Mapping):
            need_items = self.needs.items()
        else:
            if isinstance(self.needs, (str, bytes)):
                raise ValueError("needs must be a mapping or an iterable of key strings, not one string")
            try:
                need_items = ((key, None) for key in self.needs)
            except TypeError as exc:
                raise ValueError("needs must be a mapping or an iterable of key strings") from exc

        for key, expected in need_items:
            if not isinstance(key, str) or not key:
                raise ValueError(f"need keys for {self.context_id!r} must be non-empty strings")
            normalized_needs[key] = _validate_scalar(expected, where=f"needs[{key!r}]")

        if self.utility is not None and (type(self.utility) is not int or self.utility < 0):
            raise ValueError("utility must be a non-negative integer or None")

        object.__setattr__(self, "facts", MappingProxyType(dict(sorted(normalized_facts.items()))))
        object.__setattr__(self, "needs", MappingProxyType(dict(sorted(normalized_needs.items()))))

    @property
    def value(self) -> int:
        return len(self.facts) if self.utility is None else self.utility

    def canonical_dict(self) -> dict[str, Any]:
        return {
            "id": self.context_id,
            "facts": dict(self.facts),
            "needs": dict(self.needs),
            "utility": self.utility,
        }


@dataclass(frozen=True)
class AnchorExclusion:
    context_id: str
    conflicts: Mapping[str, tuple[JsonScalar, JsonScalar]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "conflicts": {
                key: {"context_value": context_value, "anchor_value": anchor_value}
                for key, (context_value, anchor_value) in self.conflicts.items()
            },
        }


@dataclass(frozen=True)
class NeedWitness:
    key: str
    required_value: JsonScalar | None
    supplied_value: JsonScalar

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "required_value": self.required_value,
            "supplied_value": self.supplied_value,
            "matching_mode": "presence_only" if self.required_value is None else "exact_value",
        }


@dataclass(frozen=True)
class UnmetNeed:
    key: str
    required_value: JsonScalar | None
    provider_has_key: bool
    supplied_value: JsonScalar | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "required_value": self.required_value,
            "provider_has_key": self.provider_has_key,
            "supplied_value": self.supplied_value,
        }


@dataclass(frozen=True)
class ServiceWitness:
    consumer: str
    provider: str
    needs: tuple[NeedWitness, ...]
    unmet_needs: tuple[UnmetNeed, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "consumer": self.consumer,
            "provider": self.provider,
            "satisfied_needs": [need.to_dict() for need in self.needs],
            "unmet_needs_with_this_partner": [need.to_dict() for need in self.unmet_needs],
            "all_needs_satisfied_by_this_partner": not self.unmet_needs,
        }


@dataclass(frozen=True)
class PairPlan:
    left: str
    right: str
    services: tuple[ServiceWitness, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "left": self.left,
            "right": self.right,
            "services": [service.to_dict() for service in self.services],
        }


@dataclass(frozen=True)
class DistributionPlan:
    schema: str
    algorithm: str
    input_digest: str
    anchor: Mapping[str, JsonScalar]
    registered_contexts: tuple[str, ...]
    eligible_contexts: tuple[str, ...]
    anchor_exclusions: tuple[AnchorExclusion, ...]
    selected_contexts: tuple[str, ...]
    unmatched_eligible: tuple[str, ...]
    isolated_eligible: tuple[str, ...]
    pairs: tuple[PairPlan, ...]
    total_utility: int
    utility_by_context: Mapping[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "algorithm": self.algorithm,
            "input_digest_sha256": self.input_digest,
            "anchor": dict(self.anchor),
            "registered_contexts": list(self.registered_contexts),
            "eligible_contexts": list(self.eligible_contexts),
            "anchor_exclusions": [item.to_dict() for item in self.anchor_exclusions],
            "selected_contexts": list(self.selected_contexts),
            "unmatched_eligible": list(self.unmatched_eligible),
            "isolated_eligible": list(self.isolated_eligible),
            "pairs": [pair.to_dict() for pair in self.pairs],
            "objective": {
                "total_utility": self.total_utility,
                "selected_context_count": len(self.selected_contexts),
                "ordering": ["maximize_total_utility", "then_maximize_selected_context_count"],
            },
            "utility_by_context": dict(self.utility_by_context),
        }


@dataclass(frozen=True)
class PlanDelta:
    old_schema: str
    new_schema: str
    old_algorithm: str
    new_algorithm: str
    old_digest: str
    new_digest: str
    anchor_changed: bool
    newly_registered: tuple[str, ...]
    removed_from_registry: tuple[str, ...]
    newly_eligible: tuple[str, ...]
    newly_excluded: tuple[str, ...]
    selected_added: tuple[str, ...]
    selected_removed: tuple[str, ...]
    pairing_added: tuple[tuple[str, str], ...]
    pairing_removed: tuple[tuple[str, str], ...]
    service_changed_pairs: tuple[tuple[str, str], ...]
    utility_changed_contexts: tuple[str, ...]
    old_total_utility: int
    new_total_utility: int
    utility_delta: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "old_schema": self.old_schema,
            "new_schema": self.new_schema,
            "old_algorithm": self.old_algorithm,
            "new_algorithm": self.new_algorithm,
            "old_digest_sha256": self.old_digest,
            "new_digest_sha256": self.new_digest,
            "anchor_changed": self.anchor_changed,
            "newly_registered": list(self.newly_registered),
            "removed_from_registry": list(self.removed_from_registry),
            "newly_eligible": list(self.newly_eligible),
            "newly_excluded": list(self.newly_excluded),
            "selected_added": list(self.selected_added),
            "selected_removed": list(self.selected_removed),
            "pairing_added": [list(pair) for pair in self.pairing_added],
            "pairing_removed": [list(pair) for pair in self.pairing_removed],
            "service_changed_pairs": [list(pair) for pair in self.service_changed_pairs],
            "utility_changed_contexts": list(self.utility_changed_contexts),
            "old_total_utility": self.old_total_utility,
            "new_total_utility": self.new_total_utility,
            "utility_delta": self.utility_delta,
        }


def _need_witnesses(consumer: ContractContext, provider: ContractContext) -> tuple[NeedWitness, ...]:
    witnesses: list[NeedWitness] = []
    for key, expected in consumer.needs.items():
        if key not in provider.facts:
            continue
        supplied = provider.facts[key]
        if expected is None or _same_value(expected, supplied):
            witnesses.append(NeedWitness(key, expected, supplied))
    return tuple(witnesses)


def _service_witness(consumer: ContractContext, provider: ContractContext) -> ServiceWitness | None:
    witnesses = _need_witnesses(consumer, provider)
    if not witnesses:
        return None
    satisfied_keys = {witness.key for witness in witnesses}
    unmet = tuple(
        UnmetNeed(
            key=key,
            required_value=expected,
            provider_has_key=key in provider.facts,
            supplied_value=provider.facts.get(key),
        )
        for key, expected in consumer.needs.items()
        if key not in satisfied_keys
    )
    return ServiceWitness(consumer.context_id, provider.context_id, witnesses, unmet)


def _anchor_conflicts(
    context: ContractContext, anchor: Mapping[str, JsonScalar]
) -> dict[str, tuple[JsonScalar, JsonScalar]]:
    return {
        key: (context.facts[key], anchor[key])
        for key in sorted(context.facts.keys() & anchor.keys())
        if not _same_value(context.facts[key], anchor[key])
    }


def _canonical_digest(contexts: tuple[ContractContext, ...], anchor: Mapping[str, JsonScalar]) -> str:
    payload = {
        "schema": SCHEMA,
        "algorithm": ALGORITHM,
        "anchor": dict(sorted(anchor.items())),
        "contexts": [context.canonical_dict() for context in contexts],
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _validate_anchor(anchor: Mapping[str, Any]) -> dict[str, JsonScalar]:
    if not isinstance(anchor, Mapping):
        raise ValueError("anchor must be a mapping")
    normalized: dict[str, JsonScalar] = {}
    for key, value in anchor.items():
        if not isinstance(key, str) or not key:
            raise ValueError("anchor keys must be non-empty strings")
        normalized[key] = _validate_scalar(value, where=f"anchor[{key!r}]")
    return dict(sorted(normalized.items()))


def _normalize_contexts(contexts: Iterable[ContractContext]) -> tuple[ContractContext, ...]:
    unsorted_contexts = tuple(contexts)
    if any(not isinstance(item, ContractContext) for item in unsorted_contexts):
        raise ValueError("contexts must contain only ContractContext instances")
    context_list = tuple(sorted(unsorted_contexts, key=lambda item: item.context_id))
    ids = [item.context_id for item in context_list]
    if len(set(ids)) != len(ids):
        raise ValueError("context_id values must be unique")
    return context_list


def _build_compatibility_graph(eligible: tuple[ContractContext, ...]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(
        (item.context_id, {"utility": item.value}) for item in eligible
    )
    # The secondary context-count objective can add at most N utility points
    # from all edge tie-breakers, so N+1 keeps total utility lexicographically primary.
    primary_scale = len(eligible) + 1
    for left, right in combinations(eligible, 2):
        if not consistent(left.facts, right.facts):
            continue
        services: list[ServiceWitness] = []
        left_served = _service_witness(left, right)
        right_served = _service_witness(right, left)
        if left_served:
            services.append(left_served)
        if right_served:
            services.append(right_served)
        if not services:
            continue
        score = (left.value + right.value) * primary_scale + 2
        graph.add_edge(
            left.context_id,
            right.context_id,
            weight=score,
            services=tuple(services),
        )
    return graph


def build_compatibility_graph(
    contexts: Iterable[ContractContext], anchor: Mapping[str, JsonScalar]
) -> nx.Graph:
    """Expose the eligible-context graph for diagnostics and small-scale audits.

    Nodes are context IDs. Edges have integer weight and directional
    service witnesses. The returned graph is a fresh mutable copy; changing it
    cannot mutate any ContractContext or any previously returned plan.
    """
    context_list = _normalize_contexts(contexts)
    anchor_values = _validate_anchor(anchor)
    eligible = tuple(
        item for item in context_list if not _anchor_conflicts(item, anchor_values)
    )
    return _build_compatibility_graph(eligible)


def plan_distribution(
    contexts: Iterable[ContractContext], anchor: Mapping[str, JsonScalar]
) -> DistributionPlan:
    """Compute a maximum-utility, fully paired context distribution.

    Objective is lexicographic: (1) maximize total selected utility, then
    (2) maximize selected context count. The second criterion ensures that
    zero-utility pairs are retained when they do not reduce total utility.
    A selected context is always an endpoint of exactly one returned pair.
    Pair admission remains existential: at least one need is satisfied in at
    least one direction. Each direction also reports any needs the partner
    does not satisfy, preventing a partial link from looking like full closure.
    """
    anchor_values = _validate_anchor(anchor)
    context_list = _normalize_contexts(contexts)
    ids = [item.context_id for item in context_list]
    conflicts_by_id = {item.context_id: _anchor_conflicts(item, anchor_values) for item in context_list}
    eligible = tuple(item for item in context_list if not conflicts_by_id[item.context_id])
    excluded = tuple(
        AnchorExclusion(item.context_id, MappingProxyType(conflicts_by_id[item.context_id]))
        for item in context_list if conflicts_by_id[item.context_id]
    )

    graph = _build_compatibility_graph(eligible)
    matching = nx.max_weight_matching(graph, maxcardinality=False, weight="weight")
    normalized_pairs: list[PairPlan] = []
    selected: set[str] = set()
    for first, second in matching:
        left_id, right_id = sorted((first, second))
        selected.update((left_id, right_id))
        edge = graph[left_id][right_id]
        services = tuple(sorted(
            edge["services"], key=lambda item: (item.consumer, item.provider)
        ))
        normalized_pairs.append(PairPlan(left_id, right_id, services))
    normalized_pairs.sort(key=lambda pair: (pair.left, pair.right))

    selected_ids = tuple(sorted(selected))
    eligible_ids = tuple(item.context_id for item in eligible)
    unmatched = tuple(context_id for context_id in eligible_ids if context_id not in selected)
    isolated = tuple(context_id for context_id in eligible_ids if graph.degree[context_id] == 0)
    utility_by_id = {item.context_id: item.value for item in context_list}
    return DistributionPlan(
        schema=SCHEMA,
        algorithm=ALGORITHM,
        input_digest=_canonical_digest(context_list, anchor_values),
        anchor=MappingProxyType(anchor_values),
        registered_contexts=tuple(ids),
        eligible_contexts=eligible_ids,
        anchor_exclusions=excluded,
        selected_contexts=selected_ids,
        unmatched_eligible=unmatched,
        isolated_eligible=isolated,
        pairs=tuple(normalized_pairs),
        total_utility=sum(utility_by_id[context_id] for context_id in selected_ids),
        utility_by_context=MappingProxyType(utility_by_id),
    )


def compare_plans(previous: DistributionPlan, current: DistributionPlan) -> PlanDelta:
    """Produce an explicit delta between two distribution plans."""
    old_registered, new_registered = set(previous.registered_contexts), set(current.registered_contexts)
    old_eligible, new_eligible = set(previous.eligible_contexts), set(current.eligible_contexts)
    old_selected, new_selected = set(previous.selected_contexts), set(current.selected_contexts)
    old_pair_details = {(pair.left, pair.right): pair.to_dict() for pair in previous.pairs}
    new_pair_details = {(pair.left, pair.right): pair.to_dict() for pair in current.pairs}
    old_pairs, new_pairs = set(old_pair_details), set(new_pair_details)
    common_pairs = old_pairs & new_pairs
    service_changed = tuple(sorted(
        pair for pair in common_pairs if old_pair_details[pair] != new_pair_details[pair]
    ))
    common_registry = old_registered & new_registered
    utility_changed = tuple(sorted(
        context_id for context_id in common_registry
        if previous.utility_by_context.get(context_id) != current.utility_by_context.get(context_id)
    ))
    return PlanDelta(
        old_schema=previous.schema,
        new_schema=current.schema,
        old_algorithm=previous.algorithm,
        new_algorithm=current.algorithm,
        old_digest=previous.input_digest,
        new_digest=current.input_digest,
        anchor_changed=dict(previous.anchor) != dict(current.anchor),
        newly_registered=tuple(sorted(new_registered - old_registered)),
        removed_from_registry=tuple(sorted(old_registered - new_registered)),
        newly_eligible=tuple(sorted(new_eligible - old_eligible)),
        newly_excluded=tuple(sorted(old_eligible - new_eligible)),
        selected_added=tuple(sorted(new_selected - old_selected)),
        selected_removed=tuple(sorted(old_selected - new_selected)),
        pairing_added=tuple(sorted(new_pairs - old_pairs)),
        pairing_removed=tuple(sorted(old_pairs - new_pairs)),
        service_changed_pairs=service_changed,
        utility_changed_contexts=utility_changed,
        old_total_utility=previous.total_utility,
        new_total_utility=current.total_utility,
        utility_delta=current.total_utility - previous.total_utility,
    )


def load_spec(data: Mapping[str, Any]) -> tuple[list[ContractContext], dict[str, JsonScalar]]:
    """Load the stable JSON input shape used by the command-line demo."""
    if not isinstance(data, Mapping) or data.get("schema") != "context-contract-distribution-input.v0.1":
        raise ValueError("unsupported input schema")
    raw_contexts = data.get("contexts")
    if not isinstance(raw_contexts, list):
        raise ValueError("input contexts must be a list")
    contexts = []
    for index, item in enumerate(raw_contexts):
        if not isinstance(item, Mapping) or not isinstance(item.get("id"), str):
            raise ValueError(f"contexts[{index}] must be an object with a string 'id'")
        try:
            contexts.append(ContractContext(
                context_id=item["id"],
                facts=item.get("facts", {}),
                needs=item.get("needs", {}),
                utility=item.get("utility"),
            ))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid contexts[{index}]: {exc}") from exc
    return contexts, _validate_anchor(data.get("anchor", {}))


if __name__ == "__main__":  # pragma: no cover - convenience for quick introspection
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="JSON distribution input spec")
    args = parser.parse_args()
    with args.spec.open("r", encoding="utf-8") as handle:
        spec = json.load(handle)
    context_items, anchor_state = load_spec(spec)
    print(json.dumps(plan_distribution(context_items, anchor_state).to_dict(), indent=2, ensure_ascii=False))
