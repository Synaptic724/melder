# Task: Add codegen debug dump

## Metadata
- Task ID: TASK-2026-01-25-codegen-debug-dump
- Story: STORY-2026-01-25-fast-path-codegen
- Status: draft
- Owner:
- Priority: p3
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Add a debug mode that dumps generated plan executor code for inspection.

## Scope Boundaries
- In scope:
  - Debug dump formatting and file output.
- Out of scope:
  - Executor logic changes.

## Steps / Checklist
- [ ] Add configuration flag for debug dump.
- [ ] Write generated code to a deterministic location.
- [ ] Document dump location and format.

## Deliverables
- Debug dump option for generated plan executors.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/compiled_plan_codegen.py (new)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k codegen_dump

## Risks / Rollback Notes
- Risk: dumping code leaks sensitive data.
  Mitigation: avoid dumping argument values; only structure.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; codegen debug dump pending.
