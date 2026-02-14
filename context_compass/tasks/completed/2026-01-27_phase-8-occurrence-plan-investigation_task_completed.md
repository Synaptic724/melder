# Task: Investigate Phase 8 occurrence plan inputs and outputs

- Completed: 2026-01-27
- Summary: Archived Phase 8 occurrence plan investigation ticket per user
  direction; checklist items remain as recorded below.

## Metadata
- Task ID: TASK-2026-01-27-phase-8-occurrence-plan-investigation
- Story: STORY-2026-01-27-phase-8-occurrence-plan
- Status: complete
- Owner:
- Priority: p1
- Created: 2026-01-27
- Updated: 2026-01-27

## Objective
Map the current occurrence planning work in MeldEngine and identify the exact
inputs and outputs needed to compile an OccurrencePlan during Phase 8.

## Scope Boundaries
- In scope:
  - Review current occurrence planning code paths and inputs.
  - Record required data from Phase 1-7 artifacts.
  - Produce a written investigation note with evidence references.
- Out of scope:
  - Implementing the compiler.
  - Any runtime behavior changes.

## Steps / Checklist
- [ ] Review occurrence planning logic in `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`.
- [ ] Identify Phase 1-7 artifacts used as inputs (spell, blueprint, topology).
- [ ] Record output structure and decisions (ordering, per-path expansion, reuse).
- [ ] Write investigation note with evidence references and UNKNOWNs.

## Deliverables
- `context_compass/artifacts/fast_path_meld_plan/phase8_occurrence_plan_investigation.md`

## Files / Paths Impacted
- context_compass/tasks/2026-01-27_phase-8-occurrence-plan-investigation_task.md
- context_compass/artifacts/fast_path_meld_plan/phase8_occurrence_plan_investigation.md

## Validation
- Not run.
- Recommended commands:
  - None (docs-only).

## Risks / Rollback Notes
- Risk: missing edge cases (spellspace, many).
  Mitigation: include explicit checks for those paths and mark UNKNOWNs.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Draft investigation completed with evidence references in
`context_compass/artifacts/fast_path_meld_plan/phase8_occurrence_plan_investigation.md`.
Findings cover occurrence graph construction, ordered node expansion, execution
order, and instance plan outputs plus UNKNOWNs for blueprint ordering and DAG
socket kind sources.
