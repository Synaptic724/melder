# Task: Compile mutation patch map for plans

## Metadata
- Task ID: TASK-2026-01-25-mutation-patch-map
- Story: STORY-2026-01-25-override-mutation-fast-path
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Compile patch instructions for mutation overrides so the plan can be adjusted
without rebuilding a RootResolutionBlueprint.

## Scope Boundaries
- In scope:
  - Mapping mutation override inputs to dependency rewiring instructions.
- Out of scope:
  - Full GraphMutator replacement.

## Steps / Checklist
- [ ] Review GraphMutator mutation overlay logic.
- [ ] Define patch instruction format for plan steps.
- [ ] Store mutation patch map in RootExecutionPlan.

## Deliverables
- Mutation patch map and patch rules.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/overrides/graph_mutator.py
- src/melder/aether/conduit/meld/compiled_plan.py (new)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k mutation

## Risks / Rollback Notes
- Risk: patching misses contract override behavior.
  Mitigation: fall back to GraphMutator when patching is incomplete.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; mutation patch map compilation pending.
