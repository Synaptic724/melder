# Architecture patch: find_spell_by_id_id_maps_2026_10_11

## Objective and non-goals
- Objective: `Spellbook.find_spell_by_id` answers from the Book's id maps instead of walking the live
  `_spells` map, so no concurrent bind, removal, notch, index move or transfer can make it raise
  "dictionary changed size during iteration", skip a registered spell, or raise from a concurrently cleaned
  SpellIndex - the MelderOps failures (ticket Notes 2, 7, 8).
- Non-goals: no lock on the reader path (a reader-side Book lock deadlocks conjure's phase-4 workers and
  conduit hooks, Notes 15-16); no change to bind, removal, notch, index moves or transfer; no change to
  `SpellIndex.has_spell` or the other `_spells` walkers (follow-ups R2/R3); no change to contracted lookup.

## Changed components
- Spellbook Core (`src/melder/aether/spellbook/spellbook.py`): `Spellbook.find_spell_by_id`.
- Binding Pipeline (`src/melder/aether/spellbook/spell.py`): new internal `Spell._spell_index_unless_cleaned`.

## Invariants
- A current version id resolves through `_spells_by_id` (one dict read). A superseded or parked member
  resolves through `_inactive_spells` and the parked spell's index to that index's live spell in `_spells`.
  These maps hold every version of every owned lineage: notch parks and promotes, index moves and parked
  disposal keep them in step under the Book lock, and transfer moves the whole lineage
  (`_flip_registry_and_spellbooks`, then `_migrate_inactive_members`).
- The lookup takes no Book lock and iterates no live map. The parked branch reads the index under the
  parked spell's own lock - the lock `Spell.cleanup` deletes `spell_index` under - so a spell retired
  mid-lookup answers None instead of raising.
- Answers equal the old lineage walk's except inside the windows where a writer has taken an id out of one
  map and not yet published it in the next (notch, index move, transfer between flip and migration), where
  the lookup can answer None; the walk had the same windows (fair-matrix g1 and m1).
- A returned Spell is a borrowed reference, never a lease.

## Interface deltas
- None public. `Spell._spell_index_unless_cleaned() -> Optional[SpellIndex]` is internal.
- Behaviour: `find_spell_by_id` no longer raises RuntimeError or AttributeError under concurrent changes;
  a cleaned Spellbook (RuntimeError from `check_cleaned`) is its only documented exception, as before.

## Migration order
1. Patch docs. 2. Tests (component and unit), red where they pin the old walk. 3. spellbook.py and
spell.py. 4. src_architecture, src_components and their indexes, graph descriptors. 5. Notch 0.2.8229 and
the release note. 6. Generated assets and llm_support bundles, last.

## Rollback
- Restore `find_spell_by_id`, drop `Spell._spell_index_unless_cleaned` and the two test files. No record,
  cache, spell-id or public-API change, so no data migration either way.

## Ticket coverage matrix
| patch section | ticket |
| --- | --- |
| all | tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md |
