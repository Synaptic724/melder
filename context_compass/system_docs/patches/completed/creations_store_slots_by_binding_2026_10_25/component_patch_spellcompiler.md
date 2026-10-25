# component_patch_spellcompiler

## Metadata
- Patch ID: creations_store_slots_by_binding_2026_10_25
- Component: SpellCompiler and Validation Pipeline - the emitters that file or read a store slot
- Status: draft
- Owner: Mark
- Author: melder_3 (synaptic_python_developer)
- Created: 2026-10-25T10:55:14Z
- Updated: 2026-10-25T10:55:14Z

## Component Purpose and Boundary
- Current boundary: the emitted creation code reads and publishes store slots by a spell_id bound as a constant:
  - site plans (`shared_assets/site_plan_lowering.py`): `sid{i}` in `_emit_many` (`many_store.register_many(sid{i},
    ...)`) and `_emit_shared_hit` / `_emit_miss` (`c{i}._creations.get(sid{i})`, the slot guard, `add_creation`, and
    the no-disposal publish `c{i}._creations[sid{i}] = v{i}`);
  - doors (`shared_assets/creation_runtime_door_compiler.py`): the templates' `_spell_id` in every slot read and slot
    guard;
  - the opt-in singleton specializer (`strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py`):
    `spell_id_{i}` from `step_spell_ids`, and its capture read;
  - the generalized register helpers (`generalized_no_overrides_codegen_creation_compiler.py`) and the solo templates
    (`strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py`,
    `solo_overrides_codegen_creation_compiler.py`): the namespace's `spell_id` in `register_many` / `add_creation`.
  Leasing managed sites bind `sid{i}` = the spell_id for `_managed_quantities[sid{i}]`.
- Target boundary: the same code with the store key in every store-slot position; the managed pool read keeps the
  spell_id; error texts keep naming the spell_id.

## Before/After Behavior Summary
- Before: the constant is `spell.spell_id`; the no-disposal slotted publish is an inline dict store.
- After: the constant is `spell.store_key` (site plans keep the names `sid{i}`, the doors' parameter becomes
  `_store_key`, the specializer's alias `store_key_{i}` from `step_store_keys`, the solo namespace gains `store_key`);
  the no-disposal slotted publish is `c{i}.register_slot(sid{i}, v{i})` in site plans and
  `creations_{i}.register_slot(store_key_{i}, instance_{i})` in the specializer, so the store notes the key's first
  filing. A warm hit is the same dict read of a constant.

## Interface Deltas
- Inputs: the emitters read `spell.store_key` where they read `spell.spell_id` for a slot.
- Outputs: emitted source changes (the publish call; the doors' parameter name); the creation-cache generation moves
  (Spellbook Core's patch).
- Error semantics: unchanged; messages that name the spell_id keep it.

## State and Lifecycle Deltas
- Owned state changes: none; one more namespace constant in the solo templates.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: a plan of one binding no longer reads, appends to or publishes over another binding's slot.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. `Spell.store_key` and `Creations.register_slot` exist before the emitters use them.
2. The door's slot guard and the plan's slot guard of one root stay the same lock: both are keyed by the store key
   (the door-held root rule of 0.2.73).
3. The leasing managed site's `sid{i}` stays the spell_id (pools are per spell_id).

## Validation Expectations
- Unit: the site-plan lowering tests assert the bound `sid{i}` is the store key, the shared read
  `v1 = c1._creations.get(sid1)` and `many_store.register_many(sid0, v0, dm0)` unchanged in text, and the publish
  `register_slot`; the managed tests keep `_managed_quantities[sid0]` with the spell_id; the door, solo and
  specializer contract tests bind store keys (`test_generalized_emission_contracts.py` gets `step_store_keys`).
- Component and integration: every meld form through the suites, the GIL off and on.
- Benchmark: warm melds within noise of 0.2.8270.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: the key the emitted code files and reads by.
- Remaining risks: a store-slot position missed by the rename; the closure grep lists every `_creations` access in
  emitted source.
- Next entrypoint: component_patch_spellbook_core.md (the cache generation).
