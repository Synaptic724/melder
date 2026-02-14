Completed: 2026-02-08
Summary: Delivered Audit Phase2-5 IR Payload Completeness for Full Codegen with evidence-backed consumer mapping and validation.

# Task: Audit Phase2-5 IR Payload Completeness for Full Codegen

## Metadata
- Task ID: TASK-2026-02-07-phase2-5-ir-payload-completeness-audit
- Story: STORY-2026-02-07-phase-contract-codegen-completeness
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Identify the minimum deterministic data Phase2-5 must export so emitted
override/mutation executors do not depend on live blueprint/symbolic objects at
compile or runtime.

## Scope Boundaries
- In scope:
- Audit current `phase2_5` export produced by `_capture_phase2_5_codegen_ir`.
- Build consumer matrix for root blueprint, socket/path metadata, and symbolic
  dependency fields needed by codegen.
- Identify missing deterministic fields and normalization rules.
- Out of scope:
- Implementing schema or exporter changes.

## Steps / Checklist
- [x] Inventory current `phase2_5` payload and signature inputs.
- [x] Map consumer requirements from:
  - override target routing/path matching behavior
  - mutation patch/rewire routing behavior
  - phase compiler invalidation requirements
- [x] Mark missing phase2/3/4/5 fields and assign owning phase.
- [x] Define compact normalized export shapes and ordering constraints.

## Deliverables
- Evidence matrix (exported field -> consumer -> required/unused/missing).
- Required Phase2-5 field set with deterministic normalization rules.
- Follow-on implementation checklist and test requirements.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py`
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `tests/`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- Result: 143 passed (SpellCrafter suite), 209 passed (targeted full codegen regression bundle).

## Risks / Rollback Notes
- Risk: payload growth and compile overhead.
- Mitigation: require strict consumer-mapped fields and compact normalized
  representations.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Audit outcome and field/consumer matrix summary:
- Existing fields retained and required:
  - symbolic dependencies (param shape/contract metadata),
  - local ordered ids / dependency ids,
  - phase4 validation flags/codes,
  - phase5 root/index ids.
- Missing deterministic fields identified for override/mutation codegen
  completeness and invalidation safety:
  - root lineage id,
  - phase5 socket rows (`node`, `param`, `path`, `kind`),
  - phase5 DAG edge rows (`parent`, `child`, `param`, `kind`).
- Follow-on implementation is now landed in
  `SpellCrafter._capture_phase2_5_codegen_ir` with deterministic ordering and
  expanded signature coverage.

