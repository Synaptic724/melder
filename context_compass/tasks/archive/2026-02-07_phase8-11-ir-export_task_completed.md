Completed: 2026-02-07
Summary: Exported phases 8-11 planning artifacts into deterministic spell-scoped codegen IR fields.

# Task: Export Phases 8-11 into Canonical Codegen IR

## Metadata
- Task ID: TASK-2026-02-07-phase8-11-ir-export
- Story: STORY-2026-02-07-phase11-ir-data-harvest
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Export Phase 8-11 plan artifacts into canonical Codegen IR operations so Phase 12 can generate executors without rebuilding occurrence/injection/patch/execution semantics.

## Scope Boundaries
- In scope:
- Phase 8 occurrence plan export.
- Phase 9 injection plan export.
- Phase 10 override/mutation patch map export metadata.
- Phase 11 execution plan export into compile-ready op tables.
- Out of scope:
- Phase 12 runtime routing.
- Override specialization cache behavior.

## Steps / Checklist
- [x] Define Phase 8-11 IR operation schema and naming.
- [x] Export normalized operation lists from each phase artifact.
- [x] Ensure no-overrides and override-capable plan variants are separately represented.
- [x] Add deterministic hashing/signature for IR payload versioning.

## Deliverables
- Phase 8-11 IR export wiring and schema.
- Deterministic operation payloads consumable by Phase 12 compiler.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/execution_plan.py` (if metadata exposure is required)
- `src/melder/spellbook/spell.py` (only if read accessors are needed)

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile src/melder/spellbook/spell_crafter/spell_crafter.py src/melder/spellbook/spell_crafter/blueprints/execution_plan.py`
  - `python -m pytest -q tests/unit/melder/spellbook -k \"occurrence_plan or injection_plan or patch_maps or execution_plan\"`

## Risks / Rollback Notes
- Risk: mismatch between exported op semantics and current runtime execution.
- Mitigation: parity checks against existing Phase 11-driven execution for no-overrides paths.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task captures runtime plan semantics as IR to eliminate duplicate runtime interpretation and set up deterministic Phase 12 compilation.

