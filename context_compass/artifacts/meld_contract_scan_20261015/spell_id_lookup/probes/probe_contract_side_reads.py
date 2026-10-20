"""Probe (melder_1, 2026-10-18): what the borrower's contract-side reads answer for a version's spell_id.

The owner asked (chat 2026-10-18) that every remaining finding say what the id at that place means. This probe
shows, on the running code, what each borrower-side read answers when it is handed a version's spell_id, in four
worlds. Each world is a fresh dynamic frame with caching off: a lender Book binds English under
(Greeter, "greeter"), stages French on the same SpellIndex with `bind_inactive`, and links to a borrower Book.

  A  index link: the borrower links the whole index (follows whichever version is active).
  B  version grant, then a notch away: the borrower is granted English by spell_id; the lender notches to French.
  C  version grant only: English is granted; French stays parked on the lender and is never granted.
  D  both versions granted across a notch: English granted, notch to French, French granted.

Read-only on src/: run against a copy of src from a scratch directory, e.g.
    PYTHONPATH=<copy>/src python probe_contract_side_reads.py
"""
from typing import Any, Callable, Dict, Protocol, Tuple

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Greeter(Protocol):
    """The contract English and French both implement."""

    def greet(self) -> str: ...


class English:
    """Version 1 of the greeter: bound active."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Version 2 of the greeter: staged parked on the same SpellIndex."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Note:
    """A plain spell so the borrower Book has something to conjure."""


def fresh_aether() -> None:
    """Give the next world a fresh Aether, rebound on Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def world(frame: str) -> Tuple[Spellbook, Spellbook, Conduit, Conduit, SpellIndex, Dict[str, str]]:
    """Lender (English active, French parked on Greeter's index) linked to a borrower; caching off."""
    fresh_aether()
    lender_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    lender_book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                       system_caching_enabled=False)
    borrower_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    english_id = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter",
                                  existence=Existence.many, permissions="create")
    borrower_book.bind(spell=Note, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    greeter_index = lender_book.find_spell_by_spell_id(english_id).spell_index
    french_id = lender.bind_inactive(spell=French, spell_index=greeter_index, spellframe=Greeter,
                                     binding_name="greeter", existence=Existence.many, permissions="create")
    lender.link(borrower)
    names = {english_id: "english_id", french_id: "french_id"}
    return lender_book, borrower_book, lender, borrower, greeter_index, names


def show(value: Any, names: Dict[str, str]) -> str:
    """Render an answer with spell_ids replaced by their names and Spells by their class."""
    if value is None:
        return "None"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        return names.get(value, "<peer conduit id>" if len(value) < 40 else value[:12])
    if isinstance(value, dict):
        return "{" + ", ".join(f"{show(k, names)}: {show(v, names)}" for k, v in value.items()) + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(show(v, names) for v in value) + "]"
    spell_class = getattr(value, "spell", None)
    if spell_class is not None:
        return f"Spell({spell_class.__name__})"
    return type(value).__name__


def ask(label: str, call: Callable[[], Any], names: Dict[str, str]) -> None:
    """Print what one read answers, or the exception it raises."""
    try:
        print(f"  {label:<58} -> {show(call(), names)}")
    except Exception as error:
        print(f"  {label:<58} -> raises {type(error).__name__}: {error}")


def holdings(book: Spellbook, lender: Conduit, names: Dict[str, str]) -> None:
    """Print which borrowed copies the borrower Book holds active and parked, by their own spell_id."""
    active = book._contracted_spells_by_id.get(lender.id, {})
    parked = book._inactive_contracted_spells.get(lender.id, {})
    print(f"  borrower holds active: {show(active, names)}   parked: {show(parked, names)}")


def reads(borrower: Conduit, lender: Conduit, names: Dict[str, str], ids: Tuple[str, ...]) -> None:
    """Print every contract-side read of the borrower for the given spell_ids."""
    for spell_id in ids:
        name = names[spell_id]
        ask(f"find_contracted_spell({name})", lambda: borrower.find_contracted_spell(spell_id), names)
        ask(f"get_spell_in_contracts({name})", lambda: borrower.get_spell_in_contracts(spell_id), names)
    ask("get_spells_in_contract_by_conduit(lender)['inbound']",
        lambda: borrower.get_spells_in_contract_by_conduit(lender.id)["inbound"], names)
    ask("get_all_spells_in_contracts()", lambda: list(borrower.get_all_spells_in_contracts().values()), names)
    ask("get_all_spells_in_contracts(validate=False)",
        lambda: list((borrower.get_all_spells_in_contracts(validate=False) or {}).values()), names)
    ask("validate_contracts_and_define()", lambda: list(borrower.validate_contracts_and_define().values()), names)
    ask("validate_received_contracts()", borrower.validate_received_contracts, names)


def grant(borrower: Conduit, lender: Conduit, spell_id: str) -> None:
    """Grant one version to the borrower by its spell_id, in a link transaction."""
    with borrower.transaction("link", conduits=[borrower, lender]):
        borrower.add_spell_to_contract(spell_id=spell_id, conduit=lender, permissions="create")


def main() -> None:
    """Build the four worlds and print what the borrower's reads answer in each."""
    print("A  index link (English active, French staged parked on the same index)")
    _lb, book, lender, borrower, index, names = world("probe_a")
    with borrower.transaction("link", conduits=[borrower, lender]):
        borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
    english_id, french_id = list(names)
    holdings(book, lender, names)
    reads(borrower, lender, names, (english_id, french_id))

    print("B  version grant of English, then the lender notches to French")
    _lb, book, lender, borrower, index, names = world("probe_b")
    english_id, french_id = list(names)
    grant(borrower, lender, english_id)
    lender.notch_spell(spell_index=index, spell_id=french_id)
    holdings(book, lender, names)
    reads(borrower, lender, names, (english_id,))
    print("B' control: the lender notches back to English")
    lender.notch_spell(spell_index=index, spell_id=english_id)
    holdings(book, lender, names)
    ask("validate_contracts_and_define()", lambda: list(borrower.validate_contracts_and_define().values()), names)

    print("C  version grant of English only; French stays parked on the lender, never granted")
    _lb, book, lender, borrower, index, names = world("probe_c")
    english_id, french_id = list(names)
    grant(borrower, lender, english_id)
    holdings(book, lender, names)
    reads(borrower, lender, names, (english_id, french_id))

    print("D  English granted, notch to French, French granted")
    _lb, book, lender, borrower, index, names = world("probe_d")
    english_id, french_id = list(names)
    grant(borrower, lender, english_id)
    lender.notch_spell(spell_index=index, spell_id=french_id)
    grant(borrower, lender, french_id)
    holdings(book, lender, names)
    reads(borrower, lender, names, (english_id, french_id))
    fresh_aether()


if __name__ == "__main__":
    main()
