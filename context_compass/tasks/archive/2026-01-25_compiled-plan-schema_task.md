# Task: Define RootExecutionPlan schema and invariants

## Metadata
- Task ID: TASK-2026-01-25-compiled-plan-schema
- Story: STORY-2026-01-25-compiled-plan-model
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Define the RootExecutionPlan data model, including step layout, dependency
indexing, and instance key representation.

## Scope Boundaries
- In scope:
  - Structure-of-arrays plan fields and invariants.
  - Instance key and dependency index encoding.
- Out of scope:
  - Plan compilation algorithms.

## Steps / Checklist
- [ ] Review RootResolutionBlueprint and MeldEngine usage patterns.
- [ ] Draft RootExecutionPlan fields and invariants.
- [ ] Define instance key representation and dependency index layout.
- [ ] Document plan ownership and cleanup requirements.

## Deliverables
- RootExecutionPlan schema doc and class skeleton.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/compiled_plan.py (new)
- src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k plan

## Risks / Rollback Notes
- Risk: plan layout is too complex for fast execution.
  Mitigation: keep arrays flat and avoid nested dicts.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; plan schema design pending.
