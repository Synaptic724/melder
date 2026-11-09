"""Scratch check: does binding_name alone trigger the missed wake-up, and how does a SpellMap consumer behave?"""
import sys

import melder as md
from melder.aether.conduit.meld.contracts.spell_map import SpellMap


class English:
    """The provider."""

    def greet(self) -> str:
        """Return the greeting."""
        return "hello"


class ByClass:
    """Asks for English by class annotation."""

    def __init__(self, greeter: English) -> None:
        self.greeter = greeter


class ByMap:
    """Asks for whatever is filed at ('langs', 'v1') through a SpellMap default."""

    def __init__(self, greeter: English = SpellMap(spellframe="langs", binding_name="v1")) -> None:
        self.greeter = greeter


def show(label, call):
    """Print what call returns, or the exception type and first line it raises."""
    try:
        print("  %-62s -> %s" % (label, call()))
    except Exception as error:
        print("  %-62s -> raises %s: %s" % (label, type(error).__name__, (str(error).splitlines() or [""])[0][:90]))


case = sys.argv[1]
print("%s (GIL %s)" % (case, "on" if sys._is_gil_enabled() else "off"))
book = md.Spellbook()
if case == "binding_name_only":
    book.bind(spell=ByClass, existence="many", permissions="create")
    world = book.conjure(dynamic=True, name="world")
    show("meld(ByClass), nothing bound yet", lambda: type(world.meld(ByClass).greeter).__name__)
    world.bind(spell=English, existence="many", permissions="create", binding_name="v1")
    show("meld(ByClass) after bind(English, binding_name='v1'), no frame",
         lambda: type(world.meld(ByClass).greeter).__name__)
elif case == "spellmap_waiting":
    book.bind(spell=ByMap, existence="many", permissions="create")
    box = {}
    show("conjure with ByMap and nothing at ('langs','v1')",
         lambda: (box.setdefault("world", book.conjure(dynamic=True, name="world")), "ok")[1])
elif case == "spellmap_late_bind":
    book.bind(spell=English, existence="many", permissions="create", spellframe="langs", binding_name="v1")
    world = book.conjure(dynamic=True, name="world")
    show("bind(ByMap) after conjure, English already at ('langs','v1')",
         lambda: (world.bind(spell=ByMap, existence="many", permissions="create"), "ok")[1])
    show("meld(ByMap)", lambda: type(world.meld(ByMap).greeter).__name__)
