

# Story: Discover Phase 12 And CreationContext Optimization Paths

## Metadata
- Story ID: STORY-2026-02-17-phase12-creation-context-discovery-and-benchmark
- Epic: EPIC-2026-02-17-phase12-creation-context-codegen-performance
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-17T15:53:33Z
- Updated: 2026-02-17T17:00:02Z

## User Narrative
As a performance-focused maintainer, I want discovery across Phase 12 and
`CreationContext` with pinned-core benchmark baselines, so that we can choose
medium/high-risk optimizations with measurable upside.

## Value / MRP Alignment
Discovery-first de-risks performance work and establishes the success framework
before code changes.

## Ticket Contract
- ENTRY_GATE: story is routed in `attention_board.md` and child tasks are
  present.
- EXECUTION_BOUNDARY: discovery and benchmark protocol only; no wide runtime
  rewrites.
- DEPENDENCIES: benchmark harness task + per-location discovery tasks.
- EXIT_GATE: all child tasks complete with evidence, and risk-ranked options
  are documented.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` when an option likely affects
  contracts or lock semantics.

## Requirements (Functional)
- Produce hotspot notes for each location task.
- Produce medium-risk and high-risk improvement options.
- Define benchmark success protocol:
  - Before + after runs per change.
  - P-core pinning required.
  - 75% cProfile signal + 25% time-diff signal.

## Requirements (Non-Functional)
- Maintain deterministic benchmark commands.
- Keep all claims evidence-backed.

## Scope Boundaries
- In scope:
  - Discovery for `creation_context.py` and both Phase 12 executors.
  - Benchmark harness protocol design for pinned-core and cProfile weighting.
- Out of scope:
  - Direct optimization implementation (separate execution wave after approval).

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: user requested discovery story with location tasks and
  benchmark scoring plan.

## Dependencies / Related Work
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `benchmarks/p_core_affinity/p_core_affinity.py`
- EPIC-2026-02-17-phase12-creation-context-codegen-performance

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-17-phase12-no-overrides-discovery
- [x] Task: TASK-2026-02-17-phase12-overrides-discovery
- [x] Task: TASK-2026-02-17-creation-context-discovery
- [x] Task: TASK-2026-02-17-codegen-benchmark-pcore-baseline-and-scoring
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- All four location/protocol tasks completed with evidence.
- At least three medium-risk and three high-risk options documented with
  expected call-count impact.
- Baseline benchmark commands specified for pinned-core before/after workflow.

## Validation / Test Plan
- Not run.
- Planned discovery validation commands:
  - `python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores`

## UX / API / Data Notes
- Benchmark data model must include cProfile artifacts and time medians per
  route for weighted scoring.

## Risks / Mitigations
- Risk: discovery under-specifies correctness constraints.
  Mitigation: require contract notes and rollback considerations per option.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should cProfile capture be embedded in existing report JSON or emitted as
  sidecar artifact files?

## Decision Log
- Pending shortlist approval for implementation wave 1.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: story closure

## Notes
- DATETIME: 2026-02-17T15:53:33Z
  TYPE: FACT
  CLAIM: Current benchmark runner emits route medians/ratios and can apply
    P-core affinity via CLI/env.
  EVIDENCE:
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:358-362
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:945-996
  - benchmarks/p_core_affinity/p_core_affinity.py:385-402
  IMPACT: Discovery can immediately define deterministic before/after protocol.
  NEXT: Create and route all location/protocol tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T16:20:08Z
  TYPE: FACT
  CLAIM: Benchmark protocol task is complete with pinned-core baseline and
    weighted cProfile/time scoring outputs, and ticket was moved to completed.
  EVIDENCE:
  - tickets/tasks/completed/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task_completed.md:1-215
  - benchmarks/testing_other_di/results/codegen_benchmark_baseline.json:3-745
  - benchmarks/testing_other_di/results/codegen_benchmark_after.json:807-853
  IMPACT: Story now needs only the three location discovery tasks and risk
    option synthesis before closure.
  NEXT: Route active attention to the story and select first location discovery
    task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T16:48:45Z
  TYPE: FACT
  CLAIM: No-overrides discovery task is now active and has first-pass hotspot
    evidence for compile-time source expansion and transient namespace setup.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:3-111
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:583-633
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1392-1505
  IMPACT: Story execution has moved from routing setup into concrete
    per-location discovery with evidence-backed optimization leverage points.
  NEXT: Finish no-overrides candidate table, then activate overrides discovery
    task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T16:52:56Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: No-overrides discovery now has a complete option pack (three medium,
    three high risk) and can serve as the first lane for cross-task synthesis.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:38-71
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:148-172
  - benchmarks/testing_other_di/results/codegen_benchmark_baseline.json:217-222
  - benchmarks/testing_other_di/results/codegen_benchmark_after.json:277-282
  IMPACT: Story has one completed location discovery package and can now route
    execution to overrides and then creation-context tasks.
  NEXT: Activate overrides discovery task and mirror this option-capture format.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T16:55:17Z
  TYPE: FACT
  CLAIM: No-overrides task is now in review and overrides task is active with
    its own medium/high option set captured.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:3-172
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:3-111
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:116-128
  IMPACT: Story now holds two discovery lanes worth of option evidence and can
    route final discovery to creation-context.
  NEXT: Activate creation-context discovery and capture its option table.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T16:58:00Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: All three location tasks now hold risk-ranked option tables, yielding
    a complete discovery package for cross-location ranking and user selection.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:53-172
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:53-155
  - tickets/tasks/2026-02-17_creation_context_discovery_task.md:55-155
  - context_compass/attention_board.md:23-61
  IMPACT: Story can now transition from evidence collection to shortlist
    synthesis without blocking on additional discovery lanes.
  NEXT: Produce ranked medium/high shortlist for implementation-wave approval.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T17:00:02Z
  TYPE: DECISION_REQUEST
  CLAIM: Consolidated wave-1 shortlist is ready: medium candidates
    {NR-M1, OR-M1, CC-M2} and high candidates {OR-H1, CC-H1, NR-H2}.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:64-71
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:64-72
  - tickets/tasks/2026-02-17_creation_context_discovery_task.md:64-72
  - benchmarks/testing_other_di/results/codegen_benchmark_baseline.json:301-313
  - benchmarks/testing_other_di/results/codegen_benchmark_after.json:361-373
  IMPACT: Discovery can transition into implementation planning immediately once
    candidate IDs are approved.
  NEXT: User selects approved wave-1 candidate IDs (medium/high) and risk level.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Reference child-task notes for evidence.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Story discovery is complete across benchmark, no-overrides, overrides, and
creation-context lanes; next step is ranked shortlist synthesis for user approval.