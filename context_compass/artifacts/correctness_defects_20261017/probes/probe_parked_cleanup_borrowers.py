"""Probe (melder_0, 2026-10-17; EPIC-2026-10-17-correctness_defects, sweep A2): what an index-link borrower keeps
when the lender disposes a parked version of the linked index.

Cases, each in a fresh Aether and its own dynamic frame with caching off. A lender Book binds English active on an
index and stages French parked on it (`Conduit.bind_inactive`, which sends the member to index-link borrowers); a
borrower links and contracts the whole index (`add_index_to_contract`).
  P1  control: `remove_from_spell_index(French)` - the lender sends `_emit_index_member_removed`.
  P2  `cleanup_spell(French)` while English keeps the index alive - what the borrower holds for French afterwards,
      and what the borrower's contract listing, contracted lookup and an index unlink then do.

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_parked_cleanup_borrowers.py
"""
from typing import Protocol

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
    """English active and French parked on one index of the lender; the borrower contracts the whole index."""
    lender_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    lender_book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                      system_caching_enabled=False)
    borrower_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    english_id = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter",
                                  existence=Existence.many, permissions="create")
    borrower_book.bind(spell=Note, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    index = lender_book.find_spell_by_id(english_id).spell_index
    french_id = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                                     existence=Existence.many, permissions="create")
    lender.link(borrower)
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
    names = {english_id: "English", french_id: "French"}
    return lender_book, borrower_book, lender, borrower, index, english_id, french_id, names


def borrower_view(step: str, borrower_book: Spellbook, lender: Conduit, names: dict) -> None:
    """Print what the borrower Book holds for the lender's versions."""
    parked = borrower_book._inactive_contracted_spells.get(lender._id, {})
    active = borrower_book._contracted_spells_by_id.get(lender._id, {})
    ids = borrower_book._contracted_spell_ids.get(lender._id, set())
    print(f"  [{step}]")
    print(f"    borrower active copies: {sorted(names.get(i, i[:10]) for i in active)}")
    print(f"    borrower parked copies: "
          f"{sorted((names.get(i, i[:10]), 'cleaned' if s._cleaned else 'live') for i, s in parked.items())}")
    print(f"    borrower borrowed ids: {sorted(names.get(i, i[:10]) for i in ids)}")


def listing(borrower: Conduit, lender: Conduit, names: dict) -> None:
    """Print the borrower's contract listing for the lender, or the error it raises."""
    try:
        rows = borrower.get_spells_in_contract_by_conduit(lender._id)
        shown = {key: sorted(names.get(spell_id, spell_id[:10]) for spell_id, _spell in value)
                 for key, value in (rows or {}).items()}
        print(f"    borrower.get_spells_in_contract_by_conduit(lender) -> {shown}")
    except Exception as error:
        print(f"    borrower.get_spells_in_contract_by_conduit(lender) raised {type(error).__name__}: {error}")


def p1() -> None:
    """Control: remove_from_spell_index sends the member removal."""
    print("P1 control: lender.remove_from_spell_index(French) with English active")
    lender_book, borrower_book, lender, borrower, index, english_id, french_id, names = world("p1")
    borrower_view("after the index link", borrower_book, lender, names)
    lender.remove_from_spell_index(spell_id=french_id, source_index=index)
    borrower_view("after remove_from_spell_index(French)", borrower_book, lender, names)
    listing(borrower, lender, names)


def p2() -> None:
    """cleanup_spell of the parked version while the index survives."""
    print("P2 lender.cleanup_spell(French) with English keeping the index alive")
    lender_book, borrower_book, lender, borrower, index, english_id, french_id, names = world("p2")
    borrower_view("after the index link", borrower_book, lender, names)
    french = lender_book._inactive_spells[french_id]
    lender.cleanup_spell(spell=french)
    print(f"    lender still owns French: {french_id in lender_book._spell_ids}; French cleaned: {french._cleaned}")
    borrower_view("after cleanup_spell(French)", borrower_book, lender, names)
    listing(borrower, lender, names)
    try:
        found = borrower.find_contracted_spell(french_id)
        print(f"    borrower.find_contracted_spell(French's id) -> "
              f"{None if found is None else (type(found).__name__, 'cleaned' if found._cleaned else 'live')}")
    except Exception as error:
        print(f"    borrower.find_contracted_spell(French's id) raised {type(error).__name__}: {error}")
    try:
        with borrower.transaction("link", conduits=[borrower, lender]):
            result = borrower.remove_index_from_contract(index_id=index.id, conduit=lender)
        print(f"    borrower.remove_index_from_contract(index_id=...) -> {result}")
    except Exception as error:
        print(f"    borrower.remove_index_from_contract(index_id=...) raised {type(error).__name__}: {error}")
    borrower_view("after the unlink", borrower_book, lender, names)


def main() -> None:
    """Run every case in its own fresh Aether."""
    for case in (p1, p2):
        fresh_aether()
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
        print()
    fresh_aether()


if __name__ == "__main__":
    main()
