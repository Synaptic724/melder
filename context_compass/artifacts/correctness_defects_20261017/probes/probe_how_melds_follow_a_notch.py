"""Probe (melder_1, 2026-10-24; STORY-2026-10-17-notch_moves_signature_by_incoming_key_only): which ways of reaching
a spell follow a notch? Public calls only, one case per process:

    python probe_how_melds_follow_a_notch.py same   # English -> French, both at (Greeter, 'greeter')
    python probe_how_melds_follow_a_notch.py diff   # English at 'greeter' -> Spanish at 'spanish'

Before and after the notch it melds: by spell_id, by address (old and new), by SpellName, by spellframe alone, a
consumer injected by its Protocol annotation, a consumer whose SpellMap default names the old address, and, in a
linked borrower Book holding the index by contract, a meld by address and a consumer injected by annotation.
"""
import sys
from typing import Protocol

import melder as md
from melder.aether.conduit.meld.contracts.spell_map import SpellMap


class Greeter(Protocol):
    def greet(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


class Spanish:
    def greet(self) -> str:
        return "hola"


class ByProtocol:
    """Injected by its annotation: any active Greeter."""
    def __init__(self, greeter: Greeter) -> None:
        self.greeter = greeter


class ByMap:
    """Injected through a SpellMap default naming the address (Greeter, 'greeter')."""
    def __init__(self, greeter: Greeter = SpellMap(spellframe=Greeter, binding_name="greeter")) -> None:
        self.greeter = greeter


class Speaker:
    """A borrower's consumer, injected by its annotation."""
    def __init__(self, greeter: Greeter) -> None:
        self.greeter = greeter


def show(label, call):
    try:
        print("  %-50s -> %s" % (label, call()))
    except Exception as error:
        first = str(error).splitlines()[0] if str(error) else ""
        print("  %-50s -> raises %s: %s" % (label, type(error).__name__, first[:150]))


def says(obj):
    """Name what an object is or holds, and what it greets with."""
    target = obj.greeter if hasattr(obj, "greeter") else obj
    return "%s (%r)" % (type(target).__name__, target.greet())


case = sys.argv[1]
incoming_cls, incoming_name = (French, "greeter") if case == "same" else (Spanish, "spanish")
lender = md.Spellbook()
english_id = lender.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                         permissions="create")
by_protocol = lender.bind(spell=ByProtocol, existence="many", permissions="create")
by_map = lender.bind(spell=ByMap, existence="many", permissions="create")
world = lender.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english_id).spell_index
incoming_id = world.bind_inactive(spell=incoming_cls, spell_index=index, spellframe=Greeter,
                                  binding_name=incoming_name, existence="many", permissions="create")
other = md.Spellbook()
speaker = other.bind(spell=Speaker, existence="many", permissions="create")
borrower = other.conjure(dynamic=True, name="borrower")
world.link(borrower)
with borrower.transaction("link", conduits=[borrower, world]):
    borrower.add_index_to_contract(index=index, conduit=world, permissions="create")


def report(when):
    print("[%s]" % when)
    show("lender meld(spell_id=<English>)", lambda: says(world.meld(spell_id=english_id)))
    show("lender meld(spell_id=<%s>)" % incoming_cls.__name__, lambda: says(world.meld(spell_id=incoming_id)))
    show("lender meld at (Greeter, 'greeter')", lambda: says(world.meld(spellframe=Greeter, binding_name="greeter")))
    if case == "diff":
        show("lender meld at (Greeter, 'spanish')",
             lambda: says(world.meld(spellframe=Greeter, binding_name="spanish")))
    show("lender meld('English')  (SpellName)", lambda: says(world.meld("English")))
    show("lender meld('%s')  (SpellName)" % incoming_cls.__name__, lambda: says(world.meld(incoming_cls.__name__)))
    show("lender meld(spellframe=Greeter)", lambda: says(world.meld(spellframe=Greeter)))
    show("lender consumer injected by Protocol annotation", lambda: says(world.meld(spell_id=by_protocol)))
    show("lender consumer with SpellMap(Greeter, 'greeter')", lambda: says(world.meld(spell_id=by_map)))
    show("borrower meld at (Greeter, 'greeter')",
         lambda: says(borrower.meld(spellframe=Greeter, binding_name="greeter")))
    if case == "diff":
        show("borrower meld at (Greeter, 'spanish')",
             lambda: says(borrower.meld(spellframe=Greeter, binding_name="spanish")))
    show("borrower consumer injected by Protocol annotation", lambda: says(borrower.meld(spell_id=speaker)))


print("case %s: English at (Greeter, 'greeter') -> %s at (Greeter, %r)" % (case, incoming_cls.__name__, incoming_name))
report("before the notch")
show("notch to %s" % incoming_cls.__name__,
     lambda: world.notch_spell(spell_index=index, spell_id=incoming_id).spell_name)
report("after the notch")
borrower.cleanup()
world.cleanup()
