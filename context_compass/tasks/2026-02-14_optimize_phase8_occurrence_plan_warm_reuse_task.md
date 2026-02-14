# Task: Optimize Phase8 Occurrence Plan Warm Reuse

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase8-occurrence-plan-warm-reuse
- Story: STORY-2026-02-14-phase-testing-optimization-backlog
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce warm phase8-11 overhead by reusing phase8 occurrence plans when deterministic phase8 inputs are unchanged and a cached occurrence plan is present.

## Scope Boundaries
- In scope:
- Add deterministic phase8 occurrence-plan input signature tracking in `SpellCrafter`.
- Reuse cached occurrence plan on unchanged signature.
- Preserve current rebuild behavior when signature is changed/missing or cache is absent.
- Add focused tests for unchanged-signature reuse and changed-signature rebuild.
- Out of scope:
- Rewriting `OccurrencePlanBuilder` internals.
- Changing occurrence-plan artifact schema.

## Steps / Checklist
- [x] Confirm phase8 occurrence-plan rebuild remains top warm hotspot after phase10 follow-up.
- [x] Implement phase8 occurrence-plan warm-reuse gate in `run_phase_occurrence_plan`.
- [x] Add focused unit tests for unchanged-signature reuse and changed-signature rebuild.
- [x] Rerun targeted spell-crafter tests and component harness profile.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Phase8 warm path that reuses cached occurrence plans on stable phase8 inputs.
- Validation artifacts showing behavior parity and warm profile impact.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `context_compass/artifacts/*phase8*occurrence_plan_warm_reuse*`

## Validation
- Executed:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "run_phase_occurrence_plan or occurrence_plan_warm_reuse or phase8_10_runs_mark_phase8_11_codegen_ir_dirty_without_eager_capture"` -> `3 passed, 159 deselected`.
  - `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` -> `1 passed`.
- Artifacts:
  - `context_compass/artifacts/2026-02-14_phase8_occurrence_plan_warm_reuse_targeted_unit_tests.txt`
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_occurrence_plan_warm_reuse_output.txt`

## Risks / Rollback Notes
- Risk: stale occurrence plans if signature omits a phase8-affecting input.
- Rollback: remove phase8 warm-reuse gate and restore unconditional occurrence-plan rebuild.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Validation is green for this follow-up: targeted spell-crafter slice passes (`3 passed`) and harness rerun passes (`1 passed`) with lower warm 8-11 total (`group_8_11_total_ms` `2.206 -> 2.114`), lower warm execution-plan slice (`0.988 -> 0.751`), and stable warm runtime (`0.008s`) despite slightly higher call count (`25787 -> 26552`).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase8_occurrence_plan_warm_reuse_targeted_unit_tests.txt:1-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_occurrence_plan_warm_reuse_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_occurrence_plan_warm_reuse_output.txt:59-59, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase10_patch_maps_warm_reuse_output.txt:7-9
  IMPACT: Task objective is implemented and validated with net warm-path gain on total phase8-11 chain.
  NEXT: Route task/story/epic to review and walk acceptance with user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Implemented phase8 warm-reuse gate: `SpellCrafter` now tracks a conservative occurrence-plan input signature, reuses cached occurrence plan on unchanged signature, and rebuilds when signature changes/missing. Added focused unit tests covering unchanged-signature reuse and changed-signature rebuild behavior.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:192-242, src/melder/spellbook/spell_crafter/spell_crafter.py:779-911, src/melder/spellbook/spell_crafter/spell_crafter.py:4019-4073, src/melder/spellbook/spell_crafter/spell_crafter.py:2648-2648, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5556-5700
  IMPACT: Core task behavior is implemented and ready for validation reruns.
  NEXT: Run targeted spell-crafter slice and component harness rerun, then attach artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: After phase10 warm-reuse improvements, phase8 occurrence-plan rebuild remains the largest warm slice (`phase_occurrence_plan_ms=1.016`) with `run_phase_occurrence_plan` + `OccurrencePlanBuilder.build` at the top of warm profile.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase10_patch_maps_warm_reuse_output.txt:7-7, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase10_patch_maps_warm_reuse_output.txt:17-19, src/melder/spellbook/spell_crafter/spell_crafter.py:3887-3930
  IMPACT: There is one more high-leverage warm-path candidate in the phase8->11 chain.
  NEXT: Implement phase8 signature gate for occurrence-plan reuse and validate with targeted tests/harness reruns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: PLAN
  CLAIM: Add a conservative phase8 input signature that includes phase5 blueprint structure plus key spell/topology/contract-routing signals used by `OccurrencePlanBuilder`, gate `run_phase_occurrence_plan` on unchanged signature + cached plan, and preserve fallback full-build behavior when signature cannot be computed.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:3887-3930, src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:540-620, src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:854-1128, src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py:1578-1668
  IMPACT: Should remove repeated phase8 build cost on warm runs while maintaining safety under changing inputs.
  NEXT: Implement phase8 signature helper/field, add tests for reuse-vs-rebuild, then run validations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
New follow-up task opened from latest warm profile where phase8 occurrence-plan
rebuild is now the dominant remaining warm phase8-11 slice. No code changes for
this task are implemented, with focused unit coverage added. Validation reruns
are complete and green with net warm-chain gain. Next step is user
acceptance/closure routing.
