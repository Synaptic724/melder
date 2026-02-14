# Task: Optimize Phase11 Execution Plan Variant Reuse

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase11-execution-plan-variant-reuse
- Story: STORY-2026-02-14-phase-testing-optimization-backlog
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce warm 8-11 phase11 overhead by avoiding redundant full rebuilds of
execution-plan structural data across override variants.

## Scope Boundaries
- In scope:
- Optimize `SpellCrafter.run_phase_execution_plan` variant-construction path.
- Preserve all phase11/phase12 signatures, variant labels, and runtime behavior.
- Out of scope:
- Rewriting `ExecutionPlanBuilder` internals.
- Changing public API contracts.

## Steps / Checklist
- [ ] Confirm safe reuse boundaries for phase11 plan variant data.
- [ ] Implement low-risk variant reuse with compatibility fallback.
- [ ] Add/adjust focused tests for variant semantics and execution-plan lifecycle.
- [ ] Rerun focused spell-crafter tests and component harness for warm 8-11.
- [ ] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Reduced repeated phase11 variant build churn on warm 8-11 path.
- Updated measurements comparing pre/post warm profile for this slice.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `context_compass/stories/2026-02-14_phase_testing_optimization_backlog_story.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "run_phase_execution_plan_flushes_phase8_11_codegen_ir_before_compile or capture_phase8_11_codegen_ir_exports_sorted_payloads or capture_phase8_11_codegen_ir_signature_stable_across_map_insertion_orders or build_phase11_variant_ir_payload_signature_changes_on_variant_label or build_phase11_variant_ir_payload_signature_changes_on_step_semantic_change"`
  - `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Risks / Rollback Notes
- Risk: variant reuse could accidentally collapse per-variant semantics.
- Rollback: revert to per-variant rebuild path in `run_phase_execution_plan`.

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
  TYPE: PLAN
  CLAIM: Implement a no-overrides-base reuse path in `run_phase_execution_plan`: build `NO_OVERRIDES_FAST` once, derive `OVERRIDES` and `OVERRIDES_WITH_MUTATIONS` plans from shared structural data, and fallback to legacy per-variant rebuild when base-plan shape is incompatible (for test stubs/edge cases).
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:3726-3743, src/melder/spellbook/spell_crafter/blueprints/execution_plan.py:700-714, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:4234-4258, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5537-5567
  IMPACT: Should cut repeated phase11 builder churn while preserving cleanup safety and existing test stub compatibility.
  NEXT: Add helper methods in `SpellCrafter`, then add focused tests and run targeted validation/harness rerun.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Latest warm 8-11 profile still shows phase11 variant rebuild churn as a top cumulative hotspot (`51` calls each to `_build_execution_plan_variant` and `ExecutionPlanBuilder.build`), and current phase11 flow constructs three separate plans per spell by full rebuild.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_opt_output_run3.txt:17-23, src/melder/spellbook/spell_crafter/spell_crafter.py:3726-3743, src/melder/spellbook/spell_crafter/blueprints/execution_plan.py:1171-1201
  IMPACT: There is a measurable optimization opportunity to reuse shared phase11 structure across variants without touching public interfaces.
  NEXT: Implement variant reuse from no-overrides base with a safe fallback when plan shape is not compatible.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task opened from the latest warm profile after rank1/rank2/rank3 completion.
Primary target is phase11 variant rebuild churn in `run_phase_execution_plan`.
Next step is code implementation plus focused tests and harness rerun.
