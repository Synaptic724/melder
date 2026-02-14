Completed: 2026-02-08
Summary: Prebound no-overrides `step_instance_keys` metadata and switched emitted instance-result writes to tuple-backed lookups.

# Task: Phase12 No-Overrides Step Instance-Key Prebind Optimization

## Metadata
- Task ID: TASK-2026-02-08-phase12-no-overrides-step-instance-key-prebind
- Story: STORY-2026-02-08-codegen-meld-runtime-optimization-wave
- Status: done
- Owner:
- Priority: p2
- Created: 2026-02-08
- Updated: 2026-02-08

## Objective
Reduce emitted no-overrides step-block attribute reads by prebinding
`step_instance_keys` in executor defaults and routing instance writes through
tuple-backed locals.

## Scope Boundaries
- In scope:
- Add `step_instance_keys` prebind in no-overrides namespace/source.
- Replace emitted `plan_step.instance_key` writes with tuple lookups.
- Update compile-shape test assertions.
- Out of scope:
- Any behavior changes in existence routing or registration semantics.

## Steps / Checklist
- [x] Add `step_instance_keys` tuple in namespace defaults.
- [x] Switch emitted instance-result writes to prebound instance-key lookups.
- [x] Update no-overrides compile-shape assertion test.
- [x] Run targeted and broad regressions.

## Deliverables
- Emitted no-overrides source with reduced instance-key attribute dereferences.
- Regression assertions proving prebound instance-key metadata is available.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
- Result:
  - No-overrides blueprint suite passed (`22 passed`).
  - Extended regression suite passed (`153 passed`).
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`

## Risks / Rollback Notes
- Risk: emitted-source variable mapping mistakes could break generated execution.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Small emitted-source micro-optimization to align no-overrides metadata access
patterns with the override path.
