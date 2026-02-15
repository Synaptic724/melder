- Completed: 2026-01-19
- Summary: Implemented scope-overlap conflict checks and orchestrator admission gating.
- Summary: Added unit coverage for overlap vs disjoint scopes and admission rejection.

# Task: Implement conflict manager for transaction scope overlap

## Metadata
- Task ID: TASK-2026-01-18-melder-change-control-conflict-manager
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-19

## Objective
Define and implement the conflict manager that decides when two change requests
can run in parallel vs must be serialized based on scope-key overlap.

## Scope Boundaries
- In scope:
  - Scope-key overlap rules (exact match, prefix match, or custom).
  - Hash-aware matching using the scope hashing rules.
  - Conflict check API used by the admission gate/orchestrator.
  - Unit tests for conflict rules.
- Out of scope:
  - Embargo policy logic.
  - Execution staging or orchestration.
  - Any cross-aetheric-frame coordination.

## Steps / Checklist
- [x] Define conflict rule semantics for scope keys.
- [x] Implement overlap detection API (raw + hashed keys).
- [x] Add tests covering overlap vs disjoint cases.
- [x] Wire conflict manager into admission/orchestrator hooks.

## Deliverables
- Conflict manager API + unit tests.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- `src/melder/utilities/interfaces/interfaces.py`
- `tests/unit/melder/aether/dev_ops/`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/aether/dev_ops/`

## Risks / Rollback Notes
- Risk: Overly strict overlap rules could serialize everything. Mitigation:
  start with explicit scope keys per request type and keep rules minimal.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] User walkthrough complete and acceptance criteria confirmed

## Context / Handoff Summary
- Build conflict detection so transactions only serialize when scopes overlap,
  enabling parallelism for disjoint requests.
- Responsibilities (draft):
  - Compare normalized scope keys + scope hashes (spellbook_id, conduit_id,
    contract keys, cluster_id).
  - Return overlap/compatibility verdicts for the admission gate.
  - Provide deterministic ordering when conflicts are detected.
