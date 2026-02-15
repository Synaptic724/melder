Completed: 2026-02-08
Summary: Delivered Enrich Phase2-5 IR Payloads for Full Emitted Codegen and aligned signatures/tests for contract completeness.

# Task: Enrich Phase2-5 IR Payloads for Full Emitted Codegen

## Metadata
- Task ID: TASK-2026-02-07-phase2-5-ir-payload-enrichment
- Story: STORY-2026-02-07-phase-contract-codegen-completeness
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Implement the missing deterministic Phase2-5 payload fields required by emitted
override/mutation code generation and signature invalidation.

## Scope Boundaries
- In scope:
- Add normalized phase2/3/4/5 export fields defined by the audit.
- Add deterministic signature coverage for new `phase2_5` fields.
- Add schema/contract tests for payload ordering and required fields.
- Out of scope:
- Runtime route redesign unrelated to payload export.

## Steps / Checklist
- [x] Implement required phase2 symbolic dependency payload enrichment.
- [x] Implement required phase5 root blueprint/socket/path payload enrichment.
- [x] Update `phase2_5` signature composition to include new fields.
- [x] Add deterministic contract tests and fail-fast validation tests.

## Deliverables
- Enriched `phase2_5` payload with deterministic serialization.
- Updated signature logic for phase2_5 invalidation safety.
- Tests that fail on missing fields or nondeterministic ordering.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/root_resolution_blueprint.py`
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `tests/`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- Result: 128 passed (SpellCrafter suite), 194 passed (targeted full codegen regression bundle).

## Risks / Rollback Notes
- Risk: increased IR size and export cost.
- Mitigation: compact normalized representations with consumer-driven inclusion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Implemented deterministic `phase2_5` payload enrichment in
`SpellCrafter._capture_phase2_5_codegen_ir`:
- Added Phase5 root lineage id export.
- Added normalized Phase5 socket rows (`node_id`, `param_name`, `param_path_id`,
  `socket_kind`) from root blueprint socket refs.
- Added normalized Phase5 DAG edge rows (`parent`, `child`, `param`, `socket_kind`)
  from root blueprint DAG topology.
- Expanded `phase2_5` signature composition to fingerprint all new fields.

Added regression coverage for new payload fields and signature invalidation when
Phase5 schema rows change.


