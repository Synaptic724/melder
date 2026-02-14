Completed: 2026-02-08
Summary: Prebound per-step must-register flags in Phase12 overrides source and added empty-target override-value fast-path helper with compile-shape and helper coverage.

# Task: Phase12 Overrides Must-Register Prebind Optimization

## Metadata
- Task ID: TASK-2026-02-08-phase12-overrides-must-register-prebind
- Story: STORY-2026-02-08-codegen-meld-runtime-optimization-wave
- Status: done
- Owner:
- Priority: p2
- Created: 2026-02-08
- Updated: 2026-02-08

## Objective
Reduce override emitted-path attribute reads by prebinding `step_must_register`
flags and using tuple-backed lookups in the many-step registration branch.

## Scope Boundaries
- In scope:
- Add `step_must_register_flags` prebind in overrides namespace/source.
- Switch many-branch registration guard to tuple-backed bool.
- Add helper micro-optimization for no-target override construction.
- Add/adjust compile-shape tests.
- Out of scope:
- Behavioral changes to registration semantics.

## Steps / Checklist
- [x] Add must-register prebind tuple in overrides namespace.
- [x] Update emitted many branch to use prebound registration flags.
- [x] Add helper fast path for empty override target tuples.
- [x] Run targeted + broad regressions.

## Deliverables
- Reduced per-step attribute reads for override many-branch registration checks.
- Regression tests confirming metadata prebind availability.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
- Result:
  - Overrides blueprint suite passed (`24 passed`).
  - Extended regression suite passed (`178 passed`).
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`

## Risks / Rollback Notes
- Risk: emitted-source variable mismatches could break overrides codegen at runtime.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
This task continues emitted-source metadata prebinding for overrides step blocks
with a narrow helper micro-optimization, covering must-register tuple prebinds
and empty-target override materialization fast paths.

