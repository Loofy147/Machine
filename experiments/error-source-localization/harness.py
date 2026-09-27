#!/usr/bin/env python3
"""Deterministic error-source localization v0 harness.

Research status: harness validation, not evidence of machine introspection.
The hidden fault is scoring-only. Controllers observe scores and intervention
consequences; they never receive the fault class or a target repair label.
"""
from __future__ import annotations
import argparse, json, random, statistics
from dataclasses import dataclass
from typing import List, Tuple

FAULTS = ("F0", "F1", "F2", "F3", "F4")
ACTIONS = ("operate", "reschedule", "remodel", "repartition")
TRUE_ACTION = {"F0": None, "F1": "operate", "F2": "reschedule", "F3": "repartition", "F4": "remodel"}
POINTS = [(x1, x2) for x1 in (0,1) for x2 in (0,1)] * 4
TRAIN = POINTS[:8]
TEST = POINTS[8:]

@dataclass
class Config:
    representation: int = 1
    model_good: bool = True
    policy_good: bool = True
    operation_good: bool = True
    def clone(self): return Config(self.representation, self.model_good, self.policy_good, self.operation_good)

class Env:
    def __init__(self, fault: str):
        self.fault = fault
        self.base = Config()
        if fault == "F1": self.base.operation_good = False
        elif fault == "F2": self.base.policy_good = False
        elif fault == "F3": self.base.representation = 0
        elif fault == "F4": self.base.model_good = False

    @staticmethod
    def target(x1, x2): return x1 ^ x2

    def score(self, cfg: Config, split: List[Tuple[int,int]]) -> float:
        correct = 0
        for x1, x2 in split:
            y = self.target(x1, x2)
            if cfg.representation == 0:
                pred = int((x1 + x2) >= 1)
            else:
                pred = int((x1 + x2 - 2*x1*x2) >= 0.5)
            if not cfg.model_good: pred = 1 - pred
            if not cfg.policy_good: pred = 1 - pred
            if not cfg.operation_good: pred = 1 - pred
            correct += int(pred == y)
        return correct / len(split)

    def apply(self, cfg: Config, action: str) -> Config:
        c = cfg.clone()
        if action == "operate": c.operation_good = True
        elif action == "reschedule": c.policy_good = True
        elif action == "remodel": c.model_good = True
        elif action == "repartition": c.representation = 1
        else: raise ValueError(action)
        return c

class Policy:
    def __init__(self, mode: str, seed: int, shared=None):
        self.mode = mode
        self.rng = random.Random(seed)
        self.alpha_beta = shared if shared is not None else {a:[1.0,1.0] for a in ACTIONS}

    def choose(self, tried: set[str]) -> str:
        remaining = [a for a in ACTIONS if a not in tried]
        if self.mode == "random": return self.rng.choice(ACTIONS)
        if self.mode == "local": return self.rng.choice(("operate","reschedule","remodel"))
        if self.mode == "probe": return remaining[0] if remaining else self.rng.choice(ACTIONS)
        if self.mode == "adaptive":
            pool = remaining if remaining else list(ACTIONS)
            samples={a:self.rng.betavariate(*self.alpha_beta[a]) for a in pool}
            return max(pool, key=lambda a:samples[a])
        raise ValueError(self.mode)

    def observe(self, action: str, gain: float):
        ok = gain > 1e-12
        a,b = self.alpha_beta[action]
        self.alpha_beta[action] = [a + int(ok), b + int(not ok)]

def run_episode(fault: str, policy: Policy, budget: int):
    env = Env(fault); cfg = env.base.clone(); initial = env.score(cfg, TRAIN)
    held_initial = env.score(cfg, TEST); pre = initial; tried=set(); trace=[]; first_recovery=None
    for step in range(budget):
        if pre >= 1.0: break
        action = policy.choose(tried); tried.add(action)
        cand = env.apply(cfg, action); post = env.score(cand, TRAIN); gain = post - pre
        trace.append({"step":step,"action":action,"pre_score":pre,"post_score":post,"gain":gain})
        if policy.mode == "adaptive": policy.observe(action, gain)
        cfg, pre = cand, post
        if post >= 1.0:
            first_recovery=action; break
    final=env.score(cfg, TRAIN); held=env.score(cfg, TEST)
    return {"fault":fault,"mode":policy.mode,"initial_train":initial,"initial_test":held_initial,"final_train":final,"final_test":held,"recovered":final>=1.0,"localized":first_recovery == TRUE_ACTION[fault],"true_action":TRUE_ACTION[fault],"first_recovery_action":first_recovery,"cost":len(trace),"trace":trace}

def aggregate(rows):
    n=len(rows)
    return {"n":n,"recovery_rate":sum(r["recovered"] for r in rows)/n,"localization_rate":sum(r["localized"] for r in rows)/n,"mean_recovery_cost":statistics.mean(r["cost"] for r in rows),"mean_final_train":statistics.mean(r["final_train"] for r in rows),"mean_final_test":statistics.mean(r["final_test"] for r in rows)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--episodes",type=int,default=100); ap.add_argument("--seed",type=int,default=20260916); ap.add_argument("--budget",type=int,default=4); ap.add_argument("--out",required=True); args=ap.parse_args()
    modes=("oracle","local","random","probe","adaptive"); rows=[]
    shared={a:[1.0,1.0] for a in ACTIONS}
    policies={m:Policy(m,args.seed+offset, shared if m=="adaptive" else None) for m,offset in zip(("local","random","probe","adaptive"),(23,37,53,71))}
    for ep in range(args.episodes):
        fault=FAULTS[ep % len(FAULTS)]
        for mode in modes:
            if mode=="oracle":
                env=Env(fault); cfg=env.base.clone(); initial=env.score(cfg,TRAIN); act=TRUE_ACTION[fault]
                if act is not None: cfg=env.apply(cfg,act); cost=1
                else: cost=0
                rows.append({"fault":fault,"mode":"oracle","initial_train":initial,"initial_test":env.score(env.base,TEST),"final_train":env.score(cfg,TRAIN),"final_test":env.score(cfg,TEST),"recovered":env.score(cfg,TRAIN)>=1.0,"localized":True,"true_action":act,"first_recovery_action":act,"cost":cost,"trace":[]})
            else: rows.append(run_episode(fault,policies[mode],args.budget))
    by_mode={m:aggregate([r for r in rows if r["mode"]==m]) for m in modes}
    by_fault={f:{m:aggregate([r for r in rows if r["mode"]==m and r["fault"]==f]) for m in modes} for f in FAULTS}
    payload={"protocol":{"episodes":args.episodes,"seed":args.seed,"budget":args.budget,"fault_schedule":"F0,F1,F2,F3,F4 repeating","train_points":TRAIN,"test_points":TEST,"matched_intervention_cost":True,"hidden_fault":True},"interpretation":"Harness validation only. Probe is fixed intervention order; adaptive is history-bearing action selection. Neither is evidence of causal reflection or self-discovered fault ontology.","aggregate":by_mode,"by_fault":by_fault,"rows":rows}
    with open(args.out,"w",encoding="utf-8") as f: json.dump(payload,f,indent=2,sort_keys=True)
    print(json.dumps({"aggregate":by_mode,"by_fault":by_fault},indent=2,sort_keys=True))
if __name__=="__main__": main()
