"""Probe: force_unshare=False (repoint) meets a version-grant borrower - the grant from the new owner is refused
(roles reversed) and the refusal is swallowed (melder_1, 2026-10-16). usage: PYTHONPATH=<tree>/src python <this script>
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

for name in ("_add_spell_to_contract", "_link"):
    orig = getattr(ConduitWard, name)
    def make(orig=orig, name=name):
        def traced(self, *a, **k):
            try:
                return orig(self, *a, **k)
            except BaseException as e:
                print(f"  {name} raised:", type(e).__name__, str(e)[:300])
                raise
        return traced
    setattr(ConduitWard, name, make())

lender_book, borrower_book, steward_book = md.Spellbook(), md.Spellbook(), md.Spellbook()
english = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many", permissions="create")
borrower_book.bind(spell=Banner, existence="many", permissions="create")
lender = lender_book.conjure(dynamic=True, name="lender")
borrower = borrower_book.conjure(dynamic=True, name="borrower")
steward = steward_book.conjure(dynamic=True, name="steward")
lender.link(borrower)
with borrower.transaction("link", conduits=[borrower, lender]):
    borrower.add_spell_to_contract(spell_id=english, conduit=lender, permissions="create")
print("Banner:", borrower.meld(spell=Banner).text)
lender.transfer_spell_ownership(spell=english, target_conduit=steward, force_unshare=False)
print("done")
