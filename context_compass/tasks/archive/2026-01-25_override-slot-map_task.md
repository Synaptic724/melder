# Task: Compile override slot map for plans

## Metadata
- Task ID: TASK-2026-01-25-override-slot-map
- Story: STORY-2026-01-25-override-mutation-fast-path
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Compile a SocketRef to plan slot map so overrides can patch values without
rebuilding override maps at runtime.

## Scope Boundaries
- In scope:
  - SocketRef to slot pointer mapping.
- Out of scope:
  - Mutation patching.

## Steps / Checklist
- [ ] Identify socket reference data in RootResolutionBlueprint.
- [ ] Build slot pointer mapping for each plan step.
- [ ] Store map in RootExecutionPlan.

## Deliverables
- Override slot map in plan data.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py
- src/melder/aether/conduit/meld/compiled_plan.py (new)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k override_slot

## Risks / Rollback Notes
- Risk: slot map misses path-specific sockets.
  Mitigation: include occurrence path in mapping key.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; override slot map compilation pending.
