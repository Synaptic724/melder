# Code description patch: AbstractElasticPool retention (elastic_pool_retention_2026_10_12)

## Control flow
1. `__init__`: as before, plus `now = clock()`; `_last_miss_at = now - settle_time_seconds` (no pressure yet);
   `_next_decay_at = now + settle_time_seconds`; `_decay_step = max(1, max(baseline, 1) * decay_pct // 100)`.
2. `acquire`: pop an idle object; on IndexError build one and call `_note_miss()`; count it in use; prepare it.
3. `_note_miss()` (no lock): `_last_miss_at = now`; `_next_decay_at = max(_next_decay_at, now + settle)`.
4. `release` (and the kernel pools' own release paths): append; if `len(idle) <= baseline_idle` return; else
   `_rebalance_after_return()`.
5. `_rebalance_after_return()`: if `max_idle == baseline_idle` (fixed capacity) pop the oldest idle object, destroy
   it and return - no clock read, no lock, the pre-0.2.8234 eviction; else `now = clock()`; if `len(idle) <= target`
   and `now < _next_decay_at` return (no lock); else destroy every object `_rebalance_locked(now)` returns.
6. `_rebalance_locked(now)` under `_lock`:
   a. under pressure (`now - _last_miss_at < settle`): if `len(idle) > target`, stretched = min(max_idle, idle +
      idle * stretch_pct // 100); if it exceeds the target, store it and `_decay_step = max(1, stretched * decay_pct //
      100)`; keep = max_idle (returns racing this one stretch through their own call, so a returning burst loses
      nothing);
   b. otherwise, if `now >= _next_decay_at`: if target > baseline, steps = 1 + (now - _next_decay_at) // interval and
      target = max(baseline, target - steps * _decay_step); then `_next_decay_at = now + interval`; keep = target;
   c. detach `min(len(idle) - keep, _decay_step)` objects with `popleft()` (oldest first) and return them.

## Edge / error semantics
- Integer arithmetic replaces the float percent products (the step for 29% of 100 is 29, not 28).
- A deque emptied by concurrent acquires during the trim ends the trim early (IndexError breaks the loop).
- A pool whose idle count exceeds `max_idle` under pressure stretches to `max_idle` and trims the rest one decay step
  per return.
- Racing `_note_miss` writes only move the decay deadline by the width of the race; the target itself is written under
  `_lock` only.
- A `destroy_object` failure propagates unchanged from the release that triggered the trim, as the eviction's
  did; the detached objects after the failing one go back to the oldest end of the idle deque (a `finally`), so
  none is dropped undestroyed and a later trim retries them.

## Invariants / idempotency
`baseline_idle <= target <= max_idle`. `cleanup()` is unchanged (idempotent, under `_lock`, destroys the idle set).

## Non-goals
No timer thread, no live cap, no change to `prepare_object`, `create_object`, `destroy_object` or `describe()` keys.
