# Architecture patch: cross_object_lock_gaps_2026_10_11

## Objective
Close three cross-object lock gaps proven after 0.2.8230, where a reader and a writer of one map are guarded by
different locks or by none: the owner-side index emissions over a ward's contract registry, the borrower-side
contract inspections over a contract's detail maps, and bind's cross-frame duplicate sweep over Aether's frame
registry; and make Conduit.cleanup_spell read its spell under the spell's own lock and emit the index destroy
exactly when the Spellbook destroyed the index. Ticket: tickets/tasks/2026-10-11_prove_and_fix_cross_object_lock_gaps_task.md.

## Non-goals
- No new transaction type: cleanup_spell stays unsealed (sealing it is a larger, separate change).
- No lock-order edge of a new kind; no change to what any operation returns on a quiet world.
- The Spellbook-internal window between cleanup_spell's locked decision and its disposal, against a concurrent
  index move into the same index, stays as it is (recorded as a residual).

## Changed components
- ConduitWard and Contracts: _emit_index_notch, _emit_index_destroy, _emit_index_member_added and
  _emit_index_member_removed walk the contract registry under the ward's own lock; _contract_member_spell writes its
  Detail under the contract lock; _get_spell_in_contracts and _get_spells_in_contract_by_conduit walk a contract's
  detail maps under that contract's lock.
- Conduit Runtime and Spellbook Core: Conduit.cleanup_spell no longer pre-reads the spell and its index; the new
  internal Spellbook._dispose_spell (the body of cleanup_spell) decides under the Book lock and returns the id of
  the index it destroyed, and a spell already disposed raises a documented RuntimeError.
- Aether Singleton and AethericFrame Services: Aether._check_for_spell and _get_all_spell_ids walk a one-call
  snapshot of the frame registry and probe other frames through new cleanup-safe AethericFrame probes;
  AethericFrame.has_spell and spells_in_index re-check cleaned under the frame lock.

## Invariants
1. Every walk of a ward's _contracts holds that ward's lock, the lock link (_create_new_contract) and sever
   (_remove_contract) write it under; the owner-side emissions therefore never meet a link or sever mid-walk,
   whether or not a transaction window is open.
2. Every walk of a contract's detail map holds that contract's lock, and every write of it holds the same lock.
3. Conduit.cleanup_spell emits the index destroy if and only if the Spellbook's disposal destroyed the index; a
   spell already disposed raises RuntimeError "cleanup_spell: spell <id> has already been disposed.", never
   AttributeError.
4. Bind's cross-frame sweep (and _get_all_spell_ids) never fails because a frame is born or torn down: it walks a
   snapshot and treats a frame that reads cleaned as holding nothing.
5. Lock order stays ward -> contract -> Book and ward -> Book (what sever and link already take); a SpellIndex,
   IndexDetail or frame lock is only ever a leaf under them.

## Interface deltas
- New internal: Spellbook._dispose_spell(spell) -> Optional[str]; AethericFrame._has_spell_unless_cleaned(spell_id)
  -> bool, _find_index_for_spell_unless_cleaned(spell_id) -> Optional[SpellIndex],
  _spells_in_index_unless_cleaned() -> set[str].
- Public behaviour: Spellbook.cleanup_spell and Conduit.cleanup_spell raise RuntimeError instead of AttributeError
  for a spell already disposed; AethericFrame.has_spell and spells_in_index raise their documented RuntimeError
  instead of AttributeError when cleanup races the call. No signature changes.

## Migration order
Tests (red where reproducible) -> src -> component docs -> architecture doc and indexes -> graph -> notch and
release note -> assets and llm_support last.

## Rollback
Revert the src files of the change set; no data, cache or record format changes (no cache generation moves).

## Coverage matrix
| invariant | test |
| --- | --- |
| 1 | cleanup_spell and notch_spell paused mid-emission while owner.link(C) runs: the link waits, no error, every borrower consistent (component) |
| 2 | get_spell_in_contracts paused mid-walk while the owner stages a member: the staging waits, no error (component) |
| 3 | second cleanup_spell of a disposed spell -> RuntimeError naming it (component) |
| 4 | bind paused in its sweep while a frame is born, and while a frame is cleaned: bind succeeds (component); frame probes on a cleaned frame (unit) |
| 5 | full tree on -X gil=0 with no hang; the orders are read off the code in the code description |
