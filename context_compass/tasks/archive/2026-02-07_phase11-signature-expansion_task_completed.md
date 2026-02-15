Completed: 2026-02-08
Summary: Delivered Expand Phase11 Signatures for Deterministic Recompile Safety scope, updated validation notes, and confirmed acceptance.

# Task: Expand Phase11 Signatures for Deterministic Recompile Safety

## Metadata
- Task ID: TASK-2026-02-07-phase11-signature-expansion
- Story: STORY-2026-02-07-phase-contract-codegen-completeness
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Implement expanded Phase11 signature generation so executor cache reuse is only
allowed when all execution semantics are unchanged.

## Scope Boundaries
- In scope:
- Add deterministic step-level signature components for each Phase11 variant.
- Wire updated signatures into `phase8_11` and per-variant payloads.
- Add regression tests for stale-signature prevention.
- Out of scope:
- Runtime route redesign outside signature/invalidation behavior.

## Steps / Checklist
- [x] Implement Phase11 step digest builder with deterministic ordering.
- [x] Extend `_build_phase11_variant_ir_payload` signatures to include step semantics.
- [x] Ensure no-overrides executor cache invalidates on any relevant semantic change.
- [x] Add tests for signature changes across dependency, contract payload,
  lock/register, and target-routing changes.

## Deliverables
- Updated signature logic and payload fields.
- Regression tests covering invalidation correctness.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/execution_plan.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `tests/`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- Result: 172 passed.

## Risks / Rollback Notes
- Risk: missing a semantic field still allows stale executors.
- Mitigation: implement from audit field list and lock with targeted tests.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Phase11 variant signatures are now guarded by regression tests that explicitly
validate semantic invalidation across dependency wiring, contract payload
changes, lock/register flags, and creation target routing changes. No-overrides
executor cache invalidation is now covered end-to-end by recapturing Phase11 IR
after semantic step changes and asserting recompilation.


