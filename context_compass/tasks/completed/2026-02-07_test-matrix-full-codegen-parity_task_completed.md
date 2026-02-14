Completed: 2026-02-08
Summary: Expanded generated-path parity matrix coverage across existences and override/mutation-targeted routes.

# Task: Build Full Parity Test Matrix for Generated Paths

## Metadata
- Task ID: TASK-2026-02-07-test-matrix-full-codegen-parity
- Story: STORY-2026-02-07-validation-perf-gates
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Cover all existences and override/mutation permutations on generated paths.

## Scope Boundaries
- In scope:
- Unit/component/integration matrix updates.
- Out of scope:
- Backward compatibility behavior.

## Steps / Checklist
- [x] Implement scoped changes.
- [x] Add/update tests for scoped behavior.
- [x] Update ticket context summary.

## Deliverables
- Scoped code and tests for this task.

### Delivered Parity Matrix Coverage
- No-overrides emitted executor existence matrix coverage for:
  - `unique`
  - `unique_per_conduit`
  - `many` (with and without registration/disposal)
  - `unique_per_spell_space`
- No-overrides target-kind coverage for:
  - `CALLER`
  - `SPELLSPACE`
  - `OWNER` (spell-owner creations precedence and context fallback)
- Overrides emitted executor coverage for spellspace scoped existing-instance rejection under targeted override payloads.
- Runtime shape/canonical semantics alignment updates:
  - canonical occurrence selection test now asserts stable lexical selection instead of first-seen insertion behavior.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `src/melder/aether/conduit/meld/meld.py`
- `tests/`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py`
- Result:
  - 226 passed.

## Risks / Rollback Notes
- Risk of semantic drift in lock/reuse/registration behavior.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Landed full parity matrix expansion for generated paths across existence scopes
and target-kind routing, including owner/scope-specific creations behavior and
spellspace override rejection semantics. Added deterministic canonical selection
assertion update in meld-engine helper tests to align with Phase8 ordering
hardening.

