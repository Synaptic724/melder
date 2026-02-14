# Task: Implement codegen executor for plans

## Metadata
- Task ID: TASK-2026-01-25-plan-codegen-executor
- Story: STORY-2026-01-25-fast-path-codegen
- Status: draft
- Owner:
- Priority: p3
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Generate a Python function per RootExecutionPlan to reduce loop and lookup
overhead in the fast path.

## Scope Boundaries
- In scope:
  - Code generation and caching per plan signature.
- Out of scope:
  - Cython implementation.

## Steps / Checklist
- [ ] Define codegen template for plan steps.
- [ ] Emit and compile a callable per plan signature.
- [ ] Cache compiled functions and clean up on plan invalidation.

## Deliverables
- Codegen executor implementation and cache.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/compiled_plan_codegen.py (new)
- src/melder/aether/conduit/meld/fast_meld_executor.py (new)

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k codegen

## Risks / Rollback Notes
- Risk: codegen errors lead to incorrect execution.
  Mitigation: keep behind a configuration flag and add tests.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; codegen executor pending.
