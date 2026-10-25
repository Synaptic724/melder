"""Diagnostic (melder_1, 2026-10-25; STORY-2026-10-17-notch_moves_signature_by_incoming_key_only, a side finding): a
consumer injected by a class annotation that lost its provider stays refused when the provider comes back under a
spellframe. Public calls for the behaviour; the socket and validity lines read internals, for the diagnosis only.
One case per process:

    python diag_class_annotated_consumer_after_notch_back.py framed             # English, French at (Greeter, 'greeter')
    python diag_class_annotated_consumer_after_notch_back.py bare               # both bound bare (today's staging)
    python diag_class_annotated_consumer_after_notch_back.py framed_bind_later  # English bound under Greeter after conjure
    python diag_class_annotated_consumer_after_notch_back.py bare_bind_later    # English bound bare after conjure

The notch cases meld ByClass (greeter: English) before a notch to French, after it and after the notch back; the bind
cases meld it with no English bound, then bind English after conjure and meld it again. Each case ends by
disposing ByClass and binding it again (cleanup_spell, then bind), the remedy for a stuck consumer.
"""
import sys
from typing import Protocol

import melder as md


class Greeter(Protocol):
    """The contract the framed versions record."""

    def greet(self) -> str: ...


class English:
    """Version 1, the class ByClass names."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Version 2, another class."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class ByClass:
    """Injected by a class annotation naming English."""

    def __init__(self, greeter: English) -> None:
        self.greeter = greeter


def show(label, call):
    """Print what `call` returns, or the type and first line of what it raises."""
    try:
        print("  %-44s -> %s" % (label, call()))
    except Exception as error:
        print("  %-44s -> raises %s: %s" % (label, type(error).__name__, (str(error).splitlines() or [""])[0][:110]))


def state_of(book, spell_id):
    """ByClass's lineage validity and the kind and dependency key of each recorded socket (internal reads)."""
    states = book._spell_system_states
    spell = book.find_spell_by_spell_id(spell_id)
    state = states.get_by_index_id(spell.spell_index.id)
    topology = states.get_local_topology_by_id(spell_id)
    sockets = [] if topology is None else [(s.socket_kind.name, s.dependency_key) for s in topology.iter_sockets()]
    return "    validity %s; sockets %s" % (state.validity.name if state is not None else None, sockets)


def meld_consumer(world, consumer_id):
    """Meld ByClass and name the class of the greeter it holds."""
    return type(world.meld(spell_id=consumer_id).greeter).__name__


def rebind_consumer(world, consumer_id):
    """Dispose ByClass and bind it again, then meld it: the remedy for a consumer stuck on an unresolved input."""
    world.cleanup_spell(spell=world.get_spell_by_spell_id(consumer_id))
    rebound_id = world.bind(spell=ByClass, existence="many", permissions="create")
    show("rebind ByClass (same spell_id: %s), then meld" % (rebound_id == consumer_id),
         lambda: meld_consumer(world, rebound_id))


def notch_case(framed):
    """English -> French -> English on one index; ByClass melded at each step."""
    frame = {"spellframe": Greeter, "binding_name": "greeter"} if framed else {}
    book = md.Spellbook()
    english_id = book.bind(spell=English, existence="many", permissions="create", **frame)
    consumer_id = book.bind(spell=ByClass, existence="many", permissions="create")
    world = book.conjure(dynamic=True, name="world")
    index = world.get_spell_by_spell_id(english_id).spell_index
    french_id = world.bind_inactive(spell=French, spell_index=index, existence="many", permissions="create", **frame)
    print("  English %s/%s, French %s/%s" % (world.get_spell_by_spell_id(english_id)._key
                                            + book.find_spell_by_spell_id(french_id)._key))
    show("meld ByClass (English active)", lambda: meld_consumer(world, consumer_id))
    print(state_of(book, consumer_id))
    show("notch to French", lambda: world.notch_spell(spell_index=index, spell_id=french_id).spell_name)
    show("meld ByClass (French active)", lambda: meld_consumer(world, consumer_id))
    print(state_of(book, consumer_id))
    show("notch back to English", lambda: world.notch_spell(spell_index=index, spell_id=english_id).spell_name)
    print(state_of(book, consumer_id))
    show("meld ByClass (English active again)", lambda: meld_consumer(world, consumer_id))
    show("meld ByClass a second time", lambda: meld_consumer(world, consumer_id))
    rebind_consumer(world, consumer_id)
    world.cleanup()


def bind_later_case(framed):
    """ByClass conjured with no English; English bound after conjure; ByClass melded before and after."""
    frame = {"spellframe": Greeter, "binding_name": "greeter"} if framed else {}
    book = md.Spellbook()
    consumer_id = book.bind(spell=ByClass, existence="many", permissions="create")
    world = book.conjure(dynamic=True, name="world")
    show("meld ByClass (no English bound)", lambda: meld_consumer(world, consumer_id))
    print(state_of(book, consumer_id))
    english_id = world.bind(spell=English, existence="many", permissions="create", **frame)
    print("  English bound after conjure at %s/%s" % world.get_spell_by_spell_id(english_id)._key)
    print(state_of(book, consumer_id))
    show("meld ByClass (English bound)", lambda: meld_consumer(world, consumer_id))
    show("meld ByClass a second time", lambda: meld_consumer(world, consumer_id))
    rebind_consumer(world, consumer_id)
    world.cleanup()


case = sys.argv[1]
print("case %s" % case)
if case in ("framed", "bare"):
    notch_case(case == "framed")
elif case in ("framed_bind_later", "bare_bind_later"):
    bind_later_case(case == "framed_bind_later")
else:
    raise SystemExit("unknown case %s" % case)
