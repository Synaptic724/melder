"""Probe (melder_0, 2026-10-19; S3 of EPIC-2026-10-17-correctness_defects): what an index-link borrower still holds
after the lender disposes a parked version, after the borrower removes the index from the contract, and after a
sever - on the current tree, at the owner's request ("can you properly test this").

Each case runs in a fresh Aether with its own dynamic frame, caching off. The lender binds English active on an
index and stages French parked on it; the borrower links and contracts the whole index (`add_index_to_contract`).
  U1  control: the borrower removes the index from the contract with nothing disposed.
  U2  the lender's `cleanup_spell(French)` while English keeps the index alive; then the borrower's
      `remove_index_from_contract`; then `sever_link`.
  U3  after the lender's `cleanup_spell(French)`, the lender stages French again (the same class, so the same
      spell_id) and notches to it: does the borrower end up holding the live French or the cleaned one?
For each step it prints the borrower Book's three entries for the lender (active, parked, borrowed ids), whether
the Book still tracks the index, the ward contract's details, and the public views.

Read-only on src/: run from the folder above with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_index_unlink_leftovers.py
"""
from typing import Protocol

from melder.__version__ import __version__
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Greeter(Protocol):
    """The contract both versions implement."""

    def greet(self) -> str: ...


class English:
    """Version 1, active."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Version 2, parked on English's index."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Note:
    """A plain spell so the borrower Book has something to conjure."""


def fresh_aether() -> None:
    """Install a fresh Aether and rebind it on Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def world(frame: str):
    """English active and French parked on one lender index; the borrower contracts the whole index."""
    lender_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    lender_book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                      system_caching_enabled=False)
    borrower_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    english_id = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter",
                                  existence=Existence.many, permissions="create")
    borrower_book.bind(spell=Note, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    index = lender_book.find_spell_by_spell_id(english_id).spell_index
    french_id = stage_french(lender, index)
    lender.link(borrower)
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
    names = {english_id: "English", french_id: "French"}
    return lender_book, borrower_book, lender, borrower, index, english_id, french_id, names


def stage_french(lender: Conduit, index) -> str:
    """Stage French parked on the index; return its spell_id."""
    return lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                                existence=Existence.many, permissions="create")


def show(step: str, borrower_book: Spellbook, borrower: Conduit, lender: Conduit, index_id: str,
         ids: dict) -> None:
    """Print what the borrower holds for the lender's versions, privately and through the public views."""
    names = {value: key for key, value in ids.items()}
    active = borrower_book._contracted_spells_by_id.get(lender._id, {})
    parked = borrower_book._inactive_contracted_spells.get(lender._id, {})
    borrowed = borrower_book._contracted_spell_ids.get(lender._id, set())
    print(f"  [{step}]")
    print(f"    Spellbook._contracted_spells_by_id[lender]: {sorted(names.get(i, i[:10]) for i in active)}")
    print("    Spellbook._inactive_contracted_spells[lender]: "
          f"{sorted((names.get(i, i[:10]), 'cleaned' if s._cleaned else 'live') for i, s in parked.items())}")
    print(f"    Spellbook._contracted_spell_ids[lender]: {sorted(names.get(i, i[:10]) for i in borrowed)}")
    print(f"    Spellbook._contracted_indexes holds the index: {index_id in borrower_book._contracted_indexes}")
    try:
        contract = borrower._conduit_ward._find_contract_by_id(lender._id)
        if contract is None:
            print("    ward contract: none")
        else:
            ward = lender._conduit_ward
            details = {name: contract._check_if_exists(ward, spell_id) for name, spell_id in ids.items()}
            print(f"    ward contract: index detail {contract._check_index_exists(ward, index_id)}, "
                  f"member details {details}")
    except Exception as error:
        print(f"    ward contract read raised {type(error).__name__}: {error}")
    try:
        rows = borrower.get_spells_in_contract_by_conduit(lender._id) or {}
        shown = {key: sorted(names.get(spell_id, spell_id[:10]) for spell_id, _spell in value)
                 for key, value in rows.items()}
        print(f"    public get_spells_in_contract_by_conduit(lender): {shown}")
    except Exception as error:
        print(f"    public get_spells_in_contract_by_conduit(lender) raised {type(error).__name__}: {error}")
    for name, spell_id in ids.items():
        try:
            found = borrower.find_contracted_spell(spell_id)
            text = None if found is None else ("cleaned" if found._cleaned else "live")
            print(f"    public find_contracted_spell({name}): {text}")
        except Exception as error:
            print(f"    public find_contracted_spell({name}) raised {type(error).__name__}: {error}")


def unlink(borrower: Conduit, lender: Conduit, index_id: str) -> None:
    """The borrower removes the index from the contract; the link stays."""
    try:
        with borrower.transaction("link", conduits=[borrower, lender]):
            result = borrower.remove_index_from_contract(index_id=index_id, conduit=lender)
        print(f"    borrower.remove_index_from_contract(index) -> {result}")
    except Exception as error:
        print(f"    borrower.remove_index_from_contract(index) raised {type(error).__name__}: {error}")


def u1() -> None:
    """Control: unlink with nothing disposed."""
    print("U1 control: the borrower removes the index from the contract, nothing disposed")
    lender_book, borrower_book, lender, borrower, index, english_id, french_id, names = world("u1")
    ids = {"English": english_id, "French": french_id}
    show("after the index link", borrower_book, borrower, lender, index.id, ids)
    unlink(borrower, lender, index.id)
    show("after remove_index_from_contract", borrower_book, borrower, lender, index.id, ids)


def u2() -> None:
    """The lender disposes French; the borrower unlinks the index; then severs."""
    print("U2 the lender's cleanup_spell(French) while English keeps the index; then the unlink; then a sever")
    lender_book, borrower_book, lender, borrower, index, english_id, french_id, names = world("u2")
    ids = {"English": english_id, "French": french_id}
    show("after the index link", borrower_book, borrower, lender, index.id, ids)
    lender.cleanup_spell(spell=lender_book._inactive_spells[french_id])
    show("after the lender's cleanup_spell(French)", borrower_book, borrower, lender, index.id, ids)
    unlink(borrower, lender, index.id)
    show("after remove_index_from_contract", borrower_book, borrower, lender, index.id, ids)
    try:
        print(f"    borrower.sever_link(lender) -> {borrower.sever_link(lender)}")
    except Exception as error:
        print(f"    borrower.sever_link(lender) raised {type(error).__name__}: {error}")
    show("after sever_link", borrower_book, borrower, lender, index.id, ids)


def u3() -> None:
    """After the lender's cleanup of French, the lender stages French again and notches to it."""
    print("U3 the lender's cleanup_spell(French), then French staged again and notched to, the link kept")
    lender_book, borrower_book, lender, borrower, index, english_id, french_id, names = world("u3")
    ids = {"English": english_id, "French": french_id}
    lender.cleanup_spell(spell=lender_book._inactive_spells[french_id])
    show("after the lender's cleanup_spell(French)", borrower_book, borrower, lender, index.id, ids)
    again = stage_french(lender, index)
    print(f"    French staged again; same spell_id: {again == french_id}")
    show("after French is staged again", borrower_book, borrower, lender, index.id, ids)
    try:
        lender.notch_spell(spell_index=index, spell_id=french_id)
        print("    lender.notch_spell(French) -> done")
    except Exception as error:
        print(f"    lender.notch_spell(French) raised {type(error).__name__}: {error}")
    show("after the notch to French", borrower_book, borrower, lender, index.id, ids)
    try:
        made = borrower.meld(spell_id=french_id)
        print(f"    borrower.meld(French) -> {type(made).__name__}.greet() = {made.greet()!r}")
    except Exception as error:
        print(f"    borrower.meld(French) raised {type(error).__name__}: {error}")


def main() -> None:
    """Run every case in its own fresh Aether."""
    print(f"melder {__version__}")
    for case in (u1, u2, u3):
        fresh_aether()
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
        print()
    fresh_aether()


if __name__ == "__main__":
    main()
