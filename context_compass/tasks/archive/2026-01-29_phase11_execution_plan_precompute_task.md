# Task: Implement Phase 11 execution plan precomputation for overrides/contracts/mutations

## Metadata
- Task ID: TASK-2026-01-29-phase11-execution-plan-precompute
- Story: STORY-2026-01-29-phase11-execution-plan-precompute
- Status: completed
- Owner: codex
- Priority: p0
- Created: 2026-01-29
- Updated: 2026-01-29

## Objective
Implement Phase 11 execution plan changes so override, contract, and mutation routing are precomputed and consumed directly by the meld engine/runtime.

## Scope Boundaries
- In scope:
  - ExecutionPlan data/model updates for precomputed routing.
  - SpellCrafter Phase 11 changes to compute plan using Phase 8-10 artifacts.
  - Meld engine consumption of precomputed plan routing.
  - Meld runtime adjustments to avoid recomputing routing.
  - Unit test updates for Phase 11 behavior.
- Out of scope:
  - Performance benchmarking.
  - Public API shape changes.

## Steps / Checklist
- [x] Inspect current Phase 11 builder and runtime/engine consumption paths.
- [x] Define execution-plan fields for override/contract/mutation routing.
- [x] Update Phase 11 compilation to precompute routing from Phase 8-10 artifacts.
- [x] Update meld engine to apply overrides/contracts using precomputed plan data.
- [x] Update meld runtime to pass plan + patch maps without recomputation.
- [x] Update/extend tests to cover the new plan behavior.
- [x] Update docstrings for any modified classes/methods.

## Deliverables
- Execution plan supports precomputed override/contract/mutation routing.
- Meld engine/runtime consumes the plan without extra planning work.
- Updated unit tests aligned with new plan semantics.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/blueprints/execution_plan.py
- src/melder/spellbook/spell_crafter/spell_crafter.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- tests/unit/melder/aether/conduit/meld/test_meld_runtime_phase11.py
- tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py
- tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine.py

## Validation
- Ran:
  - PYTHONPATH=/workspace/melder_private pytest tests/unit/melder/aether/conduit/meld/test_meld_runtime_phase11.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_execution_plan_phase11.py tests/unit/melder/aether/conduit/meld/test_meld_engine_phase11.py -q

## Risks / Rollback Notes
- Risk: Plan data mismatch causes incorrect override application.
  - Rollback: revert to previous Phase 11 builder and runtime/engine flow.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Phase 11 plans now precompute override/contract/mutation routing and runtime/engine consume them directly with updated unit tests.

