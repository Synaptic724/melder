"""S8, two broken versions side by side (melder_1, 2026-10-19): what Melder says at the notch and at every meld.

Case "recursion": SelfMade's constructor takes its own class - a loop; Melder's code for it is SELF_DEPENDENCY.
Case "ambiguous": TimedGreeter needs a Clock and two are registered - no loop; Melder says AMBIGUOUS_PROVIDER.
Both are staged at English's address on English's index, then notched to. Each case runs in its own process,
because one object is one spell and English cannot be bound twice in one process:
    python probe_failed_notch_two_reasons.py recursion
    python probe_failed_notch_two_reasons.py ambiguous
Run with src/ on sys.path, the GIL off and on.
"""
import sys
from typing import Callable, Protocol

import melder as md


class Greeter(Protocol):
    def greet(self) -> str: ...


class Clock(Protocol):
    def now(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class SelfMade:
    """Broken by a loop: to build one you need one already."""

    def __init__(self, other: SelfMade) -> None:
        self.other = other

    def greet(self) -> str:
        return "hi"


class UtcClock:
    def now(self) -> str:
        return "12:00 UTC"


class LocalClock:
    def now(self) -> str:
        return "06:00 local"


class TimedGreeter:
    """Broken without any loop: it needs a Clock, and two are registered."""

    def __init__(self, clock: Clock) -> None:
        self.clock = clock

    def greet(self) -> str:
        return "hello at " + self.clock.now()


def show(label: str, call: Callable[[], object]) -> None:
    """Print what `call` returns, or the full text of what it raises."""
    try:
        print("  %s -> %r" % (label, call()))
    except Exception as error:
        print("  %s -> raises %s:" % (label, type(error).__name__))
        for line in str(error).splitlines():
            print("      " + line)


case = sys.argv[1]
broken_class = {"recursion": SelfMade, "ambiguous": TimedGreeter}[case]
book = md.Spellbook()
english = book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                    permissions="create")
if case == "ambiguous":
    book.bind(spell=UtcClock, spellframe=Clock, binding_name="utc", existence="many", permissions="create")
    book.bind(spell=LocalClock, spellframe=Clock, binding_name="local", existence="many", permissions="create")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
broken = world.bind_inactive(spell=broken_class, spell_index=index, spellframe=Greeter, binding_name="greeter",
                             existence="many", permissions="create")
print("case %r: %s staged on the greeter index - staging raised nothing" % (case, broken_class.__name__))
show("meld English", lambda: world.meld(spell_id=english).greet())
print("notch the index to %s:" % broken_class.__name__)
show("notch_spell", lambda: world.notch_spell(spell_index=index, spell_id=broken))
print("after the failed notch the index selects:",
      broken_class.__name__ if index.selected_spell_id == broken else "English")
show("meld %s, 1st time" % broken_class.__name__, lambda: world.meld(spell_id=broken).greet())
show("meld %s, 2nd time" % broken_class.__name__, lambda: world.meld(spell_id=broken).greet())
show("meld English", lambda: world.meld(spell_id=english).greet())
world.cleanup()
