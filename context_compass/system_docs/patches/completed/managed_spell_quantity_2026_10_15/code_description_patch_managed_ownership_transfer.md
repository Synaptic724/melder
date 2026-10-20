# Code-description patch: owner stamps through an ownership transfer (managed_spell_quantity_2026_10_15, S6)

Read with component_patch_managed_ownership_transfer.md. Trigger: rollback behaviour - stamps registered for undo,
pools a stamp composed discarded, and the reverse order those actions run in.

## Control flow (execute)
1. `_mark_lineage_disabled` - rollback: the previous validity.
2. `force_unshare`: the target's borrowed entry is pre-cleaned - rollback: restore it.
3. Under both conduit locks (`SafeGuard(source._lock, target._lock)`):
   - `_flip_registry_and_spellbooks`: the registry moves (two rollbacks); the Book maps under both Book locks
     (rollback `_rollback_spellbook_move`); then, outside the Book locks, `_restamp(active)`:
     `held = managed and target store holds a pool under the id`; register `_stamp_owner(active, source, source
     Book)`; `_stamp_owner(active, target, target Book)` (spell lock, then the store's leaf lock in ensure, then the
     registry's leaf lock); when managed and not held, register `_discard_composed_pool(target store, id, the pool
     now under the id)`.
   - `_migrate_inactive_members`: the parked maps under both Book locks (rollback `_rollback_inactive_members`);
     then, outside the Book locks, `_restamp(member)` for each moved member whose `_owner_creations` is set.
4. Rows: lineage skips both; move extracts and restores every member (a restore replaces a composed pool and cleans
   it: S4) with a row rollback per member; no move takes the active member's rows out, rollback restores them.
5. Borrowers, dependencies, gating. Success clears the rollback stack; nothing registered above runs.

## Rollback (failure anywhere after step 1)
Actions run newest first: rows back to the source -> for each re-stamped parked member, newest first: discard its
composed pool, stamp it back onto the source -> parked maps back -> the active member: discard its composed pool,
stamp it back -> `_rollback_spellbook_move` -> registry flip undone -> borrowed entry restored -> validity restored.
Then `_lift_disable(gated=True)` and the incident.

## Edge and error semantics
- The discard is identity-checked. With a move the composed pool was already replaced by the moved pool, which the
  row rollback took back to the source, so the target holds nothing under the id: no-op, nothing cleaned. With no
  move, or a failure before the rows moved, the composed pool is still there: removed, unregistered, cleaned (empty).
- A target store that held a pool under the id before the stamp: ensure returned it (re-pointed at the Spell); no
  discard is registered, so the rollback never touches it.
- The stamp-back's ensure on the source store finds the pool the row rollback put back (or that never left):
  idempotent. If a row rollback failed (its failure swallowed), ensure composes an empty pool in the source and the
  moved pool stays in the target, registered there - a degraded state after a failed undo, with the incident filed.
- A stamp that raises midway has its stamp-back already registered, so the rollback rewrites the source stamp.
  Re-stamping a member whose stamp never changed rewrites the same values, plus a fresh CreationContextFactory and a
  cleared CreationContext, which every stamp does.
- A member never stamped (`_owner_creations` None) gets neither a stamp nor a stamp-back; its maps and
  `_owner_conduit_id` move and roll back as before.

## Invariants and idempotency
- After a successful transfer every member that carried a stamp names the target root's store; after a failed one,
  the store it named before; the target holds no pool the transfer composed.
- `discard_managed_quantity(id, pool)` removes that pool at most once; any later call returns False.
- No disposal: the transfer cleans only a pool it composed and discards, which never held an object.
- Locks: stamps under the conduit locks and outside the Book locks (conduit -> spell -> store leaf -> registry leaf,
  the flip's existing order); rollbacks hold no conduit lock; no new edge joins frame -> conduit -> Book.

## Non-goals
- Stamping versions staged before conjure (raised to the owner); how rows move, which rows no-move takes, restore's
  cleanup of a replaced pool; automatic worlds (transfers are dynamic-only).
