"""The 0.2.8261 release-note example, run as written (melder_0; S3 of EPIC-2026-10-17-correctness_defects).

Run from a scratch directory with a tree's src/ on sys.path, the GIL off and on:
    PYTHONPATH=<tree>/src python -X gil=0 <this file>
On 0.2.8261 it prints "release-note example: OK". On 0.2.8260 the notch raises AttributeError in the borrower
fan-out, which the note's comment on that line names.
"""
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


class Banner:
    def __init__(self, greeter: Greeter = md.SpellContract(spellframe=Greeter, binding_name="greeter")) -> None:
        self.text = greeter.greet().upper()


lender_book = md.Spellbook()
borrower_book = md.Spellbook()
english = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                           permissions="create")
borrower_book.bind(spell=Banner, existence="many", permissions="create")
lender = lender_book.conjure(dynamic=True, name="lender")
borrower = borrower_book.conjure(dynamic=True, name="borrower")
lender.link(borrower)
index = lender.get_spell_by_spell_id(english).spell_index
french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                              existence="many", permissions="create")
borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
assert borrower.meld(spell=Banner).text == "HELLO"

lender.cleanup_spell(spell=lender.get_spell_by_spell_id(french))  # the borrower lets French go as well
french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                              existence="many", permissions="create")  # staged again: the same spell_id
lender.notch_spell(spell_index=index, spell_id=french)  # raised AttributeError until 0.2.8261
assert borrower.meld(spell=Banner).text == "BONJOUR"
print(f"melder {md.__version__}: release-note example: OK")
