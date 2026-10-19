"""S8's release-note example, run as written (melder_1). Run with src/ on sys.path, the GIL off and on."""
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


class TimedGreeter:                    # needs a Clock - and two are registered
    def __init__(self, clock: Clock) -> None:
        self.clock = clock

    def greet(self) -> str:
        return "hello at " + self.clock.now()


book = md.Spellbook()
english = book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many")
book.bind(spell=UtcClock, spellframe=Clock, binding_name="utc", existence="many")
book.bind(spell=LocalClock, spellframe=Clock, binding_name="local", existence="many")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
timed = world.bind_inactive(spell=TimedGreeter, spell_index=index, spellframe=Greeter, binding_name="greeter",
                            existence="many")

try:
    world.notch_spell(spell_index=index, spell_id=timed)
except md.SpellbookValidationError as error:
    print(str(error).splitlines()[0])
    # notch_spell refused: 'TimedGreeter' (spell_id ...) failed its structural check, so the notch did not
    # happen; 'English' (spell_id ...) is still the active version of the index.

assert index.selected_spell_id == english      # it selected TimedGreeter until 0.2.8262
assert world.meld(spellframe=Greeter, binding_name="greeter").greet() == "hello"   # raised until 0.2.8262
print("release-note example: OK")
