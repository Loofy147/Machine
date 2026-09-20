from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).parents[2]
TARGET = ROOT / "experiments" / "substrate-interpreter-v0.2"
sys.path.insert(0, str(TARGET))

from machine import Interpreter, S2, NIL, Prim, Const, RelationLookupHit, RelationLookupMiss
from oracle import Hit, Miss

@dataclass(frozen=True)
class EqKey:
    token: str

class ExperimentalS2Target:
    """Target-specific adapter; not part of the S2 semantic specification."""

    def _run(self, relation, key, hidden_state=None):
        expr = Prim(
            "relation_lookup_direct",
            (Prim("state_read", (Const("rel"),)), Const(key)),
        )
        state = {"rel": relation}
        if hidden_state:
            state.update(hidden_state)
        return Interpreter(S2, state).run(expr).result

    def lookup(self, relation, key):
        raw = self._run(relation, key)
        if isinstance(raw, RelationLookupMiss):
            return Miss()
        if isinstance(raw, RelationLookupHit):
            return Hit(raw.value)
        raise AssertionError(f"target returned an unrecognized concrete lookup result: {raw!r}")

    def lookup_with_hidden_state(self, relation, key, hidden_state):
        raw = self._run(relation, key, hidden_state)
        if isinstance(raw, RelationLookupMiss):
            return Miss()
        if isinstance(raw, RelationLookupHit):
            return Hit(raw.value)
        raise AssertionError(f"target returned an unrecognized concrete lookup result: {raw!r}")

    def eq_k(self, a, b):
        return a == b

    def equivalent_key_pair(self):
        return EqKey("a"), EqKey("a")

    def snapshot_relation(self, relation):
        return repr(relation)

def make_target():
    return ExperimentalS2Target()
