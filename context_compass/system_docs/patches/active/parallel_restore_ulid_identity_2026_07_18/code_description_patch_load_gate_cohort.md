# Code Description Patch: cohort-aware LoadGate (S3)

Lane: parallel_restore_ulid_identity_2026_07_18.
Ticket: STORY-2026-07-18-cohort-aware-load-gate.
This is the concurrency-sensitive entry-gate artifact required by
patch_framework_gating.md before ANY gate code changes.

## Control Flow (after)

1. `acquire(label)` - UNCHANGED law (refuses when any holder exists, including the caller;
   records holder thread id + label) - plus: resets the span's cohort to empty. A span
   always begins as a cohort of one (the holder), byte-identical to today.
2. `enroll_worker(thread_ident)` (gate) / `Aether.enroll_load_worker(thread_ident)`
   (delegating verb) - HOLDER-ONLY: the span owner names its worker threads. Under the one
   existing condition lock:
   - cleaned gate -> RuntimeError (spans cannot exist after teardown);
   - no holder -> RuntimeError "no active load span" (enrollment outside a span is a
     pairing bug, mirroring the nested-acquire law);
   - caller is not the holder thread -> RuntimeError naming the holder label (workers never
     self-enroll; authority stays with the span owner);
   - ident must be a positive int, bools rejected -> ValueError otherwise;
   - set-add semantics: re-enrolling is an idempotent no-op; enrolling the holder's own
     ident is a harmless no-op by construction (the holder already passes).
3. `withdraw_worker(thread_ident)` / `Aether.withdraw_load_worker(...)` - HOLDER-ONLY,
   same refusals as enroll; set-discard semantics (withdrawing a non-member is an
   idempotent no-op). A withdrawn thread parks at its NEXT passage check; a currently
   parked thread re-checks membership on every condition wake, so withdrawal takes effect
   at the next wake, never by interruption.
4. `wait_for_passage(timeout)` - passes immediately when the gate is open, the caller IS
   the holder, OR the caller is a cohort member; otherwise parks on the condition exactly
   as today (same timeout, same teach-grade error naming the holder label). Membership is
   re-read under the lock on every loop iteration.
5. `release()` - UNCHANGED holder-only law; additionally clears the cohort
   unconditionally. NO membership survives a span; the single-thread world is restored
   exactly as today.
6. `cleanup()` - tombstone posture preserved: holder slots become None tombstones and the
   cohort set is CLEARED IN PLACE (kept, not deleted) for the same late-waiter safety
   rationale already documented on the holder slots. Terminal state remains OPEN.
7. `describe()` - additionally reports cohort_size and a detached sorted cohort id list.

## Edge / Error Semantics

- Enrollment races: all cohort mutation and every membership read happen under the ONE
  existing condition lock. No new locks -> no new lock-order surface; the existing law
  (gate condition never awaited while holding the mediator lock) is untouched because the
  mediator call sites are untouched.
- Abandoned span (holder dies without release): identical to today - the gate stays held
  until Aether teardown cleans it; cleanup clears holder AND cohort together. This patch
  does not add liveness detection (non-goal), it only guarantees the cohort cannot
  outlive the span under any exit: release clears it, cleanup clears it.
- Foreign threads: park/timeout behavior is BYTE-IDENTICAL - a non-member observes exactly
  the same wait loop and the same RuntimeError text at deadline.
- Aether delegating verbs raise RuntimeError when the LoadGate is unavailable (mirrors
  acquire_load_authority's existing posture).

## Idempotency

- enroll x2 = one membership; withdraw of a non-member = no-op; release/cleanup clear all.
- acquire after a completed span starts from an empty cohort by construction.

## Explicit Non-Goals

- NO change to the one-load-at-a-time law or nested-acquire refusal.
- NO change to foreign-thread park semantics, timeouts, or diagnostics.
- NO mediator changes (passage remains gate-internal; call sites untouched).
- NO change to acquire_load_authority's drain protocol.
- NO liveness/watchdog machinery for dead holders or dead workers.
- Loader-side enrollment of scheduler pool threads is S4 scope (the pool exists there);
  S3 delivers the capability plus its adversarial suite driving real threads directly.

## Validation Expectations

Adversarial suite (new unit file beside the existing gate tests, >= 20 tests/100 LOC on
the delta): member passes while held; foreign thread parks and times out with the existing
error; holder-only enrollment (worker self-enroll refuses; no-span refuses; cleaned
refuses); invalid idents refuse; withdraw-then-check parks; parked member wakes on
release; release clears cohort (post-span foreign park proves it); cleanup terminal-open
wakes parked foreigners; describe reports cohort truthfully; re-enroll/withdraw
idempotency. Owner-run 3.14t.
