# Task: Compile occurrence plan from root blueprints

## Metadata
- Task ID: TASK-2026-01-25-occurrence-plan-compilation
- Story: STORY-2026-01-25-plan-compilation-phase8
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Compile occurrence graph expansion and execution order during conjure for each
RootResolutionBlueprint.

## Scope Boundaries
- In scope:
  - Occurrence expansion and deterministic execution order.
  - Existence.many path expansion handling.
- Out of scope:
  - Arg binding compilation.

## Steps / Checklist
- [ ] Map MeldEngine occurrence graph logic to compiler inputs.
- [ ] Build occurrence list and execution order for each root.
- [ ] Encode instance keys and canonical occurrences where needed.

## Deliverables
- Occurrence plan data structure attached to RootExecutionPlan.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- src/melder/aether/conduit/meld/compiled_plan.py (new)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k occurrence

## Risks / Rollback Notes
- Risk: occurrence expansion diverges from MeldEngine behavior.
  Mitigation: mirror existing logic and add tests.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; occurrence plan compilation pending.
