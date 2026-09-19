from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).parents[2]
TARGET = ROOT / "experiments" / "substrate-interpreter-v0.2"
sys.path.insert(0, str(TARGET))

from machine import Interpreter, S2, NIL, Prim, Const
from oracle import Hit

@dataclass(frozen=True)
class EqKey:
    token: str

class ExperimentalS2Target:
    """Target-specific adapter; not part of the S2 semantic specification."""

    def _run(self, relation, key):
        expr = Prim(
            "relation_lookup_direct",
            (Prim("state_read", (Const("rel"),)), Const(key)),
        )
        return Interpreter(S2, {"rel": relation}).run(expr).result

    def lookup(self, relation, key):
        raw = self._run(relation, key)
        # The adapter may not use relation membership to decode an ambiguous result.
        # NIL is therefore a conformance failure when it can represent both Miss and Hit(NIL).
        if raw is NIL:
            raise AssertionError("ambiguous concrete result: cannot distinguish Miss from Hit(NIL)")
        return Hit(raw)

    def eq_k(self, a, b):
        return a == b

    def equivalent_key_pair(self):
        return EqKey("a"), EqKey("a")

    def snapshot_relation(self, relation):
        return repr(relation)

def make_target():
    return ExperimentalS2Target()