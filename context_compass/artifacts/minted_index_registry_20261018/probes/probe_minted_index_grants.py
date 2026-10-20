"""Probe (melder_1, 2026-10-18; STORY-2026-10-17-minted_index_missing_from_frame_registry, S4): what a borrower's grant
by spell_id gives it for French, by where French sits - the copy's state on the borrower beside French's on the lender.

Each case runs in a fresh Aether and a dynamic frame with caching off. Book L binds English active as
(Greeter, 'english'), conjures root 'lender', stages French parked on English's index as (Greeter, 'french') and links
a borrower root. Then `borrower.add_spell_to_contract(spell_id=French)` inside a link transaction:
  G1  control - French parked in English's index;
  G2  French parked alone in the index remove_from_spell_index mints (which selects it; activation takes a notch);
  G3  French notched active in that index.
Read-only on src/: run from this folder with the src under test first on sys.path, e.g.
    PYTHONPATH=<tree>/src python -X gil=0 probes/probe_minted_index_grants.py
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
    """Version 2, parked; moved into its own index in G2 and G3."""

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


def first_line(error: BaseException) -> str:
    """The first line of an error's text, trimmed."""
    return str(error).strip().split("\n")[0][:150]


def case(name: str, frame: str, move: bool, notch: bool) -> None:
    """Build the world, place French, grant it by spell_id and print where its copy lands."""
    fresh_aether()
    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                system_caching_enabled=False)
    borrower_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    english_id = book.bind(spell=English, spellframe=Greeter, binding_name="english",
                           existence=Existence.many, permissions="create")
    borrower_book.bind(spell=Note, existence=Existence.many, permissions="create")
    lender = book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    index = book.find_spell_by_spell_id(english_id).spell_index
    french_id = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="french",
                                     existence=Existence.many, permissions="create")
    lender.link(borrower)
    if move:
        lender.remove_from_spell_index(spell_id=french_id, source_index=index)
    french = book.find_spell_by_spell_id(french_id)
    if notch:
        lender.notch_spell(spell_index=french.spell_index, spell_id=french_id)
    on_lender = "active" if french_id in book._spells_by_id else "parked"
    print(f"{name}: French {on_lender} on the lender; its index selects it: "
          f"{french.spell_index.selected_spell_id == french_id}")
    try:
        with borrower.transaction("link", conduits=[borrower, lender]):
            granted = borrower.add_spell_to_contract(spell_id=french_id, conduit=lender, permissions="create")
        active = french_id in borrower_book._contracted_spells_by_id.get(lender._id, {})
        parked = french_id in borrower_book._inactive_contracted_spells.get(lender._id, {})
        print(f"    grant -> {granted}; the borrower's copy: active {active}, parked {parked}")
    except Exception as error:
        print(f"    grant raised {type(error).__name__}: {first_line(error)}")
    borrower.cleanup()
    lender.cleanup()


def main() -> None:
    """Run G1-G3, each in a fresh Aether."""
    case("G1 control: French parked in English's index", "g1", move=False, notch=False)
    case("G2 French parked alone in the minted index", "g2", move=True, notch=False)
    case("G3 French notched active in the minted index", "g3", move=True, notch=True)
    fresh_aether()


if __name__ == "__main__":
    main()
