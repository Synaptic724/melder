"""Probe (melder_1, 2026-10-18; S4): the release note's example, run as written; on a tree without the fix the
lookup of French's spell_id after the move raises, with the fix every assert holds.

Run from this folder with the src under test first on sys.path, e.g.
    PYTHONPATH=<tree>/src python -X gil=0 probes/probe_release_note_s4.py
"""
import melder as md


class English:
    def greet(self) -> str:
        return "hello"


class French:
    def greet(self) -> str:
        return "bonjour"


book = md.Spellbook()
english = book.bind(spell=English, existence="many", binding_name="english")
world = book.conjure(dynamic=True, name="world")
index = world.get_spell_by_spell_id(english).spell_index
french = world.bind_inactive(spell=French, spell_index=index, existence="many", binding_name="french")

world.remove_from_spell_index(spell_id=french, source_index=index)  # French gets an index of its own, parked
try:
    own_index = world.get_spell_by_spell_id(french).spell_index
except ValueError as error:
    print("get_spell_by_spell_id(french) raised ValueError:", str(error).split(" not found")[0][:20], "... not found")
    raise SystemExit(0)
world.notch_spell(spell_index=own_index, spell_id=french)
assert world.get_conduit_by_spell_id(french) is world
assert world.meld(spell_id=french).greet() == "bonjour"
assert world.meld(spell_id=english).greet() == "hello"
print("every assert holds")
