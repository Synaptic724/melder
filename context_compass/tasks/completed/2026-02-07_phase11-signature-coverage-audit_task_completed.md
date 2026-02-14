Completed: 2026-02-08
Summary: Delivered Audit Phase11 Signature Coverage for Codegen Invalidation and validated results with targeted codegen suites.

# Task: Audit Phase11 Signature Coverage for Codegen Invalidation

## Metadata
- Task ID: TASK-2026-02-07-phase11-signature-coverage-audit
- Story: STORY-2026-02-07-phase-contract-codegen-completeness
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Produce an evidence-backed audit of which Phase11 execution semantics currently
affect signatures and which do not, so executor invalidation cannot miss
behavioral changes.

## Scope Boundaries
- In scope:
- Compare `_build_phase11_variant_ir_payload` signature inputs against runtime
  consumers of plan metadata.
- Identify missing signature inputs that can cause stale executor reuse.
- Define deterministic signature fields required for no-overrides, overrides,
  and overrides-with-mutations variants.
- Out of scope:
- Implementing signature changes.

## Steps / Checklist
- [x] Map current signature inputs in `SpellCrafter._build_phase11_variant_ir_payload`.
- [x] Map execution semantics consumed by:
  - `compile_phase12_no_overrides_executor`
  - `compile_phase12_overrides_executor`
  - `MeldRuntime` specialization cache routing.
- [x] Produce a required-signature field list with deterministic normalization rules.
- [x] Define test cases that prove invalidation on each behavioral field change.

## Deliverables
- Audit notes in ticket context summary with file/symbol evidence.
- Final required field list for Phase11 variant signatures.
- Follow-on implementation checklist for signature expansion and tests.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/execution_plan.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `tests/`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- Result: 143 passed (SpellCrafter suite), 209 passed (targeted full codegen regression bundle).

## Risks / Rollback Notes
- Risk: incomplete signature coverage can allow stale compiled executors.
- Mitigation: require explicit field-to-signature mapping and regression tests
  before implementation.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Audit outcome:
- `phase11` variant signatures must include:
  - `plan_variant`
  - `root_spell_id`
  - `steps_rows_signature` (covers step-level execution semantics)
  - `transient_signature` (covers no-overrides transient arrays)
- `steps_rows_signature` now captures deterministic row fields consumed by
  no-overrides and overrides compilers (existence/routing/dependency/override/
  contract/lock/register/disposal semantics).
- `MeldRuntime` override shape keying consumes override payload `signature` +
  `steps_rows_signature`, so variant semantic drift invalidates specialization
  cache keys.

Coverage added in `test_spell_crafter.py` includes broad semantic-field
invalidation parametrization and explicit variant-label distinctness tests.

