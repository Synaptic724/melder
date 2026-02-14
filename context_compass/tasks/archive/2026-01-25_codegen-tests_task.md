# Task: Add tests for codegen executors

## Metadata
- Task ID: TASK-2026-01-25-codegen-tests
- Story: STORY-2026-01-25-fast-path-codegen
- Status: draft
- Owner:
- Priority: p3
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Add tests that validate generated code executors produce correct instances and
registration behavior.

## Scope Boundaries
- In scope:
  - Unit tests for codegen executor behavior.
- Out of scope:
  - Benchmark results.

## Steps / Checklist
- [ ] Add tests for generated executor correctness.
- [ ] Add tests for signature invalidation and cache refresh.

## Deliverables
- Unit tests for codegen executors.

## Files / Paths Impacted
- tests/unit/melder/aether/conduit/meld/test_codegen_executor.py (new)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k codegen_executor

## Risks / Rollback Notes
- Risk: tests depend on codegen formatting.
  Mitigation: assert behavior, not exact source.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; codegen tests pending.
