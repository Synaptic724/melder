# Task: Define plan storage and cleanup lifecycle

## Metadata
- Task ID: TASK-2026-01-25-plan-storage-lifecycle
- Story: STORY-2026-01-25-compiled-plan-model
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Define where plans live (blueprint, spell, or conduit) and how they are cleaned
up with existing lifecycle rules.

## Scope Boundaries
- In scope:
  - Storage location decisions.
  - Cleanup and ownership rules.
- Out of scope:
  - Plan compilation logic.

## Steps / Checklist
- [ ] Review cleanup rules for Spellbook, Conduit, and RootResolutionBlueprint.
- [ ] Decide storage location and ownership for plan objects.
- [ ] Define cleanup order and nulling requirements.

## Deliverables
- Plan storage and cleanup policy documented.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py
- src/melder/aether/conduit/conduit.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/spellbook -k cleanup

## Risks / Rollback Notes
- Risk: plan objects survive cleanup and leak memory.
  Mitigation: enforce deterministic cleanup and nulling.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; plan storage and cleanup policy pending.
