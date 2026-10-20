"""S8 on 0.2.8260, after the new bind (a spell_id is the SHA256 of the object's code): are the versions separate
spells, and does the patch's premise about English's address still hold? (melder_1, 2026-10-19)

Four classes go on one index at one address (spellframe Greeter, binding name "greeter"): English bound active;
French, SelfMade and TimedGreeter staged. Printed: each spell_id and binding hash, then the frame's claim on that
address and where the Book's address lookup routes - before staging, after staging, after the failed notch.
Run with src/ on sys.path, the GIL off and on.
"""
from typing import Protocol

import melder as md
from melder.aether.aether import Aether


class Greeter(Protocol):
    def greet(self) -> str: ...


class Clock(Protocol):
    def now(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


class SelfMade:
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
    def __init__(self, clock: Clock) -> None:
        self.clock = clock

    def greet(self) -> str:
        return "hello at " + self.clock.now()


book = md.Spellbook()
english = book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                    permissions="create")
book.bind(spell=UtcClock, spellframe=Clock, binding_name="utc", existence="many", permissions="create")
book.bind(spell=LocalClock, spellframe=Clock, binding_name="local", existence="many", permissions="create")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
key = world.get_spell_by_spell_id(english).key
names = {english: "English"}


def show_address(label: str) -> None:
    """Print who the frame says owns the greeter address and where the Book's address lookup routes."""
    claim = Aether().get_frame("default").get_lookup(key)
    lookup = book._lookup_spells.get(key)
    route = "the greeter index" if lookup is index else repr(lookup)
    print("  %-40s frame claim: %-12s Book lookup: %s" % (label, names.get(claim, repr(claim)), route))


print("address", key)
show_address("before staging")
for cls in (French, SelfMade, TimedGreeter):
    names[world.bind_inactive(spell=cls, spell_index=index, spellframe=Greeter, binding_name="greeter",
                              existence="many", permissions="create")] = cls.__name__
by_name = {name: spell_id for spell_id, name in names.items()}
print("one index, one address, four spells:")
for name in ("English", "French", "SelfMade", "TimedGreeter"):
    spell = world.get_spell_by_spell_id(by_name[name])
    print("  %-12s spell_id %s...  binding_hash %s...  same index: %s"
          % (name, by_name[name][:16], spell.binding_hash[:16], spell.spell_index is index))
print("  distinct spell_ids:", len(set(by_name.values())), "of", len(by_name))
show_address("after staging three at English's address")
try:
    world.notch_spell(spell_index=index, spell_id=by_name["TimedGreeter"])
    print("  notch to TimedGreeter returned")
except Exception as error:
    codes = sorted(set(part.split("]")[0] for part in str(error).split("[")[1:]))
    print("  notch to TimedGreeter raised %s %s" % (type(error).__name__, codes))
print("  the index now selects:", names[index.selected_spell_id])
show_address("after the failed notch")
world.cleanup()
