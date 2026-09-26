"""Does a unique build ever take a SCOPE store's lock (lesser or shared SpellSpace)? melder_0, 2026-09-25.

Thread A melds a scope-based consumer P through door D (lesser conduit or shared SpellSpace): D's store lock is
held for P's build; A is paused exactly when it requests unique U's Spell lock. Thread C melds U through the SAME
door. If C, holding U's Spell lock, ever requests D's store lock, that request is refused and recorded: a cycle.
"""
import json
import sys
from threading import Thread

from melder import Aether, Conduit, Existence, Spellbook
from meld_only_standalone_probe import ObservedLock, Trace, spells_of


class Q:
    """Scope-based leaf (per-conduit or per-SpellSpace)."""

    def __init__(self) -> None:
        """No deps."""


class MViaQ:
    """many that depends on the scope-based Q."""

    def __init__(self, q: Q) -> None:
        """Hold q."""
        self.q = q


class MDisp:
    """many with a disposal method, no deps."""

    def __init__(self) -> None:
        """No deps."""

    def close(self) -> None:
        """Disposal."""


class UViaM:
    """unique -> many -> scope."""

    def __init__(self, m: MViaQ) -> None:
        """Hold m."""
        self.m = m


class UDisp:
    """unique -> disposal many (row 4b)."""

    def __init__(self, m: MDisp) -> None:
        """Hold m."""
        self.m = m


class PViaM:
    """Scope consumer of UViaM."""

    def __init__(self, u: UViaM) -> None:
        """Hold u."""
        self.u = u


class PDisp:
    """Scope consumer of UDisp."""

    def __init__(self, u: UDisp) -> None:
        """Hold u."""
        self.u = u


def run(case: str, door_kind: str) -> dict:
    """One interleaving."""
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Spellbook._aether
    scope = "unique_per_conduit" if door_kind == "lesser" else "unique_per_spell_space"
    book = Spellbook(aetheric_frame=f"scope-{case}-{door_kind}")
    if case == "unique_many_scope":
        book.bind(spell=Q, existence=scope)
        book.bind(spell=MViaQ, existence="many")
        book.bind(spell=UViaM, existence="unique")
        book.bind(spell=PViaM, existence=scope)
        consumer, unique_type = PViaM, UViaM
    else:
        book.bind(spell=MDisp, existence="many", disposal_method_names=["close"])
        book.bind(spell=UDisp, existence="unique")
        book.bind(spell=PDisp, existence=scope)
        consumer, unique_type = PDisp, UDisp
    root = book.conjure(name="scope-probe")
    door = root.create_lesser_conduit() if door_kind == "lesser" else root.create_spellspace()
    door.meld(spell=consumer)  # warm
    door_store = door._meld._conduit_creations if door_kind == "lesser" else door._meld._spellspace_creations
    root_store = root._meld._conduit_creations
    for sp in spells_of(book):  # back to never-built everywhere
        for st in (door_store, root_store):
            st._creations.pop(sp.spell_id, None)
            st._disposable_creations.pop(sp.spell_id, None)
    u = next(s for s in spells_of(book) if s.spell is unique_type)
    trace = Trace()
    raw_store, raw_u = door_store._lock, u._lock
    store_lock, u_lock = ObservedLock(raw_store, trace, "scope_store"), ObservedLock(raw_u, trace, "u_spell")
    u_lock.pause_thread, store_lock.refuse_thread = "meld-A", "meld-C"
    out: dict = {"A": [], "C": []}

    def go(tag: str, target: type) -> None:
        try:
            out[tag].append(type(door.meld(spell=target)).__name__)
        except BaseException as e:
            out[tag].append(f"{type(e).__name__}: {e}")

    door_store._lock, u._lock = store_lock, u_lock
    try:
        a = Thread(target=go, args=("A", consumer), name="meld-A", daemon=True)
        a.start()
        a_paused = u_lock.paused.wait(6)
        c = Thread(target=go, args=("C", unique_type), name="meld-C", daemon=True)
        c.start()
        c.join(5)
        c_stuck = c.is_alive()
    finally:
        u_lock.resume.set()
        a.join(10)
        c.join(10)
        door_store._lock, u._lock = raw_store, raw_u
    rows = trace.rows
    cycle = (a_paused and ("meld-A", "scope_store", "acquired") in rows
             and ("meld-C", "u_spell", "acquired") in rows and ("meld-C", "scope_store", "would_block") in rows)
    return {"case": case, "door": door_kind, "cycle_formed": cycle, "A_paused_holding_scope_store": a_paused,
            "C_requested_scope_store": any(r[0] == "meld-C" and r[1] == "scope_store" for r in rows),
            "C_stuck_elsewhere": c_stuck, "A": out["A"], "C": out["C"]}


if __name__ == "__main__":
    results = [run(case, door) for case in ("unique_many_scope", "disposal_many") for door in ("lesser", "space")]
    json.dump({"python": sys.version, "gil": sys._is_gil_enabled(), "results": results},
              open("scope_store_probe_results.json", "w"), indent=2)
    for r in results:
        print(r)
