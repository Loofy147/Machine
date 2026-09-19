import pytest
from .target_experimental_v0_2 import make_target

@pytest.fixture
def target():
    return make_target()

@pytest.fixture
def nil_value():
    from pathlib import Path
    import sys
    root = Path(__file__).parents[2]
    sys.path.insert(0, str(root / "experiments" / "substrate-interpreter-v0.2"))
    from machine import NIL
    return NIL

@pytest.fixture
def equivalent_pair():
    return ("a", "a")

@pytest.fixture
def third_equivalent_key():
    return "a"