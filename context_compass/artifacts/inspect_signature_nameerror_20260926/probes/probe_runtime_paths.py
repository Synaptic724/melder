"""Does any ordinary runtime path reach the VALUE-format contract fallback after conjure?

Usage: python -X gil=0 probe_runtime_paths.py <src_root>
"""
import sys
import traceback

sys.path.insert(0, sys.argv[1])
sys.path.insert(0, "/home/claude/work/probes_inspect")

import probe_user_mod as um  # noqa: E402
from melder.aether.aether import Aether  # noqa: E402
from melder.aether.spellbook.spellbook import Spellbook  # noqa: E402
from melder.aether.conduit.conduit import Conduit  # noqa: E402
from melder.aether.spellbook.existence.existence import Existence  # noqa: E402


def step(name, fn):
    try:
        value = fn()
        print(f"{name}: OK -> {value!r}"[:160])
    except Exception as exc:
        tb = traceback.extract_tb(exc.__traceback__)
        frames = [f for f in tb if "/melder/" in f.filename]
        where = f" @ {frames[-1].filename.split('/src/')[-1]}:{frames[-1].lineno}" if frames else ""
        print(f"{name}: RAISED {type(exc).__name__}: {exc}{where}"[:220])
        cause = exc.__cause__ or exc.__context__
        depth = 0
        while cause is not None and depth < 4:
            ctb = traceback.extract_tb(cause.__traceback__)
            cf = [f for f in ctb if "/melder/" in f.filename]
            cw = f" @ {cf[-1].filename.split('/src/')[-1]}:{cf[-1].lineno}" if cf else ""
            print(f"    caused by {type(cause).__name__}: {cause}{cw}"[:220])
            cause = cause.__cause__ or cause.__context__
            depth += 1


def fresh(dynamic):
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    return Spellbook(aetheric_frame=f"runtime-probe-{dynamic}")


for dynamic in (True, False):
    print(f"--- dynamic={dynamic}")
    book = fresh(dynamic)
    book.bind(spell=um.Engine, existence=Existence.unique, permissions="create")
    car_id = book.bind(spell=um.Car, existence=Existence.many, permissions="create")
    conduit = book.conjure(name="rp", dynamic=dynamic)
    step("S0 meld Car", lambda: type(conduit.meld(spell_id=car_id)).__name__)
    step("S1 bind Garage after conjure", lambda: book.bind(spell=um.Garage, existence=Existence.many, permissions="create"))
    step("S1 meld Garage", lambda: type(conduit.meld(spell=um.Garage)).__name__)
    step("S1 meld Car again", lambda: type(conduit.meld(spell_id=car_id)).__name__)
    lesser = None

    def make_lesser():
        global lesser
        lesser = conduit.create_lesser_conduit()
        return type(lesser.meld(spell=um.Garage)).__name__
    step("S2 lesser meld Garage", make_lesser)
    Aether._reset_singleton_for_tests()
