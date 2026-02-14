# Task: Align transfer-of-ownership test stubs with conduit-scoped revalidation

- Completed: 2026-02-03
- Summary: Aligned transfer-of-ownership test stubs with conduit-scoped revalidation and owned spell_id unregistration.

## Metadata
- Task ID: TASK-2026-02-02-transfer-ownership-test-stub-alignment
- Story: N/A
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-02
- Updated: 2026-02-03

## Objective
Update transfer-of-ownership test stubs so they match the new conduit-scoped revalidator contract and owned spell_id unregister behavior.

## Scope Boundaries
- In scope:
  - Add `_revalidate_fn_by_conduit` to `FakeChangeControlManager`.
  - Add `_unregister_owned_spell_id` to `FakeSpellbook`.
  - Update tests to set the conduit-scoped revalidator map.
- Out of scope:
  - Production code changes.
  - Any new transfer or spellbook behaviors.

## Steps / Checklist
- [x] Update `FakeChangeControlManager` with conduit-scoped revalidator storage.
- [x] Add `FakeSpellbook._unregister_owned_spell_id` stub.
- [x] Update incident tests to use `_revalidate_fn_by_conduit`.
- [ ] Re-run the targeted transfer tests (optional, user-run; not run in this task).

## Deliverables
- Updated transfer test stubs and incident tests aligned with current contracts.

## Files / Paths Impacted
- `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py`
- `context_compass/tasks/2026-02-02_transfer_ownership_test_stub_alignment_task.md`

## Validation
- Not run.
- Recommended commands:
  - pytest -q tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py

## Risks / Rollback Notes
- Risk: Stub contract drift hides real regressions.
  Mitigation: Keep stub behavior aligned with production contract changes.

## Done Checklist
- [x] Required steps complete; optional validation not run
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Aligned transfer-of-ownership test stubs with the conduit-scoped revalidator map and owned spell_id unregister helper in `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py`. Validation not run.
