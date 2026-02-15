Completed: 2026-02-08
Summary: Added two-key split fast path and tuple-preserving root-args normalization in runtime override payload split helper, with tuple-identity coverage.

# Task: MeldRuntime Split Override Two-Key Fast Path

## Metadata
- Task ID: TASK-2026-02-08-meld-runtime-split-override-two-key-fastpath
- Story: STORY-2026-02-08-codegen-meld-runtime-optimization-wave
- Status: done
- Owner:
- Priority: p2
- Created: 2026-02-08
- Updated: 2026-02-08

## Objective
Reduce override payload split overhead for common `__args__ + one-target` calls
by adding a dedicated two-key branch in runtime split normalization.

## Scope Boundaries
- In scope:
- Normalize tuple/list root args with tuple-preserving behavior.
- Add direct `len == 2` target payload branch in `_split_override_payload`.
- Preserve non-mutating split behavior and validation semantics.
- Run targeted + broad regressions.
- Out of scope:
- Any changes to patch-map application logic.

## Steps / Checklist
- [x] Add tuple-preserving root-args normalization.
- [x] Add two-key split fast path in `_split_override_payload`.
- [x] Run targeted + broad regressions.

## Deliverables
- Reduced allocation/copy work in common split-override payload shapes.
- Regression validation for split helper behavior.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
- Result:
  - MeldRuntime suite passed (`52 passed`).
  - Extended regression suite passed (`201 passed`).
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`

## Risks / Rollback Notes
- Risk: split-path branch conditions could accidentally mutate or mis-shape target payloads.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
This pass is limited to override payload normalization before Phase10 mapping.

