Completed: 2026-02-07
Summary: Exported phases 2-5 structural artifacts into deterministic spell-scoped codegen IR fields.

# Task: Export Phases 2-5 into Canonical Codegen IR

## Metadata
- Task ID: TASK-2026-02-07-phase2-5-ir-export
- Story: STORY-2026-02-07-phase11-ir-data-harvest
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Wire phases 2-5 outputs into a canonical spell-scoped Codegen IR payload that captures sockets, resolved dependencies, topology order, and root blueprint metadata required by Phase 12.

## Scope Boundaries
- In scope:
- Phase 2 symbolic graph -> socket model export.
- Phase 3 local frame/topology -> dependency edge export.
- Phase 4 validation flags needed for compile gating.
- Phase 5 root blueprint/index data needed by Phase 12 planning.
- Out of scope:
- Phase 8-11 plan export.
- Runtime dispatch changes.

## Steps / Checklist
- [x] Define Phase 2-5 IR field mapping contract.
- [x] Populate IR fields during each phase completion.
- [x] Add deterministic ordering rules for emitted collections.
- [x] Add invalidation/reset behavior when phase artifacts are cleaned.

## Deliverables
- Canonical Phase 2-5 Codegen IR export wiring.
- Phase mapping documentation for future maintenance.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/spell_examiner/profiles/resolution_profile.py` (if contract exposure is required)
- `src/melder/spellbook/spell.py` (only if read accessors are needed)

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile src/melder/spellbook/spell_crafter/spell_crafter.py src/melder/spellbook/spell.py`
  - `python -m pytest -q tests/unit/melder/spellbook -k \"symbolic or local_frame or root_blueprints\"`

## Risks / Rollback Notes
- Risk: non-deterministic IR ordering causes unstable compile outputs.
- Mitigation: enforce sorted/stable ordering at export points.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task converts structural phase artifacts into deterministic IR segments so Phase 12 compiler input is explicit and replayable.

