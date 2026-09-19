from machine import *

def scan_program(key):
    find = Lambda("key", Lambda("rel",
        Let("items", Prim("iter",(Var("rel"),)),
            If(Prim("is_nil",(Var("items"),)), Const(NIL),
                Let("e", Apply(Var("head"),Var("items")),
                    If(Prim("eq",(Apply(Var("head"),Var("e")),Var("key"))),
                       Apply(Var("tail"),Var("e")),
                       Apply(Apply(Var("find"),Var("key")),Apply(Var("tail"),Var("items")))))))))
    return LetRec("find", find,
        Let("rel", Prim("state_read",(Const("rel"),)),
            Apply(Apply(Var("find"),Const(key)),Var("rel"))))

def direct_program(key):
    return Prim("relation_lookup_direct",
                (Prim("state_read",(Const("rel"),)),Const(key)))

def test_closure_and_lexical_scope():
    expr=Let("x",Const(7),Let("f",Lambda("y",Prim("eq",(Var("x"),Var("y")))),Apply(Var("f"),Const(7))))
    assert Interpreter(S1).run(expr).result is True

def test_state_read_write():
    expr=Begin((Prim("state_write",(Const("x"),Const(9))),Prim("state_read",(Const("x"),))))
    assert Interpreter(S1,{"x":1}).run(expr).result == 9

def test_same_representation_contract_difference():
    relation={"a":10,"b":20,"c":30}
    try:
        Interpreter(S1,{"rel":relation}).run(direct_program("b"))
    except LanguageError:
        pass
    else:
        raise AssertionError("S1 must reject direct lookup")
    assert Interpreter(S2,{"rel":relation}).run(direct_program("b")).result == 20

def test_object_language_scan_matches_direct_access():
    relation={f"k{i}":i*10 for i in range(5)}
    keys=["k4","k0","k2","missing","k3"]
    scan=[Interpreter(S1,{"rel":relation}).run(scan_program(k)).result for k in keys]
    direct=[Interpreter(S2,{"rel":relation}).run(direct_program(k)).result for k in keys]
    assert scan == direct == [40,0,20,NIL,30]

def test_s2_is_conservative_for_s1_programs():
    relation={f"k{i}":i*10 for i in range(5)}
    for key in ["k4","k0","missing"]:
        s1=Interpreter(S1,{"rel":relation,"x":1}).run(scan_program(key))
        s2=Interpreter(S2,{"rel":relation,"x":1}).run(scan_program(key))
        assert s1.result == s2.result
        assert s1.machine_data == s2.machine_data == {"rel":relation,"x":1}

def test_s2_direct_lookup_is_read_only_for_machine_state():
    relation={"a":10,"b":20}
    before={"rel":relation,"marker":7}
    st=Interpreter(S2,before).run(direct_program("b"))
    assert st.result == 20
    assert st.machine_data == before

def test_s2_access_cost_is_explicit_and_nonzero():
    st=Interpreter(S2,{"rel":{"a":10}}).run(direct_program("a"))
    # One state_read access + one direct-lookup access.
    assert st.access_ticks == 2

def test_s2_missing_key_preserves_lookup_contract():
    st=Interpreter(S2,{"rel":{"a":10}}).run(direct_program("missing"))
    assert st.result == NIL
