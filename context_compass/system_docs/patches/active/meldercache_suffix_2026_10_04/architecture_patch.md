# Architecture patch: meldercache_suffix_2026_10_04

## Objective and non-goals
- Objective: Melder's on-disk cache bundles are named `<name>.meldercache` instead of `<name>.melc`,
  so a file under `__melder_cache__` reads plainly as a cache.
- Non-goals: no change to bundle contents, the envelope fields, the format generation (20), cache
  locations or admission rules; no migration, reading or deletion of old `.melc` files.

## Changed components
- Caching system (`CachingSystem`, per-conduit creation caches).
- Build-asset cache (`asset_cache`, the bind-guard and agent-documentation caches).

## Invariants
- Every cache bundle Melder writes ends in `.meldercache`; Melder never reads a `.melc` file.
- A missing bundle is a cold cache: compile, then emit under the new name.
- Cache files are never committed or shipped: `.gitignore` ignores both suffixes and the distribution
  check forbids both.

## Interface deltas
- `CachingSystem.BUNDLE_SUFFIX` and `AssetCachePolicy.BUNDLE_SUFFIX`: `.melc` -> `.meldercache`.
  Both are internal constants; `CachingSystem.bundle_path` reports the new name.

## Migration order
1. Constants and wording in src/. 2. Tests, ignore rules, CI list. 3. Docs, version notch and release
note. 4. Regenerated assets, graph, indexes and bundles.

## Rollback
- Restore both constants; caches regenerate under whichever name is current.

## Ticket coverage matrix
| patch section | ticket |
| --- | --- |
| all | tickets/tasks/2026-10-04_rename_cache_suffix_to_meldercache_task.md |
