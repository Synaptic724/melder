# component_patch_meld_resolution_runtime

## Metadata
- Patch ID: creations_store_slots_by_binding_2026_10_25
- Component: Meld Resolution Runtime (`src/melder/aether/conduit/meld/conduit_meld.py`, `spellspace_meld.py`;
  docstrings of `meld.py`)
- Status: draft
- Owner: Mark
- Author: melder_3 (synaptic_python_developer)
- Created: 2026-10-25T10:55:14Z
- Updated: 2026-10-25T10:55:14Z

## Component Purpose and Boundary
- Current boundary: the two concrete doors select a store by the resolved spell's existence (caller conduit,
  spellspace, owner store, lineage root, cluster team store) and authorize purge; `_describe_spell_live_creation_status`
  and `meld_existing_spell` read that store with `get_creation(spell_id)` and interpret the value by the spell's
  existence (`many`: a list's length, else 0; others: one when not None).
- Target boundary: the same store selection and authority. The probes count the spell's shelf in that store;
  `meld_existing_spell` reads the asking binding's slot. `purge` is unchanged in the doors (the store walks the shelf).

## Before/After Behavior Summary
- Before: S8 - a new `many` binding reads live with the old binding's count; S9 - a `many` rebound from `unique`
  reads not live while the old object sits under its id; `meld_existing_spell` can return the old binding's object.
- After: `creation_count = store.count_spell_creations(spell.spell_id)` (every binding's objects in the selected
  store; 0 with no store, as today) and `is_live = creation_count > 0`, for `many`, `unique_per_conduit`,
  `unique_per_spell_space`, `unique`, lineage and cluster; `existing_creation` and managed pools as today.
  `meld_existing_spell` reads `store.get_creation(spell.store_key)`: the object a meld of this binding returns, or
  "not live".

## Interface Deltas
- Inputs: none changed.
- Outputs: `describe_live_creation_status` keeps its keys; `creation_count` can exceed one for a slotted existence
  while a removed binding's object is alive beside the new binding's (each counted).
- Error semantics: unchanged (`meld_existing_spell` raises ValueError "Spell '<spell_id>' is not live.").

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: S8, S9.
- Changed failure mode: during a rebind under another binding, before the new binding builds, `has_live_creation`
  answers True (the old binding's object counts) while `meld_existing_spell` raises "not live" (the new binding's
  slot is empty), as the approved design separates the spell's objects from the object a meld returns.

## Dependency and Ordering Constraints
1. `Creations.count_spell_creations` and `Spell.store_key` exist first.
2. The fast meld doors stay keyed by spell_id: an entry of a removed Spell fails its guard (its creation context is
   gone) and the meld takes the full lane to the new Spell, whose executor reads the new key.

## Validation Expectations
- Component: the probes after a rebind (S8, S9) through `has_live_creation` and `describe_live_creation_status`;
  `meld_existing_spell` after a rebind; a meld by spell_id string after a rebind returns the new binding's object.
- Unit: the door tests that stub a store read the count verb.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: what the probes count and which slot `meld_existing_spell` reads.
- Remaining risks: none.
- Next entrypoint: component_patch_conduit_runtime.md.
