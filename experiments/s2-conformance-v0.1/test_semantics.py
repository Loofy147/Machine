import pytest

from oracle import Miss, Hit, expected_lookup, assert_result_equal, assert_lookup_matches_oracle

def test_present_key(target):
    relation = {"a": 10, "b": 20}
    assert_lookup_matches_oracle(target, relation, "b")

def test_absent_key(target):
    relation = {"a": 10}
    assert_lookup_matches_oracle(target, relation, "missing")

def test_miss_is_distinct_from_valid_nil_like_value(target, nil_value):
    relation = {"present": nil_value}
    hit = target.lookup(relation, "present")
    assert isinstance(hit, Hit), "valid value must remain Hit(v) even if it resembles a concrete miss encoding"
    assert_result_equal(hit, expected_lookup(relation, "present", target.eq_k))
    try:
        miss = target.lookup(relation, "absent")
    except AssertionError as exc:
        raise AssertionError("target cannot encode Miss distinctly from Hit(NIL)") from exc
    assert isinstance(miss, Miss)
    assert_result_equal(miss, expected_lookup(relation, "absent", target.eq_k))

def test_eq_k_laws(target):
    x, y = target.equivalent_key_pair()
    z = type(x)("b")
    assert target.eq_k(x, x)
    assert target.eq_k(x, y)
    assert target.eq_k(y, x)
    assert target.eq_k(y, y)
    assert not target.eq_k(x, z)
    assert not target.eq_k(z, x)
    assert target.eq_k(x, y) and target.eq_k(y, y) and target.eq_k(x, y)
    relation = {x: 42}
    assert_lookup_matches_oracle(target, relation, y)
    assert_lookup_matches_oracle(target, relation, z)

def test_eq_k_invariance(target):
    x, y = target.equivalent_key_pair()
    relation = {x: 42}
    assert_lookup_matches_oracle(target, relation, y)

def test_value_opacity(target):
    values = [0, False, "v", (1, 2), {"nested": 3}]
    for i, value in enumerate(values):
        relation = {f"k{i}": value}
        assert_lookup_matches_oracle(target, relation, f"k{i}")

def test_read_only(target):
    relation = {"a": {"nested": [1, 2]}}
    before = target.snapshot_relation(relation)
    assert_lookup_matches_oracle(target, relation, "a")
    after = target.snapshot_relation(relation)
    assert after == before

def test_repeatability(target):
    relation = {"a": 7}
    r1 = target.lookup(relation, "a")
    r2 = target.lookup(relation, "a")
    assert_result_equal(r1, expected_lookup(relation, "a", target.eq_k))
    assert_result_equal(r2, r1)

def test_empty_relation(target):
    assert_lookup_matches_oracle(target, {}, "a")

def test_relation_isolation(target):
    r1 = {"a": 1}
    r2 = {"a": 2}
    assert_lookup_matches_oracle(target, r1, "a")
    assert_lookup_matches_oracle(target, r2, "a")

def test_representation_independence(target):
    from collections import UserDict
    r1 = {"a": 1, "b": 2}
    r2 = UserDict([("b", 2), ("a", 1)])
    assert_lookup_matches_oracle(target, r1, "a")
    assert_lookup_matches_oracle(target, r2, "a")

def test_information_boundary_ignores_undeclared_state(target):
    relation = {"a": 42}
    key = "a"
    baseline = target.lookup_with_hidden_state(relation, key, {})
    hidden_variants = [
        {"noise": 99},
        {"other_relation": {"a": 999}},
        {"oracle_answer": Miss()},
    ]
    for hidden in hidden_variants:
        actual = target.lookup_with_hidden_state(relation, key, hidden)
        assert_result_equal(actual, baseline)

def test_invalid_inputs_are_outside_result_algebra(target):
    invalid_relations = [[], object(), 7]
    for relation in invalid_relations:
        try:
            target.lookup(relation, "a")
        except Exception:
            pass
        else:
            raise AssertionError("invalid relation input was accepted as normal S2 lookup")
    try:
        target.lookup({"a": 1}, [])
    except Exception:
        pass
    else:
        raise AssertionError("invalid key input was accepted as normal S2 lookup")
