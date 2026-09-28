# code_description_patch_input_door

## Metadata
- Patch ID: meld_entry_cache_2026_09_27
- Component: Meld Resolution Runtime - the name/class warm lane of `Conduit.meld` and `SpellSpace.meld`
- Status: draft
- Owner: user (implementation: fable_0)
- Created: 2026-09-27T21:39:56Z
- Updated: 2026-09-27T21:39:56Z

## Trigger Justification
- Hot-path control flow read by many threads at once on 3.14t; the guard ladder is the concurrency contract.

## Control-Flow Description (Pseudocode Level)
1. `Conduit.meld(spell, *, spell_id, spellframe, binding_name, override)`: cleaned check;
   `meld_component = self._meld`.
2. If `spellframe is None and binding_name is None and not self.__dynamic_environment__`:
   - `spell is None`: `fast_entry = _fast_meld_doors.get(spell_id)` when `type(spell_id) is str` (the id
     lane, unchanged);
   - else `spell_id is None`: `fast_entry = _fast_input_doors.get(spell)`, a TypeError (unhashable) is a miss;
   - else `fast_entry = None`.
3. On `fast_entry`: unpack `(door_spell, captured_context, captured_epoch, existing_object_entry)`; inside a
   try/except AttributeError read the ladder `not _meld_hooks`, `door_spell._door_epoch == captured_epoch`,
   `door_spell._creation_context is captured_context`, `not _spellbook._spellbook_validation_required`; on pass
   pick `_no_overrides_instance_executor` (override None) or `_overrides_executor` (non-empty dict), read per hit
   through the live context; call it (existing-object entries return `door_spell.user_created_object`); run the
   cache-emit check; return.
4. Miss: the id shape continues in the door's positional id lane as today; every other shape falls to the
   existing delegate, which mints on success.
5. `ConduitMeld.meld` / `SpellSpaceMeld.meld` else-branch: after resolution compute `fast_input_key` per the
   component patch; the two success arms write the entry under it (the id arms are unchanged and exclusive).
6. `SpellSpace.meld` mirrors steps 2-4 against its own door.

## Edge/Error and Rollback Semantics
- Unhashable `spell`: miss (TypeError caught around the `get` only), the door resolves it uncached as today.
- Cleaned spell/context/door: AttributeError inside the ladder is a miss; a constructor's own AttributeError is
  outside the try and propagates.
- Notch: the outgoing spell's epoch bumps and its context is cleared; the entry misses; the slow lane resolves
  the promoted member and re-mints under the same key.
- Removal then rebind under the same name: the removed spell's slots are deleted (miss); the new spell is minted
  on the next successful meld.
- Rollback: delete the two read blocks, the two mints, the slot and the upgrade clear.

## Invariants and Idempotency Expectations
- A hit and the slow lane return the same object for stored lifetimes and equivalent fresh objects for `many`.
- Re-minting is idempotent: the entry for a key is always the last successful slow-lane result for that key.
- Racing first melds converge last-write-wins on a dict write (per-op atomicity), as for the id registry.

## Explicit Non-Goals
- No read of `_fast_input_doors` inside the door subclasses; no read of `_fast_meld_doors` by name.
- No cap or eviction: cardinality is bounded by the mint rule.
- No change for `spellframe`/`binding_name` addresses, dynamic worlds, hooks, list/tuple/empty overrides.

## Validation Focus Points
- The ladder text in the four front-door blocks is identical (review); the differential test covers the arms.
- Every remap event in the component patch has a test that proves the miss and the re-mint.

## Context / Handoff Summary
- What changed: nothing yet (draft before the src edits).
- Remaining unknowns: none blocking.
- Next entrypoint: `Meld.__slots__`/`__init__`/`cleanup` in `meld.py`.
