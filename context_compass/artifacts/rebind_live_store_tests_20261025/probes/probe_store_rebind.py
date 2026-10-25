"""Probe: what the Creations store does when a class is bound again under the same spell_id.

TASK-2026-10-25-rebind_while_old_objects_are_alive_tests; the owner's question in chat (2026-10-25 03:36 MDT):
"what exactly is happening in the creations store explain all your problems with it".
Each case: a fresh Aether, caching off, a dynamic root on its own frame; every meld and purge at the root.
  S1  many(close) -> rebind many(shutdown): meld, teardown               (problem 1, known)
  S2  unique(close) -> rebind many(close): meld                          (problem 2, known)
  S3  many(close), two objects -> rebind unique(close): meld             -> what comes back?
  S4  many(close) -> rebind unique_per_conduit(close): meld              -> what comes back?
  S5  unique(close) -> rebind unique(shutdown): meld, teardown           -> which object, which methods?
  S6  unique(close) -> rebind many(close): purge(spell_id) before a meld
  S7  many(close), two objects -> rebind unique(close): purge(spell_id)  -> count, what is disposed
  S8  many(close) -> rebind many(shutdown): live probes before a meld
  S9  unique(close) -> rebind many(close): live probes before a meld
  S10 no rebind: User(many, close) needs Dep(many, close); purge Dep; meld User again; teardown order
  S11 no rebind: the first User meld supplies its Dep by override, the second builds one; teardown order
"""
import sys
import traceback

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook

BUILT = []
ORDER = []


class Svc:
    def __init__(self):
        self.calls = []
        BUILT.append(self)

    def close(self):
        self.calls.append("close")

    def shutdown(self):
        self.calls.append("shutdown")


class Dep:
    def __init__(self):
        self.closed = False
        BUILT.append(self)

    def close(self):
        self.closed = True
        ORDER.append(("dep", BUILT.index(self)))


class User:
    def __init__(self, dep: Dep):
        self.dep = dep
        BUILT.append(self)

    def close(self):
        ORDER.append(("user", BUILT.index(self), "its dep already closed" if self.dep.closed else "dep still open"))


def world(frame):
    Aether._reset_singleton_for_tests()
    a = Aether()
    Spellbook._aether = a
    Conduit._aether = a
    BUILT.clear()
    ORDER.clear()
    book = Spellbook(aetheric_frame=frame)
    book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False, disposal=None,
                                disposal_method_names=None)
    book.get_configuration().freeze()
    return book.conjure(dynamic=True, name="root")


def bind(root, cls, existence, names, frame_key="svc"):
    kw = {} if names is None else {"disposal_method_names": names}
    return root.bind(spell=cls, existence=existence, spellframe=frame_key, binding_name=frame_key, **kw)


def remove(root, sid, frame):
    root.cleanup_spell(spell=root.get_spell_by_spell_id(sid, frame))


def meld(root, frame_key="svc"):
    return root.meld(spellframe=frame_key, binding_name=frame_key)


def describe(value):
    if isinstance(value, list):
        return f"a Python list of {len(value)} Svc objects"
    return f"a {type(value).__name__} object"


def teardown(root):
    try:
        root.cleanup()
        return "teardown ok"
    except BaseException as error:
        return f"teardown raised {type(error).__name__}: {error}"


def calls():
    return [getattr(o, "calls", None) for o in BUILT]


def case(name, body):
    try:
        print(f"{name}: {body()}")
    except BaseException as error:
        print(f"{name}: UNEXPECTED {type(error).__name__}: {error}")
        traceback.print_exc(limit=3)


def s1():
    root = world("s1")
    sid = bind(root, Svc, "many", ["close"]); meld(root); remove(root, sid, "s1")
    sid2 = bind(root, Svc, "many", ["shutdown"]); meld(root)
    end = teardown(root)
    return f"same id {sid2 == sid}; {end}; calls per object built {calls()}"


def s2():
    root = world("s2")
    sid = bind(root, Svc, "unique", ["close"]); meld(root); remove(root, sid, "s2")
    bind(root, Svc, "many", ["close"])
    try:
        meld(root); out = "meld returned"
    except AttributeError as error:
        out = f"meld raised AttributeError: {error}"
    end = teardown(root)
    return f"{out}; objects built {len(BUILT)}; {end}; calls {calls()}"


def s3():
    root = world("s3")
    sid = bind(root, Svc, "many", ["close"]); meld(root); meld(root); remove(root, sid, "s3")
    bind(root, Svc, "unique", ["close"])
    got = meld(root)
    again = meld(root)
    end = teardown(root)
    return (f"meld returned {describe(got)} (same value next meld: {again is got}); objects built {len(BUILT)}; "
            f"{end}; calls {calls()}")


def s4():
    root = world("s4")
    sid = bind(root, Svc, "many", ["close"]); meld(root); remove(root, sid, "s4")
    bind(root, Svc, "unique_per_conduit", ["close"])
    got = meld(root)
    end = teardown(root)
    return f"meld returned {describe(got)}; objects built {len(BUILT)}; {end}; calls {calls()}"


def s5():
    root = world("s5")
    sid = bind(root, Svc, "unique", ["close"]); first = meld(root); remove(root, sid, "s5")
    bind(root, Svc, "unique", ["shutdown"])
    got = meld(root)
    end = teardown(root)
    return (f"meld returned the first definition's object: {got is first}; objects built {len(BUILT)}; {end}; "
            f"calls {calls()}")


def s6():
    root = world("s6")
    sid = bind(root, Svc, "unique", ["close"]); meld(root); remove(root, sid, "s6")
    sid2 = bind(root, Svc, "many", ["close"])
    try:
        out = f"purge returned {root.purge(spell_id=sid2)}"
    except BaseException as error:
        out = f"purge raised {type(error).__name__}: {error}"
    end = teardown(root)
    return f"{out}; {end}; calls {calls()}"


def s7():
    root = world("s7")
    sid = bind(root, Svc, "many", ["close"]); meld(root); meld(root); remove(root, sid, "s7")
    sid2 = bind(root, Svc, "unique", ["close"])
    try:
        out = f"purge returned {root.purge(spell_id=sid2)}"
    except BaseException as error:
        out = f"purge raised {type(error).__name__}: {error}"
    after = calls()
    end = teardown(root)
    return f"{out}; calls right after the purge {after}; {end}"


def s8():
    root = world("s8")
    sid = bind(root, Svc, "many", ["close"]); meld(root); remove(root, sid, "s8")
    sid2 = bind(root, Svc, "many", ["shutdown"])
    out = []
    for probe in ("has_live_creation", "describe_live_creation_status"):
        try:
            out.append(f"{probe} -> {getattr(root, probe)(spell=sid2)!r}")
        except BaseException as error:
            out.append(f"{probe} raised {type(error).__name__}: {error}")
    end = teardown(root)
    return f"before the new spell built anything: {'; '.join(out)}; {end}"


def s9():
    root = world("s9")
    sid = bind(root, Svc, "unique", ["close"]); meld(root); remove(root, sid, "s9")
    sid2 = bind(root, Svc, "many", ["close"])
    out = []
    for probe in ("has_live_creation", "describe_live_creation_status"):
        try:
            out.append(f"{probe} -> {getattr(root, probe)(spell=sid2)!r}")
        except BaseException as error:
            out.append(f"{probe} raised {type(error).__name__}: {error}")
    end = teardown(root)
    return f"before the new spell built anything: {'; '.join(out)}; {end}"


def s10():
    root = world("s10")
    dep_id = bind(root, Dep, "many", ["close"], frame_key="dep")
    bind(root, User, "many", ["close"], frame_key="user")
    meld(root, "user")                    # dep#0 (Dep key first), user#1 (User key second)
    purged = root.purge(spell_id=dep_id)  # dep#0 closed; the Dep key leaves the store
    ORDER.clear()
    meld(root, "user")                    # dep#2 (Dep key again, now after User), user#3 (appended under User)
    end = teardown(root)
    return f"purged {purged}; {end}; teardown order {ORDER}"


def s11():
    root = world("s11")
    bind(root, Dep, "many", ["close"], frame_key="dep")
    bind(root, User, "many", ["close"], frame_key="user")
    supplied = Dep()                                                # built by the caller, not recorded
    root.meld(spellframe="user", binding_name="user", override={"dep": supplied})   # user#1: User key first
    meld(root, "user")                    # dep#2 (Dep key now after User), user#3 (appended under User)
    end = teardown(root)
    return f"{end}; teardown order {ORDER}"



if __name__ == "__main__":
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()}")
    for name, body in [("S1", s1), ("S2", s2), ("S3", s3), ("S4", s4), ("S5", s5), ("S6", s6), ("S7", s7),
                       ("S8", s8), ("S9", s9), ("S10", s10),
                       ("S11", s11)]:
        case(name, body)
