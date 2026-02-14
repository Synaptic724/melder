# Task: Update tests for conduit-scoped change-control APIs

- Completed: 2026-02-03
- Summary: Closed per user request; test updates and validation remain pending.

## Metadata
- Task ID: TASK-2026-02-02-conduit-scoped-ccm-test-updates
- Story: N/A
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-02
- Updated: 2026-02-03

## Objective
Align test stubs and expectations with conduit-scoped change-control APIs and updated runtime context fields.

## Scope Boundaries
- In scope:
  - Update test stubs to accept conduit_id parameters for change-control calls.
  - Update tests for new per-conduit dirty tracking structures and describe keys.
  - Add missing context fields (conduit_id, cancel_event) in meld runtime tests.
  - Add missing owned spell_id unregistration stub in transfer contract tests.
- Out of scope:
  - Production code changes.
  - Any behavior changes outside tests.

## Steps / Checklist
- [ ] Update transfer-of-ownership contract test stubs for owned spell_id unregistration.
- [ ] Update meld runtime test context and change-control stubs for conduit_id + cancel_event.
- [ ] Update meld dirty-root gating tests for conduit-scoped change-control.
- [ ] Update ChangeControlManager unit tests for conduit-scoped APIs and describe keys.
- [ ] Update DevOpsManager and Aether tests for conduit_id requirements.
- [ ] Update spell crafter change-control tests to seed empty phase-5 blueprints.

## Deliverables
- Tests updated to pass against conduit-scoped change-control contracts.

## Files / Paths Impacted
- `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py`
- `tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py`
- `tests/unit/melder/aether/conduit/meld/test_meld.py`
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_manager.py`
- `tests/unit/melder/aether/dev_ops/test_dev_ops_manager.py`
- `tests/unit/melder/aether/test_aether.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `context_compass/tasks/completed/2026-02-02_conduit-scoped-ccm-test-updates.md`

## Validation
- Not run.
- Recommended commands:
  - pytest -q tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py
  - pytest -q tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_manager.py
  - pytest -q tests/unit/melder/aether/dev_ops/test_dev_ops_manager.py
  - pytest -q tests/unit/melder/aether/test_aether.py
  - pytest -q tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py
  - pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py
  - pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py

## Risks / Rollback Notes
- Risk: Test expectations drift from production contracts.
  Mitigation: Update tests strictly to reflect current method signatures and per-conduit state maps.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Created task to update tests for conduit-scoped change-control APIs and context
fields. Pending test updates and validation. Closed per user request with test
work still outstanding.
