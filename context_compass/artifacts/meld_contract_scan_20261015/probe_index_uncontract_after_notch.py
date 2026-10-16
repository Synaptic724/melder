"""Probe: remove_index_from_contract after the lender notched to a version staged after the index link
(melder_1, 2026-10-16; found while verifying the 0.2.8250 release-note example).

usage: PYTHONPATH=<tree>/src python <this script> [stage_before_link]   (from a scratch directory)
Prints the borrower Book's contracted maps for the lender after each step, then the result of
remove_index_from_contract. With `stage_before_link` the version is staged before the link instead.
"""
import sys
from typing import Protocol

import melder as md

STAGE_FIRST = "stage_before_link" in sys.argv[1:]


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


def name_of(spell_id, ids):
    return ids.get(spell_id, spell_id[:12])


def show(step, borrower_book, lender, ids, index):
    cid = lender._id
    active = sorted(name_of(s, ids) for s in borrower_book._contracted_spells_by_id.get(cid, {}))
    parked = sorted(name_of(s, ids) for s in borrower_book._inactive_contracted_spells.get(cid, {}))
    existence = sorted(name_of(s, ids) for s in borrower_book._contracted_spell_ids.get(cid, set()))
    members = sorted(name_of(s, ids) for s in index._spells_in_index)
    print(f"{step}: index members={members} active={active} parked={parked} existence={existence}")


lender_book = md.Spellbook()
borrower_book = md.Spellbook()
english = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                           permissions="create")
borrower_book.bind(spell=Banner, existence="many", permissions="create")
lender = lender_book.conjure(dynamic=True, name="lender")
borrower = borrower_book.conjure(dynamic=True, name="borrower")
index = lender.get_spell_by_id(english).spell_index
ids = {english: "English"}
if STAGE_FIRST:
    french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                                  existence="many", permissions="create")
    ids[french] = "French"
lender.link(borrower)
borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
show("after the index link", borrower_book, lender, ids, index)
print("Banner:", borrower.meld(spell=Banner).text)
if not STAGE_FIRST:
    french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                                  existence="many", permissions="create")
    ids[french] = "French"
    show("after bind_inactive(French)", borrower_book, lender, ids, index)
lender.notch_spell(spell_index=index, spell_id=french)
show("after the notch to French", borrower_book, lender, ids, index)
print("Banner:", borrower.meld(spell=Banner).text)
try:
    borrower.remove_index_from_contract(index_id=index.id, conduit=lender)
    show("after remove_index_from_contract", borrower_book, lender, ids, index)
except Exception as error:
    message = str(error)
    for spell_id, label in ids.items():
        message = message.replace(spell_id, label)
    print(f"remove_index_from_contract: {type(error).__name__}: {message[:160]}")
    show("after the failed removal", borrower_book, lender, ids, index)
print(f"melder {md.__version__}")
