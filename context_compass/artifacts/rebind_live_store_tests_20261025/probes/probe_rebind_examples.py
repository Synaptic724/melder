"""Probe: more examples of the two rebind defects (TASK-2026-10-25-rebind_while_old_objects_are_alive_tests).

Written for the owner's question (chat 2026-10-25: "explain the problems again with more examples an detail").
Each case runs in a fresh cold Aether, caching off, a dynamic root "root" on its own frame:
  E1 `many` bound with close, then shutdown, then flush, each melded at the root     -> what disposes each object?
  E2 `many` bound with [flush, close], then [close]                                  -> the second object's calls
  E3 the old object in a lesser's store, the new one melded at the root             -> per-store, or global?
  E4 the lesser returned to its pool before the rebind, a new lesser melds          -> the emptied store
  E5 `unique` / `unique_per_conduit` rebound as `many`, three melds at the root      -> errors, objects built, disposed
  E6 the same rebind, the new meld through a lesser                                 -> only the holding store fails?
  E7 a `unique` with its own append(), rebound as `many`                            -> no error at all?
"""
import sys

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook

BUILT = []


class Svc:
    def __init__(self):
        self.calls = []
        BUILT.append(self)

    def flush(self):
        self.calls.append("flush")

    def close(self):
        self.calls.append("close")

    def shutdown(self):
        self.calls.append("shutdown")


class Log:
    """A `unique` that happens to have an append method."""

    def __init__(self):
        self.items = []
        self.calls = []
        BUILT.append(self)

    def append(self, item):
        self.items.append(item)

    def close(self):
        self.calls.append("close")


def world(frame):
    Aether._reset_singleton_for_tests()
    a = Aether()
    Spellbook._aether = a
    Conduit._aether = a
    BUILT.clear()
    book = Spellbook(aetheric_frame=frame)
    book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False, disposal=None,
                                disposal_method_names=None)
    book.get_configuration().freeze()
    return book.conjure(dynamic=True, name="root")


def bind(root, cls, existence, names):
    kw = {} if names is None else {"disposal_method_names": names}
    return root.bind(spell=cls, existence=existence, spellframe="svc", binding_name="svc", **kw)


def remove(root, sid, frame):
    root.cleanup_spell(spell=root.get_spell_by_spell_id(sid, frame))


def meld(door):
    return door.meld(spellframe="svc", binding_name="svc")


def ex_three_generations():
    root = world("e1")
    sid = bind(root, Svc, "many", ["close"]); a = meld(root); remove(root, sid, "e1")
    bind(root, Svc, "many", ["shutdown"]); b = meld(root); remove(root, sid, "e1")
    bind(root, Svc, "many", ["flush"]); c = meld(root)
    root.cleanup()
    print("E1 close -> shutdown -> flush, all melded at the root:", a.calls, b.calls, c.calls)


def ex_extra_method():
    root = world("e2")
    sid = bind(root, Svc, "many", ["flush", "close"]); a = meld(root); remove(root, sid, "e2")
    bind(root, Svc, "many", ["close"]); b = meld(root)
    root.cleanup()
    print("E2 ['flush','close'] -> ['close']: first", a.calls, "second", b.calls)


def ex_other_store():
    root = world("e3")
    scope = root.create_lesser_conduit(name="scope")
    sid = bind(root, Svc, "many", ["close"]); a = meld(scope); remove(root, sid, "e3")
    bind(root, Svc, "many", ["shutdown"]); b = meld(root)
    scope.cleanup(); root.cleanup()
    print("E3 old object in a lesser, new one melded at the root:", "first", a.calls, "second", b.calls)


def ex_scope_ended_first():
    root = world("e4")
    scope = root.create_lesser_conduit(name="scope")
    sid = bind(root, Svc, "many", ["close"]); a = meld(scope)
    scope.cleanup()
    remove(root, sid, "e4")
    bind(root, Svc, "many", ["shutdown"])
    scope2 = root.create_lesser_conduit(name="scope2"); b = meld(scope2); scope2.cleanup()
    root.cleanup()
    print("E4 lesser returned before the rebind, new lesser:", "first", a.calls, "second", b.calls,
          "same shell:", scope2 is scope)


def ex_repeated_failing_melds(existence):
    root = world("e5")
    sid = bind(root, Svc, existence, ["close"]); a = meld(root); remove(root, sid, "e5")
    bind(root, Svc, "many", ["close"])
    errors = 0
    for _ in range(3):
        try:
            meld(root)
        except AttributeError:
            errors += 1
    root.cleanup()
    print(f"E5 {existence} -> many, three melds at the root: AttributeErrors {errors}, built {len(BUILT)},",
          "disposal calls per object", [x.calls for x in BUILT])


def ex_other_door(existence):
    root = world("e6")
    sid = bind(root, Svc, existence, ["close"]); a = meld(root); remove(root, sid, "e6")
    bind(root, Svc, "many", ["close"])
    scope = root.create_lesser_conduit(name="scope")
    try:
        b = meld(scope); outcome = "returned " + ("the old object" if b is a else "a new object")
    except AttributeError as e:
        outcome = f"AttributeError {e}"
    scope.cleanup(); root.cleanup()
    print(f"E6 {existence} -> many, the new meld through a lesser:", outcome, [x.calls for x in BUILT])


def ex_append_corner():
    root = world("e7")
    sid = root.bind(spell=Log, existence="unique", spellframe="svc", binding_name="svc", disposal_method_names=["close"])
    old = meld(root); remove(root, sid, "e7")
    root.bind(spell=Log, existence="many", spellframe="svc", binding_name="svc", disposal_method_names=["close"])
    try:
        new = meld(root); outcome = "returned " + ("the old object" if new is old else "a new object")
    except AttributeError as e:
        new = None; outcome = f"AttributeError {e}"
    held = list(old.items)
    root.cleanup()
    print("E7 a `unique` with its own append(), rebound as many:", outcome,
          "| old object's items now:", ["the new object" if x is new else type(x).__name__ for x in held],
          "| disposal calls: old", old.calls, "new", None if new is None else new.calls)


if __name__ == "__main__":
    print("python", sys.version.split()[0], "gil", sys._is_gil_enabled())
    ex_three_generations()
    ex_extra_method()
    ex_other_store()
    ex_scope_ended_first()
    ex_repeated_failing_melds("unique")
    ex_repeated_failing_melds("unique_per_conduit")
    ex_other_door("unique")
    ex_other_door("unique_per_conduit")
    ex_append_corner()
    Aether._reset_singleton_for_tests()
