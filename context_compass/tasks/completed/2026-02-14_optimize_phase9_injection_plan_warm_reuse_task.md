Completed: 2026-02-14
Summary: Accepted in the phase-testing closure pass; implementation and validation artifacts are captured in this task.

# Task: Optimize Phase9 Injection Plan Warm Reuse

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase9-injection-plan-warm-reuse
- Story: STORY-2026-02-14-phase-testing-optimization-backlog
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce warm phase8-11 overhead by reusing phase9 injection plans when deterministic phase9 inputs are unchanged and a cached injection plan is present.

## Scope Boundaries
- In scope:
- Add deterministic phase9 injection-plan input signature tracking in `SpellCrafter`.
- Reuse cached injection plan on unchanged signature.
- Preserve rebuild behavior when signature changes/missing or cache is absent.
- Add focused tests for unchanged-signature reuse and changed-signature rebuild.
- Out of scope:
- Rewriting `InjectionPlanBuilder` internals.
- Changing injection-plan schema/contracts.

## Steps / Checklist
- [x] Confirm phase9 injection-plan rebuild remains a measurable warm hotspot after phase8 follow-up.
- [x] Implement phase9 injection-plan warm-reuse gate in `run_phase_injection_plan`.
- [x] Add focused unit tests for unchanged-signature reuse and changed-signature rebuild.
- [x] Rerun targeted spell-crafter tests and component harness profile.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Phase9 warm path that reuses cached injection plans on stable phase9 inputs.
- Validation artifacts showing behavior parity and warm profile impact.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `context_compass/artifacts/*phase9*injection_plan_warm_reuse*`

## Validation
- Executed:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "run_phase_injection_plan or injection_plan_warm_reuse or phase8_10_runs_mark_phase8_11_codegen_ir_dirty_without_eager_capture"` -> `3 passed, 161 deselected`.
  - `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` -> `1 passed`.
- Artifacts:
  - `context_compass/artifacts/2026-02-14_phase9_injection_plan_warm_reuse_targeted_unit_tests.txt`
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase9_injection_plan_warm_reuse_output.txt`

## Risks / Rollback Notes
- Risk: stale injection plans if signature omits an injection-affecting occurrence-plan field.
- Rollback: remove phase9 warm-reuse gate and restore unconditional injection-plan rebuild.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Validation is green for this follow-up: targeted spell-crafter slice passes (`3 passed`) and harness rerun passes (`1 passed`) with reduced warm phase9 slice (`phase_injection_plan_ms` `0.179 -> 0.164`) and fewer warm injection-plan builds (`17 -> 15`), while total warm 8-11 time remains near-neutral/noisy (`2.114 -> 2.161`, both at `0.008s` cProfile runtime).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase9_injection_plan_warm_reuse_targeted_unit_tests.txt:1-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase9_injection_plan_warm_reuse_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase9_injection_plan_warm_reuse_output.txt:25-28, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase9_injection_plan_warm_reuse_output.txt:59-59, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_occurrence_plan_warm_reuse_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_occurrence_plan_warm_reuse_output.txt:28-28
  IMPACT: Phase9-specific work is reduced with no correctness regressions in targeted coverage; full warm-chain impact is modest and within run-to-run noise.
  NEXT: Route task/story/epic to review and walk acceptance with user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Implemented phase9 warm-reuse gate: `SpellCrafter` now tracks an injection-plan input signature derived from occurrence-plan semantics, reuses cached injection plan on unchanged signature, and rebuilds when signature changes/missing. Added focused unit tests covering unchanged-signature reuse and changed-signature rebuild behavior.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:194-245, src/melder/spellbook/spell_crafter/spell_crafter.py:910-988, src/melder/spellbook/spell_crafter/spell_crafter.py:4152-4222, src/melder/spellbook/spell_crafter/spell_crafter.py:2719-2719, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5701-5839
  IMPACT: Core task behavior is implemented and ready for validation reruns.
  NEXT: Run targeted spell-crafter slice and component harness rerun, then attach artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: After the phase8 follow-up, warm profile still shows phase9 injection-plan rebuild as a measurable slice (`phase_injection_plan_ms=0.179`) with `run_phase_injection_plan` and `InjectionPlanBuilder.build` present in warm top profile.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_occurrence_plan_warm_reuse_output.txt:7-7, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_occurrence_plan_warm_reuse_output.txt:25-28, src/melder/spellbook/spell_crafter/spell_crafter.py:4081-4126
  IMPACT: There is a remaining warm-path opportunity in phase9 after phase8/10 reuse work.
  NEXT: Implement phase9 signature gate for injection-plan reuse and validate with targeted tests/harness reruns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: PLAN
  CLAIM: Add a deterministic phase9 input signature derived from occurrence-plan compile-affecting fields, gate `run_phase_injection_plan` on unchanged signature + cached plan, and preserve fallback full-build behavior when signature cannot be computed.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:4019-4126, src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:486-531
  IMPACT: Should reduce warm phase9 overhead without changing injection-plan semantics.
  NEXT: Implement phase9 signature field/helper and add focused reuse-vs-rebuild tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
New follow-up task opened from latest warm profile where phase9 injection-plan
rebuild remains a measurable warm slice after phase8/10 improvements. No code
changes for this task are implemented, with focused unit coverage added.
Validation reruns are complete and green with reduced phase9 slice and
near-neutral total warm-chain impact.
