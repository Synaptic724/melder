# Task: Optimize Phase8-11 Codegen IR Capture Frequency

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase8-11-codegen-ir-capture-frequency
- Story: STORY-2026-02-13-optimize-spellcrafter-phases
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce repeated full phase8-11 IR/signature rebuilds during one spell phase
chain while preserving export correctness for downstream phase12/runtime usage.

## Scope Boundaries
- In scope:
- `SpellCrafter` phase8/9/10/11 capture call pattern and `_capture_phase8_11_codegen_ir`.
- Slice-level or dirty-flagged export strategy that avoids redundant rebuild work.
- Out of scope:
- Changing phase semantics or removing required phase12 IR fields.
- Runtime API shape changes.

## Steps / Checklist
- [x] Map current IR freshness requirements and phase-to-phase consumers.
- [x] Implement staged/dirty capture strategy with deterministic signature behavior.
- [x] Add/adjust tests validating phase8-11 export correctness and signature stability.
- [x] Validate with component harness warm/cold measurements for group 8-11.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Reduced `_capture_phase8_11_codegen_ir` recomputation frequency.
- Updated evidence showing non-regression and performance impact.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
- `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`

## Validation
- `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "capture_phase8_11_codegen_ir or compile_phase12_no_overrides_executor or phase8_10_runs_mark_phase8_11_codegen_ir_dirty_without_eager_capture or run_phase_execution_plan_flushes_phase8_11_codegen_ir_before_compile or codegen_ir_property_flushes_phase8_11_when_dirty"` -> `11 passed, 135 deselected`; output captured in `context_compass/artifacts/2026-02-14_phase8_11_capture_frequency_unit_tests.txt`.
- `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py` -> `146 passed`; output captured in `context_compass/artifacts/2026-02-14_phase8_11_capture_frequency_full_spell_crafter_unit_tests.txt`.
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` (run 1) -> `1 passed, 3 warnings`; output captured in `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output.txt`.
- `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py` (run 2) -> `1 passed, 3 warnings`; output captured in `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output_run2.txt`.

## Risks / Rollback Notes
- Risk: stale IR/signature state across phase transitions.
- Rollback: restore per-phase eager capture calls and current payload build flow.

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
  CLAIM: `src_architecture` and `src_components` now explicitly disambiguate dirty semantics: SpellCrafter `phase8_11` dirty means IR freshness invalidation, while change-control dirty roots remain meld-time revalidation gates.
  EVIDENCE: context_compass/architecture/src_architecture.md:470-487, context_compass/components/src_components.md:720-760, context_compass/components/src_components.md:810-817, context_compass/components/src_components.md:1071-1077, context_compass/components/src_components.md:1114-1118, src/melder/spellbook/spell_crafter/spell_crafter.py:529-546, src/melder/spellbook/spell_crafter/spell_crafter.py:1966-1997, src/melder/spellbook/spell_crafter/spell_crafter.py:3513-3517, src/melder/spellbook/spell_crafter/spell_crafter.py:3579-3583, src/melder/spellbook/spell_crafter/spell_crafter.py:3647-3651, src/melder/spellbook/spell_crafter/spell_crafter.py:3780-3787, src/melder/aether/dev_ops/change_control_manager/change_control_manager.py:1403-1475, src/melder/aether/conduit/meld/meld.py:502-532
  IMPACT: Future re-onboarding can quickly distinguish export-freshness invalidation from runtime dirty-root gating and avoid incorrect debugging assumptions.
  NEXT: Continue phase-story execution with this terminology as the canonical distinction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Routing docs were synchronized to rank-1 outcomes; story/epic/attention-board now point to dirty-capture validation artifacts and rank-2 as next step.
  EVIDENCE: context_compass/stories/2026-02-13_optimize_spellcrafter_phases_story.md:67-100, context_compass/epics/2026-02-13_optimize_melder_epic.md:122-157, context_compass/attention_board.md:23-38
  IMPACT: Re-entry context now reflects current execution state and avoids stale 'execute rank-1' routing.
  NEXT: Request user acceptance for rank-1 and either close task or proceed directly to rank-2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Harness reruns show major warm 8-11 reduction after dirty-capture strategy (`group_8_11_total_ms`: `26.496/26.023` -> `10.610/10.567`; warm cProfile sample `0.081/0.082s` -> `0.035/0.035s`).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output_run2.txt:7-9
  IMPACT: Rank-1 task delivers strong measured ROI by removing repeated phase8-11 IR rebuilds from the warm phase chain.
  NEXT: Sync story/epic/attention-board evidence pointers and request user acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Full spell-crafter unit suite passed after the capture-frequency change (`146 passed`), confirming broad non-regression beyond focused phase8-11 tests.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase8_11_capture_frequency_full_spell_crafter_unit_tests.txt:14-14
  IMPACT: Increases confidence that dirty-capture flow does not break existing spell-crafter contracts.
  NEXT: Use harness deltas to finalize rank-1 review package.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Focused unit validation passed for phase8_11 capture/compile paths, including new dirty-capture behavior tests.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase8_11_capture_frequency_unit_tests.txt:12-12, tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:5298-5474
  IMPACT: Confirms behavior-level correctness for the new dirty flush contract before performance measurement.
  NEXT: Run component harness reruns and compare warm group_8_11 totals against pre-change anchors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Implemented dirty-capture strategy in `SpellCrafter`: phases8-10 now mark phase8_11 IR dirty instead of eager capture, phase11 flushes dirty IR before phase12 compile, and `codegen_ir` property performs lazy dirty flush for external readers.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:200-200, src/melder/spellbook/spell_crafter/spell_crafter.py:529-545, src/melder/spellbook/spell_crafter/spell_crafter.py:1966-1995, src/melder/spellbook/spell_crafter/spell_crafter.py:3473-3516, src/melder/spellbook/spell_crafter/spell_crafter.py:3523-3582, src/melder/spellbook/spell_crafter/spell_crafter.py:3589-3651, src/melder/spellbook/spell_crafter/spell_crafter.py:3729-3786
  IMPACT: Removes repeated eager phase8_11 rebuilds in phase chain while preserving freshness at phase11 compile boundary and on-demand reads.
  NEXT: Validate with focused spell-crafter unit tests and component harness reruns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: The critical `phase8_11` IR consumers require execution-variant payloads that are only meaningful after phase11 build, and run-phase flow already compiles phase12 immediately after phase11 capture.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:1979-2027, src/melder/spellbook/spell_crafter/spell_crafter.py:3740-3747, src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:232-240, src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:257-266
  IMPACT: We can safely reduce eager capture calls in phases8-10 if we preserve freshness before phase12 compile and on-demand external IR reads.
  NEXT: Implement a dirty-flag capture policy: mark dirty in phases8-10, eagerly flush in phase11, and lazy-flush on `codegen_ir` access.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Warm phase8-11 profiling shows `_capture_phase8_11_codegen_ir` as the dominant SpellCrafter frame, called 68 times in one warm run due to invocation after each phase8/9/10/11 pass.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:17-22, src/melder/spellbook/spell_crafter/spell_crafter.py:3473-3477, src/melder/spellbook/spell_crafter/spell_crafter.py:3539-3542, src/melder/spellbook/spell_crafter/spell_crafter.py:3607-3611, src/melder/spellbook/spell_crafter/spell_crafter.py:3740-3746, src/melder/spellbook/spell_crafter/spell_crafter.py:1809-1959
  IMPACT: This is the top-ranked follow-up candidate for reducing repeated phase8-11 export overhead.
  NEXT: Begin by codifying exact IR freshness contract by phase boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Rank-1 implementation is complete and in review. SpellCrafter now uses
phase8_11 dirty capture semantics (mark in phases8-10, flush at phase11 and on
`codegen_ir` read). Focused and full spell-crafter unit suites passed, and
component harness reruns show major warm 8-11 reductions with stable repeated
samples. Next step is user acceptance and then rank-2 task execution.
