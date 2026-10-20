"""The 0.2.8260 release-note example, run as written (melder_1; S7). Run with src/ on sys.path, GIL off and on."""
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
parked = world.get_spell_by_spell_id(french)

world.cleanup()                 # the root's teardown tears the Spellbook down
assert parked.cleaned           # False until 0.2.8260
parked.cleanup()                # returns; raised "Spellbook has already been cleaned." until 0.2.8260
print("release-note example: OK")
