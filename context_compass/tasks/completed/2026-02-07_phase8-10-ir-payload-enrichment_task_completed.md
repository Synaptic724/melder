Completed: 2026-02-08
Summary: Delivered Enrich Phase8-10 IR Payloads for Override and Mutation Codegen and aligned signatures/tests for contract completeness.

# Task: Enrich Phase8-10 IR Payloads for Override and Mutation Codegen

## Metadata
- Task ID: TASK-2026-02-07-phase8-10-ir-payload-enrichment
- Story: STORY-2026-02-07-phase-contract-codegen-completeness
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Implement the missing deterministic Phase8/9/10 payload fields required by full
emitted override and mutation executor compilation.

## Scope Boundaries
- In scope:
- Add normalized Phase8 occurrence/export fields required by emitters.
- Add normalized Phase9 injection wiring fields required by emitters.
- Add normalized Phase10 patch-map detail fields needed for override/mutation routing.
- Update signatures to include new payload segments.
- Out of scope:
- Removing existing runtime routes that are not directly tied to payload export.

## Steps / Checklist
- [x] Implement required Phase8 payload field export and normalization.
- [x] Implement required Phase9 payload field export and normalization.
- [x] Implement required Phase10 payload field export and normalization.
- [x] Update `phase8_11` signature composition to cover new fields.
- [x] Add schema/contract tests for deterministic payload ordering and content.

## Deliverables
- Enriched `phase8_11` payload contract with deterministic serialization.
- Tests that fail on missing required fields or nondeterministic ordering.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `src/melder/spellbook/spell_crafter/blueprints/injection_plan.py`
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- `src/melder/spellbook/spell_crafter/blueprints/execution_plan.py`
- `tests/`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- Result: 128 passed (SpellCrafter suite), 194 passed (targeted full codegen regression bundle).

## Risks / Rollback Notes
- Risk: payload growth and compile cost increase.
- Mitigation: keep fields compact and consumer-driven; add targeted benchmarks.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Implemented deterministic schema enrichment for Phase8/9/10 export in
`SpellCrafter._capture_phase8_11_codegen_ir`:
- Phase8 occurrence details now include graph rows, instance-key rows, canonical
  occurrence rows, and contract override rows.
- Phase9 injection details now include per-instance injection rows with
  dependency keys, contract payload items, and aggregation/positional flags.
- Phase10 patch map details now include normalized override target rows
  (with specificity) and mutation target rows.
- `phase8_11` signature now fingerprints all enriched segments to prevent stale
  executor reuse.

Tests now assert deterministic ordering/content for enriched payloads and verify
signature stability across equivalent insertion orders.

