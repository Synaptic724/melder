# component_patch_spellbook_core_creation_cache

## Metadata
- Patch ID: stable_callable_spell_ids_2026_09_26
- Component: Spellbook Core (Binding and Conjure) - conjure creation cache
- Status: completed (promoted 2026-09-26; archived at closure)
- Owner: user (writer: melder_1)
- Created: 2026-09-26T10:42:41Z
- Updated: 2026-09-26T10:42:41Z

## Component Purpose and Boundary
- Current boundary: SpellbookCreationSystem classifies the bundle (full_hit / mixed / full_miss), loads
  payloads on full_hit, stages payloads at conjure end otherwise; CachingSystem persists the bundle.
- Target boundary: unchanged.

## Before/After Behavior Summary
- Before: a non-full-hit conjure stages only the MISSING live ids; payloads of already-cached live spells
  and of ids no longer live stay. After a provider id change the consumer keeps a plan referencing the old
  id; the next full hit fails at the consumer's first meld ("generalized manifest references unknown
  spell_id"). Stale ids accumulate forever.
- After: a non-full-hit conjure removes every payload in the bundle, then stages every live
  payload-eligible spell from this conjure's artifacts (sorted ids), and marks the bundle for emission when
  anything was removed. Generation 12 ("complete_bundle_restage") cold-resets bundles written earlier.

## Interface Deltas
- None public. CachingSystem.CACHE_VERSION_HISTORY gains 12.

## State and Lifecycle Deltas
- Bundle content after a non-full-hit conjure equals the payloads buildable now; no stale ids.

## Failure Mode Deltas
- Removed: the stale-consumer hydration RuntimeError; unbounded bundle growth.
- New: none. A spell whose payload cannot be built this conjure is simply absent (compiles next time).

## Dependency and Ordering Constraints
1. Runs after phases 8-11 (unchanged position at conjure end); uses Spellbook._emit_spell_cache unchanged.

## Validation Expectations
- Component: provider A -> B -> B -> B across fresh worlds melds every time; bundle count equals the live
  count after each non-full-hit conjure; existing caching component tests unchanged.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: conjure-end restage + prune, generation 12.
- Remaining risks: re-staging costs one manifest export per live spell on non-full-hit conjures.
- Next entrypoint: code_description_patch_conjure_cache_restage.md.
