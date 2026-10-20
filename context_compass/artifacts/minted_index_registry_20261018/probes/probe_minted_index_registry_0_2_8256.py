# Copied by melder_1 (2026-10-18) from correctness_defects_20261017/probes/probe_minted_index_registry.py for S4's re-verification on
# 0.2.8256; the only change: the 0.2.8253 renames find_spell_by_id -> find_spell_by_spell_id and
# get_spell_by_id -> get_spell_by_spell_id (a parked spell_id now answers its own spell).
"""Probe (melder_0, 2026-10-17; EPIC-2026-10-17-correctness_defects, sweep A3): is the index
`remove_from_spell_index` mints known to the frame's spell registry?

Cases, each in a fresh Aether and its own dynamic frame with caching off; a lender Book binds English active and
stages French parked on English's index.
  M1  control: French parked in English's index - what the frame-level lookups answer for French's spell_id.
  M2  after `remove_from_spell_index(French)` - French alone, parked, in the minted index.
  M3  after a notch makes French active inside the minted index (French bound under its own binding name, so no
      signature is shared with English).
For each: the Book's own exact read (`_get_owned_spell`), the frame's `find_index_for_spell` and
`find_conduit_id_for_spell`, `Conduit.get_spell_by_spell_id`, `Conduit.get_conduit_by_spell_id`, a meld by spell_id, and in
M3 a borrower's `add_spell_to_contract(spell_id=French)` (the grant check asks `get_spell_by_spell_id`).

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_minted_index_registry.py
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
    """Version 2, parked, later moved into its own index."""

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
    """English active; French staged on English's index under its own binding name; a borrower Book linked."""
    lender_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    lender_book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                      system_caching_enabled=False)
    borrower_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    english_id = lender_book.bind(spell=English, spellframe=Greeter, binding_name="english",
                                  existence=Existence.many, permissions="create")
    borrower_book.bind(spell=Note, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    index = lender_book.find_spell_by_spell_id(english_id).spell_index
    french_id = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="french",
                                     existence=Existence.many, permissions="create")
    lender.link(borrower)
    names = {english_id: "English", french_id: "French"}
    return lender_book, lender, borrower, index, french_id, names


def ask(step: str, lender_book: Spellbook, lender: Conduit, french_id: str, names: dict) -> None:
    """Print what each lookup answers for French's spell_id."""
    frame = lender_book._aetheric_frame
    owned = lender_book._get_owned_spell(french_id)
    print(f"  [{step}]")
    print(f"    Book _get_owned_spell(French) -> {None if owned is None else names.get(owned.spell_id)}"
          f" ({'active' if owned is not None and owned._active else 'parked'})")
    index = frame.find_index_for_spell(french_id)
    print(f"    frame.find_index_for_spell(French) -> {'None' if index is None else 'an index'}")
    print(f"    frame.find_conduit_id_for_spell(French) is the lender: "
          f"{frame.find_conduit_id_for_spell(french_id) == lender._id}")
    for label, call in (("get_spell_by_spell_id", lambda: lender.get_spell_by_spell_id(french_id)),
                        ("get_conduit_by_spell_id", lambda: lender.get_conduit_by_spell_id(french_id))):
        try:
            answer = call()
            shown = names.get(getattr(answer, "spell_id", None), None) or type(answer).__name__
            print(f"    lender.{label}(French) -> {shown}")
        except Exception as error:
            print(f"    lender.{label}(French) raised {type(error).__name__}: {error}")


def m1() -> None:
    """Control: French parked in the registered index."""
    print("M1 control: French parked in English's index")
    lender_book, lender, _borrower, _index, french_id, names = world("m1")
    ask("French parked in English's index", lender_book, lender, french_id, names)


def m2() -> None:
    """French alone, parked, in the minted index."""
    print("M2 remove_from_spell_index(French): French alone and parked in the minted index")
    lender_book, lender, _borrower, index, french_id, names = world("m2")
    lender.remove_from_spell_index(spell_id=french_id, source_index=index)
    ask("after remove_from_spell_index(French)", lender_book, lender, french_id, names)


def m3() -> None:
    """French active inside the minted index."""
    print("M3 notch French active inside the minted index")
    lender_book, lender, borrower, index, french_id, names = world("m3")
    lender.remove_from_spell_index(spell_id=french_id, source_index=index)
    minted = lender_book._get_owned_spell(french_id).spell_index
    lender.notch_spell(spell_index=minted, spell_id=french_id)
    ask("after the notch inside the minted index", lender_book, lender, french_id, names)
    try:
        obj = lender.meld(spell_id=french_id)
        print(f"    lender.meld(spell_id=French) -> {type(obj).__name__}")
    except Exception as error:
        print(f"    lender.meld(spell_id=French) raised {type(error).__name__}: {error}")
    try:
        with borrower.transaction("link", conduits=[borrower, lender]):
            granted = borrower.add_spell_to_contract(spell_id=french_id, conduit=lender, permissions="create")
        print(f"    borrower.add_spell_to_contract(spell_id=French) -> {granted}")
    except Exception as error:
        print(f"    borrower.add_spell_to_contract(spell_id=French) raised {type(error).__name__}: {error}")


def main() -> None:
    """Run every case in its own fresh Aether."""
    for case in (m1, m2, m3):
        fresh_aether()
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
        print()
    fresh_aether()


if __name__ == "__main__":
    main()
