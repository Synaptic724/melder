- Completed: 2026-01-19
- Summary: Implemented embargo manager scaffolding with open/close, advisory hints, diagnostics, and tests.

# Task: Implement embargo manager for scoped change control

## Metadata
- Task ID: TASK-2026-01-18-melder-change-control-embargo-manager
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-19

## Objective
Introduce an optional embargo manager that can block or hint against change
requests based on scope keys (spellbook, conduit, contract peer, cluster)
within a single AethericFrame. Embargoes are **internal state** driven by
transactions (bind/link/transfer/mutation), not standalone transactions.

## Scope Boundaries
- In scope:
  - Embargo definitions for scope keys (transaction-driven).
  - API to check/deny incoming transaction requests.
  - Advisory (non-blocking) embargo hints for agent coordination.
  - Diagnostics for active embargoes.
- Out of scope:
  - Enforcement of execution order (handled by orchestrator/admission gate).
  - Embargo TTL automation or priority scheduling.
  - Public begin_embargo/end_embargo APIs (handled implicitly by transactions).
  - Any cross-aetheric-frame embargo logic.

## Steps / Checklist
- [x] Define embargo record schema (scope key, reason tag, owner request id).
- [x] Add internal open/close APIs used by the orchestrator.
- [x] Add check API used by admission/orchestrator.
- [x] Add advisory embargo hints (non-blocking warnings).
- [x] Add diagnostics for active embargoes.
- [x] Add tests for embargo gating behavior.

## Deliverables
- Embargo manager API + tests.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- `src/melder/utilities/interfaces/interfaces.py`
- `tests/unit/melder/aether/dev_ops/`

## Validation
- Passed (user-reported).
- Recommended commands:
  - `pytest tests/unit/melder/aether/dev_ops/`

## Risks / Rollback Notes
- Risk: Embargo defaults could block all mutation unintentionally. Mitigation:
  embargo is opt-in and requires explicit scope keys.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] User walkthrough complete and acceptance criteria confirmed

## Context / Handoff Summary
- Add embargo capability to pause mutation requests by scope within a single
  frame, enabling deterministic agent coordination.
- Responsibilities (draft):
  - Maintain active embargo records (scope, reason, owner request id).
  - Provide hard-block checks and advisory hints ("soft locks").
  - Surface embargo diagnostics for agents and orchestrators.
  - Support implicit embargo lifecycles triggered by bind/link transactions.
  - Release embargoes automatically on commit/abort.
  - If a provider conduit starts a change, embargo inbound link/contract
    requests targeting that provider while the change is active.
