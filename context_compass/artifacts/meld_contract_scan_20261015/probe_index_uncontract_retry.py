"""Probe: what a failed remove_index_from_contract leaves, and what a second call does (melder_1, 2026-10-16).

usage: PYTHONHASHSEED=<n> PYTHONPATH=<tree>/src python <this script>   (from a scratch directory)
English is staged-over: the lender stages French on the index-linked index and notches to it, so the borrower holds
French active and English parked. Prints the borrower's copies and index tracking after each unlink attempt.
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
index = lender.get_spell_by_id(english).spell_index
borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
french = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                              existence="many", permissions="create")
lender.notch_spell(spell_index=index, spell_id=french)
names = {english: "English", french: "French"}


def show(step):
    cid = lender._id
    active = sorted(names.get(s, s[:12]) for s in borrower_book._contracted_spells_by_id.get(cid, {}))
    parked = sorted(names.get(s, s[:12]) for s in borrower_book._inactive_contracted_spells.get(cid, {}))
    tracked = index.id in borrower_book._contracted_indexes
    contract = borrower._conduit_ward._find_contract_by_id(lender._id)
    linked = contract is not None and contract._check_index_exists(lender._conduit_ward, index.id)
    print(f"{step}: active={active} parked={parked} borrower tracks index={tracked} contract links index={linked}")


def unlink(step):
    try:
        borrower.remove_index_from_contract(index_id=index.id, conduit=lender)
        print(f"{step}: returned")
    except Exception as error:
        message = str(error)
        for spell_id, label in names.items():
            message = message.replace(spell_id, label)
        print(f"{step}: {type(error).__name__}: {message[:100]}")
    show(f"  after {step}")


show("before the unlink")
unlink("first remove_index_from_contract")
unlink("second remove_index_from_contract")
print("order of spells_in_index():", [names[s] for s in index.spells_in_index()])
print(f"melder {md.__version__}")
