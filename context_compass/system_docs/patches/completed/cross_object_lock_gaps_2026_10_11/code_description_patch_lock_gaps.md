# Code description patch: cross-object lock gaps (cross_object_lock_gaps_2026_10_11)

## Control flow
1. Owner-side emissions: `check_cleaned()`; `with self._lock:` (the ward's) for the walk of `self._contracts` and the
   per-contract work inside it - IndexDetail updates, `contract._lock` around detail removals, peer Book calls
   (`_inactivate_contract_spell`, `_ensure_contracted_active`, `_remove_contracted_index`), `_contract_member_spell` /
   `_uncontract_member_spell`; contract records emitted after the ward lock.
2. `_contract_member_spell`: `with contract._lock: added = contract._add(owner_ward, detail)`; the borrower Book call
   after the contract lock.
3. `_get_spell_in_contracts`: under the caller's ward lock (as before), `with contract._lock:` read
   `detail_map.get(spell_id)` and, when it does not hold the id, walk the map's Details with `has_spell`; release;
   resolve the matched index through `Spellbook._find_contracted_spell`.
4. `_get_spells_in_contract_by_conduit`: under the ward lock, `with contract._lock:` iterate the peer's detail map
   resolving each id with `_find_contracted_spell_by_id(sid, peer_ward._id)`, then this ward's map resolving each id
   with `find_spell_by_id(sid)`.
5. `Spellbook._find_contracted_spell_by_id`: `_contracted_spells_by_id[conduit_id].get(spell_id)`; else the parked copy
   in `_inactive_contracted_spells[conduit_id]`, its index through `_spell_index_unless_cleaned()`, and
   `_contracted_spells[conduit_id].get(index)`; else the 0.2.8230 walk.
6. `cleanup_spell`: Conduit -> `Spellbook._dispose_spell`: `with self._lock:` (Book) read ownership from
   `_spells_by_id` / `_inactive_spells` by identity and, when owned, the index, its id and `is_sole_member`; outside
   the lock classify a non-owned spell through `Spell._spell_index_unless_cleaned`; then the existing refusal and
   disposal branches; return the destroyed index id or None. The Conduit emits
   `_emit_index_destroy(index_id, (spell_id,))` when not None.
7. Frame sweeps: `frames = self._aetheric_frame_view`; `if len(frames) <= 1`; `for other_name, other_frame in frames`;
   probes take the frame lock once and answer from the registries, or False / None / set() when `_cleaned`.

## Edge semantics
A link or sever of the owner waits for an emission in flight; a borrower read waits for a contract write in flight;
neither path calls user code under the new locks. Lock orders: ward -> contract -> {Book, spell, Detail, SpellIndex}
(as sever), ward -> Book (as link), frame -> SpellIndex (as find_index_for_spell), frame -> Aether (cleanup's detach).
spellbook.py takes no ward or contract lock, contract, Detail, SpellIndex and Spell code take only their own lock, and
none of the Book helpers the emissions and contract reads call reaches the Aether or a frame - so frame teardown,
which takes ward locks under its frame lock, closes no cycle with them. The listing's conduit-lock call was the one
inverted edge (ward -> conduit against link and sever's conduit -> ward) and is gone.

## Invariants / idempotency
cleanup_spell stays non-idempotent by contract (a second call raises, now RuntimeError); the emissions are unchanged
in what they write; the frame view is replaced whole on every registry write, never mutated.

## Non-goals
No transaction for cleanup_spell; no change to the index-move seams; no cache or record format change; the 0.2.8230
snapshots are not reworked.
