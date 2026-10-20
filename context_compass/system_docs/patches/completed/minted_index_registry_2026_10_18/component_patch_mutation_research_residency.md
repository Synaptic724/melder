# Component patch: residency reads a separated version parked (minted_index_registry_2026_10_18)

## Before / after behavior
- Before: `_locate_live_membership` walks every live frame's `find_index_for_spell` and reports a version `active`
  when its index selects it (`index.selected_spell_id == spell_id`), else `parked`. A version in a minted index is
  not found at all, because the index is not registered, so `residency_view` reads `declared_only` - parked there
  (V2) and after a notch makes it active there (V3).
- With the registration alone (prototype A): the index is found and selects its parked member (activation takes a
  notch - the owner's S10 ruling), so V2 reads `active` while the Book holds the version parked.
- After: a version is `active` only when its index selects it AND the frame's lineage registry tracks it as that
  index's current version (`frame.spell_system_states.get_by_index_id(index.id).current_spell_id == spell_id`);
  every other live member reads `parked`. `bind` registers a lineage with its new version and a notch re-registers
  the index with the version it makes active; parking never registers one, so the minted index's parked member has
  no lineage until a notch. The state is read by index id: `register_index` keys a state by its new current
  spell_id without dropping the previous key, so `get_by_spell_id` also answers a version a notch moved away from.

## Interface deltas
- None in signatures. Docstrings: `residency_view`'s Contract defines `active` with the lineage condition and says a
  version moved into an index of its own stays parked until a notch; `_locate_live_membership`'s Contract says what
  active means and why the state is read by index id.

## State and failure deltas
- No new state. The two lineage reads sit inside the per-frame `try`, so a frame cleaned meanwhile is skipped as
  before. A read that races a notch answers the state it reads; residency is a query-time join and holds no lock
  across reads. Members of a registered index read as before: its lineage tracks the version it selects.

## Dependency and ordering
- Reads `AethericFrame.spell_system_states` (public property), `SpellSystemStates.get_by_index_id` (the registry's
  lock alone) and `SpellSystemState.current_spell_id` (the state's lock alone); holds no other lock. Edits only
  mutation_research.py, CRLF throughout in the working tree, kept.

## Validation expectations
- Integration: `residency_view(French)` reads `parked` with French in the minted index (V2) and `active` after a
  notch there (V3); English active and French parked on English's index read as before (V1), and so does a later
  version parked there (V4).
- GIL off and on; probe V1-V4 re-run.
