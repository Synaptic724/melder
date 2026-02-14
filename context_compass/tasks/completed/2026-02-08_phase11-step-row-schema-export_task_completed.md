Completed: 2026-02-08
Summary: Delivered Export Phase11 Step Rows as Schema-Only IR scope, updated validation notes, and confirmed acceptance.

# Task: Export Phase11 Step Rows as Schema-Only IR

## Metadata
- Task ID: TASK-2026-02-08-phase11-step-row-schema-export
- Story: STORY-2026-02-07-phase-contract-codegen-completeness
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-08
- Updated: 2026-02-08

## Objective
Replace Phase11 IR `steps` object export with schema-only `steps_rows` data so
IR payloads are deterministic and serializable.

## Scope Boundaries
- In scope:
- Add `steps_rows` export for all Phase11 variants with primitives/tuples only.
- Add deterministic ordering and stable signature coverage for `steps_rows`.
- Preserve legacy `steps` object field temporarily for compatibility during cutover.
- Out of scope:
- Removing legacy `steps` field in this ticket.
- Compiler consumer migration.

## Steps / Checklist
- [x] Define finalized `steps_rows` row schema (required keys and types).
- [x] Export `steps_rows` in `_build_phase11_variant_ir_payload`.
- [x] Include `steps_rows` in variant signature fingerprint.
- [x] Add tests for schema presence, required fields, and deterministic ordering.

## Deliverables
- Schema-only `steps_rows` payload export.
- Signature contract updated to cover `steps_rows`.
- Regression tests for row export stability.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py`
- Result: 120 passed (SpellCrafter suite), 33 passed (related runtime/compiler suites).

## Risks / Rollback Notes
- Risk: schema omission can silently drop required semantics for compilers.
- Mitigation: explicit required-field tests + signature assertions.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Created from Phase11 serialization audit that found live `ExecutionPlanStep`
objects in IR payloads. First normalization slice exports schema rows while
keeping compatibility fields. Implemented `steps_rows` and
`steps_rows_signature` export, added schema-safe value freezing, and expanded
IR contract tests for row content and deterministic signature behavior.


