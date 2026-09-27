# Code description patch: ConduitWard lineage walk and Aether LIVE lookup (2026-09-27)

## Trigger
Concurrency-sensitive: the walk runs while pooled scope cycles link and detach children on other threads.

## Control flow
Aether.get_conduit_by_id(conduit_id, aetheric_frame_name="default"):
  frame = _resolve_lookup_frame(aetheric_frame_name)        # TypeError / ValueError as specified
  roots = frame._conduits.copy()                             # atomic snapshot
  if conduit_id in roots: return roots[conduit_id]
  for root in roots.values():
      ward = root's `_conduit_ward`; skip the root if it was deleted (hard teardown in progress)
      found = ward._get_lesser_conduit(conduit_id); if found: return found
  raise ValueError naming the id and the frame
ConduitWard._get_lesser_conduit(conduit_id):
  for child in self._lesser_conduits.copy().values():
      if child._id == conduit_id: return child
      ward = child's `_conduit_ward`; skip the child if it was deleted
      if ward is not None: recurse; return a hit
  return None

## Edge and error behaviour
- A scope linked or detached during the walk may or may not be seen; the walk never raises for it.
- No rollback: the walk is read-only.

## Invariants and idempotency
- Read-only; no locks taken; repeated calls with no lifecycle change return the same object.

## Non-goals
- No frame-wide id index (would add work to every scope cycle); no change to the two-lock guard on the parent dict.

## Validation focus
- Deterministic: a child whose `_id` read pops a sibling from the parent dict (live iteration raises, snapshot does
  not); a child with a deleted ward is skipped; nested and anonymous lessers resolve through Aether.
