# Task: Implement change orchestrator for staged commit/rollback

## Metadata
- Task ID: TASK-2026-01-18-melder-change-control-orchestrator
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: completed
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-20

## Objective
Implement a change orchestrator that acts as the **single serialized admission
gate** for change requests, stages mutations, runs structural validation, and
commits changes atomically (or aborts on failure). The orchestrator is rule-
based and does not maintain a queue or thread pool; admitted work can proceed
in parallel once the gate releases.

## Scope Boundaries
- In scope:
  - Staged mutation pipeline: preflight, stage, validate, commit/abort.
  - Integration points for bind (scan requires active bind transaction),
    link/contract, unlink, transfer, cluster share.
  - Admission lock + conflict/embargo checks for every request.
  - Post-commit dirty marking and resolution gating.
- Out of scope:
  - Conflict/embargo policy decisions (handled elsewhere).
  - Request queues, priority scheduling, SLA/TTL, or DLQ behavior.
  - Any cross-aetheric-frame coordination.

## Steps / Checklist
- [x] Define orchestrator interface + admission lock.
- [x] Implement staged updates for each request type (local + contracted maps).
  - [x] Bind updates staged binding keys during active bind transactions.
- [x] Apply conflict/embargo checks before admission.
- [x] Open/close implicit embargoes for bind/link transactions.
- [x] Run structural phases 1-4 for affected spells before commit.
- [x] Commit staged maps and mark dirty collections/roots as needed.
- [x] Abort path clears staged data and leaves live state unchanged.

## Deliverables
- Change orchestrator implementation with staged commit/rollback behavior.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/aether/aether.py`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/integration/melder/`

## Risks / Rollback Notes
- Risk: Staging complexity can diverge from live state. Mitigation: keep
  staged maps minimal and validate before commit.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] User walkthrough complete and acceptance criteria confirmed

## Context / Handoff Summary
- Orchestrator performs the staged mutation pipeline and ensures atomic
  visibility of changes on commit, acting as the **single admission gate** that
  all change requests must funnel through.
- Responsibilities (draft):
  - Serialize admission via a lock and consult conflict/embargo managers.
  - Stage changes per request type (local bindings, contracted maps, cluster shares).
  - Run structural phases 1-4 before commit.
  - Abort cleanly with no visibility changes on failure.
  - Release embargoes on commit/abort for deterministic lifecycles.
  - Allow parallel execution only when conflict checks declare scopes disjoint.
- Spellbook bind now updates staged binding keys mid-transaction; integration
  test coverage added in `tests/integration/melder/spellbook/test_spellbook_integration_core.py`.
## Implementation Notes
- Admission gate + conflict/embargo checks are implemented in the
  orchestrator; staging/commit/abort now run through ChangeControlManager.
- Implicit embargoes open on admission using derived scope keys and
  release on commit/abort.
- Orchestrator tracks staged mutation metadata per admitted request for
  diagnostics and commit/abort hooks.
- Commit hooks can run structural validation and dirty-marking logic.
- ChangeControlManager now enables a default structural validator for bind
  transactions and a default dirty marker for binding/contracted frame keys.
- Dirty marking now considers staged contract keys in addition to binding keys.
- ChangeControlManager now exposes a staged-metadata update API so callers can
  refresh binding/contract metadata between admission and commit.
- Spellbook.bind now refreshes staged binding keys for active bind transactions
  (via `update_staged_request`) so commit-time hooks can use accurate metadata.
