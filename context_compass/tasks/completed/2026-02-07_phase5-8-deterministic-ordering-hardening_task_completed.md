Completed: 2026-02-08
Summary: Delivered Harden Phase5-8 Deterministic Ordering for Export and Signatures scope, updated validation notes, and confirmed acceptance.

# Task: Harden Phase5-8 Deterministic Ordering for Export and Signatures

## Metadata
- Task ID: TASK-2026-02-07-phase5-8-deterministic-ordering-hardening
- Story: STORY-2026-02-07-phase-contract-codegen-completeness
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-08

## Objective
Implement canonical deterministic ordering in Phase5-8 builders so equivalent
graphs always emit the same ordered payloads, signatures, and generated source.

## Scope Boundaries
- In scope:
- Apply canonical ordering in root DAG node/edge construction and topo ties.
- Apply canonical ordering in occurrence execution-order build and cycle fallback.
- Ensure root-id selection and diagnostic root references are deterministic.
- Add regression tests covering multi-root and tie conditions.
- Out of scope:
- Schema expansion unrelated to ordering.

## Steps / Checklist
- [x] Implement deterministic ordering for root and reachable node traversal.
- [x] Implement stable tie-break ordering in `topological_sort`.
- [x] Implement deterministic cycle fallback ordering in occurrence planning.
- [x] Add deterministic-order regression tests for repeated equivalent builds.

## Deliverables
- Phase5/8 ordering hardening changes.
- Regression tests proving identical ordering across repeated runs.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py`
- `src/melder/spellbook/spell_crafter/dag/directed_acyclic_work_graph.py`
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/dag tests/unit/melder/spellbook/spell_crafter/system/test_spell_system_root_blueprint_builder.py tests/unit/melder/spellbook/test_conjure_hotspot_fixes.py`
- Result: 165 passed.

## Risks / Rollback Notes
- Risk: ordering changes can alter historical but valid topological order tests.
- Mitigation: assert dependency constraints plus canonical tie-break behavior.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Implemented deterministic ordering across Phase5-8 paths: root traversal/build,
DAG topological tie-breaks, occurrence-order fallback, and deterministic
diagnostic root selection. Added deterministic regression assertions and validated
with targeted DAG/system/hotspot tests.

