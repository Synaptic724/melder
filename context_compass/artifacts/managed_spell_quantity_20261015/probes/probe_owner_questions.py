"""Probe for the owner's questions of 2026-10-16 (melder_0): each scenario prints what Melder does today.

Q1  a version parked with bind_inactive BEFORE conjure, notched in after it, then melded - per existence;
    the same version parked AFTER conjure (control); and the parked-before-conjure case with conjure also stamping
    parked versions (a probe-only patch, to show the size of the fix).
Q2  activation hooks on a managed spell: do they run again when a pooled object is leased a second time?
Q4  a meld whose construction fails: does the managed object leased for it go back to the pool?
Q5  managed_spell_meld with an override on the managed spell's own parameter: count, idle and objects alive.

Run from a scratch directory: PYTHONPATH=<repo>/src python -X gil=0 <this file>
"""
import traceback
from typing import Any, List

from melder import Aether, Existence, ReleaseManagedSpell, Spellbook
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook_creation_system import SpellbookCreationSystem


class ServiceA:
    def __init__(self) -> None:
        self.version = "a"


class ServiceB:
    def __init__(self) -> None:
        self.version = "b"


def fresh_aether() -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def q1_case(existence: Existence, park_after_conjure: bool) -> str:
    fresh_aether()
    book = Spellbook()
    book._aetheric_frame_configuration.with_system_state("dynamic")
    managed = {"managed_spell_limit": 4} if existence is Existence.managed_spell_quantity else {}
    id_a = book.bind(spell=ServiceA, existence=existence, permissions="create", binding_name="svc", **managed)
    index = book.find_spell_by_id(id_a).spell_index
    if park_after_conjure:
        conduit = book.conjure(name="root", dynamic=True)
        id_b = book.bind_inactive(spell=ServiceB, spell_index=index, existence=existence, permissions="create",
                                  binding_name="svc_b", **managed)
    else:
        id_b = book.bind_inactive(spell=ServiceB, spell_index=index, existence=existence, permissions="create",
                                  binding_name="svc_b", **managed)
        conduit = book.conjure(name="root", dynamic=True)
    spell_b = book._get_owned_spell(id_b)
    stamped = spell_b._owner_creations is not None
    conduit.notch_spell(spell_index=index, spell=spell_b)
    try:
        obj = conduit.meld(spell_id=id_b)
        result = f"meld works -> {type(obj).__name__}"
    except Exception as exc:
        result = f"meld FAILS: {type(exc).__name__}: {str(exc)[:110]}"
    conduit.cleanup()
    return f"stamped before notch={stamped}; {result}"


def q1() -> None:
    print("Q1  version parked with bind_inactive, notched in, then melded (dynamic world)")
    for existence in (Existence.unique, Existence.unique_per_conduit, Existence.many,
                      Existence.managed_spell_quantity):
        print(f"  {existence.name:24} parked BEFORE conjure: {q1_case(existence, False)}")
        print(f"  {existence.name:24} parked AFTER conjure:  {q1_case(existence, True)}")
    original = SpellbookCreationSystem.define_conduit_into_spells

    def stamp_parked_too(spellbook: Spellbook, conduit: Conduit) -> None:
        original(spellbook, conduit)
        caching_enabled = spellbook._resolve_system_caching_enabled()
        with spellbook._lock:
            for parked in spellbook._inactive_spells.values():
                if parked._owner_creations is None:
                    parked._add_owned_conduit(
                        conduit._id, conduit._name, conduit._creations,
                        dynamic_environment=conduit.__dynamic_environment__,
                        creation_gate_controller=conduit._creation_gate_controller,
                        caching_enabled=caching_enabled,
                    )

    SpellbookCreationSystem.define_conduit_into_spells = staticmethod(stamp_parked_too)
    try:
        for existence in (Existence.unique, Existence.unique_per_conduit, Existence.many,
                          Existence.managed_spell_quantity):
            print(f"  {existence.name:24} parked BEFORE conjure, conjure stamps parked (probe-only patch): "
                  f"{q1_case(existence, False)}")
    finally:
        SpellbookCreationSystem.define_conduit_into_spells = staticmethod(original)


class Connection:
    built = 0

    def __init__(self) -> None:
        Connection.built += 1
        self.serial = Connection.built


def q2() -> None:
    fresh_aether()
    calls: List[int] = []
    book = Spellbook()
    book.bind(spell=Connection, existence=Existence.managed_spell_quantity, permissions="create",
              activation_hooks=[lambda obj: calls.append(obj.serial)])
    conduit = book.conjure(name="root")
    first = conduit.meld(Connection)
    ReleaseManagedSpell().release(first)
    second = conduit.meld(Connection)
    print("Q2  activation hook on a managed spell, lease -> release -> lease again")
    print(f"  same object both times: {first is second}; objects built: {Connection.built}; "
          f"hook ran for serials {calls}")
    conduit.cleanup()


class Channel:
    built = 0
    closed = 0

    def __init__(self) -> None:
        Channel.built += 1

    def close(self) -> None:
        Channel.closed += 1


class Exploding:
    def __init__(self) -> None:
        raise RuntimeError("Exploding.__init__ failed")


class Consumer:
    def __init__(self, channel: Channel, exploding: Exploding) -> None:
        self.channel = channel
        self.exploding = exploding


class FailingConsumer:
    def __init__(self, channel: Channel) -> None:
        raise RuntimeError("FailingConsumer.__init__ failed after its channel was leased")


def q4() -> None:
    fresh_aether()
    book = Spellbook()
    book.bind(spell=Channel, existence=Existence.managed_spell_quantity, permissions="create",
              disposal_method_names=["close"])
    book.bind(spell=Exploding, existence=Existence.many, permissions="create")
    book.bind(spell=Consumer, existence=Existence.many, permissions="create")
    book.bind(spell=FailingConsumer, existence=Existence.many, permissions="create")
    conduit = book.conjure(name="root")
    pool = conduit._creations.get_managed_quantity(book.find_spell_by_id(
        next(s.spell_id for s in book._spells.values() if s.spell_name == "Channel")).spell_id)
    print("Q4  a meld whose construction fails: what happens to the managed object leased for it")
    try:
        conduit.meld(Consumer)
        print("  unexpected: Consumer built")
    except Exception as exc:
        print(f"  meld(Consumer) [sibling dependency raises] -> {type(exc).__name__}; Channel pool: "
              f"count={pool.count} idle={pool.idle_count} (Channel built {Channel.built}, closed {Channel.closed})")
    try:
        conduit.meld(FailingConsumer)
        print("  unexpected: FailingConsumer built")
    except Exception as exc:
        print(f"  meld(FailingConsumer) [its own constructor raises] -> {type(exc).__name__}; Channel pool: "
              f"count={pool.count} idle={pool.idle_count} (Channel built {Channel.built}, closed {Channel.closed})")
    conduit.cleanup()


class Sink:
    def __init__(self) -> None:
        self.lines: List[str] = []


class Pipe:
    built = 0
    closed = 0

    def __init__(self, sink: Sink) -> None:
        Pipe.built += 1
        self.sink = sink

    def close(self) -> None:
        Pipe.closed += 1


def q5() -> None:
    fresh_aether()
    book = Spellbook()
    book.bind(spell=Sink, existence=Existence.unique, permissions="create")
    book.bind(spell=Pipe, existence=Existence.managed_spell_quantity, permissions="create",
              managed_spell_mode="limited_quantity", managed_spell_limit=2, disposal_method_names=["close"])
    conduit = book.conjure(name="root")
    release = ReleaseManagedSpell().release

    def state(label: str) -> None:
        row = ReleaseManagedSpell().describe(Pipe)[0]
        print(f"  {label:58} count={row['count']} idle={row['idle_count']} "
              f"built={Pipe.built} closed={Pipe.closed} alive={Pipe.built - Pipe.closed}")

    print("Q5  limited_quantity, limit 2; managed_spell_meld with an override on Pipe's own parameter")
    a = conduit.meld(Pipe)
    b = conduit.meld(Pipe)
    state("two leased")
    try:
        conduit.meld(Pipe)
    except Exception as exc:
        print(f"  third plain meld refused: {type(exc).__name__}")
    lease = conduit.managed_spell_meld(Pipe, override={"sink": Sink()})
    state("override meld (fresh object, not counted)")
    release(a)
    release(b)
    lease.release()
    state("all three released")
    leased: List[Any] = []
    for _ in range(6):
        try:
            leased.append(conduit.meld(Pipe))
        except Exception as exc:
            print(f"  meld #{len(leased) + 1} refused: {type(exc).__name__}")
            break
    state(f"after leasing again ({len(leased)} out)")
    for obj in leased:
        release(obj)
    state("all released")
    for cycle in (2, 3):
        lease = conduit.managed_spell_meld(Pipe, override={"sink": Sink()})
        lease.release()
        state(f"override meld + release, cycle {cycle}")
    leased = []
    for _ in range(8):
        try:
            leased.append(conduit.meld(Pipe))
        except Exception as exc:
            print(f"  meld #{len(leased) + 1} refused: {type(exc).__name__}")
            break
    state(f"after leasing again ({len(leased)} out)")
    conduit.cleanup()


for scenario in (q1, q2, q4, q5):
    try:
        scenario()
    except Exception:
        traceback.print_exc(limit=10)
Aether._reset_singleton_for_tests()
