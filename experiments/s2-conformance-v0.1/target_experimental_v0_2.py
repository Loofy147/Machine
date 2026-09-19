from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).parents[2]
TARGET = ROOT / "experiments" / "substrate-interpreter-v0.2"
sys.path.insert(0, str(TARGET))

from machine import Interpreter, S2, NIL, Prim, Const  # noqa: E402
from .oracle import Miss, Hit

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
        # A target conformance adapter may not infer Miss from relation membership.
        # The current target uses the same concrete NIL value for two abstract outcomes,
        # so an ambiguous result is an adapter/target conformance failure, not a pass.
        if raw is NIL:
            raise AssertionError("ambiguous concrete result: cannot distinguish Miss from Hit(NIL)")
        return Hit(raw)

    def eq_k(self, a, b):
        return a == b

    def equivalent_key_pair(self):
        return ("a", "a")

    def snapshot_relation(self, relation):
        return repr(relation)

def make_target():
    return ExperimentalS2Target()