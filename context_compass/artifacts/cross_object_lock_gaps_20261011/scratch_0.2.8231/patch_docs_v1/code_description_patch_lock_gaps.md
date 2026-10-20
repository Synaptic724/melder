# Code description patch: cross-object lock gaps (cross_object_lock_gaps_2026_10_11)

## Control flow
1. Owner-side emissions: check_cleaned(); `with self._lock:` (the ward's) for the walk of self._contracts and the
   per-contract work inside it; the contract-record emissions after the lock. Inside the lock the walk takes, as
   leaves or in the established order: peer and own Book locks (ward -> Book, as link), contract locks (ward ->
   contract, as sever), IndexDetail and SpellIndex locks (leaves).
2. _contract_member_spell: `with contract._lock: added = contract._add(owner_ward, detail)`; the borrower Book call
   after the contract lock.
3. Borrower inspections: under the caller's ward lock (as today), `with contract._lock:` around the walk of that
   contract's detail map(s); resolution through the caller's Book after the contract lock is released.
4. cleanup_spell: Conduit -> Spellbook._dispose_spell: `with self._lock:` (Book) read ownership from _spells_by_id /
   _inactive_spells by identity and, when owned, the index, its id and is_sole_member; outside the lock classify a
   non-owned spell via Spell._spell_index_unless_cleaned; then the existing refusal and disposal branches; return
   the destroyed index id or None. Conduit emits _emit_index_destroy(index_id, (spell_id,)) when not None.
5. Frame sweeps: for other_name, other_frame in list(self._aetheric_frames.items()); probes take the frame lock and
   answer from the registries, or False / None / set() when _cleaned.

## Edge semantics
A link or sever of the owner waits for an emission in flight; a borrower inspection waits for a contract write in
flight. Lock orders: no path takes a ward lock while holding a Book, contract, index or frame lock (spellbook.py
never takes one; contract methods never take one), so ward-first nesting cannot close a cycle.

## Non-goals
No transaction for cleanup_spell; no change to the index-move seams; no cache format change.
