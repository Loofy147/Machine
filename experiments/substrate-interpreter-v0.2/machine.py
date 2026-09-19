from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

class Expr: pass
@dataclass(frozen=True)
class Const(Expr): value: Any
@dataclass(frozen=True)
class Var(Expr): name: str
@dataclass(frozen=True)
class Lambda(Expr): param: str; body: Expr
@dataclass(frozen=True)
class Apply(Expr): fn: Expr; arg: Expr
@dataclass(frozen=True)
class If(Expr): cond: Expr; then: Expr; otherwise: Expr
@dataclass(frozen=True)
class Let(Expr): name: str; value: Expr; body: Expr
@dataclass(frozen=True)
class LetRec(Expr): name: str; value: Expr; body: Expr
@dataclass(frozen=True)
class Begin(Expr): exprs: tuple[Expr, ...]
@dataclass(frozen=True)
class SetVar(Expr): name: str; value: Expr
@dataclass(frozen=True)
class Prim(Expr): name: str; args: tuple[Expr, ...]

@dataclass(frozen=True)
class Closure:
    param: str
    body: Expr
    env: tuple[tuple[str, int], ...]

@dataclass(frozen=True)
class Primitive: name: str
@dataclass(frozen=True)
class Pair: head: Any; tail: Any

class Unit: pass
UNIT = Unit()
NIL: tuple[()] = ()

def ed(env): return dict(env)
def et(env): return tuple(sorted(env.items()))

@dataclass(frozen=True)
class KEmpty: pass
@dataclass(frozen=True)
class KLet:
    name: str; body: Expr; env: tuple[tuple[str,int], ...]; kont: Any
@dataclass(frozen=True)
class KLetRec:
    name: str; body: Expr; env: tuple[tuple[str,int], ...]; addr: int; kont: Any
@dataclass(frozen=True)
class KIf:
    then: Expr; otherwise: Expr; env: tuple[tuple[str,int], ...]; kont: Any
@dataclass(frozen=True)
class KAppFn:
    arg: Expr; env: tuple[tuple[str,int], ...]; kont: Any
@dataclass(frozen=True)
class KAppArg:
    fn: Any; kont: Any
@dataclass(frozen=True)
class KBegin:
    rest: tuple[Expr, ...]; env: tuple[tuple[str,int], ...]; kont: Any
@dataclass(frozen=True)
class KSet:
    name: str; env: tuple[tuple[str,int], ...]; kont: Any
@dataclass(frozen=True)
class KPrim:
    name: str; remaining: tuple[Expr, ...]; values: tuple[Any, ...]
    env: tuple[tuple[str,int], ...]; kont: Any

@dataclass
class MachineState:
    control: Any
    env: tuple[tuple[str,int], ...]
    kont: Any
    store: dict[int,Any]
    machine_data: dict[Any,Any] = field(default_factory=dict)
    next_addr: int = 0
    halted: bool = False
    result: Any = None
    ticks: int = 0
    access_ticks: int = 0

class LanguageError(RuntimeError): pass
class StepLimitExceeded(RuntimeError): pass

@dataclass(frozen=True)
class SubstrateContract:
    name: str
    direct_relation_lookup: bool = False

S1 = SubstrateContract("S1-generic-readable-state", False)
S2 = SubstrateContract("S2-indexed-relation-access", True)

class Interpreter:
    def __init__(self, contract: SubstrateContract, initial_state=None):
        self.contract = contract
        self.globals = {"true":True,"false":False,"nil":NIL,"unit":UNIT}
        for n in ("eq","pair","head","tail","is_nil","state_read","state_write","iter"):
            self.globals[n] = Primitive(n)
        if contract.direct_relation_lookup:
            self.globals["relation_lookup_direct"] = Primitive("relation_lookup_direct")
        self.store = {}
        self.next_addr = 0
        self.initial_state = dict(initial_state or {})

    def alloc(self, value):
        a = self.next_addr; self.next_addr += 1; self.store[a] = value; return a

    def env0(self):
        return et({k:self.alloc(v) for k,v in self.globals.items()})

    def addr(self, env, name):
        if name not in ed(env): raise LanguageError(f"unbound variable: {name}")
        return ed(env)[name]

    def run(self, expr, max_steps=100000):
        st = MachineState(expr, self.env0(), KEmpty(), self.store, dict(self.initial_state), self.next_addr)
        while not st.halted:
            self.step(st)
            if st.ticks > max_steps: raise StepLimitExceeded(max_steps)
        self.store, self.next_addr = st.store, st.next_addr
        self.initial_state = st.machine_data
        return st

    def step(self, st):
        st.ticks += 1; c = st.control
        if isinstance(c, Var):
            st.access_ticks += 1; st.control = st.store[self.addr(st.env,c.name)]; return
        if isinstance(c, Const):
            st.control = c.value; self.cont(st); return
        if isinstance(c, Lambda):
            st.control = Closure(c.param,c.body,st.env); self.cont(st); return
        if isinstance(c, Let):
            st.kont = KLet(c.name,c.body,st.env,st.kont); st.control = c.value; return
        if isinstance(c, LetRec):
            a = st.next_addr; st.next_addr += 1; st.store[a] = UNIT
            d=ed(st.env); d[c.name]=a; re=et(d)
            st.kont=KLetRec(c.name,c.body,re,a,st.kont); st.env=re; st.control=c.value; return
        if isinstance(c, If):
            st.kont=KIf(c.then,c.otherwise,st.env,st.kont); st.control=c.cond; return
        if isinstance(c, Apply):
            st.kont=KAppFn(c.arg,st.env,st.kont); st.control=c.fn; return
        if isinstance(c, Begin):
            if not c.exprs: st.control=UNIT; self.cont(st)
            else:
                st.kont=KBegin(tuple(c.exprs[1:]),st.env,st.kont); st.control=c.exprs[0]
            return
        if isinstance(c, SetVar):
            st.kont=KSet(c.name,st.env,st.kont); st.control=c.value; return
        if isinstance(c, Prim):
            if not c.args:
                st.control=self.prim(c.name,(),st); self.cont(st); return
            st.kont=KPrim(c.name,tuple(c.args[1:]),(),st.env,st.kont); st.control=c.args[0]; return
        if isinstance(c,(Closure,Primitive,Pair,Unit,bool,int,float,str,tuple,Mapping)):
            self.cont(st); return
        raise LanguageError(f"unsupported control value: {c!r}")

    def cont(self, st):
        k=st.kont
        if isinstance(k,KEmpty): st.halted=True; st.result=st.control; return
        if isinstance(k,KLet):
            a=st.next_addr; st.next_addr+=1; st.store[a]=st.control
            d=ed(k.env); d[k.name]=a; st.env=et(d); st.kont=k.kont; st.control=k.body; return
        if isinstance(k,KLetRec):
            st.store[k.addr]=st.control; st.access_ticks+=1; st.env=k.env; st.kont=k.kont; st.control=k.body; return
        if isinstance(k,KIf):
            st.env=k.env; st.kont=k.kont; st.control=k.then if st.control is not False else k.otherwise; return
        if isinstance(k,KAppFn):
            st.kont=KAppArg(st.control,k.kont); st.env=k.env; st.control=k.arg; return
        if isinstance(k,KAppArg):
            fn,arg=k.fn,st.control
            if isinstance(fn,Closure):
                a=st.next_addr; st.next_addr+=1; st.store[a]=arg
                d=ed(fn.env); d[fn.param]=a; st.env=et(d); st.kont=k.kont; st.control=fn.body; return
            if isinstance(fn,Primitive):
                st.kont=k.kont; st.control=self.prim(fn.name,(arg,),st); self.cont(st); return
            raise LanguageError(f"not callable: {fn!r}")
        if isinstance(k,KBegin):
            st.env=k.env; st.kont=k.kont
            if not k.rest: self.cont(st)
            else: st.kont=KBegin(k.rest[1:],k.env,k.kont); st.control=k.rest[0]
            return
        if isinstance(k,KSet):
            a=self.addr(k.env,k.name); st.store[a]=st.control; st.access_ticks+=1
            st.env=k.env; st.kont=k.kont; st.control=UNIT; return
        if isinstance(k,KPrim):
            vals=k.values+(st.control,)
            if k.remaining:
                st.kont=KPrim(k.name,k.remaining[1:],vals,k.env,k.kont); st.env=k.env; st.control=k.remaining[0]; return
            st.env=k.env; st.kont=k.kont; st.control=self.prim(k.name,vals,st); self.cont(st); return
        raise LanguageError(f"bad continuation: {k!r}")

    def prim(self,name,args,st):
        if name=="eq":
            if len(args)!=2: raise LanguageError("eq")
            if st: st.access_ticks += 1
            return args[0]==args[1]
        if name=="pair":
            if len(args)!=2: raise LanguageError("pair")
            return Pair(args[0],args[1])
        if name=="head":
            x=args[0]
            if isinstance(x,Pair): return x.head
            if isinstance(x,tuple) and x: return x[0]
            raise LanguageError("head")
        if name=="tail":
            x=args[0]
            if isinstance(x,Pair): return x.tail
            if isinstance(x,tuple) and x: return tuple(x[1:])
            raise LanguageError("tail")
        if name=="is_nil":
            x=args[0]; return x==NIL or (isinstance(x,tuple) and not x)
        if name=="state_read":
            if st is None: raise LanguageError("state_read outside machine")
            if args[0] not in st.machine_data: raise LanguageError("missing state key")
            st.access_ticks += 1; return st.machine_data[args[0]]
        if name=="state_write":
            if st is None or len(args)!=2: raise LanguageError("state_write")
            st.machine_data[args[0]]=args[1]; st.access_ticks += 1; return UNIT
        if name=="iter":
            if len(args)!=1: raise LanguageError("iter")
            source=args[0]
            if isinstance(source,tuple):
                items=source
            elif isinstance(source,Mapping):
                items=tuple(Pair(k,v) for k,v in source.items())
            else:
                raise LanguageError("iter")
            if st: st.access_ticks += len(items)
            return items
        if name=="relation_lookup_direct":
            if not self.contract.direct_relation_lookup: raise LanguageError("direct lookup unavailable")
            if len(args)!=2 or not isinstance(args[0],Mapping): raise LanguageError("direct lookup")
            if st: st.access_ticks += 1
            return args[0].get(args[1],NIL)
        raise LanguageError(f"unknown primitive: {name}")

def build_indexed_relation(entries: Sequence[Pair]):
    index={x.head:x.tail for x in entries}
    return index,len(index),len(index)

def scan_lookup(entries: Sequence[Pair], key):
    ticks=0
    for e in entries:
        ticks+=1
        if e.head==key: ticks+=1; return e.tail,ticks
        ticks+=1
    return NIL,ticks

def direct_lookup(indexed: Mapping[Any,Any],key):
    return indexed.get(key,NIL),1
