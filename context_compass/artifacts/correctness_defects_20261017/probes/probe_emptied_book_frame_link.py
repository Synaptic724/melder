"""Probe (melder_0, 2026-11-24; EPIC-2026-10-17-correctness_defects, item C1, task #343): does the frame lose the
spell ids a Book binds after `cleanup_spell` has removed that Book's last spell?

Cases, each in its own dynamic frame with caching off and classes of their own, so no spell_id is shared between
cases (a spell_id is the class's code, its name included):
  E1  emptied: Book A binds EmptiedFirst, then `cleanup_spell(EmptiedFirst)` leaves A with no spell; A binds
      EmptiedSecond; Book B of the same frame binds EmptiedSecond too.
  E2  control: as E1, but A also holds ControlKeep, so `cleanup_spell(ControlFirst)` does not empty it; B binds
      ControlSecond.
For each: whether the frame still registers A's root conduit in its index registry (`_spell_registry`) and its
spell-id link (`_selected_spell_registry`, the live reference to A's `_spell_ids`), whether the frame's spell-id
lookup (`Aether._check_for_spell`, the cross-Book duplicate check bind runs) finds A's later spell, and whether Book
B's bind of that same class is refused with "Spell ID collision detected". The registry reads are internal, for the
diagnosis only; the outcome is the public `bind` call.

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_emptied_book_frame_link.py
"""
from typing import Optional

from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class EmptiedFirst:
    """E1: Book A's only spell, cleaned up to empty A."""


class EmptiedSecond:
    """E1: bound by the emptied Book A, then by Book B of the same frame."""


class ControlKeep:
    """E2: keeps the control Book non-empty."""


class ControlFirst:
    """E2: cleaned up while ControlKeep stays."""


class ControlSecond:
    """E2: bound by Book A, then by Book B of the same frame."""


def book(frame: str) -> Spellbook:
    """Build a Spellbook in its own dynamic frame with the creation cache off (no files written)."""
    spellbook = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    spellbook.configure_aether_frame(
        system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
    )
    return spellbook


def frame_view(frame: str, conduit_id: str) -> str:
    """Report whether the frame registers the conduit's index set and its spell-id link (internal reads)."""
    aetheric_frame = Spellbook._aether._aetheric_frames[frame]
    return (f"index set registered={conduit_id in aetheric_frame._spell_registry}, "
            f"spell-id link registered={conduit_id in aetheric_frame._selected_spell_registry}")


def run(frame: str, keep: Optional[type], first: type, second: type) -> None:
    """Run one case: bind `first` (and `keep`), clean up `first`, bind `second`, then bind `second` in Book B."""
    label = "A is emptied by cleanup_spell" if keep is None else "control, A keeps a spell"
    print(f"--- {frame}: {label}")
    book_a = book(frame)
    root = book_a.conjure(dynamic=True, name=f"{frame}-root")
    if keep is not None:
        book_a.bind(spell=keep, existence=Existence.many)
    book_a.bind(spell=first, existence=Existence.many)
    print(f"after binding {first.__name__}:", frame_view(frame, root.id))
    root.cleanup_spell(spell=book_a.find_spell_by_spell_id(Bind.spell_id_inspector(first)))
    print(f"after cleanup_spell({first.__name__}): Book A holds {len(book_a._spell_ids)} spell(s);",
          frame_view(frame, root.id))
    book_a.bind(spell=second, existence=Existence.many)
    print(f"after A binds {second.__name__}:", frame_view(frame, root.id))
    found = Spellbook._aether._check_for_spell(Bind.spell_id_inspector(second), frame) is not None
    print(f"frame finds {second.__name__}'s spell_id:", found)
    book_b = Spellbook(aetheric_frame=frame)
    try:
        book_b.bind(spell=second, existence=Existence.many)
        print(f"Book B binds {second.__name__} too: TWO spells for one object (refusal missing)")
    except RuntimeError as error:
        print("Book B refused:", str(error)[:90], "...")
    finally:
        book_b.cleanup()


run("probe-emptied", None, EmptiedFirst, EmptiedSecond)
run("probe-control", ControlKeep, ControlFirst, ControlSecond)
