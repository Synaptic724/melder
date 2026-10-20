# Code description patch: cluster exit at leave and at root teardown (slotted_lifetime_ownership_2026_10_14)

## Control flow
1. `Conduit._cleanup_normal_conduit` calls `_leave_cluster_for_teardown()` before any other step.
2. `_leave_cluster_for_teardown`: `clusters = frame._devops_information_registry.get_cluster_objects_for_conduit(id)`
   (the frame's private registry slot: its property refuses once frame teardown has marked the frame cleaned). None:
   return. For each cluster: when the frame is not cleaned, `cluster.release_member(self)`; if that raises, log the
   error and fall through; when the frame is cleaned (frame teardown) or the exit raised, `cluster.drop_member(self)`
   (logged if it raises). Nothing is re-raised: teardown keeps going, as every other teardown step does.
3. `ConduitCluster.release_member(conduit)`: `handle_leave(conduit)` then `remove_member(conduit._id)`.
   - `handle_leave`: leader -> `unelect_leader()` (UNELECT transaction over every member including the leaver: seal,
     drain member lineages, unbind every facade, clear `master_conduit_id`); then CLUSTER_LEAVE over the members plus
     the leaver: discard it, unshare the leaver's roots from each peer and each peer's roots from the leaver while
     `shared_spells[leaver]` is still present, pop that record, unbind the leaver's facade.
   - `remove_member`: discard/pop (no-ops now), unregister the DevOps membership edge, emit the cluster record.
4. `ConduitCluster.drop_member(conduit)` (no transaction): when the conduit leads, `unbind_elected_leader()`
   (unbinds every live member's facade, clears the leader); `remove_member(conduit._id)`; unbind the conduit's own
   facade.
5. `ConduitCloud.remove_conduit_from_cluster` (posture-gated, as before) calls `release_member`.

## Edge / error semantics
- Frame teardown: the frame is marked cleaned before its roots are torn down, so the mediator cannot be reached;
  the drop is the designed path, not a failure, and logs nothing.
- A root in no cluster pays one registry dict read.
- The root ward's cleanup still severs every contract the root holds; after `release_member` no cluster-scoped
  contract of the root remains for it to find.
- `unbind_elected_leader` during a drop walks members that are all live: every earlier torn-down member dropped
  itself.

## Invariants / idempotency
`release_member` and `drop_member` are safe for a conduit that is no longer a member (every effect is a discard, a
pop or an idempotent unbind). A torn-down root is never left in `members` or as `master_conduit_id`.

## Non-goals
Transactional atomicity of membership with the share fan-out (the documented gap) is unchanged.
