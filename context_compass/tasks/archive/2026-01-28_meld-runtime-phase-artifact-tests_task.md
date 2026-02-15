# Task: Add tests for Phase 9/10 artifact wiring parity

## Metadata
- Task ID: TASK-2026-01-28-meld-runtime-phase-artifact-tests
- Story: STORY-2026-01-28-meld-runtime-phase-artifacts
- Status: completed
- Owner: codex
- Priority: p1
- Created: 2026-01-28
- Updated: 2026-01-28

## Objective
Add regression tests that prove Phase 9/10 artifact wiring preserves current
meld runtime behavior for overrides, contracts, and mutation rewires.

## Scope Boundaries
- In scope:
  - Unit tests for MeldRuntime/MeldEngine artifact usage.
  - Component or integration tests if needed to validate behavior parity.
- Out of scope:
  - Performance benchmarks.
  - Unrelated test refactors.

## Steps / Checklist
- [x] Identify current behavior cases to lock down (override precedence, contract
      payloads, mutation rewires, missing artifacts).
- [x] Add unit tests for runtime/engine paths using phase artifacts.
- [x] Add component tests if unit tests cannot capture required behavior.
- [x] Confirm tests fail on old runtime paths and pass on new wiring.

## Deliverables
- Test coverage for Phase 9/10 artifact wiring and runtime parity.

## Files / Paths Impacted
- tests/unit/melder/aether/conduit/meld/
- tests/unit/melder/spellbook/spell_crafter/
- tests/component/melder/ (if needed)

## Validation
- PYTHONPATH=/workspace/melder_private pytest -q

## Risks / Rollback Notes
- Risk: Tests encode assumptions not aligned with current behavior.
- Rollback: adjust tests to mirror evidence-based behavior.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Created to lock down behavior parity as Phase 9/10 artifacts replace runtime
fallback logic.
