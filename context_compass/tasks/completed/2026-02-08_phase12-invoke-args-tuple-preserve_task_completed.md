Completed: 2026-02-08
Summary: Updated Phase12 tuple/list positional arg handling to preserve tuples and added tuple-payload tests in both no-overrides and overrides suites.

# Task: Phase12 Invoke Args Tuple-Preserve Micro-Optimization

## Metadata
- Task ID: TASK-2026-02-08-phase12-invoke-args-tuple-preserve
- Story: STORY-2026-02-08-codegen-meld-runtime-optimization-wave
- Status: done
- Owner:
- Priority: p2
- Created: 2026-02-08
- Updated: 2026-02-08

## Objective
Reduce temporary allocation overhead in Phase12 invoke helpers by preserving
tuple `__args__` payloads directly instead of rebuilding list instances.

## Scope Boundaries
- In scope:
- Update tuple/list handling in `_invoke_spell_with_kwargs` (overrides path).
- Update tuple/list handling in `_invoke_spell_with_kwargs` (no-overrides path).
- Add regression tests for tuple positional payload execution and payload preservation behavior.
- Run targeted + broad regressions.
- Out of scope:
- Any change to `__args__` validation semantics.

## Steps / Checklist
- [x] Update both invoke helpers to preserve tuple payloads.
- [x] Add tests for tuple payload behavior in both modules.
- [x] Run targeted + broad regressions.

## Deliverables
- Reduced positional override allocation churn for tuple payloads.
- Regression tests for tuple payload handling in both Phase12 paths.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py`
- `tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
- Result:
  - Blueprint suites passed (`52 passed`).
  - Extended regression suite passed (`187 passed`).
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`

## Risks / Rollback Notes
- Risk: positional argument execution could regress if tuple/list branching is misapplied.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
This pass is limited to invoke helper internals and tuple positional payload handling.
