"""Probe R6: a spell rebound as `many` after a slotted definition left its object in the store.

register_many's docstring promises "one Existence per Spell means the key's live slot is a list or absent".
Since 0.2.8258 existence is a binding-manifest field, so cleanup_spell and a new bind of the same class as
`many` keep the spell_id. Case R6a: unique_per_conduit -> many; R6b: unique -> many. Each in a fresh cold Aether.
"""

import sys
import sysconfig
import traceback

from melder import Aether, Conduit, Spellbook

EVENTS = []


class Svc:
    """A service with one disposal-capable method that records its calls."""

    def __init__(self) -> None:
        self.tag = None

    def close(self) -> None:
        EVENTS.append((self.tag, "close"))


def fresh_world():
    Aether._reset_singleton_for_tests()
    world = Aether()
    Spellbook._aether = world
    Conduit._aether = world
    book = Spellbook(aetheric_frame="probe")
    book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False,
                                disposal=None, disposal_method_names=None)
    book.get_configuration().freeze()
    root = book.conjure(dynamic=True, name="root")
    return book, root


def run(case, first_existence):
    EVENTS.clear()
    book, root = fresh_world()
    sid1 = root.bind(spell=Svc, existence=first_existence, spellframe="svc", binding_name="svc",
                     disposal_method_names=["close"])
    a = root.meld(spellframe="svc", binding_name="svc")
    a.tag = "first"
    store = root._creations
    slot_before = type(store._creations.get(sid1)).__name__
    root.cleanup_spell(spell=root.get_spell_by_spell_id(sid1, "probe"))
    sid2 = root.bind(spell=Svc, existence="many", spellframe="svc", binding_name="svc",
                     disposal_method_names=["close"])
    print(f"{case}: {first_existence} -> many; same spell_id: {sid1 == sid2}; slot type before rebind: {slot_before}")
    try:
        b = root.meld(spellframe="svc", binding_name="svc")
        b.tag = "second"
        print(f"   second meld returned the first object: {b is a}; slot type now: "
              f"{type(store._creations.get(sid2)).__name__}")
    except Exception as exc:
        print(f"   second meld raised {type(exc).__name__}: {exc}")
        tb = traceback.extract_tb(exc.__traceback__)
        print(f"   innermost frame: {tb[-1].name} ({tb[-1].filename.rsplit('/', 1)[-1]}:{tb[-1].lineno})")
    try:
        root.cleanup()
    except Exception as exc:
        print(f"   teardown raised {type(exc).__name__}: {exc}")
    print(f"   disposal events: {EVENTS}")


if __name__ == "__main__":
    gil = getattr(sys, "_is_gil_enabled", lambda: True)()
    print(f"python {sys.version.split()[0]} free-threaded={sysconfig.get_config_var('Py_GIL_DISABLED')} gil={gil}")
    run("R6a", "unique_per_conduit")
    run("R6b", "unique")
    Aether._reset_singleton_for_tests()
