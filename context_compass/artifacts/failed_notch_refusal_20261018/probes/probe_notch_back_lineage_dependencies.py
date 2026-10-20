"""HYPOTHESIS probe (melder_1, 2026-10-19): does a plain notch back leave the notched-away version's dependencies
on the lineage, so a borrower's consumer is refused for a provider the restored version does not have?

English (no dependencies) is active on the greeter index; French needs Accent, which only the lender binds. A
borrower links to the index and binds Speaker(greeter: Greeter). The lender notches to French, melds it (French's
dependencies registered on the lineage), then notches back to English. Cases:
    H1  the borrower's Speaker melds first after the notch back (before any lender meld)
    H2  the lender melds English first, then the borrower's Speaker (control)
    H3  as H1, but the borrower never melds Speaker before the notches (its topology still the one from its
        conjure, before the link)
    H4  as H3, but the lender never melds French either: the notch's commit check compiles French's structure,
        then the notch back
Each case runs in its own process (one object is one spell):
    python probe_notch_back_lineage_dependencies.py H1
Run with src/ on sys.path, the GIL off and on. Reads internal state only to print it.
"""
import sys
from typing import Protocol

import melder as md


class Greeter(Protocol):
    def greet(self) -> str: ...


class Accent:
    def say(self, word: str) -> str:
        return word + "!"


class English:
    def greet(self) -> str:
        return "hello"


class French:
    def __init__(self, accent: Accent) -> None:
        self.accent = accent

    def greet(self) -> str:
        return self.accent.say("bonjour")


class Speaker:
    def __init__(self, greeter: Greeter) -> None:
        self.greeter = greeter


def show(label: str, call) -> None:
    """Print what `call` returns, or the first line of what it raises."""
    try:
        print("  %s -> %r" % (label, call()))
    except Exception as error:
        lines = str(error).splitlines()
        detail = " | ".join(line.strip() for line in lines[:3])
        print("  %s -> raises %s: %s" % (label, type(error).__name__, detail[:300]))


def lineage(book: md.Spellbook, index) -> str:
    """Name the lineage's registered direct dependencies (internal read, for the probe only)."""
    state = book._spell_system_states.get_by_index_id(index.id)
    names = []
    for dep_id in state.direct_dependencies:
        spell = book.find_spell_by_spell_id(dep_id)
        names.append(spell.spell_name if spell is not None else dep_id[:12])
    topology = book._spell_system_states.get_local_topology(index)
    sockets = []
    if topology is not None:
        for socket in topology.sockets:
            targets = [book.find_spell_by_spell_id(t) for t in socket.target_spell_ids]
            sockets.append("%s->%s" % (socket.param_name, [s.spell_name if s is not None else "?" for s in targets]))
    return "deps %s, index topology %s, validity %s" % (sorted(names), sockets, state.validity.name)


case = sys.argv[1]
lender = md.Spellbook()
english = lender.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                      permissions="create")
lender.bind(spell=Accent, existence="many", permissions="create")
world = lender.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
french = world.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                             existence="many", permissions="create")
other = md.Spellbook()
speaker = other.bind(spell=Speaker, existence="many", permissions="create")
borrower = other.conjure(dynamic=True, name="borrower")
world.link(borrower)
with borrower.transaction("link", conduits=[borrower, world]):
    borrower.add_index_to_contract(index=index, conduit=world, permissions="create")

print("case %s" % case)
show("lender meld English", lambda: world.meld(spell_id=english).greet())
if case not in ("H3", "H4"):
    show("borrower meld Speaker", lambda: borrower.meld(spell_id=speaker).greeter.greet())
print("  lineage:", lineage(lender, index))
show("notch to French", lambda: world.notch_spell(spell_index=index, spell_id=french).spell_name)
if case != "H4":
    show("lender meld French", lambda: world.meld(spell_id=french).greet())
print("  lineage:", lineage(lender, index))
show("notch back to English", lambda: world.notch_spell(spell_index=index, spell_id=english).spell_name)
print("  lineage after the notch back:", lineage(lender, index))
if case in ("H1", "H3", "H4"):
    show("borrower meld Speaker (first)", lambda: borrower.meld(spell_id=speaker).greeter.greet())
    show("lender meld English", lambda: world.meld(spell_id=english).greet())
    print("  lineage:", lineage(lender, index))
    show("borrower meld Speaker (again)", lambda: borrower.meld(spell_id=speaker).greeter.greet())
    show("borrower meld Speaker (third)", lambda: borrower.meld(spell_id=speaker).greeter.greet())
else:
    show("lender meld English (first)", lambda: world.meld(spell_id=english).greet())
    print("  lineage:", lineage(lender, index))
    show("borrower meld Speaker", lambda: borrower.meld(spell_id=speaker).greeter.greet())
borrower.cleanup()
world.cleanup()
