"""Relation-lookup substrate audit.

Purpose:
  Separate semantic derivability from resource cost.

Contract S1:
  - finite relation is ordinary state data;
  - fixed substrate can read relation entries sequentially;
  - key equality and branching are ordinary fixed operations;
  - no direct indexed lookup primitive is required.

Derived lookup scans the stored relation. Direct lookup is treated as an
optional efficiency primitive. Both must be semantically equivalent.

This does NOT claim the current Machine substrate already satisfies S1.
That contract must be stated explicitly before classifying relation_lookup.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional

Relation = List[Tuple[int, int]]


@dataclass
class LookupResult:
    value: Optional[int]
    ticks: int


def derived_lookup(rel: Relation, key: int) -> LookupResult:
    ticks = 0
    for k, v in rel:
        ticks += 1
        if k == key:
            return LookupResult(v, ticks)
    return LookupResult(None, ticks)


def direct_lookup(index: dict[int, int], key: int) -> LookupResult:
    return LookupResult(index.get(key), 1)


def audit_relation(rel: Relation) -> dict:
    index = dict(rel)
    rows = []
    for key, expected in rel:
        a = derived_lookup(rel, key)
        b = direct_lookup(index, key)
        assert a.value == expected == b.value
        rows.append({
            "key": key,
            "expected": expected,
            "derived": a.value,
            "direct": b.value,
            "derived_ticks": a.ticks,
            "direct_ticks": b.ticks,
        })

    return {
        "semantic_equivalence": True,
        "keys": len(rel),
        "derived_ticks_total": sum(r["derived_ticks"] for r in rows),
        "direct_ticks_total": sum(r["direct_ticks"] for r in rows),
        "rows": rows,
    }


if __name__ == "__main__":
    relation = [(2, 20), (5, 50), (8, 80), (13, 130), (21, 210)]
    print(audit_relation(relation))
