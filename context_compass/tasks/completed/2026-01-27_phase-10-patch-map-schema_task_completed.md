# Task: Define Phase 10 patch map schema and lifecycle

- Completed: 2026-01-27
- Summary: Defined patch map schema, lifecycle, and invalidation inputs with
  evidence mapping and UNKNOWNs for follow-up.

## Metadata
- Task ID: TASK-2026-01-27-phase-10-patch-map-schema
- Story: STORY-2026-01-27-phase-10-patch-maps
- Status: complete
- Owner:
- Priority: p1
- Created: 2026-01-27
- Updated: 2026-01-28

## Objective
Define the patch map data model, storage location, and invalidation rules
needed for Phase 10 compilation.

## Scope Boundaries
- In scope:
  - Define patch map fields and metadata for overrides/mutations.
  - Identify storage location and lifecycle (spell vs crafter vs conduit).
  - Define plan signature inputs and invalidation triggers.
- Out of scope:
  - Implementing the compiler or runtime executor.

## Steps / Checklist
- [x] Draft patch map schema (targets, slot edits, mutations).
- [x] Define storage location and cleanup responsibilities.
- [x] Specify invalidation inputs (wiring changes, dirty roots, validity flags).
- [x] Record decisions and UNKNOWNs in a design doc.

## Deliverables
- `context_compass/artifacts/fast_path_meld_plan/phase10_patch_map_schema.md`

## Files / Paths Impacted
- context_compass/tasks/2026-01-27_phase-10-patch-map-schema_task.md
- context_compass/artifacts/fast_path_meld_plan/phase10_patch_map_schema.md

## Validation
- Not run (docs-only).

## Risks / Rollback Notes
- Risk: schema misses mutation target specificity required by runtime.
  Mitigation: tie schema directly to evidence from Phase 10 investigation.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Draft patch map schema recorded in
`context_compass/artifacts/fast_path_meld_plan/phase10_patch_map_schema.md`
with override and mutation patch map shapes and open questions.
