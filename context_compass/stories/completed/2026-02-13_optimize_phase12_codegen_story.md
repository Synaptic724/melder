Completed: 2026-02-14
Summary: Completed phase12 execution wave: rank-1 shape-specialized source,
rank-2 helper callpath tightening, and benchmark-entrypoint repair were
implemented, validated, and accepted with user-reported override performance gains.

# Story: Optimize Phase 12 Codegen

## Metadata
- Story ID: STORY-2026-02-13-optimize-phase12-codegen
- Epic: EPIC-2026-02-13-optimize-melder
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14

## User Narrative
As a Melder maintainer, I want Phase 12 codegen hotspots mapped and prioritized,
so that emitted executors are lean and fast across override and non-override lanes.

## Value / MRP Alignment
Phase 12 emission quality materially affects runtime hot paths. Discovery-first
work ensures optimization effort lands where it gives the highest systemic value.

## Requirements (Functional)
- Identify major cost centers in Phase 12 code generation and emitted executor shape.
- Produce ranked optimization opportunities with evidence.
- Capture follow-up implementation tasks from discovery findings.

## Requirements (Non-Functional)
- Discovery pass must not alter runtime behavior.
- Findings must be grounded in concrete source evidence and measurement notes.

## Scope Boundaries
- In scope:
- Phase 12 no-overrides and overrides executor emission paths.
- Executor-shape and branching-cost discovery for generated code.
- Out of scope:
- Broader SpellCrafter phase optimization outside Phase 12.
- Mutation research runtime wiring.

## Dependencies / Related Work
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `EPIC-2026-02-13-optimize-melder`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-13-discovery-phase12-codegen - Build discovery baseline, hotspot map, and prioritized optimization candidates for Phase 12 codegen. (`context_compass/tasks/2026-02-13_discovery_phase12_codegen_task.md`)
- [x] Task: TASK-2026-02-14-optimize-phase12-override-shape-specialized-source - Specialize override source/cache keys beyond step-count to reduce warm branch/call overhead. (`context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md`)
- [x] Task: TASK-2026-02-14-optimize-phase12-override-helper-callpath-tightening - Tighten per-step override helper callpath/allocation behavior while preserving contracts. (`context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md`)
- [x] Task: TASK-2026-02-14-repair-phase12-route-matrix-benchmark-entrypoint - Repair benchmark entrypoint imports and regenerate current-head route metrics. (`context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md`)

## Acceptance Criteria
- Discovery output identifies top Phase 12 codegen hotspots with evidence.
- Follow-up optimization tasks are documented and prioritized.

## Validation / Test Plan
- Use targeted code-path inspection and relevant existing test/benchmark hooks.
- Record commands and outputs for any executed measurements.

## UX / API / Data Notes
- Internal optimization planning only; no API change in discovery pass.

## Risks / Mitigations
- Risk: generated-code optimizations introduce semantic drift.
  Mitigation: discovery output must tie each candidate to contract-preserving constraints.

## Open Questions
- Should Phase 12 prioritize branch-count reduction, call-count reduction, or cache locality first?

## Decision Log
- 2026-02-13: Story created from user-requested optimization epic setup.

## Notes
- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: User accepted the completed phase12 execution wave and reported improved override benchmark behavior from a full `test_overrides_all.py` run.
  EVIDENCE: context_compass/artifacts/2026-02-14_user_reported_override_perf_test_overrides_all.txt:1-30
  IMPACT: Story is approved for completion move.
  NEXT: Move this story to `stories/completed/` and update board/epic routing state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Benchmark-entrypoint repair is now implemented and validated in review: current-head route-matrix artifacts are regenerated successfully, with fresh route ratios captured for root/spellspace/override lanes.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:6-6, context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:22-27, context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:62-68, context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output_repaired.txt:1-3, context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_report_repaired.json:19-31
  IMPACT: Story measurement lane is unblocked on current head; all three queued phase12 tasks are now implemented/validated in review.
  NEXT: Walk rank-1/rank-2/benchmark-repair outcomes with user and request acceptance for closure/move decisions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-2 helper-callpath tightening is now implemented and validated in review (`47 passed` focused blueprint suite), with precedence/contract guardrail tests added.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:6-6, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:24-28, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:63-69, context_compass/artifacts/2026-02-14_phase12_override_helper_callpath_tightening_blueprint_pytests.txt:1-1, context_compass/artifacts/2026-02-14_phase12_override_helper_callpath_tightening_blueprint_pytests.txt:12-12
  IMPACT: Story now has two validated implementation tasks (rank-1 and rank-2) pending user acceptance and closure movement.
  NEXT: Walk rank-1 and rank-2 outcomes with user; if accepted, move both tasks to completed and execute benchmark-entrypoint repair task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Rank-1 phase12 implementation task is now in review with targeted validation passing (`62 passed`) after shape-source specialization, CreationContext plan-signature cache routing, and harness-schema alignment.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:6-6, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:24-29, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:66-72, context_compass/artifacts/2026-02-14_phase12_override_shape_specialized_source_targeted_pytests.txt:1-1, context_compass/artifacts/2026-02-14_phase12_override_shape_specialized_source_targeted_pytests.txt:12-12
  IMPACT: Story moved from discovery-only into validated execution on the top-ranked optimization lane.
  NEXT: Request user acceptance for rank-1 closure; if accepted, move task to completed and begin rank-2 helper callpath tightening.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Notes section added to enforce active_documentation for in-flight findings.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/active_documentation.md:1
  IMPACT: Keeps ticket memory durable across compaction by requiring evidence-backed notes.
  NEXT: Append new findings here as work continues.

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Discovery is complete and translated into ranked follow-up tasks: rank-1 shape-specialized override source, rank-2 helper callpath tightening, and benchmark-entrypoint repair as measurement enabler.
  EVIDENCE: context_compass/tasks/2026-02-13_discovery_phase12_codegen_task.md:157-164, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:1-70, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:1-68, context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:1-66
  IMPACT: Story moved from discovery-ready to execution-ready with scoped implementation backlog.
  NEXT: Request user acceptance for discovery closure, then start rank-1 execution task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Discovery and all ranked phase12 execution tasks are complete. Rank-1
shape-specialized source, rank-2 helper callpath tightening, and benchmark
entrypoint repair were implemented and validated with focused test/benchmark
artifacts. User accepted the wave and reported improved override benchmark
behavior from `test_overrides_all.py`. Story is ready for completion archive.

