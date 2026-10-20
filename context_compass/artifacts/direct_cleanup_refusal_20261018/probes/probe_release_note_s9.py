"""The 0.2.8256 release-note example, run as written (plus asserts on what the note says it shows)."""
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

try:
    world.get_spell_by_spell_id(english).cleanup()       # until 0.2.8256: cleaned the index under French
except RuntimeError as error:
    print(error)
    assert str(error).startswith("Spellbook cannot remove spell " + english + ": it is the active member")
else:
    raise AssertionError("not refused")

assert index.spells_in_index() == {english, french}         # nothing changed
world.notch_spell(spell_index=index, spell_id=french)       # one remedy: notch first,
world.cleanup_spell(spell=world.get_spell_by_spell_id(english))   # then dispose the old version, now parked
assert world.meld(spell_id=french).greet() == "bonjour"
assert index.spells_in_index() == {french}
print("E1 ok: refused, then notch and dispose")

# The other two remedies, each in a fresh index of the same world.
english2 = book.bind(spell=English, existence="many", binding_name="english2")
index2 = world.get_spell_by_spell_id(english2).spell_index
french2 = world.bind_inactive(spell=French, spell_index=index2, existence="many", binding_name="french2")
world.cleanup_spell(spell=world.get_spell_by_spell_id(french2))     # dispose the parked version first,
world.get_spell_by_spell_id(english2).cleanup()                       # then the active one goes with its index
assert index2.cleaned
print("E2 ok: dispose the parked version, then the active one")

english3 = book.bind(spell=English, existence="many", binding_name="english3")
index3 = world.get_spell_by_spell_id(english3).spell_index
french3 = world.bind_inactive(spell=French, spell_index=index3, existence="many", binding_name="french3")
world.remove_from_spell_index(spell_id=french3, source_index=index3)   # move the parked version out,
book.cleanup_and_remove_spell(english3)                              # then the active one goes with its index
assert index3.cleaned
assert book.find_spell_by_spell_id(french3) is not None              # French stays parked, in its own index
print("E3 ok: move the parked version out, then the active one")

try:
    world2_index = world.get_spell_by_spell_id(french).spell_index
    english4 = world.bind_inactive(spell=English, spell_index=world2_index, existence="many", binding_name="english4")
    world.cleanup_spell(spell=world.get_spell_by_spell_id(french))
except RuntimeError as error:
    print(error)
    assert str(error).startswith("cleanup_spell: spell " + french + " is the active member of a multi-member index,")
    assert str(error).endswith("or move them out with remove_from_spell_index first.")
else:
    raise AssertionError("cleanup_spell not refused")
print("E4 ok: cleanup_spell names the same remedies")
world.cleanup()
