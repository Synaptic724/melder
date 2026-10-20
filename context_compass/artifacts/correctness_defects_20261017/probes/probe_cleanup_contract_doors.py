"""Probe (melder_0, 2026-10-19; S3 of EPIC-2026-10-17-correctness_defects): which contracts keep a version the
lender cleans up, by contract kind and by cleanup door, on the current tree - before S3's fix is written.

Each case runs in a fresh Aether with its own dynamic frame, caching off. The lender binds English active on an
index (French staged parked on it where the case needs a parked version); the borrower links to the lender.
  K1  index link, the lender's `Conduit.cleanup_spell(French)` (French parked, English keeps the index).
  K2  version grant of French (parked; `add_spell_to_contract`), the lender's `Conduit.cleanup_spell(French)`.
  K3  version grant of Solo (the sole, active member of its own index), the lender's `Conduit.cleanup_spell(Solo)`.
  K4  index link, the direct `Spellbook.cleanup_spell(French)`.
  K5  index link on Solo's index, the direct `Spellbook.cleanup_spell(Solo)` (the index goes with it).
  K6  index link, a direct `French.cleanup()`.
  K7  index link, `cleanup_spell(French)` through a lesser conduit of the lender.
For each case it prints what the borrower Book holds for the lender (active, parked, borrowed ids, tracked
indexes) and the lender-side contract details, before and after the cleanup.

Read-only on src/: run from the folder above with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_cleanup_contract_doors.py
"""
from typing import Callable, Dict, Protocol, Tuple

from melder.__version__ import __version__
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Greeter(Protocol):
    """The contract the versions implement."""

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


class Solo:
    """The sole member of its own index."""

    def ping(self) -> str:
        """Return a marker."""
        return "solo"


class Note:
    """A plain spell so the borrower Book has something to conjure."""


def fresh_aether() -> None:
    """Install a fresh Aether and rebind it on Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def world(frame: str) -> Tuple[Spellbook, Spellbook, Conduit, Conduit, Dict[str, str]]:
    """The lender with English active, French parked on its index and Solo alone in its own; the borrower linked."""
    lender_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    lender_book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                      system_caching_enabled=False)
    borrower_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    english_id = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter",
                                  existence=Existence.many, permissions="create")
    solo_id = lender_book.bind(spell=Solo, binding_name="solo", existence=Existence.many, permissions="create")
    borrower_book.bind(spell=Note, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    index = lender_book.find_spell_by_spell_id(english_id).spell_index
    french_id = lender.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="greeter",
                                     existence=Existence.many, permissions="create")
    lender.link(borrower)
    ids = {"English": english_id, "French": french_id, "Solo": solo_id}
    return lender_book, borrower_book, lender, borrower, ids


def index_link(lender_book: Spellbook, lender: Conduit, borrower: Conduit, spell_id: str) -> None:
    """The borrower contracts the whole index of `spell_id`."""
    index = lender_book.find_spell_by_spell_id(spell_id).spell_index
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")


def grant(lender_book: Spellbook, lender: Conduit, borrower: Conduit, spell_id: str, frame: str) -> None:
    """The borrower contracts one version by its Spell object (a version grant)."""
    spell = lender_book.find_spell_by_spell_id(spell_id)
    with borrower.transaction("link", conduits=[borrower, lender]):
        result = borrower.add_spell_to_contract(spell=spell, conduit=lender, permissions="create",
                                                aetheric_frame=frame)
    print(f"    borrower.add_spell_to_contract({spell.spell_name}) -> {result}")


def show(step: str, borrower_book: Spellbook, borrower: Conduit, lender: Conduit, ids: Dict[str, str]) -> None:
    """Print what the borrower holds for the lender and the lender-side details of the contract."""
    names = {value: key for key, value in ids.items()}
    active = borrower_book._contracted_spells_by_id.get(lender._id, {})
    parked = borrower_book._inactive_contracted_spells.get(lender._id, {})
    borrowed = borrower_book._contracted_spell_ids.get(lender._id, set())
    print(f"  [{step}]")
    print("    borrower active entries: "
          f"{sorted((names.get(i, i[:10]), 'cleaned' if s._cleaned else 'live') for i, s in active.items())}")
    print("    borrower parked entries: "
          f"{sorted((names.get(i, i[:10]), 'cleaned' if s._cleaned else 'live') for i, s in parked.items())}")
    print(f"    borrower borrowed ids: {sorted(names.get(i, i[:10]) for i in borrowed)}")
    print(f"    borrower tracked indexes: {len(borrower_book._contracted_indexes)}")
    contract = borrower._conduit_ward._find_contract_by_id(lender._id)
    if contract is None:
        print("    contract: none")
        return
    ward = lender._conduit_ward
    details = sorted(name for name, spell_id in ids.items() if contract._check_if_exists(ward, spell_id))
    index_details = len(contract._get_index_detail_map(ward))
    print(f"    lender-side details: {details}; index details: {index_details}")


def k1(frame: str) -> None:
    """Index link; the lender's Conduit.cleanup_spell of parked French."""
    lender_book, borrower_book, lender, borrower, ids = world(frame)
    index_link(lender_book, lender, borrower, ids["English"])
    show("index link", borrower_book, borrower, lender, ids)
    lender.cleanup_spell(spell=lender_book.find_spell_by_spell_id(ids["French"]))
    show("after lender.cleanup_spell(French)", borrower_book, borrower, lender, ids)


def k2(frame: str) -> None:
    """Version grant of parked French; the lender's Conduit.cleanup_spell of French."""
    lender_book, borrower_book, lender, borrower, ids = world(frame)
    grant(lender_book, lender, borrower, ids["French"], frame)
    show("grant of French", borrower_book, borrower, lender, ids)
    lender.cleanup_spell(spell=lender_book.find_spell_by_spell_id(ids["French"]))
    show("after lender.cleanup_spell(French)", borrower_book, borrower, lender, ids)


def k3(frame: str) -> None:
    """Version grant of Solo, the sole active member of its index; the lender's Conduit.cleanup_spell of Solo."""
    lender_book, borrower_book, lender, borrower, ids = world(frame)
    grant(lender_book, lender, borrower, ids["Solo"], frame)
    show("grant of Solo", borrower_book, borrower, lender, ids)
    lender.cleanup_spell(spell=lender_book.find_spell_by_spell_id(ids["Solo"]))
    show("after lender.cleanup_spell(Solo)", borrower_book, borrower, lender, ids)
    try:
        made = borrower.meld(spell_id=ids["Solo"])
        print(f"    borrower.meld(Solo) -> {type(made).__name__}")
    except Exception as error:
        print(f"    borrower.meld(Solo) raised {type(error).__name__}: {str(error)[:160]}")


def k4(frame: str) -> None:
    """Index link; the direct Spellbook.cleanup_spell of parked French."""
    lender_book, borrower_book, lender, borrower, ids = world(frame)
    index_link(lender_book, lender, borrower, ids["English"])
    lender_book.cleanup_spell(spell=lender_book.find_spell_by_spell_id(ids["French"]))
    show("after lender_book.cleanup_spell(French)", borrower_book, borrower, lender, ids)


def k5(frame: str) -> None:
    """Index link on Solo's index; the direct Spellbook.cleanup_spell of Solo (the index goes)."""
    lender_book, borrower_book, lender, borrower, ids = world(frame)
    index_link(lender_book, lender, borrower, ids["Solo"])
    show("index link on Solo's index", borrower_book, borrower, lender, ids)
    lender_book.cleanup_spell(spell=lender_book.find_spell_by_spell_id(ids["Solo"]))
    show("after lender_book.cleanup_spell(Solo)", borrower_book, borrower, lender, ids)


def k6(frame: str) -> None:
    """Index link; a direct French.cleanup()."""
    lender_book, borrower_book, lender, borrower, ids = world(frame)
    index_link(lender_book, lender, borrower, ids["English"])
    french = lender_book.find_spell_by_spell_id(ids["French"])
    try:
        french.cleanup()
        print(f"    French.cleanup() -> done; French cleaned: {french._cleaned}")
    except Exception as error:
        print(f"    French.cleanup() raised {type(error).__name__}: {str(error)[:200]}")
    show("after French.cleanup()", borrower_book, borrower, lender, ids)


def k7(frame: str) -> None:
    """Index link; Conduit.cleanup_spell of parked French through a lesser conduit of the lender."""
    lender_book, borrower_book, lender, borrower, ids = world(frame)
    index_link(lender_book, lender, borrower, ids["English"])
    lesser = lender.create_lesser_conduit()
    try:
        lesser.cleanup_spell(spell=lender_book.find_spell_by_spell_id(ids["French"]))
        print("    lesser.cleanup_spell(French) -> done")
    except Exception as error:
        print(f"    lesser.cleanup_spell(French) raised {type(error).__name__}: {str(error)[:200]}")
    show("after lesser.cleanup_spell(French)", borrower_book, borrower, lender, ids)


def main() -> None:
    """Run every case in its own fresh Aether."""
    print(f"melder {__version__}")
    cases: Tuple[Tuple[str, str, Callable[[str], None]], ...] = (
        ("k1", "K1 index link, lender.cleanup_spell(French parked)", k1),
        ("k2", "K2 version grant of French (parked), lender.cleanup_spell(French)", k2),
        ("k3", "K3 version grant of Solo (sole active member), lender.cleanup_spell(Solo)", k3),
        ("k4", "K4 index link, direct lender_book.cleanup_spell(French)", k4),
        ("k5", "K5 index link on Solo's index, direct lender_book.cleanup_spell(Solo)", k5),
        ("k6", "K6 index link, direct French.cleanup()", k6),
        ("k7", "K7 index link, lesser.cleanup_spell(French)", k7),
    )
    for frame, title, case in cases:
        fresh_aether()
        print(title)
        try:
            case(frame)
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {str(error)[:300]}")
        print()
    fresh_aether()


if __name__ == "__main__":
    main()
