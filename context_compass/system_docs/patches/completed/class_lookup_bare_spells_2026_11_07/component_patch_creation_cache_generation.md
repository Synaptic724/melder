# component_patch_creation_cache_generation

## Metadata
- Patch ID: class_lookup_bare_spells_2026_11_07
- Component: Creation cache envelope (`CachingSystem.CACHE_VERSION_HISTORY`; Component: Spellbook Core)
- Status: completed (merged into src_architecture and src_components 2026-11-07; moved to patches/completed/)
- Owner: Mark (owner); written by melder_0 (synaptic_python_developer)
- Created: 2026-11-07T13:48:07Z
- Updated: 2026-11-07T13:48:07Z

## Component Purpose and Boundary
- Current boundary: the cache envelope admits a bundle only at the current generation and the exact Melder release
  (generation 9); the structural tier replays recorded phase 3-4 rows on a full hit.
- Target boundary: unchanged.

## Before/After Behavior Summary
- Before: generation 25 (`creation_store_slots_by_binding`).
  EVIDENCE: src/melder/utilities/caching_system/caching_system.py:245-272
- After: generation 26 (`class_lookup_bare_spells`), with a history comment beside 18-25: bundles written before
  recorded phase 3 rows in which a class lookup matched a framed or named spell; the release change already
  cold-starts every bundle (generation 9), and the bump records why, as generations 18 and 20 did for the earlier
  matching-rule changes.

## Interface Deltas
- Inputs: none.
- Outputs: `CachingSystem.CURRENT_VERSION` reads 26.
- Error semantics: none (an older bundle is cold, never an error).

## State and Lifecycle Deltas
- Owned state changes: none.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: a full structural hit replaying a class match the new rule refuses.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. Lands in the same change set as the Phase 3 rule.
2. Any test that pins the current generation number is updated with it.

## Validation Expectations
- Test/validation item 1: the caching-system unit tests that read `CURRENT_VERSION` or the history pass.
- Evidence target 1: the full suite the GIL off and on.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (the owner settled generation 26, point 11, chat 2026-11-07).

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: none beyond a test pinning 25.
- Next entrypoint: `CachingSystem.CACHE_VERSION_HISTORY`.
