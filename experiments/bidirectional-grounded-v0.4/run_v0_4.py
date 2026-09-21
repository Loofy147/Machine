from __future__ import annotations
import argparse, itertools, json, random, statistics, time
from pathlib import Path
from core import (
    dijkstra, build_must_expand_graph, max_bipartite_matching,
    minimum_vertex_cover_from_matching, interruptible_bidirectional_dijkstra,
    bidirectional_dijkstra, random_weighted_digraph, all_policies,
)

ROOT = Path(__file__).resolve().parent

def reverse(adj):
    r={u:[] for u in adj}
    for u,es in adj.items():
        for v,w in es: r[v].append((u,w))
    return r

def fixed_policy(seq):
    i=[0]
    def p(nF,nB,topF,topB):
        x=seq[i[0]]; i[0]+=1; return x
    return p

def exhaustive_n3():
    n=3; states=range(4)
    edges=[(u,v) for u in range(n) for v in range(n) if u!=v]
    schedules=list(itertools.product('FB',repeat=2*n))
    out={'graph_states':0,'solvable_graphs':0,'schedule_runs':0,'active_guard_failures':0,'naive_finite_failures':0,'mx_cover_failures':0,'konig_failures':0}
    for code in itertools.product(states,repeat=len(edges)):
        out['graph_states']+=1
        adj={u:[] for u in range(n)}; rev={u:[] for u in range(n)}
        for (u,v),s in zip(edges,code):
            if s: adj[u].append((v,s)); rev[v].append((u,s))
        ds=dijkstra(adj,0); dt=dijkstra(rev,2); c=ds.get(2)
        if c is None: continue
        out['solvable_graphs']+=1
        mx=build_must_expand_graph(n,ds,dt,c); nu,mr=max_bipartite_matching(ds.keys(),mx)
        cl,cr=minimum_vertex_cover_from_matching(ds.keys(),mx,mr)
        if len(cl)+len(cr)!=nu: out['konig_failures']+=1
        for seq in schedules:
            try:
                a=interruptible_bidirectional_dijkstra(adj,rev,0,2,fixed_policy(seq),active_guard=True,check_before_first_edge=False)
                b=interruptible_bidirectional_dijkstra(adj,rev,0,2,fixed_policy(seq),active_guard=False,check_before_first_edge=False)
            except (IndexError,KeyError):
                continue
            out['schedule_runs']+=1
            if a.mu!=c or a.N_pi<nu: out['active_guard_failures']+=1
            for u,vs in mx.items():
                for v in vs:
                    if u not in a.expanded_F and v not in a.expanded_B:
                        out['mx_cover_failures']+=1; break
            if b.mu not in (c,float('inf')): out['naive_finite_failures']+=1
    return out

def exhaustive_n4():
    n=4; states=range(3)
    edges=[(u,v) for u in range(n) for v in range(n) if u!=v]
    out={'total_graphs':0,'solvable_graphs':0,'checked_policy_runs':0,'active_guard_failures':0,'naive_finite_failures':0,'mx_cover_failures':0,'konig_failures':0,'policy':'smaller_frontier'}
    from core import make_smaller_frontier
    for code in itertools.product(states,repeat=len(edges)):
        out['total_graphs']+=1
        adj={u:[] for u in range(n)}; rev={u:[] for u in range(n)}
        for (u,v),s in zip(edges,code):
            if s: adj[u].append((v,s)); rev[v].append((u,s))
        ds=dijkstra(adj,0); dt=dijkstra(rev,3); c=ds.get(3)
        if c is None: continue
        out['solvable_graphs']+=1
        mx=build_must_expand_graph(n,ds,dt,c); nu,mr=max_bipartite_matching(ds.keys(),mx)
        cl,cr=minimum_vertex_cover_from_matching(ds.keys(),mx,mr)
        if len(cl)+len(cr)!=nu: out['konig_failures']+=1
        for guard in (True,False):
            r=interruptible_bidirectional_dijkstra(adj,rev,0,3,make_smaller_frontier(),active_guard=guard,check_before_first_edge=False)
            out['checked_policy_runs']+=1
            if guard:
                if r.mu!=c or r.N_pi<nu: out['active_guard_failures']+=1
                for u,vs in mx.items():
                    for v in vs:
                        if u not in r.expanded_F and v not in r.expanded_B:
                            out['mx_cover_failures']+=1; break
            elif r.mu not in (c,float('inf')):
                out['naive_finite_failures']+=1
    return out

def random_n4_all_schedules(seed_count=2000):
    n=4; seqs=list(itertools.product('FB',repeat=8))
    out={'random_graphs':seed_count,'solvable_graphs':0,'schedules_per_graph':len(seqs),'checked_runs':0,'active_guard_failures':0,'naive_finite_failures':0,'mx_cover_failures':0}
    for seed in range(seed_count):
        rng=random.Random(seed+99173)
        adj={u:[] for u in range(n)}
        for u in range(n):
            for v in range(n):
                if u!=v and rng.random()<0.45: adj[u].append((v,rng.randint(1,3)))
        rev=reverse(adj); ds=dijkstra(adj,0); dt=dijkstra(rev,3); c=ds.get(3)
        if c is None: continue
        out['solvable_graphs']+=1
        mx=build_must_expand_graph(n,ds,dt,c); nu,_=max_bipartite_matching(ds.keys(),mx)
        for seq in seqs:
            try:
                a=interruptible_bidirectional_dijkstra(adj,rev,0,3,fixed_policy(seq),active_guard=True,check_before_first_edge=False)
                b=interruptible_bidirectional_dijkstra(adj,rev,0,3,fixed_policy(seq),active_guard=False,check_before_first_edge=False)
            except (IndexError,KeyError): continue
            out['checked_runs']+=1
            if a.mu!=c or a.N_pi<nu: out['active_guard_failures']+=1
            for u,vs in mx.items():
                for v in vs:
                    if u not in a.expanded_F and v not in a.expanded_B: out['mx_cover_failures']+=1; break
            if b.mu not in (c,float('inf')): out['naive_finite_failures']+=1
    return out

def matched_regime(seed_count=2000):
    def project_simple(adj):
        out={u:[] for u in adj}
        for u,es in adj.items():
            best={}
            for v,w in es:
                if v not in best or w<best[v]: best[v]=w
            out[u]=sorted(best.items())
        return out
    out={'pairs':seed_count,'failures':[],'policy_runs':0,'mean_edges_simple':None,'mean_edges_multi':None,'mean_edge_multiplicity_ratio':None,'median_edge_multiplicity_ratio':None,'mean_W_ratio':None,'min_W_ratio':None,'max_W_ratio':None}
    rows=[]; ratios=[]
    for seed in range(seed_count):
        base,_=random_weighted_digraph(24,5,seed,wmin=1,wmax=10,multigraph=False,ensure_path=True)
        rng=random.Random(seed+100000); multi={u:list(es) for u,es in base.items()}
        for u,es in list(base.items()):
            for v,w in es:
                if rng.random()<0.45:
                    for _ in range(rng.randint(1,2)): multi[u].append((v,w+rng.randint(0,9)))
        simple=project_simple(multi); rS=reverse(simple); rM=reverse(multi)
        ds=dijkstra(simple,0); dm=dijkstra(multi,0); dtS=dijkstra(rS,23); dtM=dijkstra(rM,23); cS=ds.get(23); cM=dm.get(23)
        if cS!=cM: out['failures'].append([seed,'distance']); continue
        mxS=build_must_expand_graph(24,ds,dtS,cS); mxM=build_must_expand_graph(24,dm,dtM,cM)
        if mxS!=mxM: out['failures'].append([seed,'mx']); continue
        nuS,_=max_bipartite_matching(ds.keys(),mxS); nuM,_=max_bipartite_matching(dm.keys(),mxM)
        if nuS!=nuM: out['failures'].append([seed,'vc']); continue
        row={'E_simple':sum(map(len,simple.values())),'E_multi':sum(map(len,multi.values()))}
        for name,factory in all_policies().items():
            a=bidirectional_dijkstra(simple,rS,0,23,factory()); b=bidirectional_dijkstra(multi,rM,0,23,factory())
            out['policy_runs']+=1
            if a.mu!=b.mu or a.mu!=cS or a.N_pi!=b.N_pi or a.N_pi<nuS: out['failures'].append([seed,name,'behavior',a.mu,b.mu,a.N_pi,b.N_pi,nuS])
            if a.W_pi: ratios.append(b.W_pi/a.W_pi)
        rows.append(row)
    ratios_sorted=sorted(ratios)
    out['pairs']=len(rows)
    out['mean_edges_simple']=statistics.mean(r['E_simple'] for r in rows)
    out['mean_edges_multi']=statistics.mean(r['E_multi'] for r in rows)
    out['mean_edge_multiplicity_ratio']=statistics.mean(r['E_multi']/r['E_simple'] for r in rows)
    out['median_edge_multiplicity_ratio']=statistics.median(r['E_multi']/r['E_simple'] for r in rows)
    out['mean_W_ratio']=statistics.mean(ratios_sorted)
    out['min_W_ratio']=min(ratios_sorted); out['max_W_ratio']=max(ratios_sorted)
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--experiment',choices=['n3','n4','random-n4','matched','all'],default='all'); ap.add_argument('--random-graphs',type=int,default=2000); ap.add_argument('--matched-pairs',type=int,default=2000); args=ap.parse_args()
    results={}; t=time.time()
    if args.experiment in ('n3','all'): results['weighted_n3']=exhaustive_n3()
    if args.experiment in ('n4','all'): results['weighted_n4']=exhaustive_n4()
    if args.experiment in ('random-n4','all'): results['random_n4_all_schedules']=random_n4_all_schedules(args.random_graphs)
    if args.experiment in ('matched','all'): results['matched_simple_multigraph']=matched_regime(args.matched_pairs)
    results['elapsed_s']=round(time.time()-t,3)
    (ROOT/'RESULTS-V0.4.json').write_text(json.dumps(results,indent=2,sort_keys=True))
    print(json.dumps(results,indent=2))

if __name__=='__main__': main()
