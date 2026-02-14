# Task: Implement Phase 12 runtime/engine execution substitution

## Metadata
- Task ID: TASK-2026-01-29-phase12-runtime-execution-implementation
- Story: STORY-2026-01-29-phase12-precompute-meld-runtime
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-29
- Updated: 2026-01-29

## Objective
Substitute Phase 12 ExecutionAssemblyPlan into MeldRuntime/MeldEngine execution and remove duplicated planning logic from the engine.

## Scope Boundaries
- In scope:
  - Select Phase 12 plan variants in MeldRuntime and route execution to the new executor.
  - Implement MeldEngine execution using Phase 12 ExecutionAssemblyPlan steps.
  - Strip redundant override routing and creations selection duplication where Phase 12 provides precomputed data.
  - Maintain fallback to legacy paths when Phase 12 artifacts are missing or ineligible.
- Out of scope:
  - Removing Phase 11 artifacts.
  - Performance benchmarking.

## Steps / Checklist
- [x] Add Phase 12 plan selection and gating in MeldRuntime.
- [x] Add Phase 12 execution loop in MeldEngine.
- [ ] Remove or simplify duplicated override/creations routing in the legacy Phase 11/slow paths.
- [ ] Add/adjust tests for Phase 12 runtime execution.

## Deliverables
- MeldRuntime executes Phase 12 plans when eligible.
- MeldEngine consumes ExecutionAssemblyPlan steps to build instances.
- Phase 11/slow paths trimmed of redundant routing where safe.
- Updated tests for Phase 12 execution behavior.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- src/melder/spellbook/spell_crafter/blueprints/execution_assembly_plan.py

## Validation
- Not run (implementation in progress).

## Risks / Rollback Notes
- Risk: Phase 12 eligibility gating skips needed runtime checks.
  - Mitigation: keep Phase 11/slow-path fallbacks and add focused tests.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Phase 12 plan selection and execution loop are integrated into MeldRuntime/MeldEngine, with plan-based creations targeting and lock hints now applied in the Phase 12 executor path.
