# component_patch_binding_pipeline

## Metadata
- Patch ID: creations_store_slots_by_binding_2026_10_25
- Component: Binding Pipeline (Bind, Spell, SpellIndex) - Spell (`src/melder/aether/spellbook/spell.py`)
- Status: draft
- Owner: Mark
- Author: melder_3 (synaptic_python_developer)
- Created: 2026-10-25T10:55:14Z
- Updated: 2026-10-25T10:55:14Z

## Component Purpose and Boundary
- Current boundary: a Spell carries its identity - `spell_id` (the SHA256 of its code), its address `key`, and
  `binding_manifest` / `binding_hash` (how it is bound) - readable after cleanup. Stores file its objects by
  `spell_id`.
- Target boundary: a Spell also carries `store_key`, the key every Creations store files its objects under. The
  Binding Pipeline computes it; Creations and the emitters consume it.

## Before/After Behavior Summary
- Before: nothing names one binding of a spell_id; a store cannot tell two bindings of one class apart.
- After: `store_key = f"{spell_id}:{binding_hash}"`, built in `Spell.__init__` right after the binding manifest. Equal
  bind arguments of equal code give equal store keys in every process; a change of existence, disposal order, address,
  spellframe or its kind, resolvable or managed settings gives another.

## Interface Deltas
- Inputs: none new; built from `spell_id` and `binding_manifest.binding_hash`.
- Outputs: `Spell.store_key` (str), a plain slot appended last in `__slots__` (the hot fast-door slots keep their
  offsets).
- Error semantics: none.

## State and Lifecycle Deltas
- Owned state changes: one str per Spell (129 characters for a SHA256 spell_id).
- Lifecycle/cleanup changes: kept after `cleanup()`, like `spell_id` and `binding_manifest`, so a cleaned Spell still
  names the slot its objects are in. The cleanup docstring's identity list names it.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: none in this component (the store's S1-S9 end through Creations).
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. `binding_manifest` is built before `store_key`; nothing reads `store_key` during `__init__`.
2. Every construction path of a Spell (bind, bind_inactive, restore, graft) runs `__init__`, so every Spell has one.

## Validation Expectations
- Unit: `store_key` equals `f"{spell_id}:{binding_hash}"`; equal for two bindings with equal arguments; different
  when existence or the disposal names change; readable after cleanup.
- Component: a rebind under the same binding gives the removed Spell's store key (the 2026-10-03 slot).

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: one identity field.
- Remaining risks: none.
- Next entrypoint: component_patch_creations_and_spellspace.md.
