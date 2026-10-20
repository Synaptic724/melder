# Component patch: Creations and SpellSpace - SpellSpacePool retention (elastic_pool_retention_2026_10_12)

## Before / after
- `SpellSpacePool.acquire` / `acquire_untracked`: popped an idle space or built one. After: a build also calls
  `_note_miss()`; the reuse path (released flag cleared, hooks inherited) is unchanged.
- `SpellSpacePool.release`: set `_released`, appended, kept the space while idle <= `target_idle` (fixed at 20), else
  destroyed the oldest idle space. After: sets `_released`, appends; at most `baseline_idle` idle ends there; above it
  `_rebalance_after_return()` keeps, stretches, decays or trims. The acquire docstring no longer says the pools are
  built with a fixed `baseline_idle == max_idle`.

## Interface deltas
None.

## State / failure deltas
A conduit keeps up to 256 idle spellspaces (about 1.3 KiB each measured) after a burst of nested or concurrent managed
spaces, until the decay lets them go. The lease flag contract is unchanged.

## Dependency / ordering
The release order stays: lease flag, append, size check; the band's lock is a leaf; surplus spaces are destroyed after
it is released.

## Validation expectations
SpellSpacePool unit and multithreaded tests pass; a burst of nested managed spaces past 20 is kept and reused by the
next burst (probe: 50 kept, 50 reused); `SpellSpaceScopeError` on a released space is unchanged.
