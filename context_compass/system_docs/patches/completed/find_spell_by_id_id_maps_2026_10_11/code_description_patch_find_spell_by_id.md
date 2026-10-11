# Code description patch: find_spell_by_id (find_spell_by_id_id_maps_2026_10_11)

## Control flow
1. `check_cleaned()`.
2. `spell = self._spells_by_id.get(spell_id)`; return it when present (the active version).
3. `parked = self._inactive_spells.get(spell_id)`; None -> return None (no version this Book owns).
4. `spell_index = parked._spell_index_unless_cleaned()`; None -> return None (retired concurrently).
5. Return `self._spells.get(spell_index)`: the index's live spell, or None when the index has no active
   member (a fresh index from remove_from_index, or one mid-notch or destroyed).

## Edge and error semantics
- Each step is one dict read, atomic under CPython's per-object locking on the free-threaded build.
- SpellIndex hash and equality survive cleanup, so step 5 is safe for a destroyed index.
- A lookup racing Book teardown fails as before (the maps are deleted after `_cleaned` is set).

## Invariants and idempotency
- Pure lookup: creates, registers and mutates nothing.

## Explicit non-goals
- Contracted spells are not consulted (unchanged). No linearizability across the writer windows.
