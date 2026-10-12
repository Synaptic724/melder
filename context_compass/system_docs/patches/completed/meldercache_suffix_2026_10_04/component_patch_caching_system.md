# Component patch: caching system (meldercache_suffix_2026_10_04)

## Before / after behavior
- Before: conduit caches at `<cache_root>/<frame>/<conduit>.melc` (temp `<conduit>.melc.tmp`); asset
  caches at `__melder_cache__/__<asset>__/<asset>.melc`.
- After: the same paths ending in `.meldercache` (temp `<conduit>.meldercache.tmp`).

## Interface deltas
- The two BUNDLE_SUFFIX constants only. No method, envelope field or generation changes.

## State and failure deltas
- An existing `.melc` bundle is not consulted, so the first conjure or import after the upgrade is
  cold; the release-stamp check already rejects every bundle written by an older release.
- No new failure mode: an unwritable cache directory degrades exactly as before.

## Dependency and ordering
- Constants before tests; `.gitignore` before any test run writes a new-name bundle into the tree.

## Validation expectations
- Unit and component tests assert the new bundle names; a regression test shows a current-format
  `.melc` bundle beside the conduit cache is never read.
- github_workflows tests pass with both suffixes forbidden in distributions.
