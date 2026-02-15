# Task: Fix missing stub data in unit tests for recent phase updates

- Completed: 2026-01-27
- Summary: Archived test-stub data fix task per user direction; stub updates and
  phase-order coverage noted in handoff summary below.

## Metadata
- Task ID: TASK-2026-01-27-test-stub-missing-data-fix
- Story: N/A
- Status: complete
- Owner: codex
- Priority: p1
- Created: 2026-01-27
- Updated: 2026-01-27

## Objective
Update unit-test stubs to include required data fields so tests reflect current contracts after phase changes.

## Scope Boundaries
- In scope:
  - Identify failing unit tests with stub data gaps.
  - Update stubs/fixtures and expectations to include required fields.
- Out of scope:
  - Runtime code changes (meld, runtime, engine).
  - Integration tests.

## Steps / Checklist
- [x] Identify failing unit tests with stub data gaps.
- [x] Update stubs/fixtures to include required data.
- [x] Align expectations with updated contracts.
- [x] Update handoff summary.

## Deliverables
- Updated unit tests with complete stub data.

## Files / Paths Impacted
- tests/unit/** (exact files to be identified)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/...

## Risks / Rollback Notes
- Risk: overfitting tests to implementation details.
- Rollback: revert test-only changes.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Updated unit test stubs to include spell_id_pool and added Phase 8 coverage in phase-order tests. Integration failures remain out of scope for this task.
