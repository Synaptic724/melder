# Task: Implement RootExecutionPlan executor

## Metadata
- Task ID: TASK-2026-01-25-fast-path-executor
- Story: STORY-2026-01-25-fast-path-runtime
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Implement a fast-path executor that runs RootExecutionPlan steps with minimal
runtime overhead.

## Scope Boundaries
- In scope:
  - Plan execution loop and registration routing.
- Out of scope:
  - Codegen executor.

## Steps / Checklist
- [ ] Implement FastMeldExecutor to run plan steps.
- [ ] Use precomputed dependency indices and instance keys.
- [ ] Register instances into Creations and LesserCreations as needed.

## Deliverables
- FastMeldExecutor implementation and integration points.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/fast_meld_executor.py (new)
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k fast_executor

## Risks / Rollback Notes
- Risk: executor diverges from MeldEngine semantics.
  Mitigation: add unit tests comparing fast and slow path outputs.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; fast-path executor pending.
