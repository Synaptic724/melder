Completed: 2026-02-14
Summary: Accepted in the phase-testing closure pass; implementation and validation artifacts are captured in this task.

# Task: Optimize Phase11 Codegen IR Capture Hotpath

## Metadata
- Task ID: TASK-2026-02-14-optimize-phase11-codegen-ir-capture
- Story: STORY-2026-02-14-phase-testing-optimization-backlog
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Reduce cumulative time spent in Phase11 codegen IR capture/payload assembly on
the 8-11 warm path.

## Scope Boundaries
- In scope:
- Analyze and optimize `SpellCrafter` codegen IR capture/payload construction.
- Preserve existing execution-plan semantics and output contracts.
- Out of scope:
- Changing public API shape.
- Rewriting unrelated phase orchestration logic.

## Steps / Checklist
- [x] Profile and isolate per-function costs inside `_capture_phase8_11_codegen_ir`.
- [x] Optimize `_build_phase11_variant_ir_payload` and signature hashing path.
- [x] Add regression/perf-oriented tests for behavior parity.
- [x] Validate with component harness rerun and compare warm 8-11 total.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Source-level optimization in phase11 codegen IR path.
- Before/after measurement note in phase-testing backlog artifacts.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`
- `context_compass/tasks/completed/2026-02-14_discovery_phase_testing_optimization_backlog_task.md`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "capture_phase8_11_codegen_ir_signature_stable_across_map_insertion_orders or build_phase11_variant_ir_payload_signature_changes_on_variant_label or capture_phase8_11_codegen_ir_signature_changes_on_enriched_payload_semantics or build_phase11_variant_ir_payload_signature_changes_on_step_semantic_change"`
  - `python -m pytest -q -s tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`
- Result:
  - `3 passed, 140 deselected, 3 warnings in 0.16s`
  - `1 passed, 3 warnings in 0.32s`
- Output artifacts:
  - baseline: `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt`
  - post-change: `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_opt_output.txt`

## Risks / Rollback Notes
- Risk: optimization shifts may perturb codegen artifact identity contracts.
- Rollback: revert hotpath deltas and keep baseline behavior.

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
  CLAIM: Rank-1 optimization reduced warm 8-11 measured total from `34.993ms` to `27.829ms` in the component harness sample; warm cProfile sample improved from `0.091s` to `0.083s`.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:11-15, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_opt_output.txt:12-15
  IMPACT: Confirms measurable improvement on the targeted hotpath and validates this optimization slice.
  NEXT: Route active work to rank-2 task (`TASK-2026-02-14-optimize-phase8-10-plan-row-builders`).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Implemented signature-path optimization by introducing deterministic byte serialization fallback for signature parts and by hashing Phase11 `steps_rows` row-by-row instead of as one giant tuple payload.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:748-790, src/melder/spellbook/spell_crafter/spell_crafter.py:1775-1783
  IMPACT: Reduces signature construction overhead on repeated phase11 IR exports.
  NEXT: Preserve this as completed evidence and continue rank-ordered backlog execution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: PLAN
  CLAIM: Primary low-risk optimization slice is to reduce signature-building overhead in `_build_phase11_variant_ir_payload` by avoiding hashing one giant `steps_rows` tuple and to switch `_hash_codegen_signature` from `repr`-based serialization to faster deterministic byte serialization.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:747-767, src/melder/spellbook/spell_crafter/spell_crafter.py:1751-1768, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:21-24, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:30-36
  IMPACT: Targets the hottest cumulative path with minimal API surface change and should reduce warm 8-11 runtime overhead.
  NEXT: Implement the signature-path changes in `spell_crafter.py`, then run focused unit tests and the component harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Warm 8-11 cProfile shows `_capture_phase8_11_codegen_ir` and `_build_phase11_variant_ir_payload` as top cumulative hotspots, making phase11 codegen IR the highest-value optimization candidate.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:21-24, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:30-33, src/melder/spellbook/spell_crafter/spell_crafter.py:1717-1781
  IMPACT: This task is ranked first in the backlog because it targets the dominant warm-path cumulative costs.
  NEXT: Start with function-level timing instrumentation inside `_capture_phase8_11_codegen_ir`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Rank-1 optimization implementation is complete and validated with measured
before/after artifacts. Next routing target is rank-2:
`TASK-2026-02-14-optimize-phase8-10-plan-row-builders`.
