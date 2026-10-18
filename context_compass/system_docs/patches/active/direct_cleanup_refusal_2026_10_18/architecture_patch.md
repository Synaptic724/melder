# Architecture patch: direct_cleanup_refusal_2026_10_18

## Objective and non-goals
- Objective: no public way of disposing a version leaves a parked version on a cleaned index.
  `Conduit.cleanup_spell` already refuses the active member of an index that also holds parked versions ("notch away
  from it first"); the two other public doors - a direct `Spell.cleanup()` and `Spellbook.cleanup_and_remove_spell`
  - clean the index under its parked versions, which no later call can repair (probe D2 and D3, on 0.2.8252 and
  0.2.8255): a notch to such a version raises AttributeError, moving or disposing it raises "SpellIndex has already
  been cleaned.", the Book's teardown leaves it and its own `cleanup()` then raises.
- Non-goals: index-link borrowers on the direct route (it sends no ward emission; pre-existing, recorded in the
  correctness epic's A1 note); parked versions at Book teardown (STORY-2026-10-17-book_teardown_leaves_parked_
  versions_uncleaned, S7); retiring a whole lineage through a direct removal (the owner's alternative, not taken).

## Changed components
- Spellbook, the removal path: `Spellbook.cleanup_and_remove_spell` refuses the active member of a multi-member index
  before anything is unregistered, with the check `_dispose_spell` makes.
- Docstrings only: `Spell.cleanup` (its Raises lists the new refusal).

## Invariants
- A removal through `cleanup_and_remove_spell` - called directly, or from a direct `Spell.cleanup()` - leaves no
  parked version on a cleaned index: the active member of an index holding other members is refused with nothing
  changed; the sole member of an index is removed as today, with its index.
- The routes the Book drives keep their paths: `cleanup_spell` (`_dispose_spell` reaches the method only for an
  active sole member), Book teardown and the parked disposal (both set `_spellbook_cleanup`, so their
  `Spell.cleanup()` never routes here), Bind's retirement of an unpublished spell.
- The check runs in the method's first Book-locked section, before `unregister_index`; it takes the index's own lock
  inside the Book lock (Book -> index), the order `_dispose_spell` takes. No new lock or lock-order edge.

## Interface deltas
- Public behaviour, **Breaking:** `Spellbook.cleanup_and_remove_spell(spell)` and a direct `Spell.cleanup()` of the
  active member of an index that holds parked versions raise RuntimeError "Spellbook cannot remove spell <id>: it
  is the active member of a multi-member index; notch away from it before disposing it, or dispose the index's
  parked versions first with cleanup_spell." and change nothing. Signatures are unchanged. The message names no
  door, because `cleanup_spell` can meet it too (component patch, State and failure deltas).

## Migration order
1. These patch docs, linked from the story; the owner's word on the exact edits. 2. spellbook.py (held, M1-33) and
spell.py claimed from melder_0 by message. 3. Red tests. 4. The code and the two docstrings. 5. The tests, GIL off
and on; probe D1-D3 re-run. 6. System documents with their indexes, the graph, the release note; the next free
notch. 7. Closure; the rebuild last.

## Rollback
- Remove the check: the direct doors clean the index under its parked versions again. Nothing persisted, cached or
  emitted changes, so no cache generation or record version moves either way.

## Ticket coverage matrix
| patch section | ticket |
| --- | --- |
| all | tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md |
