# Component patch: CachingSystem - generation 22 (managed_settings_spell_id_2026_10_17)

## Metadata
- Patch ID: managed_settings_spell_id_2026_10_17
- Component: CachingSystem (`CACHE_VERSION_HISTORY`, `CURRENT_VERSION`, the generation comment block)
- Status: landed at 0.2.8254 and promoted to the system documents and the graph; active with the story until
  part B
- Owner: user; melder_0 (synaptic_python_developer)
- Created: 2026-10-18T00:10:00Z
- Updated: 2026-10-18T02:05:25Z

## Component Purpose and Boundary
- Current boundary: a conduit bundle is admitted only at the current format generation (21), the running Melder
  release and the interpreter tag (`_normalize_loaded_cache_data`); anything else is a cold cache.
- Target boundary: generation 22, "managed_settings_leave_spell_id"; admission unchanged.

## Before/After Behavior Summary
- Before: bundles at generation 21 of the running release are admitted.
- After: generation 21 bundles are cold. The notch already makes them cold (the release differs); the generation
  records the reason in the cache's own history, as the owner asked when codegen changed (2026-10-16, generation 21)
  and asks now for this identity change ("you gotta notch the version for the cache").

## Interface Deltas
- Inputs / outputs: `CachingSystem.CURRENT_VERSION` is 22; new bundles are written at 22.
- Error semantics: unchanged (an older bundle raises inside load and becomes a cold cache).

## State and Lifecycle Deltas
- Owned state changes: none. Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- None: each world compiles cold once after the upgrade and is rewritten at 22.

## Dependency and Ordering Constraints
1. Same notch as the fingerprint change.

## Validation Expectations
- Unit: `CURRENT_VERSION == 22`, the history entry's name, a generation-21 envelope refused as a cold cache.
- The caching suites as they are.

## Unknowns and Open Decisions
- UNKNOWN: none. DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: none.
- Next entrypoint: `src/melder/utilities/caching_system/caching_system.py:CachingSystem.CACHE_VERSION_HISTORY`.
