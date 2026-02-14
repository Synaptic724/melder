Completed: 2026-02-14
Summary: Accepted in closure pass; all linked tasks are complete and archived.

# Story: Optimize SpellCrafter Phases

## Metadata
- Story ID: STORY-2026-02-13-optimize-spellcrafter-phases
- Epic: EPIC-2026-02-13-optimize-melder
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14

## User Narrative
As a Melder maintainer, I want SpellCrafter phase costs mapped and prioritized,
so that phase execution remains efficient as graph complexity grows.

## Value / MRP Alignment
SpellCrafter phase overhead impacts both conjure preparation and runtime safety.
Discovery-first optimization gives us a stable path to reduce overhead safely.

## Requirements (Functional)
- Identify highest-cost SpellCrafter phase operations and data-flow bottlenecks.
- Produce ranked optimization opportunities with evidence.
- Capture follow-up implementation tasks from discovery findings.

## Requirements (Non-Functional)
- Discovery pass must not alter phase semantics.
- Findings must include reproducible evidence references.

## Scope Boundaries
- In scope:
- SpellCrafter phase execution path and phase-generated artifacts.
- Phase-level validation and planning overhead analysis.
- Out of scope:
- Direct meld dispatch optimization.
- Mutation research runtime wiring.

## Dependencies / Related Work
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/spellbook/spell_crafter/system/spell_system_validation_system.py`
- `src/melder/spellbook/spell_crafter/dag/resolution_frame/resolution_frame.py`
- `EPIC-2026-02-13-optimize-melder`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-13-discovery-spellcrafter-phases - Build discovery baseline, hotspot map, and prioritized optimization candidates for SpellCrafter phases. (`context_compass/tasks/completed/2026-02-13_discovery_spellcrafter_phases_task.md`)
- [x] Task: TASK-2026-02-14-optimize-phase8-11-codegen-ir-capture-frequency - Reduce repeated phase8-11 capture rebuild work with contract-safe staging. (`context_compass/tasks/completed/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md`)
- [x] Task: TASK-2026-02-14-optimize-phase11-signature-hash-pipeline - Reduce signature/hash serialization overhead in phase11 export. (`context_compass/tasks/completed/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md`)
- [x] Task: TASK-2026-02-14-optimize-phase8-10-codegen-row-builders-contract-fastpath - Remove defensive hot-path probing in row builders using contract-backed access. (`context_compass/tasks/completed/2026-02-14_optimize_phase8_10_codegen_row_builder_contract_fastpath_task.md`)

## Acceptance Criteria
- Discovery output identifies top SpellCrafter phase hotspots with evidence.
- Follow-up optimization tasks are documented and prioritized.

## Validation / Test Plan
- Use targeted code-path inspection and relevant existing test/benchmark hooks.
- Record commands and outputs for any executed measurements.

## UX / API / Data Notes
- Internal optimization planning only; no API change in discovery pass.

## Risks / Mitigations
- Risk: optimizing one phase causes regressions in others.
  Mitigation: capture per-phase boundaries and dependencies in findings.

## Open Questions
- Which phase groups should be treated as highest ROI for the first implementation pass?

## Decision Log
- 2026-02-13: Story created from user-requested optimization epic setup.

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-2 signature pipeline task moved to review after tuple-hash update for `steps_rows_signature`; latest harness shows reduced signature-path churn and improved warm profile shape (`10.833ms -> 9.804ms`, serializer calls `996 -> 612`, pickle calls `724 -> 340`).
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md:6-93, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run7.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt:7-41
  IMPACT: SpellCrafter rank-2 now has measurable warm-path gain and can be closed after user acceptance.
  NEXT: Walk rank-1/rank-2/rank-3 outcomes with user and request closure direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-3 row-builder contract-fastpath task is implemented and validated across two harness reruns; warm `group_8_11_total_ms` measured `11.047` then `10.266`, and warm cProfile sample was `0.034s` with `122060` calls versus pre-rank3 rank-2 samples `0.036s` with `123618` calls.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase8_10_codegen_row_builder_contract_fastpath_task.md:1-105, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_contract_fastpath_output.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_10_contract_fastpath_output_run2.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run6.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run7.txt:7-38
  IMPACT: Ranked SpellCrafter follow-up tasks are now implemented and validated; remaining work is acceptance/closure direction, not additional unplanned implementation.
  NEXT: Rank-3 is accepted and closed; review rank-1/rank-2 closure direction or proceed to the next discovery story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-2 signature-pipeline task is implemented with regression rollback and final container-first scalar fastpath dispatch; measured result is near-neutral wall time with reduced pickle calls.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md:61-148, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output_run2.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run6.txt:7-39, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run7.txt:7-39
  IMPACT: Rank-2 is stable and ready for keep-vs-iterate decision as a low-risk internal cleanup with reduced pickle calls but near-neutral wall-time effect.
  NEXT: Evaluate rank-2 together with rank-3 in final acceptance walkthrough.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-1 SpellCrafter task is implemented and in review with strong warm 8-11 gains after dirty-capture rollout.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md:6-58, context_compass/tasks/completed/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md:60-82, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output_run2.txt:7-9
  IMPACT: Story has validated execution progress; next priority can move to rank-2 after acceptance.
  NEXT: Review rank-1 outcomes with user and confirm whether to proceed immediately to rank-2 signature pipeline task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Discovery is complete and produced a ranked execution plan: (1) capture-frequency reduction, (2) signature hash pipeline optimization, (3) contract-fastpath row builder cleanup.
  EVIDENCE: context_compass/tasks/completed/2026-02-13_discovery_spellcrafter_phases_task.md:63-111, context_compass/tasks/completed/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md:1-76, context_compass/tasks/completed/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md:1-76, context_compass/tasks/completed/2026-02-14_optimize_phase8_10_codegen_row_builder_contract_fastpath_task.md:1-105
  IMPACT: Story moved from discovery-ready to execution-ready with explicit ranked tasks.
  NEXT: Start rank-1 task (`TASK-2026-02-14-optimize-phase8-11-codegen-ir-capture-frequency`).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Notes section added to enforce active_documentation for in-flight findings.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/active_documentation.md:1
  IMPACT: Keeps ticket memory durable across compaction by requiring evidence-backed notes.
  NEXT: Append new findings here as work continues.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
## Context / Handoff Summary
Story discovery is complete and in-progress execution has started with three
ranked implementation tasks now queued. Rank-1 is implemented with strong warm
8-11 reduction evidence. Rank-2 is now implemented and in review with tuple-hash
signature updates after one discarded regression attempt; latest run shows
measurable warm improvement and lower serializer/pickle churn. Rank-3 is now implemented with contract-
strict row builders plus fail-fast tests and two harness reruns showing mixed
wall-time variance (`11.047`, `10.266`) but lower warm profile call volume/time
shape versus rank-2 (`122060` calls at `0.034s` vs `123618` at `0.036s`). Next
step is user closure direction for rank-1/rank-2; rank-3 is accepted and closed.

