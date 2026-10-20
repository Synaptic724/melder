# Component patch: ConduitWard and Contracts (cross_object_lock_gaps_2026_10_11)

## Before / after
- _emit_index_notch, _emit_index_destroy, _emit_index_member_added, _emit_index_member_removed: walked
  self._contracts.values() with no lock, after the owner's transaction had ended (notch, add/remove index, bind
  inactive) or with no transaction (cleanup_spell); a link or sever admitted in that window resized the dict, the
  emission raised "dictionary changed size during iteration" after the owner's change had committed, and the
  borrowers not yet visited stayed out of step. After: each walk runs under `with self._lock:`; contract records are
  emitted after the lock is released, as before.
- _contract_member_spell: Contract._add ran with no lock; after: under the contract lock (as _uncontract_member_spell
  already removes under it).
- _get_spell_in_contracts and _get_spells_in_contract_by_conduit: walked a contract's detail maps holding only the
  caller's ward lock; after: each contract's maps are walked under that contract's lock; the contracted-spell
  resolution stays outside the contract lock.

## State / failure deltas
The races' RuntimeErrors (and the cleaned-Detail errors of a borrower inspection) no longer occur. A link or sever
of the owner waits for an in-flight emission (the emission's walk is short and calls no user code).

## Validation expectations
Forced interleavings for cleanup_spell, notch_spell and get_spell_in_contracts; the existing ward, contract,
index-link and transfer suites green.
