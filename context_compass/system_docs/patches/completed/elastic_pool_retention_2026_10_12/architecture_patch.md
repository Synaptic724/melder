# Architecture patch: elastic_pool_retention_2026_10_12

## Objective
Make the kernel pools keep what demand needs and let it go when demand falls. `SpellSpacePool` and `ConduitPool` are
built with `baseline_idle == max_idle == 20` and replace `acquire`/`release` with fast paths that never call the
base's stretch or decay, so `target_idle` stays 20: with more than 20 shells out at once, every extra lesser (or
spellspace) is built on the miss and destroyed when it comes back, on every burst. The base algorithm cannot serve
them either: a miss grows the target by `stretch_percent` (200) of itself, which reaches `max_idle` within three
misses, and decay runs only inside a return that overflows, so a quiet pool never shrinks and an overloaded one shrinks
while it is busiest, one trim per return. Ticket: tickets/tasks/2026-10-12_make_kernel_pools_elastic_task.md.

## Non-goals
- The pooled-spell Existence member (pools epic) and any pool limit or exhaustion behaviour.
- A background timer: decay is applied by returns (with catch-up), so a pool that sees no return keeps its shells.
- A return into a retired pool still lands in the cleared idle deque (the class docstring that said it is destroyed
  is corrected; no behaviour change).
- No public signature change; `describe()` keeps its keys; the melder_gauntlet 1-3 thread cap stays.

## Changed components
- AbstractElasticPool (shared base of both kernel pools): a miss records pressure (`_note_miss`); a return that leaves
  more than `baseline_idle` idle runs `_rebalance_after_return` (stretch under pressure, time-based decay with
  catch-up, bounded trim). `stretch_percent` becomes headroom over the observed idle count (default 0, was 200).
- Creations and SpellSpace: `SpellSpacePool` calls `_note_miss` on both miss paths and the elastic band on release.
- Conduit Runtime: `ConduitPool` does the same; `Conduit` builds both pools with baseline 20, max 256; the prewarm
  contracts say prewarmed shells above the baseline stay while the pool is under pressure and then decay.

## Invariants
1. A return that leaves at most `baseline_idle` objects idle is one append and one compare - no clock read, no lock.
2. `baseline_idle <= target_idle <= max_idle` at every write; stretch, decay and trim run under the pool's `_lock`,
   which is held for counters and deque work only - `destroy_object` runs after it is released.
3. Under pressure (a miss within `settle_time_seconds`), the target follows the idle count a return observes and only
   objects above `max_idle` are trimmed, so a burst of N <= `max_idle` concurrent objects is kept whole even while its
   returns race, and its repeat builds nothing.
4. With no miss for `settle_time_seconds`, the target falls by `decay_percent_per_interval` of its stretched value
   (at least 1) per `decay_interval_seconds`, never below `baseline_idle`; steps missed during a quiet period apply at
   the next return. Surplus idle objects go oldest first, at most one decay step per return.
5. Live objects stay uncapped: a miss always builds. Acquire is unchanged except for the miss bookkeeping.
6. A fixed-capacity pool (`max_idle == baseline_idle`) returns exactly as before: one oldest-object eviction per
   return above the baseline, no clock read, no lock.

## Interface deltas
- Internal: `AbstractElasticPool._note_miss()`, `_rebalance_after_return()`, `_rebalance_locked(now)`; slots
  `_last_miss_at`, `_next_decay_at` replace `_last_expand_at`, `_last_decay_at`; `_advisory_stretch_after_miss` and
  `_advisory_decay_after_overflow` are removed.
- Behaviour: `stretch_percent` default 200 -> 0 and meaning "growth per miss" -> "headroom"; the kernel pools' max_idle
  20 -> 256; `prewarm_spellspaces(count)` / `prewarm_lesser_conduits(count)` can now keep up to 256 shells.
- No record, cache or persisted format change.

## Migration order
Patch docs -> unit tests for the new algorithm (red on 0.2.8233) -> src (scratch, then tree) -> updated pool tests ->
full tree -> component docs -> architecture doc and indexes -> graph -> notch 0.2.8234 and release note -> assets and
llm_support last.

## Rollback
Revert abstract_elastic_pool.py, spell_space_pool.py, conduit_pool.py, the size literals in conduit.py and the test
changes; nothing persisted depends on the change.

## Coverage matrix
| invariant | evidence |
| --- | --- |
| 1 | micro-benchmark of the pool paths (82.4 vs 82.0 ns, 110.4 vs 112.7 ns) and 1-3 thread gauntlet runs |
| 2, 3 | unit: a burst past the baseline under pressure raises the target to the idle count, capped at max_idle |
| 3 | probe and gauntlet: a repeat burst builds nothing (24-64 threads: 0 rebuilt lessers per iteration) |
| 4 | unit with a fake clock: no decay inside the settle window; one step per interval; catch-up; bounded trim |
| 2 | unit, multithreaded: concurrent take/return traffic keeps the target within bounds |
| 5 | unit: a miss always builds; the kernel pools' miss paths record pressure |
| 6 | the existing fixed-capacity ConduitPool tests that make the clock raise (single and multithreaded) |
