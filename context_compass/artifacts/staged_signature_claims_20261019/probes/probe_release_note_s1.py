"""The 0.2.8263 release note's example, run as written (melder_1; STORY-2026-10-17-staged_version_releases_active_signature)."""
from typing import Protocol

import melder as md


class Greeter(Protocol):
    def greet(self) -> str: ...


class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


book = md.Spellbook()
english = book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
french = world.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                             existence="many")

assert world.meld(spellframe=Greeter, binding_name="greeter").greet() == "hello"   # raised KeyError until 0.2.8263

world.notch_spell(spell_index=index, spell_id=french)
assert world.meld(spellframe=Greeter, binding_name="greeter").greet() == "bonjour"
print("OK")
