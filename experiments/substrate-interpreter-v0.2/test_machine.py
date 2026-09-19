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

def test_closure_and_lexical_scope():
    expr=Let("x",Const(7),Let("f",Lambda("y",Prim("eq",(Var("x"),Var("y")))),Apply(Var("f"),Const(7))))
    assert Interpreter(S1).run(expr).result is True

def test_state_read_write():
    expr=Begin((Prim("state_write",(Const("x"),Const(9))),Prim("state_read",(Const("x"),))))
    assert Interpreter(S1,{"x":1}).run(expr).result == 9

def test_same_representation_contract_difference():
    relation={"a":10,"b":20,"c":30}
    try:
        Interpreter(S1,{"rel":relation}).run(
            Prim("relation_lookup_direct",(Prim("state_read",(Const("rel"),)),Const("b")))
        )
    except LanguageError:
        pass
    else:
        raise AssertionError("S1 must reject direct lookup")
    assert Interpreter(S2,{"rel":relation}).run(
        Prim("relation_lookup_direct",(Prim("state_read",(Const("rel"),)),Const("b")))
    ).result == 20

def test_object_language_scan_matches_direct_access():
    relation={f"k{i}":i*10 for i in range(5)}
    keys=["k4","k0","k2","missing","k3"]
    scan=[Interpreter(S1,{"rel":relation}).run(scan_program(k)).result for k in keys]
    direct=[Interpreter(S2,{"rel":relation}).run(
        Prim("relation_lookup_direct",(Prim("state_read",(Const("rel"),)),Const(k)))
    ).result for k in keys]
    assert scan == direct == [40,0,20,NIL,30]
