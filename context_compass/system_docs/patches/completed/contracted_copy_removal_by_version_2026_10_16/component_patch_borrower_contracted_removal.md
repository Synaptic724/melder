# Component patch: a borrower Book removes one contracted copy (contracted_copy_removal_by_version_2026_10_16)

## Before / after behavior
- Before: asked to remove version V, `_remove_contracted_spell` walked the borrower's active map for the index
  whose member set holds V (`spell_id in idx._spells_in_index`) and removed that index's active copy, whatever
  version it was; only when no active entry matched did it look in the parked map. A cleaned index was matched by
  the copy's own id. So with V parked and W (same index) active, removing V removed W's active copy, and the later
  removal of W found no copy and raised.
- After: an active entry matches only when its copy's own `spell_id` is V, for a live or a cleaned index alike;
  otherwise V's parked copy is removed; when neither exists it raises RuntimeError "Spell version V not found for
  conduit ID <peer>." before anything changes.

## Interface deltas
- None public.

## State and failure deltas
- No new state. The active branch keeps its existence handling (a live index drops every member id, a cleaned one
  the removed id); the parked branch drops V's id.
- Failure: a removal of a version the Book holds no copy of raises with the maps untouched; until now it could
  remove another version's active copy instead.

## Dependency and ordering
- Callers, each passing one version id whose copy it means: `ConduitWard._uncontract_member_spell` (index unlink,
  index destroy, a member leaving its index), `ConduitWard._remove_root_from_contracts` (a root's dependency
  fallout) and `ConduitWard._remove_spell_from_contract` (a version uncontract). An index link holds a copy of
  every member (`ConduitWard._contract_member_spell`: active for the active member, parked for the rest).

## Validation expectations
- Unit: removing parked V beside active W leaves W's copy active and marks nothing; removing W then marks its key's
  consumers; a member id with no copy raises and leaves W in place.
- Integration: a Greeter Protocol with English and French on one index, linked by a borrower; notch to French;
  `remove_index_from_contract` with English first and with French first (order forced): both copies go, the
  borrower stops tracking the index, nothing raises.
- The component test that removed a copyless member id removes the active copy by its own id instead.
- The spellbook, conduit-ward and index-link suites with the GIL off and on.
