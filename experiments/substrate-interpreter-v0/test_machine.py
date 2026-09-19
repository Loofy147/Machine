from machine import *

def test_closure_and_lexical_scope():
    expr = Let("x", Const(7), Let("f", Lambda("y", Prim("eq",(Var("x"),Var("y")))), Apply(Var("f"),Const(7))))
    assert Interpreter(S1).run(expr).result is True

def test_state_read_write():
    expr = Begin((Prim("state_write",(Const("x"),Const(9))), Prim("state_read",(Const("x"),))))
    assert Interpreter(S1,{"x":1}).run(expr).result == 9

def test_direct_lookup_is_contract_bound():
    rel = tuple(Pair(k,v) for k,v in (("a",10),("b",20),("c",30)))
    idx, off, stored = build_indexed_relation(rel)
    assert (off, stored) == (3,3)
    try:
        Interpreter(S1).run(Prim("relation_lookup_direct",(Const(idx),Const("b"))))
    except LanguageError:
        pass
    else:
        raise AssertionError("S1 must reject direct lookup")
    assert Interpreter(S2).run(Prim("relation_lookup_direct",(Const(idx),Const("b")))).result == 20

def test_object_language_recursive_scan():
    rel = tuple(Pair(k,v) for k,v in (("a",10),("b",20),("c",30),("d",40)))
    find = Lambda("key",Lambda("rel",
        If(Prim("is_nil",(Var("rel"),)),Const(NIL),
           Let("e",Apply(Var("head"),Var("rel")),
               If(Prim("eq",(Apply(Var("head"),Var("e")),Var("key"))),
                  Apply(Var("tail"),Var("e")),
                  Apply(Apply(Var("find"),Var("key")),Apply(Var("tail"),Var("rel"))))))))
    expr = LetRec("find",find,Let("rel",Prim("state_read",(Const("rel"),)),
                 Apply(Apply(Var("find"),Const("c")),Var("rel"))))
    st = Interpreter(S1,{"rel":rel}).run(expr)
    assert st.result == 30 and st.access_ticks > 0

def test_scan_direct_semantics():
    rel = tuple(Pair(k,v) for k,v in (("a",10),("b",20),("c",30),("d",40),("e",50)))
    idx, _, _ = build_indexed_relation(rel)
    keys = ["e","a","c","missing","d"]
    scan = [scan_lookup(rel,k)[0] for k in keys]
    direct = [direct_lookup(idx,k)[0] for k in keys]
    assert scan == direct
