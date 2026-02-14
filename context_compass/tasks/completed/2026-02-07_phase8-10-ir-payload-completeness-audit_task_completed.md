Completed: 2026-02-08
Summary: Delivered Audit Phase8-10 IR Payload Completeness for Full Codegen with evidence-backed consumer mapping and validation.

# Task: Audit Phase8-10 IR Payload Completeness for Full Codegen

## Metadata
- Task ID: TASK-2026-02-07-phase8-10-ir-payload-completeness-audit
- Story: STORY-2026-02-07-phase-contract-codegen-completeness
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Identify the minimum deterministic data Phase8-10 must export so emitted
executors (no-overrides, overrides, mutations) do not rely on live plan object
introspection.

## Scope Boundaries
- In scope:
- Audit `phase8_11` export payload fields versus emitter/runtime needs.
- Audit whether patch-map export currently includes enough per-spec routing data.
- Audit whether injection export includes enough per-parameter dependency wiring.
- Define required additional fields and normalization rules.
- Out of scope:
- Implementing payload schema changes.

## Steps / Checklist
- [x] Inventory current `phase8_11` payload produced by `_capture_phase8_11_codegen_ir`.
- [x] Build consumer matrix for fields used by:
  - Phase12 no-overrides compiler
  - Phase12 overrides compiler
  - Mutation routing/patch application code paths.
- [x] Mark missing deterministic fields and classify by phase owner (8/9/10/11).
- [x] Propose compact normalized shapes for each missing field.

## Deliverables
- Evidence matrix (exported field -> consumer -> required/unused/missing).
- Required field set for Phase8/9/10 payload enrichment.
- Follow-on implementation checklist and test requirements.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `src/melder/spellbook/spell_crafter/blueprints/injection_plan.py`
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `tests/`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- Result: 143 passed (SpellCrafter suite), 209 passed (targeted full codegen regression bundle).

## Risks / Rollback Notes
- Risk: over-expanding payload increases IR size and compile overhead.
- Mitigation: include compact representation and only include consumer-required fields.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Audit outcome and field/consumer matrix summary:
- Required for current emitted execution consumers:
  - `execution.<variant>.signature`, `steps_rows_signature`, `root_spell_id`,
    `steps_rows` (SpellCrafter compile wiring + MeldRuntime override shape keying).
- Required for deterministic structural IR completeness:
  - Phase8: occurrence `graph_rows`, `instance_key_rows`,
    `canonical_occurrence_rows`, `contract_override_rows`,
    `contract_override_spell_rows`.
  - Phase9: injection `instance_rows` (param source kind/dependency keys/
    override key/contract key + contract payload items).
  - Phase10: patch-map `override_target_rows` and `mutation_target_rows`.
- Follow-on implementation is now landed in `SpellCrafter._capture_phase8_11_codegen_ir`
  with deterministic ordering and signature coverage for all enriched segments.

