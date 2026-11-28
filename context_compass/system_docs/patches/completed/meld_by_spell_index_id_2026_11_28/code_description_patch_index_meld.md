# code_description_patch_index_meld

## Metadata
- Patch ID: meld_by_spell_index_id_2026_11_28
- Component: Conduit Runtime, Creations and SpellSpace, Spellbook Core (the index meld path)
- Status: implemented at 0.2.8317; merged into src_architecture, src_components, tests_components and the
  source graph
- Owner: Mark (owner); executor melder_0
- Created: 2026-11-28T18:59:59Z
- Updated: 2026-11-28T19:55:00Z

## Trigger Justification
- Concurrency: the index is read on a meld path a notch can race, and a map is written at eleven locked sites.

## Control-Flow Description (Pseudocode Level)
1. Door entry: `if spell_index_id is not None: return self._meld_by_spell_index_id(...)`; nothing else changes.
2. `Conduit._meld_by_spell_index_id`: refuse a mixed call (ValueError) or a non-str id (TypeError). Automatic:
   `spell_id = book._selected_spell_id_for_index_id(spell_index_id)`, then `return self.meld(spell_id=spell_id,
   override=override)` - the warm id lane. Dynamic: admit the conduit's ticket, read the spell_id, call the door's
   id lane (`self._meld.meld(spell_id, spell_override=override)`), unregister the ticket in `finally` - the order a
   name meld keeps today.
3. `SpellSpace._meld_by_spell_index_id`: the same refusals, the released check, then the read and
   `return self.meld(spell_id=spell_id, override=override)`.
4. `managed_spell_meld`: when `spell_index_id` is given, read the spell_id and resolve the target from it as the
   spell_id form does.
5. `Spellbook._selected_spell_id_for_index_id`: `self._spell_indexes_by_id.get(id)`, else
   `self._contracted_indexes.get(id)`; neither -> KeyError (a parked-only index named as such after a scan of the
   parked versions, on that error path only); else `spell_index.selected_spell_id`.

## Edge/Error and Rollback Semantics
- A notch landing between the read and the meld: dynamic conduits hold the ticket the notch drains; elsewhere the
  window is a name meld's, and a parked id then raises the explaining KeyError.
- No rollback: the path writes nothing.

## Invariants and Idempotency Expectations
- `set(_spell_indexes_by_id) == {index.id for index in _spells}` at every Book-lock release.
- The index path never writes state.

## Explicit Non-Goals
- No change to the warm lanes' code, the door registries or their keys.
- No SpellSystemStates read.

## Validation Focus Points
- The map's invariant across every writer.
- The existing forms' warm timings.

## Context / Handoff Summary
- What changed: implemented at 0.2.8317 as specified; the refinements and the measured cost are in
  architecture_patch.md; merged into the canonical system documents.
- Remaining risks: none in this patch; C9 of #209 is a defect found in passing, not introduced here.
- Next entrypoint: none (completed).
