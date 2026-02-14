Completed: 2026-02-08
Summary: Delivered Audit Phase11 Variant Semantics and Distinctness and validated results with targeted codegen suites.

# Task: Audit Phase11 Variant Semantics and Distinctness

## Metadata
- Task ID: TASK-2026-02-07-phase11-variant-semantics-audit
- Story: STORY-2026-02-07-phase-contract-codegen-completeness
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Verify whether Phase11 `OVERRIDES` and `OVERRIDES_WITH_MUTATIONS` variants are
semantically distinct in produced plan data and determine required contract
fields to keep variant behavior explicit and invalidation-safe.

## Scope Boundaries
- In scope:
- Audit `ExecutionPlanBuilder` behavior across all `plan_variant` values.
- Compare variant outputs against mutation/override runtime requirements.
- Identify missing variant markers or data needed for deterministic codegen.
- Out of scope:
- Implementing variant-generation changes.

## Steps / Checklist
- [x] Diff generated plan metadata for each variant using representative graphs.
- [x] Map where variant-specific behavior should originate (phase8/10/11).
- [x] Define required exported fields/signature inputs for variant distinction.
- [x] Propose follow-on implementation changes and tests.

## Deliverables
- Variant distinctness report with evidence and file/symbol references.
- Required variant contract field list and signature implications.
- Follow-on implementation checklist.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/execution_plan.py`
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `tests/`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- Result: 143 passed (SpellCrafter suite), 209 passed (targeted full codegen regression bundle).

## Risks / Rollback Notes
- Risk: variant ambiguity causes stale signatures and incorrect executor reuse.
- Mitigation: explicit variant contract fields plus targeted regression tests.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Audit finding: for equivalent graphs, `OVERRIDES` and
`OVERRIDES_WITH_MUTATIONS` often produce equivalent step rows, with distinctness
primarily carried by `plan_variant` and variant-selected Phase8/10 upstream
payloads. Contract requirement is therefore:
- Variant identity must remain explicit in exported payload (`plan_variant`).
- Variant identity must participate in variant signature hashing.
- Runtime must select `overrides` vs `overrides_with_mutations` payloads by
  route, not by inferred step differences.

Follow-on test coverage now asserts variant-label signature distinctness even
when step-row signatures are equal.

