# Task: Update MeldEngine kwargs unit tests for instance-based wiring

## Metadata
- Task ID: TASK-2026-01-28-meld-engine-kwargs-tests-update
- Story: N/A
- Status: in_progress
- Owner: codex
- Priority: p2
- Created: 2026-01-28
- Updated: 2026-01-28

## Objective
Align MeldEngine kwargs unit tests with the instance-based wiring APIs after the phase migration, and reference phase artifacts where relevant.

## Scope Boundaries
- In scope:
  - Replace `_build_kwargs_for_node` tests with `_build_kwargs_for_instance` coverage.
  - Add shared-instance canonical occurrence coverage.
- Out of scope:
  - Behavior changes in meld runtime/engine.
  - Integration/component test updates.

## Steps / Checklist
- [x] Replace node-based kwargs tests with instance-based tests.
- [x] Add coverage for shared canonical occurrence lookup.
- [ ] Review docstrings/comments for phase references.

## Deliverables
- Updated unit tests targeting `_build_kwargs_for_instance`.

## Files / Paths Impacted
- tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine.py

## Risks / Rollback Notes
- Risk: Tests could overfit to internal ordering. Keep assertions contract-level.
- Rollback: Revert test updates and restore prior node-based tests.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Updating kwargs tests to target instance-based wiring and Phase 8 occurrence graphs. Pending final review and acceptance.
