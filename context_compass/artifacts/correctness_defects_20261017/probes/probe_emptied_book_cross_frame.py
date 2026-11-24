"""Probe (melder_0, 2026-11-24; EPIC-2026-10-17-correctness_defects, item C1, task #343): which duplicate checks
besides the same-frame bind check miss the spell ids of a Book `cleanup_spell` emptied?

The frame's link to a Book's spell-id set backs four reads (`has_spell`, `spells_in_index` and their two
`_unless_cleaned` forms). Aether's bind check (`_check_for_spell`) asks the Book's frame through `has_spell` and,
under process-wide spell ids (the default), every other frame through `_has_spell_unless_cleaned`; a conjure's
integrity check (`Spellbook._spell_id_integrity_checker`) unions the frames' ids through `_get_all_spell_ids`.
Each case runs in its own process, frames dynamic with caching off:
  X1  Book A of frame xf-one is emptied by `cleanup_spell` and binds XShared; Book C of frame xf-two, conjured,
      binds XShared too.
  X2  control: as X1, but A keeps XKeep, so the cleanup does not empty it.
  X3  Book A is emptied and binds XShared; Book D of the same frame binds XShared before its conjure, then
      conjures - does the conjure's integrity check refuse it?
The registry read is internal, for the diagnosis only; the outcomes are public `bind` and `conjure` calls.

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_emptied_book_cross_frame.py X1
"""
import sys
from typing import Any, Callable

from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class XFirst:
    """Book A's spell, cleaned up to empty A (or not, in X2)."""


class XKeep:
    """X2: keeps Book A non-empty."""


class XShared:
    """Bound by Book A after the cleanup, then by a second Book."""


def book(frame: str) -> Spellbook:
    """Build a Spellbook in a dynamic frame with the creation cache off (no files written)."""
    spellbook = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    spellbook.configure_aether_frame(
        system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
    )
    return spellbook


def empty_book_a(keep: bool) -> Spellbook:
    """Conjure Book A in frame xf-one, bind XFirst (and XKeep), clean XFirst up, then bind XShared."""
    book_a = book("xf-one")
    root = book_a.conjure(dynamic=True, name="xf-one-root")
    if keep:
        book_a.bind(spell=XKeep, existence=Existence.many)
    book_a.bind(spell=XFirst, existence=Existence.many)
    root.cleanup_spell(spell=book_a.find_spell_by_spell_id(Bind.spell_id_inspector(XFirst)))
    book_a.bind(spell=XShared, existence=Existence.many)
    linked = root.id in Spellbook._aether._aetheric_frames["xf-one"]._selected_spell_registry
    print(f"Book A holds {len(book_a._spell_ids)} spell(s); frame xf-one keeps its spell-id link: {linked}")
    return book_a


def attempt(label: str, action: Callable[[], Any]) -> None:
    """Run a zero-argument call and print whether it went through or what it raised."""
    try:
        action()
        print(f"{label}: went through")
    except Exception as error:
        print(f"{label}: {type(error).__name__}: {str(error)[:110]} ...")


def run(case: str) -> None:
    """Run one case."""
    print(f"--- {case}")
    print("process-wide spell ids:", Spellbook._aether.process_wide_unique_spell_ids)
    if case in ("X1", "X2"):
        empty_book_a(keep=case == "X2")
        book_c = book("xf-two")
        book_c.conjure(dynamic=True, name="xf-two-root")
        attempt("Book C of frame xf-two binds XShared", lambda: book_c.bind(spell=XShared, existence=Existence.many))
        return
    empty_book_a(keep=False)
    book_d = Spellbook(aetheric_frame="xf-one")
    attempt("Book D of frame xf-one binds XShared before its conjure",
            lambda: book_d.bind(spell=XShared, existence=Existence.many))
    attempt("Book D conjures", lambda: book_d.conjure(dynamic=True, name="xf-one-d-root"))


run(sys.argv[1])
