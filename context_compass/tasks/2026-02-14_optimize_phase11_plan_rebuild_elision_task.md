# Task: Optimize Phase11 Plan Rebuild Elision

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase11-plan-rebuild-elision
- Story: STORY-2026-02-14-phase-testing-optimization-backlog
- Status: review
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce warm phase11 overhead by eliding repeated no-overrides execution-plan
full builds when phase8-10 inputs are semantically unchanged.

## Scope Boundaries
- In scope:
- Add a deterministic phase11 input signature gate for no-overrides plan rebuild.
- Reuse cached no-overrides plan when the phase11 input signature is unchanged.
- Preserve override/mutation variant contracts and existing phase11 outputs.
- Add focused tests for rebuild-vs-reuse behavior.
- Out of scope:
- Rewriting phase8-10 builders.
- Changing exported phase8-11 IR schema.

## Steps / Checklist
- [x] Confirm phase11 warm hotspot and identify stable input-signature fields.
- [x] Implement no-overrides plan rebuild elision gate in `run_phase_execution_plan`.
- [x] Add/adjust focused unit tests for no-overrides rebuild-vs-reuse behavior.
- [x] Rerun targeted spell-crafter tests and component harness profile.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Phase11 no-overrides plan rebuild path that reuses previous plan when
  inputs are semantically unchanged.
- Validation artifacts showing behavior parity and warm profile impact.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `context_compass/artifacts/*phase11*plan_rebuild_elision*`

## Validation
- Executed:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "run_phase_execution_plan or execution_plan_variant or plan_rebuild_elision"` -> `5 passed, 152 deselected`.
  - `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` -> `1 passed`.
- Artifacts:
  - `context_compass/artifacts/2026-02-14_phase11_plan_rebuild_elision_targeted_unit_tests.txt`
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_rebuild_elision_output.txt`

## Risks / Rollback Notes
- Risk: stale no-overrides plan reuse when signature misses a compile-affecting
  phase8-10 semantic field.
- Rollback: remove elision gate and restore unconditional no-overrides rebuild.

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
  TYPE: FACT
  CLAIM: Warm profile after the plan-based compile optimization still shows one no-overrides full-build path per spell as a top phase11 slice (`_build_execution_plan_variant` + `ExecutionPlanBuilder.build`, 17 calls each).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_based_compile_output.txt:17-20, src/melder/spellbook/spell_crafter/spell_crafter.py:3888-3893, src/melder/spellbook/spell_crafter/spell_crafter.py:3931-3967
  IMPACT: There is a remaining phase11 warm-path optimization opportunity after the no-overrides compile-signature work.
  NEXT: Identify safe phase11 input signature fields to gate no-overrides rebuild reuse.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: PLAN
  CLAIM: Implement a deterministic phase11 no-overrides input signature gate keyed by the exact data consumed by `ExecutionPlanBuilder.build` (occurrence execution/graph rows, injection specs, and spell metadata used for step construction), then reuse cached phase11 plan variants when signature is unchanged.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/execution_plan.py:1186-1234, src/melder/spellbook/spell_crafter/blueprints/execution_plan.py:1242-1292, src/melder/spellbook/spell_crafter/blueprints/execution_plan.py:1334-1351, src/melder/spellbook/spell_crafter/spell_crafter.py:3888-3916
  IMPACT: Targets the current remaining phase11 warm hotspot while preserving plan-variant and compile cache contracts.
  NEXT: Add signature helpers/cached field in `SpellCrafter`, wire elision in `run_phase_execution_plan`, and add focused unit tests for unchanged-vs-changed signatures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: SpellCrafter now contains signature-scaffolding helpers for phase11 no-overrides input hashing, but the rebuild-elision gate is not wired yet because `run_phase_execution_plan` still unconditionally rebuilds `plan_no_overrides` via `_build_execution_plan_variant`.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:1841-2043, src/melder/spellbook/spell_crafter/spell_crafter.py:4069-4101, src/melder/spellbook/spell_crafter/spell_crafter.py:2441-2444
  IMPACT: Current repo state includes partial implementation only; warm-path rebuild cost remains until gate wiring lands.
  NEXT: Wire signature compare/store in `run_phase_execution_plan`, then add focused rebuild-vs-reuse tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: The phase11 no-overrides rebuild-elision gate is now wired: `run_phase_execution_plan` computes a deterministic no-overrides input signature, reuses cached no-overrides plan when unchanged, rebuilds when changed/missing, and persists the latest signature. Focused unit tests were added for unchanged-signature reuse and changed-signature rebuild behavior.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:4069-4141, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5781-5958
  IMPACT: This task now has implemented behavior for its core objective, pending validation run evidence.
  NEXT: Run targeted spell-crafter unit tests, then attach validation results and assess whether harness rerun is required in this pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Initial validation exposed compatibility gaps with minimal phase11 test stubs; `_build_phase11_no_overrides_input_signature` now returns `None` when required occurrence/injection signature inputs are missing (including missing `select_for_runtime`/injection-spec attributes), preserving the legacy rebuild path instead of raising.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:1964-1978, src/melder/spellbook/spell_crafter/spell_crafter.py:2024-2039
  IMPACT: Existing phase11 tests that intentionally stub partial plan artifacts can continue exercising run-path behavior without failing before rebuild logic.
  NEXT: Rerun targeted phase11 unit slice and record final pass/fail artifact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Component harness validation exposed a runtime attribute mismatch in the new spell signature row (`Spell` has no `is_callable` attribute). The row now derives callability from `spell.spell_type` categories, matching phase11 fast-plan semantics.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:1864-1881, src/melder/spellbook/spell_crafter/blueprints/execution_plan.py:1542-1545, src/melder/spellbook/spell.py:699-717
  IMPACT: Prevents runtime failure in real phase11 harness runs while keeping signature drift detection aligned with actual execution-plan behavior.
  NEXT: Re-run targeted unit slice and component harness to confirm full green validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Harness rerun exposed another signature-row mismatch: `self._should_register` is not a `SpellCrafter` method. The row now applies the same register rule used by `ExecutionPlanBuilder` (`Existence.many` without disposal methods is non-registering).
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:1877-1885, src/melder/spellbook/spell_crafter/blueprints/execution_plan.py:2119-2122
  IMPACT: Restores phase11 signature-row construction on real spell runs and keeps signature semantics aligned with plan-builder registration behavior.
  NEXT: Re-run targeted unit slice and component harness; if green, record final validation outputs and advance ticket status.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: The register-rule alignment fix required adding the missing `Existence` import in `spell_crafter.py`; without it, harness execution raised `NameError` at the signature row.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:26-26, src/melder/spellbook/spell_crafter/spell_crafter.py:1878-1879
  IMPACT: Unblocks phase11 signature-row evaluation in real harness runs.
  NEXT: Re-run the targeted unit slice and component harness after the import fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Final validation is green for this task: targeted phase11 unit slice passes (`5 passed`) and component harness rerun passes (`1 passed`) with warm 8-11 sample showing `group_8_11_total_ms=3.167` and `phase_execution_plan_ms=1.383`.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase11_plan_rebuild_elision_targeted_unit_tests.txt:1-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_rebuild_elision_output.txt:7-7, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_plan_rebuild_elision_output.txt:59-59
  IMPACT: Core task deliverable is implemented and validated; ticket can move through user acceptance/closure routing.
  NEXT: Review outcomes with user and confirm acceptance criteria for close/move decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task follow-up is now implemented and validated. `run_phase_execution_plan` now
gates no-overrides full rebuild by deterministic phase11 input signature with a
safe fallback to rebuild when signature inputs are unavailable. Focused unit
coverage and component harness reruns are green with captured artifacts. Next
step is user acceptance/closure routing.
