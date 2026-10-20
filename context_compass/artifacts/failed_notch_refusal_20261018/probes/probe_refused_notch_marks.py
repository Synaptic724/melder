"""S8 (melder_1, 2026-10-19): after a refused notch, is the version left active marked for revalidation?

The owner asked that the rollback still leave the spell in a state that makes it revalidate. Melder has two "not
valid" states: `gated` (the next meld re-runs the checks) and `invalid` (every meld refuses, no re-run). This probe
prints both versions' marks after the refused notch, then melds English once. Run with src/ on sys.path.
Reads internal state only to print it.
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
    def __init__(self, clock: Clock) -> None:
        self.clock = clock

    def greet(self) -> str:
        return "hello at " + self.clock.now()


def marks(label: str) -> None:
    """Print the index's state and each version's verdict in the world conduit."""
    state = book._spell_system_states.get_by_index_id(index.id)
    verdicts = book._spell_system_states.get_conduit_resolution_state(world._id)
    english_spell = book.find_spell_by_spell_id(english)
    timed_spell = book.find_spell_by_spell_id(timed)
    print("  %s:" % label)
    print("    index state: %s (tracks %s)" % (state.validity.name,
          "English" if state.current_spell_id == english else state.current_spell_id[:12]))
    for name, spell_id in (("English", english), ("TimedGreeter", timed)):
        verdict = verdicts.get_spell_validity(spell_id)
        print("    %s verdict in world: %s" % (name, verdict.name if verdict is not None else None))
    print("    TimedGreeter check result kept: %s" % (timed_spell.validation_result_phase4 is not None))
    print("    English check result kept: %s" % (english_spell.validation_result_phase4 is not None))


book = md.Spellbook()
english = book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many", permissions="create")
book.bind(spell=UtcClock, spellframe=Clock, binding_name="utc", existence="many", permissions="create")
book.bind(spell=LocalClock, spellframe=Clock, binding_name="local", existence="many", permissions="create")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
print("world.meld(English) ->", world.meld(spell_id=english).greet())
timed = world.bind_inactive(spell=TimedGreeter, spell_index=index, spellframe=Greeter, binding_name="timed",
                            existence="many", permissions="create")
marks("before the notch")
try:
    world.notch_spell(spell_index=index, spell_id=timed)
except Exception as error:
    print("world.notch_spell(TimedGreeter) -> raises %s: %s" % (type(error).__name__, str(error).splitlines()[0][:60]))
marks("after the refused notch")
print("world.meld(English) ->", world.meld(spell_id=english).greet())
marks("after one meld of English")
world.cleanup()
