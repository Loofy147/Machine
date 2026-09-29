from __future__ import annotations
from collections import deque
import csv, json, random
from pathlib import Path

OPS=("A","B","C")

def make_graph(kind,M):
    if kind=="affine_mix":
        return lambda op,v:{"A":(v+1)%M,"B":(v+7)%M,"C":(2*v)%M}[op]
    if kind=="perm_mix":
        return lambda op,v:{"A":(v+1)%M,"B":(v+7)%M,"C":(3*v+5)%M}[op]
    if kind=="opaque_mix":
        rng=random.Random(99173+M)
        p1=list(range(M)); p2=list(range(M)); rng.shuffle(p1); rng.shuffle(p2)
        table=[(i*37+(i%11)*13+17)%M for i in range(M)]
        return lambda op,v: p1[v] if op=="A" else p2[v] if op=="B" else table[v]
    raise ValueError(kind)

def sample_queries(M,n=80,seed=17):
    rng=random.Random(seed+M); out=[]
    while len(out)<n:
        s,t=rng.randrange(M),rng.randrange(M)
        if s!=t:out.append((s,t))
    return out

def forward(succ,s,t,M,cap,adj=None):
    if s==t:return True,0
    q=deque([s]);seen={s};ticks=0
    while q:
        u=q.popleft()
        vals=adj[u] if adj is not None else [succ(op,u) for op in OPS]
        for v in vals:
            ticks+=1
            if ticks>cap:return False,ticks
            if v==t:return True,ticks
            if v not in seen:seen.add(v);q.append(v)
    return False,ticks

def reverse_neighbors_native(kind,v,M):
    if kind=="affine_mix":
        out=[(v-1)%M,(v-7)%M]
        if M%2:out.append((v*pow(2,-1,M))%M)
        elif v%2==0:
            x=v//2;out.extend([x,(x+M//2)%M])
        return out
    if kind=="perm_mix":
        inv3=pow(3,-1,M)
        return [(v-1)%M,(v-7)%M,((v-5)*inv3)%M]
    return None

def native_bidi(kind,succ,s,t,M,cap):
    if reverse_neighbors_native(kind,t,M) is None:return None,None
    if s==t:return True,0
    fq,bq=deque([s]),deque([t]);fs,bs={s},{t};ticks=0
    while fq and bq:
        if len(fq)<=len(bq):
            u=fq.popleft()
            for op in OPS:
                v=succ(op,u);ticks+=1
                if ticks>cap:return False,ticks
                if v in bs:return True,ticks
                if v not in fs:fs.add(v);fq.append(v)
        else:
            u=bq.popleft()
            for v in reverse_neighbors_native(kind,u,M):
                ticks+=1
                if ticks>cap:return False,ticks
                if v in fs:return True,ticks
                if v not in bs:bs.add(v);bq.append(v)
    return False,ticks

def build_macro(succ,M,k):
    cur=[{s} for s in range(M)]
    offline=0
    for _ in range(k):
        nxt=[set() for _ in range(M)]
        for s in range(M):
            for u in cur[s]:
                for op in OPS:
                    nxt[s].add(succ(op,u));offline+=1
        cur=nxt
    return cur,offline,sum(len(x) for x in cur)

def run():
    out=Path("experiments/mechanism-frontier-shift-v0/samples-v0")
    out.mkdir(parents=True,exist_ok=True)
    caps=[10,20,40,80,160,320,640]
    configs=[("affine_mix",30),("affine_mix",300),("affine_mix",3000),
             ("perm_mix",31),("opaque_mix",31)]
    seeds=[17,23,41]
    rows=[]
    for kind,M in configs:
        succ=make_graph(kind,M)
        macros={k:build_macro(succ,M,k) for k in (2,3,4)}
        for seed in seeds:
            qs=sample_queries(M,seed=seed)
            for cap in caps:
                for i,(s,t) in enumerate(qs):
                    f,ft=forward(succ,s,t,M,cap)
                    nb,nt=native_bidi(kind,succ,s,t,M,cap)
                    row={"kind":kind,"M":M,"seed":seed,"query_index":i,
                         "start":s,"target":t,"B_on":cap,
                         "forward":int(f),"forward_ticks":ft,
                         "native_bidi":None if nb is None else int(nb),
                         "native_bidi_ticks":nt}
                    for k,(adj,off,edges) in macros.items():
                        m,mt=forward(succ,s,t,M,cap,adj=adj)
                        row.update({f"macro{k}":int(m),
                                    f"macro{k}_online_ticks":mt,
                                    f"macro{k}_offline_ticks":off,
                                    f"macro{k}_stored_edges":edges})
                    rows.append(row)
    with open(out/"representative-v0.csv","w",newline="") as fh:
        fields=rows[0].keys()
        w=csv.DictWriter(fh,fieldnames=fields);w.writeheader()
        # 3 deterministic query samples per (graph, seed, B_on).
        for kind,M in configs:
            for seed in seeds:
                for cap in caps:
                    cell=[r for r in rows if r["kind"]==kind and r["M"]==M
                          and r["seed"]==seed and r["B_on"]==cap]
                    w.writerows((cell[0],cell[len(cell)//2],cell[-1]))
if __name__=="__main__":
    run()
