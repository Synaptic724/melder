# Task: Define Phase 8 OccurrencePlan schema and lifecycle

- Completed: 2026-01-27
- Summary: Archived Phase 8 occurrence plan schema ticket per user direction;
  checklist items remain as recorded below.

## Metadata
- Task ID: TASK-2026-01-27-phase-8-occurrence-plan-schema
- Story: STORY-2026-01-27-phase-8-occurrence-plan
- Status: complete
- Owner:
- Priority: p1
- Created: 2026-01-27
- Updated: 2026-01-27

## Objective
Define the OccurrencePlan data model, storage location, and invalidation rules
needed for Phase 8 compilation.

## Scope Boundaries
- In scope:
  - Define OccurrencePlan fields and metadata.
  - Identify storage location and lifecycle (spell vs crafter vs conduit).
  - Define plan signature inputs and invalidation triggers.
- Out of scope:
  - Implementing the compiler or runtime executor.

## Steps / Checklist
- [ ] Draft OccurrencePlan schema (fields, order, existence actions).
- [ ] Define storage location and cleanup responsibilities.
- [ ] Specify invalidation inputs (wiring changes, dirty roots, validity flags).
- [ ] Record decisions and UNKNOWNs in a design doc.

## Deliverables
- `context_compass/artifacts/README.md`

## Files / Paths Impacted
- context_compass/tasks/2026-01-27_phase-8-occurrence-plan-schema_task.md
- context_compass/artifacts/README.md

## Validation
- Not run.
- Recommended commands:
  - None (docs-only).

## Risks / Rollback Notes
- Risk: schema misses required runtime fields.
  Mitigation: tie schema directly to evidence from Phase 8 investigation.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Draft OccurrencePlan schema recorded in
`context_compass/artifacts/README.md`
with evidence mapping to MeldEngine planning outputs and UNKNOWNs for storage
location and invalidation inputs.
