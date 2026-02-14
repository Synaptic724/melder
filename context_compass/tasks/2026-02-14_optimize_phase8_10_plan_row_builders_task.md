# Task: Optimize Phase8-10 Plan Row Builder Hotpath

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase8-10-plan-row-builders
- Story: STORY-2026-02-14-phase-testing-optimization-backlog
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce warm-path cumulative cost across phase8/9/10 plan-row construction and
supporting path-materialization work.

## Scope Boundaries
- In scope:
- Optimize occurrence/injection/patch map row-building helpers used in warm 8-11.
- Preserve phase ordering, semantics, and emitted plan behavior.
- Out of scope:
- Major planner architecture rewrites.
- Execution-plan API changes.

## Steps / Checklist
- [ ] Identify dominant row-build/path-format allocations on warm 8-11 path.
- [ ] Implement low-risk reductions in repeated path formatting/sorting work.
- [ ] Add focused tests for behavior parity.
- [ ] Validate by rerunning component harness and comparing warm per-phase totals.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Optimized phase8/9/10 row builder paths.
- Updated measurement notes showing warm-path improvement.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- `src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py`
- `src/melder/spellbook/spell_crafter/dag/dag_index.py`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Risks / Rollback Notes
- Risk: changing row-build internals can alter ordering-sensitive outputs.
- Rollback: revert helper-level changes and keep current ordering contracts.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Warm 8-11 totals still show substantial cost in occurrence/injection/patch phases, and cProfile highlights row-build/path-materialization helpers as recurring cumulative contributors.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:11-11, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:26-29, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:41-47, src/melder/spellbook/spell_crafter/spell_crafter.py:3405-3521
  IMPACT: This task is ranked second as a medium-risk, broad-impact warm-path optimization slice.
  NEXT: Profile helper-level allocations for path formatting and sorting inside phase8-10 row-build paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Created from measured phase-testing backlog ranking as the second hotspot
candidate after phase11 IR capture.

