"""Probe: the default transfer (force_unshare=True) meets an index-link borrower - the per-spell removal is refused
and the refusal is swallowed (melder_1, 2026-10-16). usage: PYTHONPATH=<tree>/src python <this script>
"""
from typing import Protocol
import melder as md
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard

class Greeter(Protocol):
    def greet(self) -> str: ...

class English:
    def greet(self) -> str:
        return "hello"

class Banner:
    def __init__(self, greeter: Greeter = md.SpellContract(spellframe=Greeter, binding_name="greeter")) -> None:
        self.text = greeter.greet().upper()

orig = ConduitWard._remove_spell_from_contract
def traced(self, *a, **k):
    try:
        return orig(self, *a, **k)
    except BaseException as e:
        print("  _remove_spell_from_contract raised:", type(e).__name__, str(e)[:200])
        raise
ConduitWard._remove_spell_from_contract = traced

lender_book, borrower_book, steward_book = md.Spellbook(), md.Spellbook(), md.Spellbook()
english = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many", permissions="create")
borrower_book.bind(spell=Banner, existence="many", permissions="create")
lender = lender_book.conjure(dynamic=True, name="lender")
borrower = borrower_book.conjure(dynamic=True, name="borrower")
steward = steward_book.conjure(dynamic=True, name="steward")
lender.link(borrower)
spell = lender.get_spell_by_spell_id(english)
index = spell.spell_index
borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
print("Banner:", borrower.meld(spell=Banner).text)
print("owner before:", "lender" if spell._owner_conduit_id == lender._id else spell._owner_conduit_id)
summary = lender.transfer_spell_ownership(spell=english, target_conduit=steward)
print("owner after:", {lender._id: "lender", steward._id: "steward"}.get(spell._owner_conduit_id, spell._owner_conduit_id))
print("steward book has English:", english in steward_book._spells_by_id, "index in steward._spells:", index in steward_book._spells)
print("lender book has English:", english in lender_book._spells_by_id, "index in lender._spells:", index in lender_book._spells)
print("spell._spellbook is steward_book:", spell._spellbook is steward_book)
