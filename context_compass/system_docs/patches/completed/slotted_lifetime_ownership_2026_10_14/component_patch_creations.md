# Component patch: Creations - holder-owned children and retirement with disposal (slotted_lifetime_ownership_2026_10_14)

Component: Creations and SpellSpace (the generic `Creations` store, `ConduitCreations` inherits it). Defects D4, D5
(landed 0.2.8238); D3's invalidation helper withdrawn (owner ruling 2026-10-14: invalidation unchanged).

## Before / after
- Disposal registry values: a slotted entry is `(object, methods)`; a disposal-bearing `many` key is a
  `ManyDisposalBucket`. After: also `HolderDisposalEntry(item, methods, children)` - one slotted holder (its methods,
  possibly empty) and the disposal-bearing `many` children it adopted, each `(child, child_methods)`, in build order.
- `adopt_children(holder_key, holder, children)` (new, cold path): called by an emitted miss under the holder's build
  lock right after the holder is published. Under the store lock (a leaf): refuse silently when the store is cleaned or
  the slot no longer holds `holder`; for each `(child_key, child)` remove `child` by identity from its key's live
  bucket, scanning from the end (it was just appended), take the key's method list from its `ManyDisposalBucket`, and
  drop the bucket and its record when it empties; then replace the holder's disposal value with a
  `HolderDisposalEntry` (a tuple keeps its methods; a holder without disposal methods gets `methods=[]`), keeping the
  dict position, so reverse creation order still holds. Children not found (purged in between) are skipped.
- Whole-store disposal (`cleanup`, `clear_all`, `reset_for_pool*`) and `purge` dispose a
  `HolderDisposalEntry` as the holder's methods, then each child's methods newest-first, every failure collected.
- `extract_spell_creations` of a holder: the unique row gains `"children": [{"stored", "disposal_methods"}, ...]`
  (and `"disposable": True`, `"disposal_methods": []` for a holder without methods); `restore_spell_creations`
  rebuilds the `HolderDisposalEntry` from such a row. Rows without `children` behave exactly as before.
- WITHDRAWN (owner ruling 2026-10-14: a transfer disposes nothing): `dispose_extracted_creations` is not added.
- WITHDRAWN (owner ruling 2026-10-14: contract invalidation stays as it is): `retire_singleton_creation` is not
  added.
- Purge count is unchanged: the purged target's own entries (children are not the target's entries).

## Interface deltas
Internal: `HolderDisposalEntry`; `Creations.adopt_children` and the private `_dispose_entry` /
`_dispose_holder_entry` (0.2.8238).
`StoredDisposalValue` grows the new member. No public surface; the bind-guard manifest gains one internal class.

## State / failure deltas
- A holder's adopted children leave their spell's `many` bucket: a `many` purge or live-creation probe of the child
  spell no longer counts them (purging them there would dispose a child under its live holder - the 0.2.8235 bug).
- Children that were never adopted - a lost cold race, a pinned-override refusal, a holder constructor that raised -
  stay in their bucket and are disposed with the store, as in 0.2.8235.
- A many key's dict position is set by its first registration; adoption that empties a bucket drops the key, so the
  next registration starts a new key position (later objects, later position - order preserved).

## Dependency / ordering
- Lock order unchanged: the holder's build lock (slot guard or `Spell._lock`) is held by the miss; adoption takes the
  store lock as a leaf. Disposal never runs under the store lock.
- Emitters (site-plan lowering) call `adopt_children`; the ward is unchanged (invalidation withdrawn).

## Validation expectations
Unit: adoption moves the child out of the bucket into the holder record (with and without holder methods); missing
children are skipped; a cleaned store refuses silently; whole-store disposal order holder -> children; purge,
extract/restore round-trip with children (0.2.8238). Component: p5 (purge disposes the children), t4b (move carries
them).
