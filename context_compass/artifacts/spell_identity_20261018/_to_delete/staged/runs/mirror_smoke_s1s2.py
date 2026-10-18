"""melder_0, 2026-10-18: smoke of S1 and S2 applied to the /tmp working mirror (not the repository).

Binds a class, checks its spell_id is SpellCodeDigest's and that the Spell carries its binding manifest, refuses a
second registration of the same class under another binding name and existence (strict uniqueness), conjures, and
finds the class through inspect_spell; an unbound class is not found.
"""
import sys
sys.path.insert(0, "/tmp/m0_mq/wt/src")
import melder
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.bind.spell_code_digest import SpellCodeDigest


class Greeter:
    def greet(self) -> str:
        return "hi"


class Other:
    def run(self) -> int:
        return 1


book = Spellbook()
sid = book.bind(spell=Greeter, permissions="read", existence="unique")
print("version", melder.__version__)
print("id == digest:", sid == SpellCodeDigest().spell_id(Greeter))
spell = book.find_spell_by_spell_id(sid)
print("binding_hash:", spell.binding_hash[:12], "manifest existence:", spell.binding_manifest.describe()["existence"])
try:
    book.bind(spell=Greeter, permissions="read", existence="many", binding_name="other")
    print("second registration: ACCEPTED")
except RuntimeError as error:
    print("second registration refused:", str(error).split(". A spell_id")[0].replace(sid, "<sid>"))
conduit = book.conjure(name="root")
print("inspect_spell after conjure:", book.inspect_spell(Greeter) == sid)
print("inspect_spell of an unbound class:", book.inspect_spell(Other))
