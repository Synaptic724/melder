# Component patch: TransferOfOwnership's spell_id resolution (find_spell_by_spell_id_2026_10_17)

## Before / after behavior
- `_resolve_spell`, str handle: before, `source_conduit.get_spell_by_id(handle)` - the index's active spell, or
  None; after, the spell found by spell_id (`get_spell_by_spell_id`), then the spell its index has active in the
  source Book (`_spells` under the Book lock, the SpellIndex branch's read) - the same spell for a spell the source
  owns. When that finds nothing the branch raises its documented RuntimeError ("Unable to resolve spell for
  transfer: ...") instead of handing None, or another conduit's spell, to the ownership check. The internal
  constructions (Conduit footprint, ConduitWard transfer, the dependency sub-transfer) pass Spell objects already.
- `_deps_resolvable_on_target`: before, a dependency id resolved through `target_conduit.get_spell_by_id` to the
  index's active spell, and a miss made it False; after, the spell by spell_id and then its index's active spell in
  that spell's Book, with False when either misses - the same answer.
- `_transfer_owned_dependencies`: before, the sub-transfer received the dependency index's active spell; after,
  the same spell through the explicit step, read in the source Book. A parked Spell object is never handed to a
  sub-transfer.
- `_dirty_dependencies`: the call is renamed; it marks the spell's index, which the exact spell shares.

## Interface deltas
- None.

## State and failure deltas
- None for valid handles; the loops keep their skip-on-error handling.

## Dependency and ordering
- The explicit step takes one Book lock alone; `preflight` and `execute` call these with no lock held (the
  registry flip's `SafeGuard` blocks close before the dependency phase).

## Validation expectations
- Integration: a transfer with `include_dependencies=True` of a consumer whose dependency was notched after the
  consumer compiled moves the dependency's whole index with its active version unchanged, as before.
- Unit: the str handle of `_resolve_spell`, the dependency checks and the dependency sub-transfer keep their answers
  on the transfer test doubles (which gain the `_spell_index_unless_cleaned` read the code now makes).
