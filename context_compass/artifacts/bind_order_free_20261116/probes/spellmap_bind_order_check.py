"""Probe: a SpellMap consumer bound before its provider, against a class-annotated one. One case per process.

Usage: python -X gil=0 spellmap_bind_order_check.py <case>
Cases: late_spellmap, late_annotation, conjure_reverse_order, conjure_address_empty, frameless.
Public calls decide each behaviour line; lines marked "internal:" read private state for the diagnosis only.
"""
import sys

import melder as md
from melder.aether.conduit.meld.contracts.spell_map import SpellMap


class Anchor:
    """An unrelated spell, so a book has something to conjure."""


class ServiceBuilder:
    """The provider; filed at ('spectrum', 'ServiceBuilder') in the frame-addressed cases."""


class SpectrumBuilders:
    """Asks for the provider by frame address - the MelderOps shape."""

    def __init__(self, service_builder=SpellMap(spellframe="spectrum", binding_name="ServiceBuilder")) -> None:
        self.service_builder = service_builder


class ByAnnotation:
    """Asks for the provider by class annotation, for contrast."""

    def __init__(self, service_builder: ServiceBuilder) -> None:
        self.service_builder = service_builder


def show(label, call):
    """Print what call returns, or the exception type and the first line of its message."""
    try:
        print("  %-70s -> %s" % (label, call()))
    except Exception as error:
        first = (str(error).splitlines() or [""])[0]
        print("  %-70s -> raises %s: %s" % (label, type(error).__name__, first[:150]))


def bind(book, spell, **address):
    """Bind one spell the way MelderOps does after conjure (Spellbook.bind), many/create."""
    book.bind(spell=spell, existence="many", permissions="create", **address)
    return "ok"


def dependency(world, consumer):
    """Meld the consumer and name the type of what it received as service_builder."""
    return type(world.meld(consumer).service_builder).__name__


def registered(book, cls):
    """internal: whether a spell of cls sits in the book's maps, and whether Phase 4 ever ran for it."""
    found = [spell for spell in book._spells.values() if spell.spell is cls]
    if not found:
        return "not registered"
    return "registered, phase-4 result %s" % ("present" if found[0].validation_result_phase4 else "absent")


case = sys.argv[1]
print("%s (GIL %s)" % (case, "on" if sys._is_gil_enabled() else "off"))
book = md.Spellbook()
if case == "late_spellmap":
    bind(book, Anchor)
    world = book.conjure(dynamic=True, name="world")
    show("bind(SpectrumBuilders) after conjure, nothing at spectrum/ServiceBuilder",
         lambda: bind(book, SpectrumBuilders))
    show("internal: SpectrumBuilders after that bind", lambda: registered(book, SpectrumBuilders))
    show("meld(SpectrumBuilders)", lambda: dependency(world, SpectrumBuilders))
    show("bind(ServiceBuilder, spellframe='spectrum', binding_name='ServiceBuilder')",
         lambda: bind(book, ServiceBuilder, spellframe="spectrum", binding_name="ServiceBuilder"))
    show("meld(SpectrumBuilders) after the provider is bound", lambda: dependency(world, SpectrumBuilders))
    show("bind(SpectrumBuilders) again", lambda: bind(book, SpectrumBuilders))
elif case == "late_spellmap_control":
    bind(book, Anchor)
    world = book.conjure(dynamic=True, name="world")
    show("bind(ServiceBuilder, spellframe='spectrum', binding_name='ServiceBuilder') first",
         lambda: bind(book, ServiceBuilder, spellframe="spectrum", binding_name="ServiceBuilder"))
    show("bind(SpectrumBuilders) after its provider", lambda: bind(book, SpectrumBuilders))
    show("meld(SpectrumBuilders)", lambda: dependency(world, SpectrumBuilders))
elif case == "late_annotation":
    bind(book, Anchor)
    world = book.conjure(dynamic=True, name="world")
    show("bind(ByAnnotation) after conjure, no ServiceBuilder bound", lambda: bind(book, ByAnnotation))
    show("internal: ByAnnotation after that bind", lambda: registered(book, ByAnnotation))
    show("meld(ByAnnotation)", lambda: dependency(world, ByAnnotation))
    show("bind(ServiceBuilder) bare", lambda: bind(book, ServiceBuilder))
    show("meld(ByAnnotation) after the provider is bound", lambda: dependency(world, ByAnnotation))
elif case == "conjure_reverse_order":
    bind(book, SpectrumBuilders)
    bind(book, ServiceBuilder, spellframe="spectrum", binding_name="ServiceBuilder")
    box = {}
    show("conjure with SpectrumBuilders bound before ServiceBuilder",
         lambda: (box.setdefault("world", book.conjure(dynamic=True, name="world")), "ok")[1])
    show("meld(SpectrumBuilders)", lambda: dependency(box["world"], SpectrumBuilders))
elif case == "conjure_address_empty":
    bind(book, SpectrumBuilders)
    show("conjure with nothing at spectrum/ServiceBuilder",
         lambda: (book.conjure(dynamic=True, name="world"), "ok")[1])
elif case == "frameless":
    show("SpellMap(binding_name='ServiceBuilder')", lambda: repr(SpellMap(binding_name="ServiceBuilder")))
    show("SpellMap(spellframe='spectrum')", lambda: repr(SpellMap(spellframe="spectrum").canonical_key))
else:
    raise SystemExit("unknown case " + case)
