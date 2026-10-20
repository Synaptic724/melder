"""S8 proof in plain words (melder_1, 2026-10-19): a version switch that fails its check is left half-done.

The new version is ordinary - no recursion: TimedGreeter needs a Clock, and two clocks are registered, so Melder
cannot pick one (AMBIGUOUS_PROVIDER). Staging it is accepted (a parked version is not checked); the switch checks it
and raises - after the switch already happened. Run with src/ on sys.path, the GIL off and on.
"""
from typing import Protocol

import melder as md


class Greeter(Protocol):
    def greet(self) -> str: ...


class Clock(Protocol):
    def now(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class UtcClock:
    def now(self) -> str:
        return "12:00 UTC"


class LocalClock:
    def now(self) -> str:
        return "06:00 local"


class TimedGreeter:
    """The new version: it needs a Clock - and there are two."""

    def __init__(self, clock: Clock) -> None:
        self.clock = clock

    def greet(self) -> str:
        return "hello at " + self.clock.now()


class Speaker:
    """The borrower's consumer of the shared greeter."""

    def __init__(self, greeter: Greeter) -> None:
        self.greeter = greeter


def attempt(label: str, call) -> None:
    try:
        result = call()
        print("  %s -> %s" % (label, result))
    except Exception as error:
        print("  %s -> raises %s: %s" % (label, type(error).__name__, str(error).splitlines()[0][:110]))


book = md.Spellbook()
english = book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many", permissions="create")
book.bind(spell=UtcClock, spellframe=Clock, binding_name="utc", existence="many", permissions="create")
book.bind(spell=LocalClock, spellframe=Clock, binding_name="local", existence="many", permissions="create")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index

other_book = md.Spellbook()
speaker = other_book.bind(spell=Speaker, existence="many", permissions="create")
borrower = other_book.conjure(dynamic=True, name="borrower")
world.link(borrower)
with borrower.transaction("link", conduits=[borrower, world]):
    borrower.add_index_to_contract(index=index, conduit=world, permissions="create")

print("before the switch:")
attempt("world: greeter by name", lambda: world.meld(spellframe=Greeter, binding_name="greeter").greet())
attempt("borrower: speaker's greeter", lambda: borrower.meld(spell_id=speaker).greeter.greet())

timed = world.bind_inactive(spell=TimedGreeter, spell_index=index, spellframe=Greeter, binding_name="timed",
                            existence="many", permissions="create")
print("staged TimedGreeter (needs a Clock; UtcClock and LocalClock are both registered): accepted")
print("switch the index to TimedGreeter:")
attempt("world.notch_spell(...)", lambda: world.notch_spell(spell_index=index, spell_id=timed))
codes = []
try:
    world.meld(spell_id=timed)
except Exception as error:
    codes = sorted(set(part.split("]")[0] for part in str(error).split("[")[1:]))
print("  the reason Melder gives:", ", ".join(codes) or "(none)")

print("after the failed switch:")
selected = index.selected_spell_id
print("  the index now selects:", "TimedGreeter (the broken one)" if selected == timed
      else "English" if selected == english else selected)
attempt("world: English by its spell_id", lambda: world.meld(spell_id=english).greet())
attempt("world: greeter by name", lambda: world.meld(spellframe=Greeter, binding_name="greeter").greet())
attempt("world: the broken version by name", lambda: world.meld(spellframe=Greeter, binding_name="timed").greet())
attempt("borrower: speaker's greeter", lambda: borrower.meld(spell_id=speaker).greeter.greet())

borrower.cleanup()
world.cleanup()
