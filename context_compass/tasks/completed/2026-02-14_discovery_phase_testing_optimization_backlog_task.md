Completed: 2026-02-14
Summary: Accepted in the phase-testing closure pass; implementation and validation artifacts are captured in this task.

# Task: Discovery Phase Testing Optimization Backlog

## Metadata
- Task ID: TASK-2026-02-14-discovery-phase-testing-optimization-backlog
- Story: STORY-2026-02-14-phase-testing-optimization-backlog
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Convert measured phase-testing outputs into a ranked, evidence-backed
optimization backlog for conjure-related phase work.

## Scope Boundaries
- In scope:
- Ranking and taskization of phase optimization candidates from measured outputs.
- Out of scope:
- Implementation of the optimization tasks themselves.

## Steps / Checklist
- [x] Collect outputs from completed phase-testing baseline stories.
- [x] Rank hotspots by measured cost, risk, and expected ROI.
- [x] Create scoped optimization tasks linked to evidence.
- [x] Document decisions and residual unknowns.

## Deliverables
- Ranked optimization backlog with linked follow-up tasks.

## Discovery Output (2026-02-14)
### Readiness Gate
- Final ranking is blocked until each upstream track provides measured output:
  - harness profile run output
  - 1-4 baseline measured output
  - 5-7 conduit measured output
  - 5-7 local measured output
  - 8-11 baseline measured output

### Provisional Ranking Schema (to apply once outputs exist)
- `rank_score = cost_weight * measured_cost + frequency_weight * call_frequency - risk_weight * implementation_risk`
- Mandatory fields per candidate:
  - source track id
  - measured metric reference (`path:start_line-end_line`)
  - expected optimization surface (phase/method)
  - risk notes
  - proposed task scope

### Blocker
- Cleared on 2026-02-14 after harness measurement artifact capture.

## Ranked Optimization Candidates (2026-02-14)
### Rank 1
- Candidate: phase11 codegen IR capture and payload build hotpath.
- Measured signal:
  - warm 8-11 cProfile top cumulative functions include
    `_capture_phase8_11_codegen_ir` and `_build_phase11_variant_ir_payload`.
- Risk: medium (internal codegen shape/perf path, contract-sensitive).
- Follow-up task:
  - `TASK-2026-02-14-optimize-phase11-codegen-ir-capture`

### Rank 2
- Candidate: warm phase8-10 row-build/path-materialization hotpath.
- Measured signal:
  - warm 8-11 totals remain high across occurrence/injection/patch phases;
    cProfile includes recurring row-build/path helpers.
- Risk: medium-low (helper-level optimization with ordering sensitivity).
- Follow-up task:
  - `TASK-2026-02-14-optimize-phase8-10-plan-row-builders`

### Rank 3
- Candidate: conduit phase5 root-blueprints foundational hotpath.
- Measured signal:
  - conduit 5-7 cold/warm both dominated by `phase_root_blueprints_ms`.
- Risk: medium (foundational phase used before 6/7 and 8-11).
- Follow-up task:
  - `TASK-2026-02-14-optimize-phase5-root-blueprints-hotpath`

## Residual Unknowns
- UNKNOWN: exact percentage improvement opportunity per candidate without
  targeted micro-bench instrumentation inside each function cluster.
- UNKNOWN: cross-run variance characteristics beyond this first deterministic
  sample (`n=1`) for each group.
- Mitigation: each follow-up task must include before/after harness reruns and
  stability notes.

## Files / Paths Impacted
- `context_compass/stories/completed/2026-02-14_phase_testing_optimization_backlog_story.md`
- `context_compass/tasks/completed/2026-02-14_discovery_phase_testing_optimization_backlog_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/component -k phase`

## Risks / Rollback Notes
- Risk: low-confidence ranking due to incomplete baselines.
- Rollback: keep backlog in draft until required baseline tracks complete.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Rank-1 follow-up task has already produced measurable warm-path improvement, validating the ranking approach with concrete results.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase11_codegen_ir_capture_task.md:57-89, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:11-15, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase11_opt_output.txt:12-15
  IMPACT: Discovery-to-execution loop is now validated; next effort should continue ranked task execution.
  NEXT: Execute rank-2 task (`TASK-2026-02-14-optimize-phase8-10-plan-row-builders`).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Ranked optimization backlog is now materialized into three scoped follow-up tasks linked to measured hotspot evidence.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase11_codegen_ir_capture_task.md:1-12, context_compass/tasks/completed/2026-02-14_optimize_phase8_10_plan_row_builders_task.md:1-12, context_compass/tasks/completed/2026-02-14_optimize_phase5_root_blueprints_hotpath_task.md:1-12, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:7-11, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:20-33
  IMPACT: This discovery task now delivers actionable optimization scope rather than only a ranking schema.
  NEXT: Review ranking output with user and confirm task execution order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Readiness gate is now satisfied because measured outputs exist for harness, 1-4, 5-7 conduit, 5-7 local, and 8-11 tracks in one durable artifact.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:5-11, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:51-52
  IMPACT: Backlog ranking can now proceed without speculative placeholders.
  NEXT: Produce ranked hotspot candidates and create scoped optimization tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: RISK
  CLAIM: Ranking now would be speculative because required measured outputs are not yet present in upstream tasks.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_discovery_phase_group_1_4_baseline_task.md:80, context_compass/tasks/completed/2026-02-14_discovery_phase_group_5_7_conduit_baseline_task.md:76, context_compass/tasks/completed/2026-02-14_discovery_phase_group_5_7_local_baseline_task.md:74, context_compass/tasks/completed/2026-02-14_discovery_phase_group_8_11_baseline_task.md:83
  IMPACT: Task status should remain blocked until measurements land.
  NEXT: Unblock by implementing/running baseline harness and attaching measured outputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Upstream phase tickets currently contain discovery contracts in `review` state and no measured run outputs, so hotspot ranking cannot be evidence-complete yet.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_discovery_phase_component_cprofile_harness_task.md:6, context_compass/tasks/completed/2026-02-14_discovery_phase_component_cprofile_harness_task.md:95, context_compass/tasks/completed/2026-02-14_discovery_phase_group_1_4_baseline_task.md:6, context_compass/tasks/completed/2026-02-14_discovery_phase_group_1_4_baseline_task.md:80, context_compass/tasks/completed/2026-02-14_discovery_phase_group_5_7_conduit_baseline_task.md:6, context_compass/tasks/completed/2026-02-14_discovery_phase_group_5_7_local_baseline_task.md:6, context_compass/tasks/completed/2026-02-14_discovery_phase_group_8_11_baseline_task.md:6
  IMPACT: This backlog task must first define readiness gates and a provisional ranking frame, then wait for measured outputs before final ranking.
  NEXT: Add explicit readiness criteria and provisional ranking schema to this ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Backlog candidates must include explicit evidence pointers from phase-testing outputs.
  EVIDENCE: context_compass/WORKFLOW.md:31, context_compass/epics/completed/2026-02-14_phase_testing_epic.md:79
  IMPACT: Keeps optimization prioritization objective and reviewable.
  NEXT: Start this task after baseline discovery stories move to done.

## Context / Handoff Summary
Task is now review-ready: ranking is complete and three scoped follow-up tasks
are created from measured outputs. Next step is user review/acceptance and
selection of execution order for the new optimization tasks.
