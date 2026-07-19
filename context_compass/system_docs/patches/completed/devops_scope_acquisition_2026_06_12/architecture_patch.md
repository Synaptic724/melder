# architecture_patch

## Metadata
- Patch ID: devops_scope_acquisition_2026_06_12
- Status: in_progress
- Owner: codex
- Agent Name: reviewer_0
- Created: 2026-06-12T21:42:50Z
- Updated: 2026-06-12T21:42:50Z

## Patch Scope and Non-Goals
- Objective:
  - make scope acquisition the single admission gate for change-control
    transactions (embargo table becomes the lock table)
  - add claim modes (exclusive/shared/intent) with one static compatibility
    matrix so non-overlapping and share-compatible work admits in parallel
  - replace the coarse root-FIFO pending model with scope-local blocking
    waits plus wake-on-release and the existing timeout bound
  - give transaction strategies a commit-delta seam so registry topology is
    maintained by transactions instead of runtime reporters
  - add last-reported fact records so information strategies can skip
    re-derivation when all changes since the baseline flowed through the plane
- Non-goals:
  - removing `queue_competing_root_transactions` from the frame configuration
    surface (deprecated in mediator behavior; field removal is a follow-up)
  - implementing the full information-strategy catalog (deep views, audits)
  - new transaction families (upgrade/cleanup/removal/mutation remain future)
  - meld/read-path changes (readers never enter the admission plane)

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| embargo manager | modify | becomes the moded scope lock table with atomic acquire/wait/release | none |
| orchestrator admission | modify | admission consults scope acquisition only; conflict scan retired | embargo manager |
| transaction mediator | modify | pending = wait-then-retry admission; coarse FIFO removed; commit-delta dispatch | orchestrator, strategies |
| transaction request/manager | modify | requests carry per-scope claim modes | none |
| transaction strategies | modify | emit moded claims; gain `apply_commit_delta` | strategy ABC |
| devops information registry | modify | gains last-reported fact records and report/lookup surface | none |

## Interface and Boundary Deltas
- Boundary delta 1: `ChangeControlConflictManager` is no longer consulted at
  admission; the class remains for hash-normalization tooling but the
  orchestrator decision path reads the lock table only.
- Boundary delta 2: registry relational maps (link edges, cluster membership)
  are written by strategy commit deltas under held scopes, never by runtime
  reporters. Frame-level ownership register/unregister at conduit
  register/unregister remains the sanctioned boundary write.
- Interface delta 1: `ChangeControlTransactionRequest` gains
  `scope_claims: Tuple[Tuple[str, str], ...]` ((scope_key, mode) pairs);
  absent claims default to exclusive mode for compatibility.
- Interface delta 2: `TransactionStrategy` gains abstract
  `apply_commit_delta(...)`; all registered families implement it.
- Interface delta 3: mediator `queue_competing_root_transactions` becomes a
  deprecated no-op input; `max_transaction_wait_time_in_seconds` now bounds
  scope-wait, not FIFO-wait.

## Cross-Component Invariants
- Admission is serialized under the orchestrator lock; execution is parallel.
- A transaction holds all its claimed scopes from admission until
  commit/abort releases them; commit deltas are applied while scopes are held.
- Any two transactions with incompatible claims on one scope never run
  concurrently; compatibility is decided only by the static matrix.
- Registry fact currency invariant: last-reported baseline plus committed
  deltas equals current truth for every transaction-covered fact family.
- Waiting requests are bounded by the configured timeout and surface blocking
  evidence (scope keys + holder request ids) on expiry.

## Migration and Rollout Order
1. Land the moded lock table inside the embargo manager (default mode X
   preserves existing semantics exactly).
2. Switch orchestrator admission to acquisition; retire the conflict scan.
3. Replace mediator FIFO waiting with scope-wait-and-retry admission.
4. Add request claim modes and strategy-emitted claims (bind refines to
   S-on-spellbook / IX-on-frame; others stay X until measured).
5. Add `apply_commit_delta` and wire mediator finalize to dispatch it before
   embargo release.
6. Add registry fact records + report path from commit deltas.
7. Tests for matrix, parallel admission, wait/timeout/wake, delta application.

## Rollback Strategy
- Rollback trigger: admission regressions (deadlock, lost wakeup, or
  incorrect parallel admission) in the change-control unit ring.
- Rollback steps: revert the mediator/orchestrator/embargo commits for this
  patch id; the conflict manager path is restored by reverting the
  orchestrator change only.
- Post-rollback verification: existing transaction-surface unit ring passes.

## Validation Expectations and Evidence Plan
- Unit ring: new tests under
  `tests/unit/melder/aether/dev_ops/change_control_manager/` covering matrix
  truth table, disjoint parallel admission, S/S same-scope admission, X
  collision wait + wake-on-release, timeout with blocking evidence,
  re-entrant same-owner claims, commit-delta registry application, and fact
  record baselines.
- Runner: user-run `pytest tests/unit/melder/aether/dev_ops -q`
  (agent reports "Not run." unless executed).

## Ticket Coverage Map
- Epic: `tickets/epics/2026-05-30_simplify_mediator_root_policy_and_lazy_devops_reporting_epic.md`
- Story: `tickets/stories/2026-06-12_implement_scope_acquisition_control_plane_story.md`
- Tasks: `tickets/tasks/2026-06-12_implement_scope_lock_table_and_pending_acquisition_task.md`

## Unknowns and Decision Requests
- UNKNOWN: whether binding-key X-claims are admission-relevant or fully
  guarded by Phase-4 duplicate validation; bind keeps coarse claims
  (S spellbook + X binding keys when supplied) until measured.
- UNKNOWN: strict fairness under contention is not guaranteed (notify-all
  retry, arrival-biased); revisit if starvation is observed in field tests.
- DECISION (user, 2026-06-12 chat): blocking pending (thread waits) over
  resumable handles; generation/coverage accounting over time-based dirt;
  registry stays detail-rich ("devops station") with strategy-paid freshness.

## Context / Handoff Summary
- What changes: admission becomes one O(scopes) lock-table acquisition with
  modes; pending becomes scope-local blocking wait; registry topology is
  transaction-maintained with last-reported baselines.
- What remains: config field removal, information-strategy catalog, audit
  sampling, new families.
- Next entrypoint:
  `tickets/tasks/2026-06-12_implement_scope_lock_table_and_pending_acquisition_task.md`
