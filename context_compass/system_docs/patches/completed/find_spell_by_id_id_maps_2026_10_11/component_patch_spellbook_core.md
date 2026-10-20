# Component patch: Spellbook Core and Spell (find_spell_by_id_id_maps_2026_10_11)

## Before / after behavior
- Before: `find_spell_by_id` walked `self._spells.items()` without a lock and asked each index
  `has_spell(spell_id)`. A concurrent bind or removal raised RuntimeError("dictionary changed size during
  iteration"); a removal plus a bind that resized the dict silently skipped the searched spell (None); an
  index cleaned after being popped raised AttributeError (`_spells_in_index`) or RuntimeError from
  `has_spell`. O(n) per call.
- After: `_spells_by_id.get(spell_id)`; on a miss `_inactive_spells.get(spell_id)`, then the parked spell's
  index through `_spell_index_unless_cleaned()`, then `_spells.get(index)`. O(1), no iteration, no Book lock.

## Interface deltas
- New internal `Spell._spell_index_unless_cleaned() -> Optional[SpellIndex]`: the spell's index, or None
  once the spell is cleaned; reads under `self._lock`.

## State and failure deltas
- No state change. Removed: RuntimeError (dict size change) and AttributeError or RuntimeError from a
  concurrently cleaned index. Kept: RuntimeError from `check_cleaned()` on a cleaned Book.
- None now also answers for a parked version retired mid-lookup, and inside the writer windows.

## Dependency and ordering
- The parked branch takes one Spell lock with no Book or index lock held and calls nothing under it.
  Parked spells are off every map meld resolves through, so no build or revalidation takes that lock; a
  unique build already running when a notch parked its spell is the one long holder found, and the lookup
  waits for it.

## Validation expectations
- Component: lineage contract (current id; superseded id after a notch; add to and remove from an index;
  transfer target and source; parked disposal; contracted and unknown ids); the live map is never iterated;
  the parked-disposal window, forced with Event handshakes, answers None without raising.
- Unit: the accessor returns the index, None after cleanup, and waits for the spell lock.
- Existing tiers and the full tree stay green with the GIL disabled; the new tests pass under both GIL modes.
