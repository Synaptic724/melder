# code_description_patch_dev_ops_transactions

## Metadata
- Patch ID: devops_scope_acquisition_2026_06_12
- Component: dev_ops change-control transaction plane
- Status: in_progress
- Owner: codex
- Agent Name: reviewer_0
- Created: 2026-06-12T21:42:50Z
- Updated: 2026-06-12T21:42:50Z

## Why This Document Exists (Triggers)
- Concurrency-sensitive change: lock table, condition waits, wake-on-release.
- Policy-gate pipeline change: admission decision path is replaced.
- State-machine change: request waiting/timeout semantics added.

## Claim Modes and Compatibility (Commitment)
- Modes: `ClaimMode.EXCLUSIVE` ("x"), `ClaimMode.SHARED` ("s"),
  `ClaimMode.INTENT` ("ix"). StrEnum; values stable in payloads/logs.
- Compatibility matrix (held vs requested -> grantable):
  - X vs anything -> False; anything vs X -> False
  - S vs S -> True; S vs IX -> False; IX vs S -> False
  - IX vs IX -> True
- Same-owner rule: an owner's own held claims never block it; re-request of a
  held key with equal-or-weaker mode is a no-op; S->X upgrade is granted only
  when the owner is the sole holder of that key, else it waits like any
  acquisition.
- Default mode when unspecified: EXCLUSIVE (preserves pre-patch semantics).

## Acquisition Control Flow (Commitment)
- `try_acquire(owner_request_id, claims, reason_tag) -> AcquisitionDecision`:
  all-or-nothing under the manager lock; on failure returns blocking
  evidence tuples `(scope_key, holder_request_id, holder_mode)` and acquires
  nothing.
- `acquire_blocking(owner, claims, reason_tag, timeout) -> AcquisitionDecision`:
  loop { try_acquire; on failure wait on the manager `Condition` with
  remaining-deadline timeout }. Returns the failing decision on timeout; the
  caller raises. Spurious wakeups are safe because acquisition re-evaluates
  the full claim set every iteration.
- `release_owner(owner_request_id)`: removes every claim held by the owner,
  then `notify_all`. Commit and abort both route here through
  `release_implicit_embargoes`.
- Mediator admission loop: build request -> admission attempt (orchestrator,
  serialized) -> on scope rejection, `wait_for_release(blocking, deadline)`
  then retry admission -> on deadline, raise `RuntimeError` with blocking
  evidence. The orchestrator lock is never held while waiting.

## Idempotency and Error Semantics (Commitment)
- Acquisition failure leaves the lock table untouched (no partial grants).
- `release_owner` is idempotent; unknown owners no-op.
- Extension (`extend_embargoes`) remains unconditional-add for an active
  owner (pre-patch semantic preserved); extensions default to EXCLUSIVE.
- Cleanup marks the manager cleaned, then notifies all waiters; blocked
  acquirers observe the cleaned state and raise instead of hanging.
- Commit-delta failures poison the session abort path exactly like commit
  hook failures today: abort pipeline runs, orchestrator abort releases
  scopes, the exception propagates.

## Ordering Commitments
- Strategy `apply_commit_delta` runs after the session commit pipeline and
  before `orchestrator.commit_request`, i.e. while the transaction still
  holds its scopes. Deltas are therefore race-free against overlapping
  writers by construction.
- Fact records are stamped inside `apply_commit_delta` via
  `registry.report_fact(family, region, reporter_request_id)`.

## Explicit Non-Goals
- No per-scope condition variables (single manager condition; revisit only
  with measured contention).
- No strict FIFO fairness guarantee under contention; timeout bounds wait.
- No async/handle-based pending; threads block by design (CommandOps actors
  own their threads).
- No changes to meld/read paths.

## Edge Cases Considered
- Same-thread parallel roots: allowed pre-patch (FIFO bypass for sole-owner
  thread); post-patch this is naturally allowed because admission is
  scope-driven, not thread-driven. Distinct local roots with disjoint scopes
  admit; overlapping ones wait on themselves -> immediate timeout would be a
  self-deadlock, so acquisition treats claims already held by sessions owned
  by the current thread as same-owner-compatible ONLY when the owner request
  id matches; a thread starting a second root that overlaps its own first
  root will time out with evidence naming its own first request. This is
  intentional: same-thread nesting should join, not start parallel roots.
- Waiter wakes after manager cleanup: raises cleaned-state error.
- Zero-claim requests: admit immediately (no scopes to vet).
