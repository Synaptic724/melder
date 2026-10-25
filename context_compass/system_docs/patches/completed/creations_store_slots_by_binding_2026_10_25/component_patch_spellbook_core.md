# component_patch_spellbook_core

## Metadata
- Patch ID: creations_store_slots_by_binding_2026_10_25
- Component: Spellbook Core (Binding and Conjure) - CachingSystem
  (`src/melder/utilities/caching_system/caching_system.py`)
- Status: draft
- Owner: Mark
- Author: melder_3 (synaptic_python_developer)
- Created: 2026-10-25T10:55:14Z
- Updated: 2026-10-25T10:55:14Z

## Component Purpose and Boundary
- Current boundary: `CachingSystem.CACHE_VERSION_HISTORY` names every creation-cache generation; a bundle of another
  generation is cold. Generation 24 ("spell_index_keeps_its_binding") is in the working tree from
  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (melder_1).
- Target boundary: unchanged; one more generation.

## Before/After Behavior Summary
- Before: the current generation is 24.
- After: generation 25, "creation_store_slots_by_binding", with its comment: the emitted plans, doors, solo
  templates and specializer file and read store slots by store key and publish through `register_slot`. A release
  change already cold-starts every bundle (generation 9); the bump is the owner's rule that a codegen change bumps
  the cache.

## Interface Deltas
- Inputs: none.
- Outputs: `CachingSystem.CURRENT_VERSION` 25.
- Error semantics: none; an older bundle is cold once and rewritten at 25.

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: none.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. After generation 24: this lane edits the map once melder_1 agrees (it holds the file's last edit), and takes the
   next number if another lane lands one first.

## Validation Expectations
- Unit: the cache-version tests read the current generation from the map; any that pins a number moves with it.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: one generation entry.
- Remaining risks: two lanes landing generations out of order; read the map at landing.
- Next entrypoint: component_patch_meld_resolution_runtime.md.
