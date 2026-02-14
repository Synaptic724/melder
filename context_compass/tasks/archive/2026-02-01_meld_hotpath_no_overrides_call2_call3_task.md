# Task: Reduce meld hotpath allocations (no-overrides + CALL2/CALL3)

## Metadata
- Task ID: TASK-2026-02-01-meld-hotpath-no-overrides-call2-call3
- Story: N/A
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-01
- Updated: 2026-02-01

## Objective
Remove per-meld empty-override allocations on the no-overrides path and add
CALL2/CALL3 fast-call modes for Phase 11 execution to reduce warm-path overhead.

## Scope Boundaries
- In scope:
  - No-overrides path uses None instead of empty dicts in meld context/runtime/override payloads.
  - Phase 11 fast plan emits CALL2/CALL3 when safe.
  - MeldEngine fast-path executes CALL2/CALL3 without list/dict allocations.
  - SpellMap, SpellContract, and MutationContract default spell_override to None.
  - Update unit tests that assert default overrides or call modes.
- Out of scope:
  - Skipping cleanup or altering cleanup semantics.
  - Adding new locks or changing concurrency behavior.
  - Refactoring unrelated meld/runtime logic.

## Steps / Checklist
- [x] Update SpellMap/SpellContract/MutationContract to default spell_override to None.
- [x] Update MeldContext to store overrides as Optional and avoid per-call dict allocation.
- [x] Update MeldRuntime to avoid allocating override_map/frame_overrides when empty.
- [x] Extend ExecutionPlan fast plan to emit CALL2/CALL3 for single-dep groups.
- [x] Extend MeldEngine fast execution to handle CALL2/CALL3.
- [x] Update affected unit tests for new override semantics and fast call modes.

## Deliverables
- Code updates for no-overrides hotpath and CALL2/CALL3 fast calls.
- Updated unit tests reflecting new behavior.

## Files / Paths Impacted
- src/melder/aether/conduit/meld/contracts/spell_map.py
- src/melder/aether/conduit/meld/contracts/spell_contract.py
- src/melder/aether/conduit/meld/contracts/mutation_contract.py
- src/melder/aether/conduit/meld/meld_context/meld_context.py
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- src/melder/spellbook/spell_crafter/blueprints/execution_plan.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py
- tests/unit/melder/aether/conduit/meld/contracts/test_spell_map.py
- tests/unit/melder/aether/conduit/meld/contracts/test_spell_contract.py
- tests/unit/melder/aether/conduit/meld/contracts/test_mutation_contract.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py
  - pytest tests/unit/melder/aether/conduit/meld/contracts/test_spell_map.py
  - pytest tests/unit/melder/aether/conduit/meld/contracts/test_spell_contract.py
  - pytest tests/unit/melder/aether/conduit/meld/contracts/test_mutation_contract.py

## Risks / Rollback Notes
- Risk: override payload None-handling may affect fast-plan selection or override checks.
- Rollback: revert the touched files to restore empty-dict defaults and CALL0/CALL1-only behavior.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
User requested meld hotpath optimizations: remove empty-dict override allocations,
add CALL2/CALL3 fast call modes, and default spell_override to None (including
SpellContract). Cleanup skipping and new locks are explicitly out of scope.
Implementation complete; tests not run yet.
