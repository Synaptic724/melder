"""Probe (melder_0, 2026-10-17; EPIC-2026-10-17-correctness_defects, sweep A10): disposing the active member of an
index that still holds a parked version.

`Conduit.cleanup_spell` refuses the active member of a multi-member index ("notch away from it first"). This probe
checks the other public ways to dispose that member - a direct `Spell.cleanup()` and `Spellbook.cleanup_and_remove_spell`
- and what each leaves of the index, the parked version and an index-linked borrower.

Each case in a fresh Aether and its own dynamic frame with caching off. A lender Book binds English active on an
index and Holder active on another; a borrower links and contracts English's whole index; French is staged on
English's index (`Conduit.bind_inactive`).
  D1  control: `lender.cleanup_spell(spell=English)` - refused, nothing changes.
  D2  `English.cleanup()` (a direct Spell.cleanup) - what is left, and can French still be notched, moved, disposed
      or cleaned by the Book's teardown?
  D3  `lender_book.cleanup_and_remove_spell(english_id)` - the same questions.

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_direct_cleanup_active_member.py
"""
from typing import Protocol

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Greeter(Protocol):
    """The contract every greeter version implements."""

    def greet(self) -> str: ...


class English:
    """Version 1, active."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Version 2, staged on English's index."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Holder:
    """Another active spell of the lender, whose index is a move target."""


class Note:
    """A plain spell so the borrower Book has something to conjure."""


def fresh_aether() -> None:
    """Install a fresh Aether and rebind it on Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def world(frame: str):
    """The lender (English active, French parked, Holder active), the borrower contracting English's index."""
    lender_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    lender_book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                      system_caching_enabled=False)
    borrower_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    english_id = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter",
                                  existence=Existence.many, permissions="create")
    holder_id = lender_book.bind(spell=Holder, existence=Existence.many, permissions="create")
    borrower_book.bind(spell=Note, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    english = lender_book.find_spell_by_id(english_id)
    index = english.spell_index
    holder_index = lender_book.find_spell_by_id(holder_id).spell_index
    lender.link(borrower)
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
    french_id = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                                     existence=Existence.many, permissions="create")
    french = lender_book._inactive_spells[french_id]
    names = {english_id: "English", french_id: "French", holder_id: "Holder"}
    return lender_book, borrower_book, lender, english, french, index, holder_index, names


def attempt(label: str, fn) -> None:
    """Run `fn`; print what it returned or raised."""
    try:
        result = fn()
        shown = type(result).__name__ if result is not None else "None"
        print(f"    {label} -> {shown}")
    except Exception as error:
        print(f"    {label} raised {type(error).__name__}: {str(error).splitlines()[0][:150]}")


def view(step: str, lender_book: Spellbook, borrower_book: Spellbook, lender: Conduit, english, french, index,
         names: dict) -> None:
    """Print the index, the lender's versions, French's state, the frame registry and the borrower's copies."""
    print(f"  [{step}]")
    try:
        selected = names.get(index.selected_spell_id, index.selected_spell_id)
    except Exception as error:
        selected = f"<{type(error).__name__}>"
    print(f"    index cleaned={index.cleaned}; selects {selected}")
    active = sorted(names.get(i, i[:10]) for i in lender_book._spells_by_id if i in names)
    parked = sorted(names.get(i, i[:10]) for i in lender_book._inactive_spells if i in names)
    print(f"    lender: active {active}; parked {parked}")
    french_index = french._spell_index_unless_cleaned()
    print(f"    English cleaned={english.cleaned}; French cleaned={french.cleaned}; French's index is the index: "
          f"{french_index is index}")
    frame = lender_book._aetheric_frame
    for label, spell in (("English", english), ("French", french)):
        try:
            found = frame.find_index_for_spell(spell.spell_id) if not spell.cleaned else "<cleaned spell>"
            found = "the index" if found is index else found
        except Exception as error:
            found = f"<{type(error).__name__}: {str(error)[:60]}>"
        print(f"    frame.find_index_for_spell({label}) -> {found}")
    b_active = sorted(names.get(i, i[:10]) for i in borrower_book._contracted_spells_by_id.get(lender._id, {}))
    b_parked = sorted(names.get(i, i[:10]) for i in borrower_book._inactive_contracted_spells.get(lender._id, {}))
    print(f"    borrower: active copies {b_active}; parked copies {b_parked}")


def after_disposal(lender_book, borrower_book, lender, english, french, index, holder_index, names) -> None:
    """What can still be done with French, then the Book's teardown."""
    french_id = french.spell_id
    attempt("lender.notch_spell(spell_index=index, spell_id=French)",
            lambda: lender.notch_spell(spell_index=index, spell_id=french_id))
    attempt("lender.add_to_spell_index(spell_id=French, target_index=Holder's index)",
            lambda: lender.add_to_spell_index(spell_id=french_id, target_index=holder_index))
    attempt("lender.cleanup_spell(spell=French)", lambda: lender.cleanup_spell(spell=french))
    attempt("lender.cleanup() (the Book's teardown)", lender.cleanup)
    print(f"    after teardown: French cleaned={french.cleaned}")
    attempt("French.cleanup()", french.cleanup)


def d1() -> None:
    """Control: cleanup_spell refuses the active member of a multi-member index."""
    print("D1 control: lender.cleanup_spell(spell=English) with French parked on its index")
    state = world("d1")
    lender_book, borrower_book, lender, english, french, index, holder_index, names = state
    view("before", lender_book, borrower_book, lender, english, french, index, names)
    attempt("lender.cleanup_spell(spell=English)", lambda: lender.cleanup_spell(spell=english))
    view("after", lender_book, borrower_book, lender, english, french, index, names)


def d2() -> None:
    """A direct Spell.cleanup() of the active member."""
    print("D2 English.cleanup() (direct) with French parked on its index")
    state = world("d2")
    lender_book, borrower_book, lender, english, french, index, holder_index, names = state
    attempt("English.cleanup()", english.cleanup)
    view("after", lender_book, borrower_book, lender, english, french, index, names)
    after_disposal(*state)


def d3() -> None:
    """Spellbook.cleanup_and_remove_spell of the active member."""
    print("D3 lender_book.cleanup_and_remove_spell(English) with French parked on its index")
    state = world("d3")
    lender_book, borrower_book, lender, english, french, index, holder_index, names = state
    attempt("lender_book.cleanup_and_remove_spell(english_id)",
            lambda: lender_book.cleanup_and_remove_spell(english.spell_id))
    view("after", lender_book, borrower_book, lender, english, french, index, names)
    after_disposal(*state)


def main() -> None:
    """Run every case in its own fresh Aether."""
    for case in (d1, d2, d3):
        fresh_aether()
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
        print()
    fresh_aether()


if __name__ == "__main__":
    main()
