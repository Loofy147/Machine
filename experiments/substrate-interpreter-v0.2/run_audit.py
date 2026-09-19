import json
from pathlib import Path
from machine import *

def scan_expr(key):
    find=Lambda("key",Lambda("rel",
        Let("items",Prim("iter",(Var("rel"),)),
            If(Prim("is_nil",(Var("items"),)),Const(NIL),
                Let("e",Apply(Var("head"),Var("items")),
                    If(Prim("eq",(Apply(Var("head"),Var("e")),Var("key"))),
                       Apply(Var("tail"),Var("e")),
                       Apply(Apply(Var("find"),Var("key")),Apply(Var("tail"),Var("items")))))))))
    return LetRec("find",find,Let("rel",Prim("state_read",(Const("rel"),)),
        Apply(Apply(Var("find"),Const(key)),Var("rel"))))

def direct_expr(key):
    return Prim("relation_lookup_direct",(Prim("state_read",(Const("rel"),)),Const(key)))

def normalize_direct_result(value):
    if isinstance(value, RelationLookupHit):
        return value.value
    if isinstance(value, RelationLookupMiss):
        return NIL
    raise AssertionError(f"unknown direct lookup result: {value!r}")

def main():
    relation={f"k{i}":i*10 for i in range(5)}
    offline=5
    storage=len(relation)
    keys=["k4","k0","k2","missing","k3"]
    scan_results=[]; scan_steps=scan_access=0
    direct_results=[]; direct_steps=direct_access=0
    for k in keys:
        st=Interpreter(S1,{"rel":relation}).run(scan_expr(k))
        scan_results.append(st.result); scan_steps+=st.ticks; scan_access+=st.access_ticks
        st=Interpreter(S2,{"rel":relation}).run(direct_expr(k))
        direct_results.append(normalize_direct_result(st.result)); direct_steps+=st.ticks; direct_access+=st.access_ticks
    out={"status":"EXECUTED / LOCAL REPLAY",
         "same_persistent_representation":True,
         "substrates":{
           "S1":{"generic_state_read":True,"comparison":True,"branching":True,"sequence_traversal":True,"direct_relation_lookup":False},
           "S2":{"generic_state_read":True,"comparison":True,"branching":True,"sequence_traversal":True,"direct_relation_lookup":True}},
         "offline_representation":{"construction_ticks":offline,"stored_entries":storage},
         "object_language_scan":{"results":scan_results,"transition_ticks_total":scan_steps,"access_ticks_total":scan_access},
         "object_language_direct":{"results":direct_results,"transition_ticks_total":direct_steps,"access_ticks_total":direct_access},
         "semantic_equivalence":scan_results==direct_results,
         "resource_ratio":{"transition_ticks_scan_over_direct":scan_steps/direct_steps,"access_ticks_scan_over_direct":scan_access/direct_access}}
    Path(__file__).with_name("RESULTS-V0.2.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__": main()
