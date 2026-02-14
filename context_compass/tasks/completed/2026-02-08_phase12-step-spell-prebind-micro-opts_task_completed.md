Completed: 2026-02-08
Summary: Added tuple-backed `step_spells` prebinds to both no-overrides and overrides emitted executors and updated compile-shape tests.

# Task: Phase12 Step-Spell Prebind Micro-Optimization

## Metadata
- Task ID: TASK-2026-02-08-phase12-step-spell-prebind-micro-opts
- Story: STORY-2026-02-08-codegen-meld-runtime-optimization-wave
- Status: done
- Owner:
- Priority: p2
- Created: 2026-02-08
- Updated: 2026-02-08

## Objective
Reduce emitted step-block attribute reads by prebinding step spell objects in
both no-overrides and overrides executor defaults.

## Scope Boundaries
- In scope:
- Add `step_spells` prebind in no-overrides and overrides namespaces/sources.
- Replace emitted `plan_step.spell` reads with tuple-backed lookup locals.
- Extend compile-shape tests for both executors.
- Out of scope:
- Any execution semantics changes.

## Steps / Checklist
- [x] Add `step_spells` prebinds in no-overrides source/namespace.
- [x] Add `step_spells` prebinds in overrides source/namespace.
- [x] Update compile-shape tests to assert `step_spells` defaults.
- [x] Run targeted + broad regressions.

## Deliverables
- Emitted Phase12 executors with reduced per-step spell attribute lookups.
- Tests confirming `step_spells` appears in generated callable defaults.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py`
- `tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
- Result:
  - Blueprint suites passed (`43 passed`).
  - Extended regression suite passed (`154 passed`).
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`

## Risks / Rollback Notes
- Risk: emitted-source wiring mismatches could cause codegen runtime failures.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
This pass aligns both Phase12 emitted executors to use tuple-backed spell access
for per-step runtime metadata.
