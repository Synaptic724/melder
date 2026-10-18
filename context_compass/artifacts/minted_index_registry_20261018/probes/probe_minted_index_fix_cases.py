"""Probe (melder_1, 2026-10-18; STORY-2026-10-17-minted_index_missing_from_frame_registry, S4): the readers the
fix's shape depends on, beyond melder_0's M1-M3 (frame lookups) and V1-V4 (residency).

Each case runs in a fresh Aether and a dynamic frame with caching off. Book L binds English active as
(Greeter, 'english'), conjures root 'lender' and stages French parked on English's index as (Greeter, 'french').
  M4  another Book of the same frame binds French (same class, address and existence, so French's spell_id):
      (a) control - French parked in English's index; (b) French alone in the index remove_from_spell_index mints.
      Twice each: a Book not yet conjured (bind, then conjure) and a conjured one (a post-conjure bind).
  M5  under process-wide spell ids (the default) a Book of another frame binds French: (a) control, (b) minted.
  M6  root 'lender' torn down while French sits parked alone in the minted index (a second root keeps the frame
      alive): what the frame's spell registry keeps for the dead root, and what find_index_for_spell answers.
  M7  a transfer by spell_id of French, notched active in the minted index, to another root of the frame.
Read-only on src/: run from this folder with the src under test first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_minted_index_fix_cases.py
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
    """Version 2, parked, moved into its own index."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Note:
    """A plain spell so another Book has something to conjure."""


def fresh_aether() -> None:
    """Install a fresh Aether and rebind it on Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def first_line(error: BaseException) -> str:
    """The first line of an error's text, trimmed."""
    return str(error).strip().split("\n")[0][:150]


def book(frame: str, *, settle: bool = False) -> Spellbook:
    """A Book in `frame`; `settle` makes the frame dynamic with caching off (the frame's first Book)."""
    spellbook = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    if settle:
        spellbook.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                         system_caching_enabled=False)
    return spellbook


def lender_world(frame: str):
    """English active and French parked on English's index, in Book L under root 'lender'."""
    lender_book = book(frame, settle=True)
    english_id = lender_book.bind(spell=English, spellframe=Greeter, binding_name="english",
                                  existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    index = lender_book.find_spell_by_spell_id(english_id).spell_index
    french_id = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="french",
                                     existence=Existence.many, permissions="create")
    return lender_book, lender, index, french_id


def separate(lender_book: Spellbook, lender: Conduit, index, french_id: str):
    """Move French out of English's index into the index remove_from_spell_index mints; return that index."""
    lender.remove_from_spell_index(spell_id=french_id, source_index=index)
    return lender_book._get_owned_spell(french_id).spell_index


def bind_french(label: str, spellbook: Spellbook, french_id: str) -> bool:
    """Try binding French in `spellbook`; print whether it was accepted and with French's spell_id."""
    try:
        spell_id = spellbook.bind(spell=French, spellframe=Greeter, binding_name="french",
                                  existence=Existence.many, permissions="create")
        print(f"    {label}: bind ACCEPTED (spell_id equal to French's: {spell_id == french_id})")
        return True
    except Exception as error:
        print(f"    {label}: bind refused - {type(error).__name__}: {first_line(error)}")
        return False


def other_book_binds(frame: str, french_id: str, tag: str) -> None:
    """A Book of `frame` not yet conjured binds French, then conjures; a conjured one binds French after."""
    fresh = book(frame)
    if bind_french(f"unconjured Book ({tag})", fresh, french_id):
        try:
            fresh.conjure(dynamic=True, name=f"fresh_{tag}")
            print(f"    unconjured Book ({tag}): its conjure ACCEPTED - two Books hold French's spell_id")
        except Exception as error:
            print(f"    unconjured Book ({tag}): its conjure refused - {type(error).__name__}: {first_line(error)}")
    conjured = book(frame)
    conjured.bind(spell=Note, existence=Existence.many, permissions="create")
    conjured.conjure(dynamic=True, name=f"other_{tag}")
    bind_french(f"conjured Book ({tag})", conjured, french_id)


def m4() -> None:
    """Another Book of the frame binds French's spell_id."""
    print("M4 another Book of the same frame binds French")
    for tag in ("a", "b"):
        fresh_aether()
        lender_book, lender, index, french_id = lender_world("m4")
        if tag == "b":
            separate(lender_book, lender, index, french_id)
        print(f"  [{'a control: French parked in English' + chr(39) + 's index' if tag == 'a' else 'b French alone in the minted index'}]")
        other_book_binds("m4", french_id, tag)


def m5() -> None:
    """A Book of another frame binds French's spell_id under process-wide ids."""
    print("M5 a Book of another frame binds French (process-wide spell ids)")
    for tag in ("a", "b"):
        fresh_aether()
        lender_book, lender, index, french_id = lender_world("m5")
        if tag == "b":
            separate(lender_book, lender, index, french_id)
        print(f"  [{'a control: French parked in English' + chr(39) + 's index' if tag == 'a' else 'b French alone in the minted index'}]")
        print(f"    process-wide spell ids: {Spellbook._aether.process_wide_unique_spell_ids}")
        book("m5x", settle=True)
        other_book_binds("m5x", french_id, tag)


def m6() -> None:
    """Root teardown while French is parked alone in the minted index."""
    print("M6 root 'lender' torn down with French parked alone in the minted index")
    fresh_aether()
    lender_book, lender, index, french_id = lender_world("m6")
    keeper_book = book("m6")
    keeper_book.bind(spell=Note, existence=Existence.many, permissions="create")
    keeper_book.conjure(dynamic=True, name="keeper")
    minted = separate(lender_book, lender, index, french_id)
    frame = lender_book._aetheric_frame
    lender_id = lender._id
    print(f"    before: the minted index registered under 'lender': {minted in frame._spell_registry.get(lender_id, set())}")
    lender.cleanup()
    print(f"    after: frame cleaned: {frame.cleaned}")
    print(f"    after: the dead root keeps a spell-registry entry: {lender_id in frame._spell_registry}"
          f" (indexes: {len(frame._spell_registry.get(lender_id, set()))})")
    print(f"    after: the dead root keeps an id-set entry: {lender_id in frame._selected_spell_registry}")
    found = frame.find_index_for_spell(french_id)
    print(f"    after: find_index_for_spell(French) -> {'None' if found is None else 'an index'}")
    print(f"    after: find_conduit_id_for_spell(French) is the dead root: {frame.find_conduit_id_for_spell(french_id) == lender_id}")
    bind_french("a new Book of the frame", book("m6"), french_id)


def m7() -> None:
    """A transfer by spell_id of French, active in the minted index."""
    print("M7 transfer by spell_id of French notched active in the minted index")
    fresh_aether()
    lender_book, lender, index, french_id = lender_world("m7")
    target_book = book("m7")
    target_book.bind(spell=Note, existence=Existence.many, permissions="create")
    target = target_book.conjure(dynamic=True, name="target")
    minted = separate(lender_book, lender, index, french_id)
    lender.notch_spell(spell_index=minted, spell_id=french_id)
    try:
        lender.transfer_spell_ownership(spell=french_id, target_conduit=target)
        frame = lender_book._aetheric_frame
        print(f"    transfer ACCEPTED; French owned by the target Book: {target_book._get_owned_spell(french_id) is not None};"
              f" find_conduit_id_for_spell(French) is the target: {frame.find_conduit_id_for_spell(french_id) == target._id}")
    except Exception as error:
        print(f"    transfer refused - {type(error).__name__}: {first_line(error)}")


def main() -> None:
    """Run every case; each starts from a fresh Aether."""
    for case in (m4, m5, m6, m7):
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {first_line(error)}")
        print()
    fresh_aether()


if __name__ == "__main__":
    main()
