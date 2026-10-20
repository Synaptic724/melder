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
  versions_uncleaned, S7); retiring a whole lineage through a direct removal (the owner's alternative, not taken);
  an index kept alive with parked versions and nothing active (the hole rule, weighed and not taken by the owner on
  2026-10-18; the story's DECISION and TRADEOFF notes).

## Changed components
- Spellbook, the removal path: `Spellbook.cleanup_and_remove_spell` refuses the active member of a multi-member index
  before anything is unregistered, with the check `_dispose_spell` makes.
- Spellbook, `cleanup_spell`'s refusal (`_dispose_spell`): its message is reworded to name the same remedies; when
  and what it refuses is unchanged.
- Docstrings only: `Spell.cleanup` (its Raises lists the new refusal) and `Spellbook.cleanup_spell` (its Contract
  names the remedies).

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
  is the active member of a multi-member index, and disposing it would leave the index's parked versions without an
  active one. Notch the index to one of them, dispose them with cleanup_spell, or move them out with
  remove_from_spell_index first." and change nothing. Signatures are unchanged. The message names no door, because
  `cleanup_spell` can meet it too (component patch, State and failure deltas).
- Public behaviour: `cleanup_spell`'s refusal of the same member keeps its type and its moment and names the same
  remedies: "cleanup_spell: spell <id> is the active member of a multi-member index, and disposing it would leave
  the index's parked versions without an active one. Notch the index to one of them, dispose them with
  cleanup_spell, or move them out with remove_from_spell_index first." (it said "...; notch away from it before
  disposing it.").

## Migration order
1. These patch docs, linked from the story; the owner's word on the exact edits. 2. spellbook.py and spell.py held
(M1-33, M0-195), S9 landing before S1 (M1-37). 3. Red tests. 4. The code, the reworded message and the three
docstrings. 5. The tests, GIL off and on; probe D1-D3 re-run. 6. System documents with their indexes, the graph, the
release note; the next free notch. 7. Closure; the rebuild last; the two files handed back to melder_0.

## Rollback
- Remove the check and restore `_dispose_spell`'s old wording: the direct doors clean the index under its parked
  versions again. Nothing persisted, cached or emitted changes, so no cache generation or record version moves
  either way.

## Ticket coverage matrix
| patch section | ticket |
| --- | --- |
| all | tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md |
