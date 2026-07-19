# Code Description Patch: PhaseScheduler fail-fast quiesce (S4 REOPEN delta)

Lane: parallel_restore_ulid_identity_2026_07_18. Ticket: STORY-2026-07-18-loadplan-phase-compiler.
Trigger: concurrency-sensitive control-flow change (fail-fast unwind path).

## Problem (evidenced)
- PhaseLatch.record_error fires the barrier on the FIRST unit failure while sibling unit
  bodies keep executing (phase_latch.py:83-100, documented "without waiting for
  stragglers"); workers never interrupt mid-run bodies (phase_scheduler.py:594-638 - the
  cancel event is a pre-run check only).
- _run_single_phase raises PhaseExecutionError immediately (phase_scheduler.py:712-736),
  so a caller's exception handler runs CONCURRENTLY with stragglers. The restore engine's
  all-or-nothing _teardown_built then races _replay_one_book bodies: a straggler that
  passes conjure registers its conduit into the frame and late-appends to _built_stack;
  the LIFO drain can clean the straggler's SPELLBOOK first, then pop the late conduit -
  _cleanup_normal_conduit step 4 hits the dead book (del'd _spells), the broad except
  swallows the AttributeError, and _remove_root_conduit() never runs: a CLEANED HUSK
  stays registered in frame._conduits (owner red run, wide-pool chaos test).

## Control Flow (after)
1. latch.wait(timeout) wakes on first error (unchanged fail-fast wake).
2. Control thread cancels the run scope (unchanged).
3. Control thread set_exception's not-done units (unchanged - queued units fast-return
   at the worker; outcome writes stay race-guarded).
4. NEW - QUIESCE: latch.wait_all_reported(timeout_sec) parks until EVERY expected unit
   has reported (success, cooperative cancel, or failure). Termination guarantee: the
   worker loop reports every dequeued unit into its latch exactly once
   (phase_scheduler.py:594-638), and already-done units no-op to complete()
   (unit_of_work.py run_for_scheduler done()-check).
5. raise PhaseExecutionError (unchanged shape; .phase_name contract untouched).

## PhaseLatch delta (additive)
- Second event slot _all_reported_event: set when _remaining reaches zero in complete()
  AND record_error() (the fail-fast event keeps firing early; the quiesce event lags).
- New verb wait_all_reported(timeout_seconds) -> bool. True = no unit body in flight.

## Edge / Error Semantics
- Hung straggler: the quiesce is bounded by the same per-phase barrier budget
  (timeout_sec). A straggler that never reports times the quiesce out and the raise
  proceeds - the pre-fix race window returns for that pathological case only (the
  scheduler never kills threads; documented residual).
- Timeout path (PhaseTimeoutError) stays PREEMPTIVE by documented contract ("raises
  while a unit is still running" is the point of the barrier timeout); no quiesce there.
- External-cancel path (PhaseSchedulerError) unchanged.
- Empty phases and the stored-errors post-scan path are untouched (all units done there).

## Idempotency / Invariants
- One latch per phase run, never reused (existing law); the second event follows it.
- Fail-fast wake latency to the CALLER grows only by the stragglers' actual remaining
  body time, bounded by the barrier budget - correctness over speed at the unwind seam.

## Non-Goals
- No thread interruption/kill semantics; no change to worker pool lifecycle.
- No engine-side second bookkeeping of in-flight units (the latch owns that truth).
- No change to the sequential driver or the spellbook conjure lane semantics beyond the
  same safer unwind they inherit for free.

## Validation Expectations
- Latch unit rows: quiesce barrier lags the fail-fast wake; cross-thread final report
  wakes the quiesce waiter.
- Scheduler unit row: deterministic straggler regression - the straggler's final side
  effect is visible BEFORE run_all_phases raises (Event-sequenced, no sleeps).
- Existing fail-fast rows pass untouched (hung-straggler row pays the bounded quiesce
  timeout, then raises exactly as before).
- Integration: the UNCHANGED wide-pool chaos test is the law's regression
  (frame._conduits == {} after a poisoned level at width 4).
