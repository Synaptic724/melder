"""Probe (melder_1, 2026-10-18): which consumers a borrower's removal of one version grant touches.

`ConduitWard._remove_spell_from_contract` names the SpellContract consumers to invalidate by the key of the copy
`Spellbook._find_contracted_spell_by_id` returns for the removed spell_id; when that lookup answers None, the key is
None, which `_invalidate_contract_consumers` reads as "every SpellContract consumer of this Book": each is marked
and its stored objects are taken out of the borrower's store. This probe removes a grant of English in two worlds
and reports, for an unrelated consumer (Ticker, whose provider Clock is granted separately and never changes),
whether its stored object survives:

  E0 control: English is active when its grant is removed.
  E  English was parked by a notch to French before its grant is removed (the borrower holds English parked).

Read-only on src/: run against a copy of src from a scratch directory, e.g.
    PYTHONPATH=<copy>/src python probe_parked_grant_removal_scope.py e0|e
(one world per process: process-wide spell ids refuse the same classes bound twice in a frame).
"""
import sys
from typing import Protocol

import melder as md


class Greeter(Protocol):
    """The contract English and French implement."""

    def greet(self) -> str: ...


class IClock(Protocol):
    """The contract Clock implements."""

    def now(self) -> int: ...


class English:
    """Greeter version 1."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Greeter version 2, staged parked."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Clock:
    """The provider of Ticker's contract; granted once and never changed."""

    def now(self) -> int:
        """Return a fixed time."""
        return 7


class Banner:
    """Consumer of the greeter contract, stored per conduit."""

    def __init__(self, greeter: Greeter = md.SpellContract(spellframe=Greeter, binding_name="greeter")) -> None:
        self.text = greeter.greet().upper()


class Ticker:
    """Consumer of the clock contract, stored per conduit; unrelated to the greeter."""

    def __init__(self, clock: IClock = md.SpellContract(spellframe=IClock, binding_name="clock")) -> None:
        self.time = clock.now()


def main(choice: str) -> None:
    """Build the world, remove the English grant, and report what the unrelated consumer kept."""
    lender_book, borrower_book = md.Spellbook(), md.Spellbook()
    english_id = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence="many",
                                  permissions="create")
    clock_id = lender_book.bind(spell=Clock, spellframe=IClock, binding_name="clock", existence="many",
                                permissions="create")
    borrower_book.bind(spell=Banner, existence="unique_per_conduit", permissions="create")
    borrower_book.bind(spell=Ticker, existence="unique_per_conduit", permissions="create")
    lender = lender_book.conjure(dynamic=True, name=f"lender_{choice}")
    borrower = borrower_book.conjure(dynamic=True, name=f"borrower_{choice}")
    index = lender.get_spell_by_spell_id(english_id).spell_index
    french_id = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                                     existence="many", permissions="create")
    lender.link(borrower)
    with borrower.transaction("link", conduits=[borrower, lender]):
        borrower.add_spell_to_contract(spell_id=english_id, conduit=lender, permissions="create")
        borrower.add_spell_to_contract(spell_id=clock_id, conduit=lender, permissions="create")
    ticker_before = borrower.meld(spell=Ticker)
    print(f"== {choice}: Banner {borrower.meld(spell=Banner).text!r}, Ticker time {ticker_before.time}")
    if choice == "e":
        lender.notch_spell(spell_index=index, spell_id=french_id)
        print("  lender notched to French; borrower holds English parked:",
              english_id in borrower_book._inactive_contracted_spells.get(lender.id, {}))
    found = borrower_book._find_contracted_spell_by_id(english_id, lender.id)
    print(f"  _find_contracted_spell_by_id(english_id) -> {None if found is None else found.spell.__name__}")
    states = borrower_book._spell_system_states
    ticker_spell = next(sp for sp in borrower_book._spells_by_id.values() if sp.spell is Ticker)
    before_state = states.get_by_index_id(ticker_spell.spell_index.id)
    print(f"  Ticker lineage before the removal: {before_state.validity.name}")
    with borrower.transaction("link", conduits=[borrower, lender]):
        borrower.remove_spell_from_contract(spell_id=english_id, conduit=lender)
    after_state = states.get_by_index_id(ticker_spell.spell_index.id)
    print(f"  Ticker lineage after the removal:  {after_state.validity.name}")
    ticker_after = borrower.meld(spell=Ticker)
    print(f"  Ticker meld after the removal returns the stored object: {ticker_after is ticker_before}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "e")
