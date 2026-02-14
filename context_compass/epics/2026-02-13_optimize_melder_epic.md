# Epic: Optimize Melder Runtime and Codegen

## Metadata
- Epic ID: EPIC-2026-02-13-optimize-melder
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14
- Target Window: 2026-Q1
- Related Program/Initiative: Melder Performance Wave

## Problem / Opportunity
Melder has multiple performance-critical planes (`conjure`, `meld`,
SpellCrafter phases, CreationContext codegen, and Phase 12 codegen). We need a
single structured epic to drive discovery-first optimization and prevent
scattershot changes.

## MRP Alignment (Most Reasonable Product)
This epic keeps optimization work coherent and durable by starting with explicit
discovery in each subsystem before implementation tasks. That preserves
correctness while improving throughput and latency on real runtime paths.

## Goals (Outcomes)
- Establish discovery baselines for each targeted optimization surface.
- Produce ranked, evidence-backed optimization opportunities per surface.
- Convert discovery outputs into scoped follow-up tasks without widening scope.

## Non-Goals (Explicit Exclusions)
- Immediate broad refactors without subsystem-level discovery evidence.
- Public API redesign as part of this planning pass.
- Mutation research/runtime wiring work (currently out of scope).

## Scope Boundaries
- In scope:
- `conjure` performance path discovery.
- `meld` performance path discovery.
- SpellCrafter phase performance discovery.
- CreationContext codegen performance discovery.
- Phase 12 codegen performance discovery.
- Out of scope:
- Unrelated architecture/doc revalidation work already closed.
- Mutation research runtime wiring.

## Success Metrics
- Five linked stories exist with clear discovery tasks and acceptance criteria.
- Each discovery story yields a prioritized optimization task list with evidence.
- Epic remains traceable and compaction-safe via ticket linkage.

## Requirements (Functional + Non-Functional)
- Every story under this epic starts with exactly one discovery task.
- Discovery outputs must include: baseline, hotspot map, and candidate actions.
- Maintain Unknowns Gate discipline: unverified claims stay UNKNOWN.
- Keep implementation changes out of this setup pass.

## Constraints / Assumptions
- Constraints:
- Use existing ticket templates and folder conventions.
- Keep planning artifacts reviewable and cross-linked.
- Assumptions:
- Existing benchmark/test harnesses are available for later discovery validation.

## Dependencies / External References
- `context_compass/WORKFLOW.md`
- `context_compass/templates/epic_template.md`
- `context_compass/templates/story_template.md`
- `src/melder/spellbook/spellbook_creation_system.py`
- `src/melder/aether/conduit/meld/meld.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`

## Milestones (Track Progress)
- [ ] Milestone 1: Discovery scaffolding created and approved for all five stories.
- [ ] Milestone 2: Discovery tasks completed with evidence-backed findings.
- [ ] Milestone 3: Follow-up implementation tasks added and prioritized.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-13-optimize-conjure-paths - Discovery-first optimization plan for conjure paths.
- [ ] Story: STORY-2026-02-13-optimize-meld-paths - Discovery-first optimization plan for meld paths.
- [ ] Story: STORY-2026-02-13-optimize-spellcrafter-phases - Discovery-first optimization plan for SpellCrafter phases.
- [ ] Story: STORY-2026-02-13-optimize-creation-context-codegen - Discovery-first optimization plan for CreationContext codegen.
- [x] Story: STORY-2026-02-13-optimize-phase12-codegen - Discovery-first optimization plan for Phase 12 codegen.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-02-13-optimize-conjure-paths.
- [ ] Task: Complete story STORY-2026-02-13-optimize-meld-paths.
- [ ] Task: Complete story STORY-2026-02-13-optimize-spellcrafter-phases.
- [ ] Task: Complete story STORY-2026-02-13-optimize-creation-context-codegen.
- [x] Task: Complete story STORY-2026-02-13-optimize-phase12-codegen.
- [ ] Task: Keep architecture/components docs synced when optimization behavior changes.

## Acceptance Criteria (Epic Done)
- All five discovery stories are completed and accepted by the user.
- Each story includes evidence-backed findings and concrete follow-up tasks.
- Optimization scope and priority order are agreed for implementation phase.

## Risks / Mitigations
- Risk: premature optimization without evidence.
  Mitigation: discovery-first gate in every story.
- Risk: scope creep across runtime subsystems.
  Mitigation: strict story boundaries and explicit out-of-scope sections.

## Validation / Test Approach
- Discovery validation via code-path evidence and targeted benchmark/test runs as
  applicable per story.
- No blanket claims without explicit run output.

## Rollout / Adoption Plan
- Complete discovery in each story.
- Review findings with user.
- Expand each story with implementation tasks in priority order.

## Open Questions
- What throughput/latency targets should define success for this wave?
- Which workloads should be treated as primary optimization baselines?

## Decision Log
- 2026-02-13: User requested a new optimization epic with five discovery-first stories.

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: SpellCrafter rank-2 signature pipeline task moved to review after tuple-hash `steps_rows_signature` update; latest harness shows warm gain (`10.833ms -> 9.804ms`) and reduced signature serialization churn (`996 -> 612`, pickle `724 -> 340`).
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md:6-93, src/melder/spellbook/spell_crafter/spell_crafter.py:1756-1758, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run7.txt:7-38, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_signature_pipeline_output_run8.txt:7-41
  IMPACT: Epic SpellCrafter lane now has rank-1 (review), rank-2 (review), and rank-3 (done), with closure pending user acceptance direction.
  NEXT: Walk SpellCrafter rank outcomes with user and close/move accepted tickets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Conjure story now has all three ranked follow-up tasks implemented and in review (scheduler-lifecycle reduction, phase-unit-allocation fastpath, activation/validation scan fastpath) with fresh validation artifacts.
  EVIDENCE: context_compass/tasks/2026-02-14_conjure_scheduler_lifecycle_reduction_task.md:6-47, context_compass/tasks/2026-02-14_conjure_phase_unit_allocation_fastpath_task.md:6-62, context_compass/tasks/2026-02-14_conjure_activation_and_validation_scan_fastpath_task.md:6-44, context_compass/artifacts/2026-02-14_conjure_scheduler_lifecycle_single_run_fastpath_pytests.txt:1-12, context_compass/artifacts/2026-02-14_conjure_phase_unit_allocation_fastpath_pytests.txt:1-12, context_compass/artifacts/2026-02-14_conjure_activation_validation_scan_fastpath_pytests.txt:1-12
  IMPACT: Epic conjure lane is ready for user acceptance-driven closure routing.
  NEXT: Confirm acceptance for the three conjure review tasks and move approved tickets to completed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Conjure scheduler-lifecycle reduction is now implemented and in review: conduit resolution phases 5-11 run in a single scheduler lifecycle with preserved foundational-error plan gating semantics.
  EVIDENCE: context_compass/tasks/2026-02-14_conjure_scheduler_lifecycle_reduction_task.md:6-33, src/melder/spellbook/spellbook_creation_system.py:740-759, src/melder/spellbook/spellbook_creation_system.py:852-933, context_compass/artifacts/2026-02-14_conjure_scheduler_lifecycle_single_run_fastpath_pytests.txt:1-12
  IMPACT: Highest-ranked conjure hotspot has moved from discovery into validated implementation.
  NEXT: Request user acceptance for scheduler-lifecycle reduction and continue closure routing for remaining conjure tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: User accepted phase12 execution outcomes and reported improved override benchmark behavior; phase12 story/task lane is now closed for this wave.
  EVIDENCE: context_compass/artifacts/2026-02-14_user_reported_override_perf_test_overrides_all.txt:1-30, context_compass/stories/completed/2026-02-13_optimize_phase12_codegen_story.md:1-5
  IMPACT: Epic progress for phase12 moved from review to closed-completed state.
  NEXT: Keep epic focus on remaining active stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Phase12 benchmark-entrypoint repair is implemented and validated in review; current-head route-matrix artifacts now regenerate successfully.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:6-6, context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:37-43, context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:62-68, context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output_repaired.txt:1-3, context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_report_repaired.json:19-31
  IMPACT: Phase12 lane is now fully execution-complete in review (rank-1, rank-2, and measurement-unblock task), pending user acceptance and closure moves.
  NEXT: Request user acceptance for phase12 review tasks and close/move approved tickets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Phase12 rank-2 helper-callpath tightening is implemented and validated in review with focused blueprint tests passing.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:6-6, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:38-46, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:63-69, context_compass/artifacts/2026-02-14_phase12_override_helper_callpath_tightening_blueprint_pytests.txt:1-1, context_compass/artifacts/2026-02-14_phase12_override_helper_callpath_tightening_blueprint_pytests.txt:12-12
  IMPACT: Epic phase12 lane now has two validated implementation tasks (rank-1 and rank-2), with benchmark-entrypoint repair remaining for fresh route metrics.
  NEXT: Request user acceptance for rank-1/rank-2 closures, then execute benchmark-entrypoint repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Phase12 rank-1 implementation (shape-specialized source + plan-signature cache routing) is complete and validated in review with targeted suites passing.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:6-6, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:41-49, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:66-72, context_compass/artifacts/2026-02-14_phase12_override_shape_specialized_source_targeted_pytests.txt:1-1, context_compass/artifacts/2026-02-14_phase12_override_shape_specialized_source_targeted_pytests.txt:12-12
  IMPACT: Epic phase12 lane has moved from ranked planning into validated execution, leaving rank-2 helper-callpath tightening and benchmark-entrypoint repair as next actions.
  NEXT: Request user acceptance for rank-1 closure and then execute rank-2 task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Phase12 discovery is complete with ranked follow-up tasks (shape-specialized source, helper callpath tightening) plus a benchmark-entrypoint repair task to unblock fresh current-head route metrics.
  EVIDENCE: context_compass/tasks/2026-02-13_discovery_phase12_codegen_task.md:157-164, context_compass/stories/completed/2026-02-13_optimize_phase12_codegen_story.md:63-70, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:1-70, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:1-68, context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:1-66
  IMPACT: Epic now has execution-ready scope for all targeted discovery tracks, with phase12 sequencing and measurement-unblock path explicitly defined.
  NEXT: Request user acceptance for phase12 discovery closure, then execute rank-1 phase12 task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: SpellCrafter rank-1 execution task is implemented and in review with major warm 8-11 reduction after phase8-11 dirty-capture rollout.
  EVIDENCE: context_compass/tasks/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md:6-58, context_compass/tasks/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md:60-90, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output.txt:7-9, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase8_11_capture_freq_opt_output_run2.txt:7-9
  IMPACT: Epic’s SpellCrafter branch has moved from planning-only into high-impact validated implementation.
  NEXT: Confirm rank-1 acceptance and continue with rank-2 signature pipeline task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: SpellCrafter discovery moved from ready to execution-ready: hotspot mapping is complete and three ranked follow-up tasks are now queued under the story.
  EVIDENCE: context_compass/tasks/2026-02-13_discovery_spellcrafter_phases_task.md:6-113, context_compass/stories/2026-02-13_optimize_spellcrafter_phases_story.md:6-55, context_compass/tasks/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md:1-76, context_compass/tasks/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md:1-76, context_compass/tasks/completed/2026-02-14_optimize_phase8_10_codegen_row_builder_contract_fastpath_task.md:1-105
  IMPACT: Epic progress advanced on the SpellCrafter branch and now has concrete next implementation targets.
  NEXT: Execute rank-1 SpellCrafter follow-up task while continuing remaining discovery tracks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Notes section added to enforce active_documentation for in-flight findings.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/active_documentation.md:1
  IMPACT: Keeps ticket memory durable across compaction by requiring evidence-backed notes.
  NEXT: Append new findings here as work continues.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created with five linked discovery-first stories for optimization of
conjure, meld, SpellCrafter phases, CreationContext codegen, and Phase 12
codegen. Meld discovery is now complete and documented with ranked hotspot
candidates and follow-up implementation tasks in
`context_compass/stories/2026-02-13_optimize_meld_paths_story.md`. SpellCrafter
discovery is now complete and execution-ready with three ranked follow-up tasks
queued. Rank-1 is implemented and in review with strong warm 8-11 gains, and
rank-2 is implemented and in review with tuple-hash signature-path gains.
Conjure scheduler-lifecycle reduction is now implemented and in review with
focused fastpath regression coverage.
Phase12 discovery is now complete and execution-ready with ranked follow-up
tasks plus a benchmark-entrypoint repair task to restore fresh route metrics.
Phase12 rank-1, rank-2, and benchmark-entrypoint repair are implemented and
validated in review; next step is user acceptance and closure movement for
those phase12 tasks. User accepted this wave and the phase12 story was moved to
completed.

