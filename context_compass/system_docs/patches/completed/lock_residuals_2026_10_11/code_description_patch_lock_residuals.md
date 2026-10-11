# Code description patch: lock residuals (lock_residuals_2026_10_11)

## Control flow
1. `Conduit.find_contracted_spell(spell_id)`: `check_cleaned()`; `spellbook = self._spellbook`; for each id in
   `list(spellbook._contracted_spells)`: `spellbook._find_contracted_spell_by_id(spell_id, id)`; first hit returned;
   else None.
2. `Conduit.inspect_spell`: `check_cleaned()`; `return self._spellbook.inspect_spell(spell, aetheric_frame)`.
3. `Spellbook.inspect_spell`: try: `with self._lock:` scan `self._spells.values()` by identity, remember
   `matched` and the selected id; on a match return the id when `_check_for_spell` confirms it, else None. Otherwise
   resolve the frame, walk `list(frame._conduits.values())`, skip None and self Books, walk
   `list(book._spells.values())` by identity, confirm through `_check_for_spell`; else the fingerprint fallback.
   except: log, None.
4. `Spellbook._dispose_spell(spell)`: `check_cleaned()`; `with self._lock:` if the id is in `_disposing_spell_ids`
   note it; else read ownership, index, index id, sole membership as before and, when owned and not (active and not
   sole), add the id. Outside: raise the overlap RuntimeError if noted; the not-owned classification and the
   multi-member refusal as before; `try:` the unchanged active / inactive branches `finally: with self._lock:`
   discard the id.

## Edge semantics
The overlap refusal happens before invalidation, so the late call changes nothing. A call after the first finished
finds the spell gone and raises "has already been disposed." as in 0.2.8231. A failed disposal clears its mark, so a
retry runs. `find_contracted_spell` and stage 2 of `inspect_spell` may miss, or still see, a peer, root or spell added
or removed during the call. No lock is held while user code or another object's lock is taken in these paths.

## Invariants / idempotency
cleanup_spell stays non-idempotent (a later call raises). The mark set holds an id only while that id's disposal
runs. Lookups stay pure reads.

## Non-goals
No transaction for cleanup_spell, no spell lock across the disposal, no change to `Spell.cleanup`'s direct path, to
the index-move seams, or to any cache or record format.
