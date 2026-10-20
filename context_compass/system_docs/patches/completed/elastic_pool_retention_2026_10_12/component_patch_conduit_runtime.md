# Component patch: Conduit Runtime - ConduitPool retention and pool sizes (elastic_pool_retention_2026_10_12)

## Before / after
- `ConduitPool.create_object` (the miss probe `create_lesser_conduit` calls): popped an idle lesser or returned None.
  After: the None path calls `_note_miss()` first, so the caller's build counts as pressure.
- `ConduitPool.return_lesser_conduit`: appended, kept the shell while idle <= `target_idle` (fixed at 20), else
  popped the oldest idle lesser and destroyed it. After: appends; at most `baseline_idle` idle ends there; above it
  `_rebalance_after_return()` keeps, stretches, decays or trims.
- `Conduit.__init__` builds `SpellSpacePool` and the root's `ConduitPool` with baseline 20, max 256 (was 20/20), and
  `upgrade_to_normal` builds the new root's `ConduitPool` the same way.
- `prewarm_spellspaces` / `prewarm_lesser_conduits` docstrings: still clamped to `max_idle` (now 256); shells above
  the baseline stay while the pool is under pressure, then decay.

## Interface deltas
None public. Sizes and the prewarm ceiling change as above.

## State / failure deltas
A root keeps up to 256 idle lessers (about 6.7 KiB each measured, plus each one's idle spellspaces) after a burst,
for at least the settle time (30 minutes), instead of destroying all above 20 on return. No new failure mode.

## Dependency / ordering
The pool's `_lock` is a leaf taken inside `return_lesser_conduit` after the lesser has finished its pool return
(descendants, spaces, store, hooks); `destroy_object` (permanent cleanup of a surplus shell) runs after the lock is
released, as the eviction did before.

## Validation expectations
Existing ConduitPool unit and multithreaded tests pass with the new sizes; tests that set `_target_idle` to force
eviction also set `_baseline_idle` (and `_max_idle`); gauntlet runs past 20 threads rebuild no lesser after the first
burst.
