"""Probe: does a `many` key's disposal record outlive a rebind of its spell under other disposal names?

Cases (each in a fresh cold Aether, caching off, dynamic root "root" in frame "probe"):
  R1 rebind with another list, both products built by the root     -> which methods dispose the second product?
  R2 control: rebind with the same list                              -> both products disposed with it
  R3 the products built by a lesser scope, the lesser's pool return  -> same question in the lesser's store
  R4 old definition without disposal names, new one with them        -> the new product's own list
  R5 old definition with them, new one without                       -> is the new product recorded at all?
Prints, per case: the spell_id equality, the store record's method list, and the disposal events per product.
"""

import sys
import sysconfig

from melder import Aether, Conduit, Spellbook

EVENTS = []


class Svc:
    """A `many` service with two disposal-capable methods; records which ones run."""

    def __init__(self) -> None:
        self.tag = None

    def close(self) -> None:
        EVENTS.append((self.tag, "close"))

    def shutdown(self) -> None:
        EVENTS.append((self.tag, "shutdown"))


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


def bind(root, names):
    kwargs = {} if names is None else {"disposal_method_names": names}
    return root.bind(spell=Svc, existence="many", spellframe="svc", binding_name="svc", **kwargs)


def record_of(store, sid):
    rec = store._disposable_creations.get(sid)
    return None if rec is None else list(rec.methods)


def run(case, first, second, via_lesser=False):
    EVENTS.clear()
    book, root = fresh_world()
    scope = root.create_lesser_conduit(name="scope") if via_lesser else None
    melder_door = scope if via_lesser else root
    sid1 = bind(root, first)
    a = melder_door.meld(spellframe="svc", binding_name="svc")
    a.tag = "first"
    store = melder_door._creations
    rec_before = record_of(store, sid1)
    root.cleanup_spell(spell=root.get_spell_by_spell_id(sid1, "probe"))
    sid2 = bind(root, second)
    b = melder_door.meld(spellframe="svc", binding_name="svc")
    b.tag = "second"
    rec_after = record_of(store, sid2)
    live = store._creations.get(sid2)
    live_tags = None if live is None else [getattr(x, "tag", "?") for x in live]
    spell2_list = list(root.get_spell_by_spell_id(sid2, "probe").disposal_method_names)
    if via_lesser:
        scope.cleanup()
        ended = list(EVENTS)
        root.cleanup()
    else:
        root.cleanup()
        ended = list(EVENTS)
    print(f"{case}: first={first} second={second} via_lesser={via_lesser}")
    print(f"   same spell_id: {sid1 == sid2}; the second Spell's own list: {spell2_list}")
    print(f"   record after first meld: {rec_before}; after second meld: {rec_after}; bucket: {live_tags}")
    print(f"   disposal events when the store ended: {ended}")


if __name__ == "__main__":
    gil = getattr(sys, "_is_gil_enabled", lambda: True)()
    print(f"python {sys.version.split()[0]} free-threaded={sysconfig.get_config_var('Py_GIL_DISABLED')} gil={gil}")
    run("R1", ["close"], ["shutdown"])
    run("R2", ["close"], ["close"])
    run("R3", ["close"], ["shutdown"], via_lesser=True)
    run("R4", None, ["shutdown"])
    run("R5", ["close"], None)
    Aether._reset_singleton_for_tests()
