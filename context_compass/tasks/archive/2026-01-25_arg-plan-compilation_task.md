# Task: Compile argument binding recipes per step

## Metadata
- Task ID: TASK-2026-01-25-arg-plan-compilation
- Story: STORY-2026-01-25-plan-compilation-phase8
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Compile argument binding recipes so each plan step can assemble args without
runtime graph traversal.

## Scope Boundaries
- In scope:
  - Dependency index mapping for args and kwargs.
  - Default and constant handling rules.
- Out of scope:
  - Override patching.

## Steps / Checklist
- [ ] Inspect SpellRequirements and local DAG data.
- [ ] Map dependencies to step indices for each parameter.
- [ ] Encode args and kwargs layouts in plan arrays.

## Deliverables
- Arg plan arrays and mapping rules in RootExecutionPlan.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/requirements/spell_requirements.py
- src/melder/aether/conduit/meld/compiled_plan.py (new)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k args

## Risks / Rollback Notes
- Risk: mismatch between arg plan and callable signature.
  Mitigation: reuse existing requirements metadata and add tests.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; arg plan compilation pending.
