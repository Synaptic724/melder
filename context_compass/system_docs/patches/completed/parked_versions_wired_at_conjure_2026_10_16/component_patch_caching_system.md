# Component patch: CachingSystem - generation 21

## Metadata
- Patch ID: parked_versions_wired_at_conjure_2026_10_16
- Component: `CachingSystem` (src/melder/utilities/caching_system/caching_system.py)
- Writer: melder_0 (synaptic_python_developer)
- Created: 2026-10-16T09:42:54Z
- Status: built as written; promoted at landing (0.2.8248) and archived 2026-10-16T11:41:08Z

## Before (0.2.8247)
- `CACHE_VERSION_HISTORY` ends at 20 ("annotation_kind_matching") and `CURRENT_VERSION = max(...)` is 20. A bundle is
  admitted only when its generation equals `CURRENT_VERSION` (with the exact Melder release and the interpreter
  cache tag); anything else is a cold cache that the next conjure rebuilds.
- The managed lease codegen (0.2.8245) moved no generation: plans are emitted at hydration from manifest rows, rows of
  non-managed spells did not change, and every notch already makes the cache cold (generation 9 admits only its own
  release). The owner reversed that S5 decision on 2026-10-16: codegen changes bump the cache.

## After
- `CACHE_VERSION_HISTORY[21] = "managed_spell_lease_codegen"`; `CURRENT_VERSION` is 21. The comment block above the
  map gains a "Version 21" paragraph: it retires bundles written before the managed lease codegen (0.2.8245) - plans
  gained the leasing and fresh managed sites, the doors the "managed" route rows and the generalized manifest its
  route key - and records that rows of other spells did not change, so the bump is the explicit retirement the owner
  asked for when codegen changes.

## Interface deltas
- `CachingSystem.CACHE_VERSION_HISTORY` and `CURRENT_VERSION` (internal class attributes).

## State and failure deltas
- Every generation-20 bundle is cold once after the upgrade and is rewritten at 21 by the next conjure. No new error
  path; the existing admission handles a stale generation.

## Dependency and ordering
- None: no lock, no read on a meld path; the generation is read at load and written at emit, as today.

## Validation expectations
- tests/integration/melder/spellbook/test_cache_schema_version_integration.py: the expected history gains 21, so
  generation 21 is admitted and 1-20 are cold (red until the map has 21).
- The caching unit tests, which write `CURRENT_VERSION`, stay green.
