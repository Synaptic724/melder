"""Scratch probe (read-only design work, TASK-2026-11-07-spellframe_ambiguity_validation_check part (a)).

Measures what Melder does TODAY when a class lookup misses a class that is registered only under a
spellframe or a binding name: single class socket, single string socket, list[Class], SpellMap(Class),
SpellMap(Class, binding_name=...); automatic world, dynamic world (consumer bound before conjure) and a
dynamic world with the consumer late-bound after conjure. Controls: nothing registered, bound bare, bound
bare AND under a frame (a same-named version). Plus the AMBIGUOUS_PROVIDER control for the late-bind path
and two order-dependent dynamic cases (provider late-bound after a conjured consumer).

Run: python -X gil=0 hidden_class_probe.py  (and -X gil=1). Writes nothing outside the process.
"""
import sys
import traceback
from typing import Protocol

from melder import Aether, Conduit, Spellbook, SpellMap
from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind


class Greeter(Protocol):
    """The interface."""

    def greet(self) -> str: ...


class English:
    """The implementation a consumer names by class."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """A second implementation (AMBIGUOUS control)."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


def version_of(cls: type, **values: object) -> type:
    """Same name/qualname/module, new code (tests/_spell_identity_test_support.version_of)."""
    namespace = {"__module__": cls.__module__, "__qualname__": cls.__qualname__}
    namespace.update(values)
    return type(cls.__name__, (cls,), namespace)


class SingleClass:
    """greeter: English."""

    def __init__(self, greeter: English) -> None:
        self.greeter = greeter


class SingleString:
    """greeter: "English" (a string that resolves in this module)."""

    def __init__(self, greeter: "English") -> None:
        self.greeter = greeter


class ListClass:
    """greeters: list[English] (required)."""

    def __init__(self, greeters: list[English]) -> None:
        self.greeters = greeters


class SpellMapClass:
    """greeter = SpellMap(English)."""

    def __init__(self, greeter=SpellMap(English)) -> None:
        self.greeter = greeter


class SpellMapNamed:
    """greeter = SpellMap(English, binding_name="english")."""

    def __init__(self, greeter=SpellMap(English, binding_name="english")) -> None:
        self.greeter = greeter


class ByProtocol:
    """greeter: Greeter (AMBIGUOUS control)."""

    def __init__(self, greeter: Greeter) -> None:
        self.greeter = greeter


CONSUMERS = {
    "single_class": (SingleClass, "greeter", lambda: English()),
    "single_string": (SingleString, "greeter", lambda: English()),
    "list_class": (ListClass, "greeters", lambda: [English()]),
    "spellmap_class": (SpellMapClass, "greeter", lambda: English()),
    "spellmap_named": (SpellMapNamed, "greeter", lambda: English()),
}

ENGLISH_V2 = version_of(English, version=2)

PLACEMENTS = {
    "protocol": [dict(spell=English, spellframe=Greeter)],
    "protocol_named": [dict(spell=English, spellframe=Greeter, binding_name="english")],
    "category": [dict(spell=English, spellframe="greeters")],
    "category_named": [dict(spell=English, spellframe="greeters", binding_name="english")],
    "bare_named": [dict(spell=English, binding_name="english")],
    "two_frames": [dict(spell=English, spellframe=Greeter, binding_name="english"),
                   dict(spell=ENGLISH_V2, spellframe="greeters", binding_name="english")],
    "CONTROL_bare": [dict(spell=English)],
    "CONTROL_bare_and_framed": [dict(spell=English), dict(spell=ENGLISH_V2, spellframe=Greeter)],
    "CONTROL_none": [],
}


def fresh_world() -> None:
    """Cold Aether, exactly as the integration fixtures reset it."""
    Aether._reset_singleton_for_tests()
    world = Aether()
    Spellbook._aether = world
    Conduit._aether = world


def make_book(mode: str, frame: str) -> Spellbook:
    """One Book, caching off, automatic or dynamic posture."""
    book = Spellbook(aetheric_frame=frame)
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book.configure_aether_frame(system_state=mode, system_caching_enabled=False,
                                disposal=None, disposal_method_names=None)
    return book


def outcome(call):
    """Run call; return ('ok', value) or ('raises', exception)."""
    try:
        return "ok", call()
    except Exception as error:  # noqa: BLE001 - a probe records every failure
        return "raises", error


def render(step: str, result) -> None:
    """Print one step: ok + value, or the exception type and its full text (and PhaseExecutionError inners)."""
    status, value = result
    if status == "ok":
        print(f"    {step}: ok -> {value}")
        return
    error = value
    print(f"    {step}: RAISES {type(error).__name__}")
    for line in str(error).splitlines():
        print(f"        | {line}")
    inner = getattr(error, "errors", None)
    if inner:
        for item in inner[:3]:
            print(f"        inner {type(item).__name__}: {item}")


def socket_kinds(book: Spellbook, consumer_cls: type) -> str:
    """Describe the consumer's Phase-3 sockets: kind, targets, references, dependency key."""
    try:
        for spell in book._spell_id_pool.values():
            if spell.spell is consumer_cls:
                topology = spell._spell_system_states.get_local_topology(spell.spell_index)
                if topology is None:
                    return "no topology"
                return "; ".join(
                    f"{s.param_name}:{s.socket_kind.name} targets={len(s.target_spell_ids)} "
                    f"refs={len(s.referenced_spell_ids)} key={s.dependency_key}"
                    for s in topology.sockets
                )
        return "consumer not in pool"
    except Exception as error:  # noqa: BLE001
        return f"unreadable: {type(error).__name__}: {error}"


def phase4_codes(book: Spellbook, consumer_cls: type) -> str:
    """Return the consumer's Phase-4 issue codes with severities, when the result is still held."""
    for spell in book._spell_id_pool.values():
        if spell.spell is consumer_cls:
            result = spell.validation_result_phase4
            if result is None:
                return "phase4 result released"
            return ", ".join(f"{i.severity}:{i.code}" for i in result.issues) or "no issues"
    return "consumer not in pool"


def run_case(placement: str, consumer: str, mode: str, late: bool, counter: list) -> None:
    """One world: bind the provider placement, the consumer (before or after conjure), conjure, meld."""
    consumer_cls, param, supply = CONSUMERS[consumer]
    counter[0] += 1
    fresh_world()
    book = make_book(mode, f"probe-{counter[0]}")
    world = None
    print(f"[{placement} | {consumer} | {mode}{' late-bound consumer' if late else ''}]")
    try:
        for spec in PLACEMENTS[placement]:
            book.bind(existence="many", permissions="create", **spec)
        if not late:
            book.bind(spell=consumer_cls, existence="many", permissions="create")
        result = outcome(lambda: book.conjure(name="root", dynamic=(mode == "dynamic")))
        render("conjure", result)
        if result[0] != "ok":
            return
        world = result[1]
        if late:
            render("late bind consumer", outcome(lambda: world.bind(spell=consumer_cls, existence="many",
                                                                   permissions="create")))
        print(f"    sockets: {socket_kinds(book, consumer_cls)}")
        render("meld(consumer)", outcome(lambda: type(world.meld(consumer_cls)).__name__))
        render(f"meld(consumer, override={{{param!r}: ...}})",
               outcome(lambda: type(world.meld(consumer_cls, override={param: supply()})).__name__))
    finally:
        try:
            if world is not None:
                world.cleanup()
        except Exception:
            pass
        try:
            book.cleanup()
        except Exception:
            pass


def run_ambiguous_control(counter: list) -> None:
    """AMBIGUOUS_PROVIDER: how a late-bound consumer is refused - at bind, at meld, or both."""
    counter[0] += 1
    fresh_world()
    book = make_book("dynamic", f"probe-{counter[0]}")
    world = None
    print("[AMBIGUOUS control | ByProtocol (greeter: Greeter) | dynamic late-bound consumer]")
    try:
        book.bind(spell=English, existence="many", permissions="create", spellframe=Greeter, binding_name="english")
        book.bind(spell=French, existence="many", permissions="create", spellframe=Greeter, binding_name="french")
        world = book.conjure(name="root", dynamic=True)
        render("late bind consumer", outcome(lambda: world.bind(spell=ByProtocol, existence="many",
                                                               permissions="create")))
        print(f"    consumer still registered after a refused bind: "
              f"{any(s.spell is ByProtocol for s in book._spell_id_pool.values())}")
        print(f"    sockets: {socket_kinds(book, ByProtocol)}")
        render("meld(consumer)", outcome(lambda: type(world.meld(ByProtocol)).__name__))
        render("meld(consumer, override={'greeter': ...})",
               outcome(lambda: type(world.meld(ByProtocol, override={"greeter": English()})).__name__))
    finally:
        try:
            if world is not None:
                world.cleanup()
        except Exception:
            pass
        book.cleanup()


def run_order_case(label: str, late_spec: dict, counter: list) -> None:
    """Dynamic: SingleClass conjured with nothing registered (UNRESOLVED_INPUT), then English bound late."""
    counter[0] += 1
    fresh_world()
    book = make_book("dynamic", f"probe-{counter[0]}")
    world = None
    print(f"[ORDER {label} | single_class | dynamic: consumer conjured unresolved, English bound late]")
    try:
        book.bind(spell=SingleClass, existence="many", permissions="create")
        world = book.conjure(name="root", dynamic=True)
        print(f"    sockets before: {socket_kinds(book, SingleClass)}")
        render("late bind English", outcome(lambda: world.bind(existence="many", permissions="create", **late_spec)))
        render("meld(consumer)", outcome(lambda: type(world.meld(SingleClass)).__name__))
        print(f"    sockets after meld: {socket_kinds(book, SingleClass)}")
    finally:
        try:
            if world is not None:
                world.cleanup()
        except Exception:
            pass
        book.cleanup()


def run_class_door(counter: list) -> None:
    """The class meld door for a framed English (for comparison with the injection message)."""
    counter[0] += 1
    fresh_world()
    book = make_book("automatic", f"probe-{counter[0]}")
    world = None
    print("[DOOR | meld(English) with English under Greeter | automatic]")
    try:
        book.bind(spell=English, existence="many", permissions="create", spellframe=Greeter, binding_name="english")
        world = book.conjure(name="root")
        render("meld(English)", outcome(lambda: type(world.meld(English)).__name__))
    finally:
        try:
            if world is not None:
                world.cleanup()
        except Exception:
            pass
        book.cleanup()


def main() -> None:
    """Run the matrix."""
    from melder.__version__ import __version__ as melder_version
    print(f"hidden_class_probe on melder {melder_version}, python {sys.version.split()[0]}, "
          f"gil_enabled={sys._is_gil_enabled()}")
    counter = [0]
    selected = sys.argv[1:] or None
    for placement in PLACEMENTS:
        for consumer in CONSUMERS:
            if consumer == "spellmap_named" and placement not in ("bare_named", "protocol_named", "category_named"):
                continue
            for mode, late in (("automatic", False), ("dynamic", False), ("dynamic", True)):
                key = f"{placement}:{consumer}:{mode}:{late}"
                if selected and not any(s in key for s in selected):
                    continue
                try:
                    run_case(placement, consumer, mode, late, counter)
                except Exception:
                    print("    PROBE ERROR")
                    traceback.print_exc(file=sys.stdout)
    if not selected:
        run_ambiguous_control(counter)
        run_order_case("framed", dict(spell=English, spellframe=Greeter, binding_name="english"), counter)
        run_order_case("bare", dict(spell=English), counter)
        run_class_door(counter)


if __name__ == "__main__":
    main()
