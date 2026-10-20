"""
Probe: the public lifecycle of `Existence.managed_spell_quantity`, case by case.

Purpose:
    EPIC-2026-10-18-managed_spell_examples_and_docs, S1 (STORY-2026-10-18-managed_spell_lifecycle_map). The UX
    law (`UX_and_AIX_experiences/AGENTS.md`) lets an example assert only behaviour verified in source or proven by
    a probe row. Each case below runs one lifecycle step through the public `melder` surface and prints what
    happened, so the examples and the Sphinx page assert exactly that.

Run from the repository root on 3.14t (GIL off, then on):
    PYTHONPATH=src python probe_managed_lifecycle.py
    PYTHONPATH=src PYTHON_GIL=1 python probe_managed_lifecycle.py

Each case runs in a fresh world: the probe resets the hosted roots and Aether the way the example harness's
conftest does (`UX_and_AIX_experiences/pytest_examples/conftest.py`), which needs one deep import that the
examples themselves never use.
"""
import sys
import threading
import time
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple

import melder as md
from melder.aether.spellbook.spellbook import Spellbook as _HarnessSpellbook


def fresh_world() -> None:
    """Reset the process-wide roots and Aether, as the example harness does between examples."""
    md.MutationResearch._reset_singleton_for_tests()
    md.Crystallizer._reset_singleton_for_tests()
    md.Nexus._reset_singleton_for_tests()
    md.Aether._reset_singleton_for_tests()
    aether = md.Aether()
    _HarnessSpellbook._aether = aether
    md.Conduit._aether = aether


RESULTS: List[Tuple[str, str]] = []


def row(case: str, text: str) -> None:
    """Print one probe row and keep it for the summary."""
    RESULTS.append((case, text))
    print(f"[{case}] {text}")


def run(case: str, body: Callable[[], None]) -> None:
    """Run one case in a fresh world; a raise is reported as a FAILED row, never hidden."""
    fresh_world()
    try:
        body()
    except Exception as error:
        row(case, f"FAILED {type(error).__name__}: {error}")
        traceback.print_exc()
    finally:
        fresh_world()


def snapshot(cls: type) -> Dict[str, Any]:
    """Return the one pool snapshot of a class (the cases bind each class once)."""
    snapshots = md.ReleaseManagedSpell().describe(cls)
    assert len(snapshots) == 1, snapshots
    return snapshots[0]


def counts(cls: type) -> str:
    """Return count / idle / out of a class's one pool as text."""
    s = snapshot(cls)
    return f"count={s['count']} idle={s['idle_count']} out={s['out_count']}"


# --------------------------------------------------------------------------------------------------------------
# Classes (each case binds its own classes, once)
# --------------------------------------------------------------------------------------------------------------
class Connection:
    """A pooled object with an observable close (its disposal method)."""

    built: int = 0

    def __init__(self) -> None:
        Connection.built += 1
        self.serial: int = Connection.built
        self.closed: bool = False

    def close(self) -> None:
        self.closed = True


class Buffer:
    """A pooled object with state a reset clears, and a reset call log."""

    def __init__(self) -> None:
        self.data: List[str] = []
        self.resets: List[str] = []
        self.closed: bool = False

    def clear(self) -> None:
        self.data.clear()
        self.resets.append("clear")

    def rewind(self) -> None:
        self.resets.append("rewind")

    def close(self) -> None:
        self.closed = True


class FragileBuffer:
    """A pooled object whose reset raises once it is marked broken."""

    def __init__(self) -> None:
        self.broken: bool = False
        self.closed: bool = False

    def reset(self) -> None:
        if self.broken:
            raise ValueError("cannot reset a broken buffer")

    def close(self) -> None:
        self.closed = True


class Ticket:
    """A limited_quantity object."""

    def __init__(self) -> None:
        self.closed: bool = False

    def close(self) -> None:
        self.closed = True


class Slot:
    """A queue object."""

    def __init__(self) -> None:
        self.closed: bool = False

    def close(self) -> None:
        self.closed = True


class Lease:
    """An object leased through managed_spell_meld."""

    def __init__(self) -> None:
        self.uses: int = 0


class Plain:
    """A non-managed spell."""


class RequestHandler:
    """A many consumer that receives a pooled Connection by injection and gives it back at its disposal."""

    def __init__(self, connection: Connection) -> None:
        self.connection: Connection = connection
        self.done: bool = False

    def finish(self) -> None:
        if self.done:
            return
        self.done = True
        md.ReleaseManagedSpell().release(self.connection)


class Holder:
    """A many consumer that keeps its Connection and never gives it back."""

    def __init__(self, connection: Connection) -> None:
        self.connection: Connection = connection


class PerScope:
    """A unique_per_conduit spell (for the scope-ordering case)."""


class NeedsPerScope:
    """A managed spell depending on a unique_per_conduit spell."""

    def __init__(self, scoped: PerScope) -> None:
        self.scoped: PerScope = scoped


class Settings:
    """A managed spell rebound with other settings."""

    def __init__(self) -> None:
        self.closed: bool = False

    def close(self) -> None:
        self.closed = True


class Movable:
    """A managed spell whose pool moves with an ownership transfer."""


class Configured:
    """A managed spell bound through SpellBinder."""

    def __init__(self) -> None:
        self.dirty: bool = False

    def reset(self) -> None:
        self.dirty = False


class WithArg:
    """A managed spell with a plain constructor parameter (for overrides)."""

    def __init__(self, size: int = 1) -> None:
        self.size: int = size


# --------------------------------------------------------------------------------------------------------------
# Cases
# --------------------------------------------------------------------------------------------------------------
def p01_elastic_basics() -> None:
    book = md.Spellbook()
    spell_id = book.bind(spell=Connection, existence=md.Existence.managed_spell_quantity,
                         disposal_method_names=["close"])
    conduit = book.conjure()
    try:
        before = snapshot(Connection)
        row("P01", f"pool composed at conjure, before any meld: mode={before['mode']} limit={before['limit']} "
                   f"{counts(Connection)} spell_id_matches={before['spell_id'] == spell_id}")
        row("P01", f"has_live_creation before any meld: {conduit.has_live_creation('Connection')}")
        a: Connection = conduit.meld("Connection")
        b: Connection = conduit.meld("Connection")
        row("P01", f"two melds, nothing released: distinct={a is not b} {counts(Connection)}")
        row("P01", f"has_live_creation now: {conduit.has_live_creation('Connection')}")
        md.ReleaseManagedSpell().release(a)
        row("P01", f"after releasing a: {counts(Connection)} a.closed={a.closed}")
        c: Connection = conduit.meld("Connection")
        row("P01", f"next meld reuses the released object: c_is_a={c is a} {counts(Connection)}")
        md.ReleaseManagedSpell().release(b)
        md.ReleaseManagedSpell().release(c)
        d: Connection = conduit.meld("Connection")
        row("P01", f"newest released is leased first (LIFO): d_is_c={d is c} d_is_b={d is b}")
        md.ReleaseManagedSpell().release(d)
        row("P01", f"snapshot keys: {sorted(snapshot(Connection))}")
        row("P01", f"purge of a managed spell removes nothing: {conduit.purge('Connection')}")
    finally:
        conduit.cleanup()
    row("P01", f"root teardown disposed the idle objects: a.closed={a.closed} b.closed={b.closed}")
    row("P01", f"describe after teardown: {md.ReleaseManagedSpell().describe(Connection)}")
    book.cleanup()


def p02_elastic_small_limit_trims() -> None:
    book = md.Spellbook()
    book.bind(spell=Connection, existence="managed_spell_quantity", disposal_method_names=["close"],
              managed_spell_mode="elastic", managed_spell_limit=2)
    conduit = book.conjure()
    try:
        objects = [conduit.meld("Connection") for _ in range(3)]
        row("P02", f"elastic limit 2 still builds a third: {counts(Connection)}")
        for obj in objects:
            md.ReleaseManagedSpell().release(obj)
        closed = [obj.closed for obj in objects]
        row("P02", f"releasing 3 into a pool that keeps 2: closed={closed} {counts(Connection)}")
        s = snapshot(Connection)
        row("P02", f"retention: baseline_idle={s['baseline_idle']} max_idle={s['max_idle']} "
                   f"target_idle={s['target_idle']}")
    finally:
        conduit.cleanup()
    book.cleanup()


def p03_limited_quantity() -> None:
    book = md.Spellbook()
    book.bind(spell=Ticket, existence=md.Existence.managed_spell_quantity, disposal_method_names=["close"],
              managed_spell_mode=md.ManagedSpellMode.limited_quantity, managed_spell_limit=2)
    conduit = book.conjure()
    try:
        first = conduit.meld("Ticket")
        second = conduit.meld("Ticket")
        row("P03", f"two leases at limit 2: {counts(Ticket)}")
        try:
            conduit.meld("Ticket")
            row("P03", "third lease UNEXPECTEDLY succeeded")
        except md.ManagedSpellExhaustedError as refused:
            row("P03", f"third lease refused: ManagedSpellExhaustedError is MeldExecutionError="
                       f"{isinstance(refused, md.MeldExecutionError)} mode={refused.mode} limit={refused.limit} "
                       f"timeout_seconds={refused.timeout_seconds} spell_name={refused.spell_name}")
            row("P03", f"message: {refused}")
        row("P03", f"nothing was built by the refusal: {counts(Ticket)}")
        md.ReleaseManagedSpell().release(first)
        third = conduit.meld("Ticket")
        row("P03", f"after a release the lease is served the released object: third_is_first={third is first} "
                   f"{counts(Ticket)}")
        md.ReleaseManagedSpell().release_all([second, third])
        row("P03", f"release_all gives both back: {counts(Ticket)}")
    finally:
        conduit.cleanup()
    book.cleanup()


def p04_queue_handoff_and_timeout() -> None:
    book = md.Spellbook()
    book.bind(spell=Slot, existence=md.Existence.managed_spell_quantity, disposal_method_names=["close"],
              managed_spell_mode="queue", managed_spell_limit=1, managed_spell_timeout_seconds=5.0)
    conduit = book.conjure()
    try:
        held = conduit.meld("Slot")
        got: Dict[str, Any] = {}
        started = threading.Event()

        def waiter() -> None:
            started.set()
            begin = time.monotonic()
            got["obj"] = conduit.meld("Slot")
            got["waited"] = time.monotonic() - begin

        thread = threading.Thread(target=waiter)
        thread.start()
        started.wait()
        time.sleep(0.2)
        row("P04", f"waiter still waiting while the only Slot is out: alive={thread.is_alive()}")
        md.ReleaseManagedSpell().release(held)
        thread.join(5.0)
        row("P04", f"release hands the object to the waiter: same={got.get('obj') is held} "
                   f"waited~{got.get('waited', -1):.2f}s {counts(Slot)}")
    finally:
        conduit.cleanup()
    book.cleanup()

    fresh_world()
    book = md.Spellbook()
    book.bind(spell=Slot, existence=md.Existence.managed_spell_quantity,
              managed_spell_mode="queue", managed_spell_limit=1, managed_spell_timeout_seconds=0.3)
    conduit = book.conjure()
    try:
        conduit.meld("Slot")
        begin = time.monotonic()
        try:
            conduit.meld("Slot")
            row("P04", "second queue lease UNEXPECTEDLY succeeded")
        except md.ManagedSpellExhaustedError as refused:
            elapsed = time.monotonic() - begin
            row("P04", f"queue refuses at its timeout: waited>=0.3={elapsed >= 0.3} mode={refused.mode} "
                       f"limit={refused.limit} timeout_seconds={refused.timeout_seconds}")
            row("P04", f"message: {refused}")
    finally:
        conduit.cleanup()
    book.cleanup()


def p05_resets() -> None:
    book = md.Spellbook()
    book.bind(spell=Buffer, existence=md.Existence.managed_spell_quantity, disposal_method_names=["close"],
              managed_spell_reset_methods=["clear", "rewind"])
    book.bind(spell=FragileBuffer, existence=md.Existence.managed_spell_quantity, disposal_method_names=["close"],
              managed_spell_reset_methods=("reset",))
    conduit = book.conjure()
    try:
        buf: Buffer = conduit.meld("Buffer")
        buf.data.append("request-1")
        md.ReleaseManagedSpell().release(buf)
        row("P05", f"release runs the resets in order: resets={buf.resets} data={buf.data}")
        again: Buffer = conduit.meld("Buffer")
        row("P05", f"the next lease gets the reset object: same={again is buf} data={again.data}")
        md.ReleaseManagedSpell().release(again)

        fragile: FragileBuffer = conduit.meld("FragileBuffer")
        fragile.broken = True
        try:
            md.ReleaseManagedSpell().release(fragile)
            row("P05", "raising reset UNEXPECTEDLY did not raise")
        except ValueError as error:
            row("P05", f"a raising reset propagates its error ({error}); the object was destroyed: "
                       f"closed={fragile.closed} {counts(FragileBuffer)}")
        replacement = conduit.meld("FragileBuffer")
        row("P05", f"the next lease builds a new object: new={replacement is not fragile} {counts(FragileBuffer)}")
    finally:
        conduit.cleanup()
    book.cleanup()


def p06_leases() -> None:
    book = md.Spellbook()
    book.bind(spell=Lease, existence=md.Existence.managed_spell_quantity)
    book.bind(spell=Plain, existence=md.Existence.many)
    conduit = book.conjure()
    try:
        with conduit.managed_spell_meld(Lease) as obj:
            obj.uses += 1
            row("P06", f"inside the with block the object is out: {counts(Lease)} type={type(obj).__name__}")
        row("P06", f"the with block gave it back: {counts(Lease)}")
        lease = conduit.managed_spell_meld("Lease")
        row("P06", f"managed_spell_meld returns a ManagedSpellLease={isinstance(lease, md.ManagedSpellLease)} "
                   f"same_object_reused={lease.object is obj} released={lease.released}")
        lease.release()
        lease.release()
        row("P06", f"release twice is one release: released={lease.released} {counts(Lease)}")
        try:
            lease.object
            row("P06", "lease.object after release UNEXPECTEDLY answered")
        except RuntimeError as error:
            row("P06", f"lease.object after release raises RuntimeError: {error}")
        try:
            with conduit.managed_spell_meld(Lease) as inner:
                raise KeyError("the block failed")
        except KeyError:
            row("P06", f"a raising block still releases and does not suppress: {counts(Lease)}")
        melded = conduit.meld("Lease")
        with md.ReleaseManagedSpell().managed(melded) as same:
            row("P06", f"ReleaseManagedSpell().managed(obj) leases what meld returned: same={same is melded}")
        row("P06", f"and gives it back on exit: {counts(Lease)}")
        try:
            conduit.managed_spell_meld("Plain")
            row("P06", "managed_spell_meld of a many spell UNEXPECTEDLY worked")
        except ValueError as error:
            row("P06", f"managed_spell_meld refuses another existence: {error}")
    finally:
        conduit.cleanup()
    book.cleanup()


def p07_injection_request_scopes() -> None:
    book = md.Spellbook()
    book.bind(spell=Connection, existence=md.Existence.managed_spell_quantity, disposal_method_names=["close"])
    book.bind(spell=RequestHandler, existence=md.Existence.many, disposal_method_names=["finish"])
    root = book.conjure()
    try:
        with root.enter_lesser_conduit() as request:
            h1: RequestHandler = request.meld("RequestHandler")
            h2: RequestHandler = request.meld("RequestHandler")
            row("P07", f"each injection is its own lease: distinct={h1.connection is not h2.connection} "
                       f"{counts(Connection)}")
        row("P07", f"the request scope's exit disposed the handlers, which gave the leases back: "
                   f"h1.done={h1.done} h2.done={h2.done} {counts(Connection)}")
        with root.enter_lesser_conduit() as request:
            h3: RequestHandler = request.meld("RequestHandler")
            row("P07", f"the next request reuses a pooled connection: reused="
                       f"{h3.connection is h1.connection or h3.connection is h2.connection} {counts(Connection)}")
        row("P07", f"after the second request: {counts(Connection)}")
    finally:
        root.cleanup()
    book.cleanup()


def p08_teardown_with_objects_out() -> None:
    book = md.Spellbook()
    book.bind(spell=Connection, existence=md.Existence.managed_spell_quantity, disposal_method_names=["close"])
    book.bind(spell=Holder, existence=md.Existence.many)
    root = book.conjure()
    idle = root.meld("Connection")
    out = root.meld("Connection")
    held: Holder = root.meld("Holder")
    md.ReleaseManagedSpell().release(idle)
    row("P08", f"before teardown: {counts(Connection)}")
    root.cleanup()
    row("P08", f"root teardown disposes idle objects only: idle.closed={idle.closed} out.closed={out.closed} "
               f"held.connection.closed={held.connection.closed}")
    try:
        md.ReleaseManagedSpell().release(out)
        row("P08", "release after teardown UNEXPECTEDLY worked")
    except Exception as error:
        row("P08", f"release after teardown: {type(error).__name__}: {error}")
    book.cleanup()


def p09_release_refusals() -> None:
    book = md.Spellbook()
    book.bind(spell=Connection, existence=md.Existence.managed_spell_quantity)
    book.bind(spell=Plain, existence=md.Existence.many)
    conduit = book.conjure()
    try:
        plain = conduit.meld("Plain")
        try:
            md.ReleaseManagedSpell().release(plain)
            row("P09", "release of a non-managed object UNEXPECTEDLY worked")
        except ValueError as error:
            row("P09", f"release of a non-managed object: ValueError: {error}")
        conn = conduit.meld("Connection")
        try:
            md.ReleaseManagedSpell().release(conn, spell_id=123)  # wrong type on purpose
            row("P09", "release with a non-str spell_id UNEXPECTEDLY worked")
        except TypeError as error:
            row("P09", f"release with a non-str spell_id: TypeError: {error}")
        try:
            md.ReleaseManagedSpell().release(conn, spell_id="0" * 64)
            row("P09", "release with an unmatched spell_id UNEXPECTEDLY worked")
        except ValueError as error:
            row("P09", f"release with an unmatched spell_id: ValueError: {error}")
        md.ReleaseManagedSpell().release(conn, conduit=conduit)
        row("P09", f"release with conduit= picks the pool its root holds: {counts(Connection)}")
        try:
            md.ReleaseManagedSpell().describe("Connection")
            row("P09", "describe of a str UNEXPECTEDLY worked")
        except TypeError as error:
            row("P09", f"describe of a non-class: TypeError: {error}")
    finally:
        conduit.cleanup()
    book.cleanup()


def p10_bind_refusals() -> None:
    def refuse(label: str, kwargs: Dict[str, Any], spell: Any = Ticket) -> None:
        fresh_world()
        book = md.Spellbook()
        try:
            book.bind(spell=spell, **kwargs)
            row("P10", f"{label}: UNEXPECTEDLY accepted")
        except Exception as error:
            row("P10", f"{label}: {type(error).__name__}: {error}")
        finally:
            book.cleanup()

    def factory() -> Ticket:
        return Ticket()

    refuse("option on another existence", {"existence": "many", "managed_spell_limit": 3})
    refuse("a function bound managed", {"existence": "managed_spell_quantity"}, spell=factory)
    refuse("limited_quantity without a limit",
           {"existence": "managed_spell_quantity", "managed_spell_mode": "limited_quantity"})
    refuse("queue without a timeout",
           {"existence": "managed_spell_quantity", "managed_spell_mode": "queue", "managed_spell_limit": 1})
    refuse("timeout on elastic",
           {"existence": "managed_spell_quantity", "managed_spell_timeout_seconds": 1.0})
    refuse("limit 0", {"existence": "managed_spell_quantity", "managed_spell_limit": 0})
    refuse("unknown mode", {"existence": "managed_spell_quantity", "managed_spell_mode": "lifo"})
    refuse("reset name that is not a method",
           {"existence": "managed_spell_quantity", "managed_spell_reset_methods": ["rinse"]})
    refuse("reset names as a bare string",
           {"existence": "managed_spell_quantity", "managed_spell_reset_methods": "close"})


def p11_spellbinder() -> None:
    book = md.Spellbook()
    binder = md.SpellBinder(book)
    spell_id = (
        binder.bind(Configured)
        .as_managed_spell_quantity("limited_quantity", limit=3, reset_methods=["reset"])
        .finalize()
    )
    conduit = book.conjure()
    try:
        obj: Configured = conduit.meld(spell_id=spell_id)
        obj.dirty = True
        md.ReleaseManagedSpell().release(obj)
        s = snapshot(Configured)
        row("P11", f"SpellBinder.as_managed_spell_quantity: mode={s['mode']} limit={s['limit']} "
                   f"reset={s['reset_method_names']} dirty_after_release={obj.dirty} {counts(Configured)}")
    finally:
        conduit.cleanup()
    book.cleanup()


def p12_settings_rebind_dynamic() -> None:
    configuration = md.SpellbookConfiguration()
    configuration.with_defaults()
    book = md.Spellbook(configuration=configuration)
    first_id = book.bind(spell=Settings, existence="managed_spell_quantity", disposal_method_names=["close"],
                         managed_spell_mode="limited_quantity", managed_spell_limit=1)
    root = book.conjure(dynamic=True, name="settings-root")
    try:
        out = root.meld("Settings")
        try:
            root.meld("Settings")
            row("P12", "limit 1 UNEXPECTEDLY leased twice")
        except md.ManagedSpellExhaustedError:
            row("P12", f"limit 1 refuses a second lease: {counts(Settings)}")
        root.cleanup_spell(spell=root.get_spell_by_spell_id(first_id))
        second_id = root.bind(spell=Settings, existence="managed_spell_quantity", disposal_method_names=["close"],
                              managed_spell_mode="limited_quantity", managed_spell_limit=3)
        s = snapshot(Settings)
        row("P12", f"cleanup_spell + bind with limit 3: same_spell_id={second_id == first_id} limit={s['limit']} "
                   f"{counts(Settings)} out_still_open={not out.closed}")
        more = [root.meld("Settings"), root.meld("Settings")]
        row("P12", f"two more leases under the new limit: {counts(Settings)}")
        md.ReleaseManagedSpell().release_all([out, *more])
        row("P12", f"all three back: {counts(Settings)}")
    finally:
        root.cleanup()
    book.cleanup()


def p13_transfer_moves_the_pool() -> None:
    configuration = md.SpellbookConfiguration()
    configuration.with_defaults()
    source_book = md.Spellbook(configuration=configuration)
    spell_id = source_book.bind(spell=Movable, existence="managed_spell_quantity")
    source = source_book.conjure(dynamic=True, name="old-home")
    target_configuration = md.SpellbookConfiguration()
    target_configuration.with_defaults()
    target_book = md.Spellbook(configuration=target_configuration)
    target = target_book.conjure(dynamic=True, name="new-home")
    try:
        source.link(target)
        obj = source.meld("Movable")
        md.ReleaseManagedSpell().release(obj)
        before = snapshot(Movable)
        row("P13", f"before: holding_root_is_source={before['holding_conduit_id'] == source.id} {counts(Movable)}")
        source.transfer_spell_ownership(spell=spell_id, target_conduit=target)
        after = snapshot(Movable)
        row("P13", f"after transfer: holding_root_is_target={after['holding_conduit_id'] == target.id} "
                   f"{counts(Movable)}")
        moved = target.meld("Movable")
        row("P13", f"the new owner leases the idle object the pool carried: same={moved is obj}")
        md.ReleaseManagedSpell().release(moved)
        row("P13", f"release still routes by class: {counts(Movable)}")
    finally:
        target.cleanup()
        source.cleanup()
    target_book.cleanup()
    source_book.cleanup()


def p14_spellspace() -> None:
    book = md.Spellbook()
    book.bind(spell=Connection, existence=md.Existence.managed_spell_quantity)
    conduit = book.conjure()
    try:
        with conduit.enter_spellspace() as space:
            try:
                obj = space.meld("Connection")
                row("P14", f"SpellSpace.meld of a managed spell leases from the root pool: {counts(Connection)} "
                           f"type={type(obj).__name__}")
                md.ReleaseManagedSpell().release(obj)
            except Exception as error:
                row("P14", f"SpellSpace.meld of a managed spell: {type(error).__name__}: {error}")
            try:
                removed = space.purge("Connection")
                row("P14", f"SpellSpace.purge of a managed spell: {removed}")
            except Exception as error:
                row("P14", f"SpellSpace.purge of a managed spell: {type(error).__name__}: {error}")
        row("P14", f"after the space: {counts(Connection)}")
    finally:
        conduit.cleanup()
    book.cleanup()


def p15_scope_ordering() -> None:
    book = md.Spellbook()
    book.bind(spell=PerScope, existence=md.Existence.unique_per_conduit)
    book.bind(spell=NeedsPerScope, existence=md.Existence.managed_spell_quantity)
    try:
        conduit = book.conjure()
        row("P15", "a managed spell depending on unique_per_conduit UNEXPECTEDLY conjured")
        conduit.cleanup()
    except Exception as error:
        text = str(error).replace("\n", " | ")
        row("P15", f"managed -> unique_per_conduit at conjure: {type(error).__name__}: {text[:420]}")
    book.cleanup()


def p16_override_object() -> None:
    book = md.Spellbook()
    book.bind(spell=WithArg, existence=md.Existence.managed_spell_quantity)
    conduit = book.conjure()
    try:
        pooled = conduit.meld("WithArg")
        md.ReleaseManagedSpell().release(pooled)
        fresh = conduit.meld("WithArg", override={"size": 9})
        row("P16", f"override builds a fresh object: fresh_is_pooled={fresh is pooled} size={fresh.size} "
                   f"{counts(WithArg)}")
        md.ReleaseManagedSpell().release(fresh)
        row("P16", f"releasing the override object pools it uncounted: {counts(WithArg)}")
    finally:
        conduit.cleanup()
    book.cleanup()


def p17_teardown_order_with_consumer_release() -> None:
    book = md.Spellbook()
    book.bind(spell=Connection, existence=md.Existence.managed_spell_quantity, disposal_method_names=["close"])
    book.bind(spell=RequestHandler, existence=md.Existence.many, disposal_method_names=["finish"])
    root = book.conjure()
    handler: RequestHandler = root.meld("RequestHandler")
    row("P17", f"a handler melded on the ROOT holds a lease: {counts(Connection)}")
    try:
        root.cleanup()
        row("P17", "root teardown with a root-held handler raised nothing")
    except BaseException as error:
        inner = getattr(error, "exceptions", [error])
        row("P17", f"root teardown with a root-held handler: {type(error).__name__}: {error} | inner="
                   f"{[type(e).__name__ + ': ' + str(e)[:160] for e in inner]}")
    row("P17", f"handler.done={handler.done} connection.closed={handler.connection.closed}")
    book.cleanup()


def p18_registry_singleton() -> None:
    first = md.ReleaseManagedSpell()
    second = md.ReleaseManagedSpell()
    row("P18", f"ReleaseManagedSpell() is one process singleton: {first is second}")
    release = md.ReleaseManagedSpell().release
    book = md.Spellbook()
    book.bind(spell=Connection, existence=md.Existence.managed_spell_quantity)
    conduit = book.conjure()
    try:
        obj = conduit.meld("Connection")
        release(obj)
        row("P18", f"a bound release works for a hot loop: {counts(Connection)}")
    finally:
        conduit.cleanup()
    book.cleanup()


def p19_release_paths_after_teardown() -> None:
    book = md.Spellbook()
    book.bind(spell=Connection, existence=md.Existence.managed_spell_quantity, disposal_method_names=["close"])
    root = book.conjure()
    by_lease = root.managed_spell_meld("Connection")
    by_registry = root.meld("Connection")
    root.cleanup()
    try:
        by_lease.release()
        row("P19", "lease.release() after teardown UNEXPECTEDLY worked")
    except RuntimeError as error:
        row("P19", f"lease.release() after teardown (the lease holds the pool): RuntimeError: {error} "
                   f"released={by_lease.released}")
    try:
        md.ReleaseManagedSpell().managed(by_registry)
        row("P19", "managed(obj) after teardown UNEXPECTEDLY worked")
    except ValueError as error:
        row("P19", f"managed(obj) after teardown (resolved through the registry): ValueError: {error}")
    row("P19", f"objects that were out stay open: {not by_registry.closed}")
    book.cleanup()


def main() -> None:
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()} melder {md.__version__}")
    cases = [
        ("P01", p01_elastic_basics),
        ("P02", p02_elastic_small_limit_trims),
        ("P03", p03_limited_quantity),
        ("P04", p04_queue_handoff_and_timeout),
        ("P05", p05_resets),
        ("P06", p06_leases),
        ("P07", p07_injection_request_scopes),
        ("P08", p08_teardown_with_objects_out),
        ("P09", p09_release_refusals),
        ("P10", p10_bind_refusals),
        ("P11", p11_spellbinder),
        ("P12", p12_settings_rebind_dynamic),
        ("P13", p13_transfer_moves_the_pool),
        ("P14", p14_spellspace),
        ("P15", p15_scope_ordering),
        ("P16", p16_override_object),
        ("P17", p17_teardown_order_with_consumer_release),
        ("P18", p18_registry_singleton),
        ("P19", p19_release_paths_after_teardown),
    ]
    for case, body in cases:
        run(case, body)
    failed = [text for _case, text in RESULTS if text.startswith("FAILED")]
    print(f"rows={len(RESULTS)} failed={len(failed)}")


if __name__ == "__main__":
    main()
