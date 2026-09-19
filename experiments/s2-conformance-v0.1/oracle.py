from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Miss:
    pass

@dataclass(frozen=True)
class Hit:
    value: Any

LookupResult = Miss | Hit

def expected_lookup(relation: dict, key: Any, eq_k):
    matches = [(stored_key, value) for stored_key, value in relation.items() if eq_k(stored_key, key)]
    assert len(matches) <= 1, "abstract relation violated: multiple Eq_K-equivalent associations"
    if not matches:
        return Miss()
    return Hit(matches[0][1])

def assert_result_equal(actual, expected):
    assert type(actual) is type(expected)
    if isinstance(expected, Miss):
        return
    assert actual.value == expected.value