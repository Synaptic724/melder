# Architecture patch: cross_object_lock_gaps_2026_10_11

## Objective
Close the cross-object lock gaps proven after 0.2.8230, where the reader and the writer of one map are guarded by
different locks or by none: (a) the owner-side index emissions over a ward's contract registry, (b) the
borrower-side contract reads over a contract's detail maps, (c) bind's cross-frame duplicate sweep over Aether's frame
registry, and (c2) the frame's cached-id read over each conjured Book's live id set. Make Conduit.cleanup_spell decide
under the Book lock and emit the index destroy exactly when the Spellbook destroyed the index, and remove the deadlock
between the contract listing and link/sever found on the way. Rule (owner direction, 2026-10-11): a reader answers by
key or holds the writers' lock; where neither is possible, the writers publish an immutable view on their rare write
and readers take it in one read - no per-call copy where an O(1) read exists. Ticket:
tickets/tasks/2026-10-11_prove_and_fix_cross_object_lock_gaps_task.md (Notes 1-11).

## Non-goals
- No new transaction type: cleanup_spell stays unsealed (sealing it is a larger, separate change).
- No new kind of lock-order edge; no change to what any operation returns on a quiet world.
- The 0.2.8230 snapshots (the book-wide phase factories and cleanup pass, inspect_spell over another Book, the transfer
  impact walk, the fallback walk of Spellbook._find_contracted_spell_by_id) are not reworked here.
- Residuals left as they are: the Spellbook-internal window between cleanup_spell's locked decision and its disposal
  against a concurrent index move into the same index; Conduit.find_contracted_spell's live walk of the contracted
  map under the conduit lock.

## Changed components
- ConduitWard and Contracts: the four owner-side emissions walk the contract registry under the ward lock;
  _contract_member_spell writes its Detail under the contract lock; _get_spell_in_contracts walks a contract's detail
  maps under that contract's lock and tries the detail keyed by the id first; _get_spells_in_contract_by_conduit walks
  under the contract lock and resolves ids through this conduit's Book (inbound `_find_contracted_spell_by_id`,
  outbound `find_spell_by_id`), never through the Conduit lookups, which take the conduit lock.
- Spellbook Core: `_find_contracted_spell_by_id` answers by key before its 0.2.8230 walk (the active borrowed copy by
  its version id; a parked copy's index keys the lineage's active copy); the new internal `_dispose_spell` is
  cleanup_spell's body and returns the id of the index it destroyed.
- Conduit Runtime: cleanup_spell no longer pre-reads the spell and its index; it emits the destroy `_dispose_spell`
  reports.
- Aether Singleton: an immutable `(name, frame)` view of the frame registry, republished under the Aether lock by
  frame birth, detach and teardown; both sweeps read it.
- AethericFrame Services: cleanup-safe probes for the sweeps; has_spell and spells_in_index re-check cleaned under the
  frame lock; spells_in_index takes each Book's set with one update call; cleanup keeps `_lock`.

## Invariants
1. Every walk of a ward's `_contracts` holds that ward's lock, the lock link (`_create_new_contract`) and sever
   (`_remove_contract`) write it under, whether or not a transaction window is open.
2. Every walk of a contract's detail map holds that contract's lock, and every write of it holds the same lock.
3. A contract read answers by key where the key is known and takes no conduit lock under the ward lock.
4. Conduit.cleanup_spell emits the index destroy if and only if the Spellbook's disposal destroyed the index; a spell
   already disposed raises RuntimeError "cleanup_spell: spell <id> has already been disposed.", never AttributeError.
5. Bind's cross-frame sweep and `_get_all_spell_ids` never fail because a frame is born or torn down, and copy nothing
   per call: they read the published frame view and ask each other frame through probes that answer a cleaned frame
   as holding nothing.
6. A frame read of a Book's live `_spell_ids` takes the set with one call (`in`, `set.update`), never element by
   element.
7. Lock orders: ward -> contract -> {Book, spell, Detail, SpellIndex} (as sever); ward -> Book (as link); frame ->
   SpellIndex (as find_index_for_spell); frame -> Aether (cleanup's detach). Nothing this patch runs under a ward
   lock (the emission bodies, the contract reads) takes a conduit, frame or Aether lock, so frame teardown taking
   ward locks under its frame lock closes no cycle with them.

## Interface deltas
- New internal: `Spellbook._dispose_spell(spell) -> Optional[str]`; `AethericFrame._has_spell_unless_cleaned(spell_id)
  -> bool`, `_find_index_for_spell_unless_cleaned(spell_id) -> Optional[SpellIndex]`,
  `_spells_in_index_unless_cleaned() -> set[str]`; `Aether._aetheric_frame_view`.
- Public behaviour: Spellbook.cleanup_spell and Conduit.cleanup_spell raise RuntimeError instead of AttributeError for
  a spell already disposed; AethericFrame.has_spell and spells_in_index raise their documented RuntimeError instead of
  AttributeError when cleanup races the call; AethericFrame.cleanup keeps `_lock`; get_spells_in_contract_by_conduit
  no longer deadlocks with link or sever. No signature changes.

## Migration order
Tests (red where reproducible) -> src -> component docs -> architecture doc and indexes -> graph -> notch and release
note -> assets and llm_support last.

## Rollback
Revert the five src files and the test changes; no data, cache or record format changes (no cache generation moves).

## Coverage matrix
| invariant | test |
| --- | --- |
| 1 | cleanup_spell and notch_spell paused mid-emission while owner.link(C) runs: the link waits, no error, every borrower consistent (component) |
| 2 | get_spell_in_contracts paused mid-walk while the owner stages a member: the staging waits, no error (component) |
| 3 | listing paused under the ward lock while the borrower severs: both finish (component); outbound answered from the Book, the Conduit lookup not called (unit) |
| 4 | second cleanup_spell of a disposed spell -> RuntimeError naming it (component) |
| 5 | bind parked in its sweep while a frame is born, and while a frame is cleaned: bind succeeds (component); probes on live and cleaned frames (unit) |
| 6 | a Book adds to its id set in the middle of the frame's read: the read returns (unit, both readers) |
| 7 | full tree on -X gil=0 with no hang; the orders are read off the code in the code description |
