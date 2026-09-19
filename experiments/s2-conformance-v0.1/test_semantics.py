from oracle import Miss, Hit, expected_lookup, assert_result_equal

def test_present_key(target):
    relation = {"a": 10, "b": 20}
    assert_result_equal(target.lookup(relation, "b"), Hit(20))

def test_absent_key(target):
    relation = {"a": 10}
    try:
        result = target.lookup(relation, "missing")
    except AssertionError as exc:
        raise AssertionError("target could not encode a distinct Miss result") from exc
    assert isinstance(result, Miss)

def test_miss_is_distinct_from_valid_nil_like_value(target, nil_value):
    relation = {"present": nil_value}
    hit = target.lookup(relation, "present")
    assert isinstance(hit, Hit), "valid value must remain Hit(v) even if it resembles a concrete miss encoding"
    try:
        miss = target.lookup(relation, "absent")
    except AssertionError as exc:
        raise AssertionError("target cannot encode Miss distinctly from Hit(NIL)") from exc
    assert isinstance(miss, Miss)

def test_eq_k_laws(target):
    x, y = target.equivalent_key_pair()
    z = target.equivalent_key_pair()[1]
    assert target.eq_k(x, x)
    assert target.eq_k(x, y) == target.eq_k(y, x)
    if target.eq_k(x, y) and target.eq_k(y, z):
        assert target.eq_k(x, z)

def test_eq_k_invariance(target):
    x, y = target.equivalent_key_pair()
    relation = {x: 42}
    assert_result_equal(target.lookup(relation, y), Hit(42))

def test_value_opacity(target):
    values = [0, False, "v", (1, 2), {"nested": 3}]
    for i, value in enumerate(values):
        relation = {f"k{i}": value}
        assert_result_equal(target.lookup(relation, f"k{i}"), Hit(value))

def test_read_only(target):
    relation = {"a": {"nested": [1, 2]}}
    before = target.snapshot_relation(relation)
    target.lookup(relation, "a")
    after = target.snapshot_relation(relation)
    assert after == before

def test_repeatability(target):
    relation = {"a": 7}
    r1 = target.lookup(relation, "a")
    r2 = target.lookup(relation, "a")
    assert r1 == r2

def test_empty_relation(target):
    result = target.lookup({}, "a")
    assert isinstance(result, Miss)

def test_relation_isolation(target):
    r1 = {"a": 1}
    r2 = {"a": 2}
    assert_result_equal(target.lookup(r1, "a"), Hit(1))
    assert_result_equal(target.lookup(r2, "a"), Hit(2))

def test_representation_independence(target):
    r1 = {"a": 1, "b": 2}
    r2 = {"b": 2, "a": 1}
    assert_result_equal(target.lookup(r1, "a"), Hit(1))
    assert_result_equal(target.lookup(r2, "a"), Hit(1))