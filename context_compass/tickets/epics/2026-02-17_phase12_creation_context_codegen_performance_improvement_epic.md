# Epic: Improve Phase 12 And CreationContext Codegen Performance

## Metadata
- Epic ID: EPIC-2026-02-17-phase12-creation-context-codegen-performance
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-17T15:53:33Z
- Updated: 2026-02-17T18:28:41Z
- Target Window: 2026-Q1
- Related Program/Initiative: Codegen Runtime Optimization

## Problem / Opportunity
Phase 12 no-overrides, Phase 12 overrides, and `CreationContext` are hot runtime
paths. We need an evidence-first optimization program with pinned-core benchmark
discipline and explicit before/after success criteria.

## MRP Alignment (Most Reasonable Product)
Build a durable optimization workflow first: repeatable benchmark protocol,
risk-ranked options, and safe implementation sequencing. This avoids ad-hoc
speed changes that regress correctness or observability.

## Ticket Contract
- ENTRY_GATE: active board route points to this epic/story lane and discovery
  tasks exist per location.
- EXECUTION_BOUNDARY: `src/melder/aether/conduit/meld/creation_context/`,
  `src/melder/spellbook/spell_crafter/blueprints/`, and
  `benchmarks/testing_other_di/`.
- DEPENDENCIES: Story + tasks in this epic, pinned-core benchmark script,
  route-matrix benchmark output.
- EXIT_GATE: discovery completed, risk-ranked options accepted, before/after
  benchmark protocol executed for each implementation wave.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any optimization changes API,
  lock semantics, or override correctness contracts.

## Goals (Outcomes)
- Define and run pinned-core baseline benchmarking for fast and override routes.
- Produce medium-risk and high-risk optimization candidates with evidence.
- Implement only approved candidates with required before/after measurements.

## Non-Goals (Explicit Exclusions)
- Broad refactors outside Phase 12 and `CreationContext`.
- Benchmark changes unrelated to codegen hot paths.

## Scope Boundaries
- In scope:
  - Discovery in `creation_context.py`, `phase12_no_overrides_executor.py`,
    `phase12_overrides_executor.py`, and benchmark harness configuration.
  - Performance plan with medium/high-risk options.
  - Benchmark rubric: 75% cProfile signal, 25% time delta signal.
- Out of scope:
  - Unrelated runtime architecture rewrites.
  - Any non-benchmark validation claims without execution evidence.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: user requested epic/story/tasks for Phase 12 and
  `CreationContext` performance improvement planning.

## Success Metrics
- Required pre/post benchmark for each implementation attempt:
  - `warm_root_ns`
  - `warm_override_root_args_ns`
  - `warm_override_targeted_ns`
- Weighted success score:
  - 75%: cProfile call-count and cumulative-time improvement on target routes.
  - 25%: route median time improvement from benchmark delta report.
- cProfile expectation: successful optimizations should reduce call volume in
  targeted hot paths.

## Requirements (Functional + Non-Functional)
- Benchmarks must run with pinned P-cores.
- Before-change and after-change measurements are mandatory per success claim.
- Discovery output must include risk classification and rollback notes.

## Constraints / Assumptions
- P-core pinning is available through benchmark flags/env.
- cProfile output schema does not yet exist in benchmark JSON; discovery task
  must define structured integration approach.

## Dependencies / External References
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `benchmarks/p_core_affinity/p_core_affinity.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`

## Problem / Opportunity
Phase 12 no-overrides, Phase 12 overrides, and `CreationContext` are hot runtime
paths. We need an evidence-first optimization program with pinned-core benchmark
discipline and explicit before/after success criteria.

## MRP Alignment (Most Reasonable Product)
Build a durable optimization workflow first: repeatable benchmark protocol,
risk-ranked options, and safe implementation sequencing. This avoids ad-hoc
speed changes that regress correctness or observability.

## Ticket Contract
- ENTRY_GATE: active board route points to this epic/story lane and discovery
  tasks exist per location.
- EXECUTION_BOUNDARY: `src/melder/aether/conduit/meld/creation_context/`,
  `src/melder/spellbook/spell_crafter/blueprints/`, and
  `benchmarks/testing_other_di/`.
- DEPENDENCIES: Story + tasks in this epic, pinned-core benchmark script,
  route-matrix benchmark output.
- EXIT_GATE: discovery completed, risk-ranked options accepted, before/after
  benchmark protocol executed for each implementation wave.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any optimization changes API,
  lock semantics, or override correctness contracts.

## Goals (Outcomes)
- Define and run pinned-core baseline benchmarking for fast and override routes.
- Produce medium-risk and high-risk optimization candidates with evidence.
- Implement only approved candidates with required before/after measurements.

## Non-Goals (Explicit Exclusions)
- Broad refactors outside Phase 12 and `CreationContext`.
- Benchmark changes unrelated to codegen hot paths.

## Scope Boundaries
- In scope:
  - Discovery in `creation_context.py`, `phase12_no_overrides_executor.py`,
    `phase12_overrides_executor.py`, and benchmark harness configuration.
  - Performance plan with medium/high-risk options.
  - Benchmark rubric: 75% cProfile signal, 25% time delta signal.
- Out of scope:
  - Unrelated runtime architecture rewrites.
  - Any non-benchmark validation claims without execution evidence.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: user requested epic/story/tasks for Phase 12 and
  `CreationContext` performance improvement planning.

## Success Metrics
- Required pre/post benchmark for each implementation attempt:
  - `warm_root_ns`
  - `warm_override_root_args_ns`
  - `warm_override_targeted_ns`
- Weighted success score:
  - 75%: cProfile call-count and cumulative-time improvement on target routes.
  - 25%: route median time improvement from benchmark delta report.
- cProfile expectation: successful optimizations should reduce call volume in
  targeted hot paths.

## Requirements (Functional + Non-Functional)
- Benchmarks must run with pinned P-cores.
- Before-change and after-change measurements are mandatory per success claim.
- Discovery output must include risk classification and rollback notes.

## Constraints / Assumptions
- P-core pinning is available through benchmark flags/env.
- cProfile output schema does not yet exist in benchmark JSON; discovery task
  must define structured integration approach.

## Dependencies / External References
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `benchmarks/p_core_affinity/p_core_affinity.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`

## Milestones (Track Progress)
- [x] Milestone 1: Discovery and baseline complete.
- [ ] Milestone 2: Wave-1 medium candidate implementation and validation.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-17-phase12-creation-context-discovery-and-benchmark -
      discovery, baseline, and risk-ranked options.
- [ ] Story: STORY-2026-02-17-system-improvement-discovery-phase2 -
      run discovery again and find opportunities to improve the system.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-02-17-phase12-no-overrides-discovery
- [ ] Task: TASK-2026-02-17-phase12-overrides-discovery
- [ ] Task: TASK-2026-02-17-creation-context-discovery
- [x] Task: TASK-2026-02-17-codegen-benchmark-pcore-baseline-and-scoring
- [ ] Task: TASK-2026-02-17-phase12-wave1-medium-implementation
- [x] Task: TASK-2026-02-17-phase12-wave2-candidate-selection
- [ ] Task: TASK-2026-02-17-phase12-or-m1-isolated-implementation

## Acceptance Criteria (Epic Done)
- Discovery story accepted by user.
- Medium-risk and high-risk options documented with tradeoffs.
- Benchmark protocol (before/after, pinned cores, weighted scoring) accepted.

## Risks / Mitigations
- Risk: speed gains regress correctness in override/locking lanes.
  Mitigation: require before/after correctness checks and scoped changes only.
- Risk: benchmark noise from non-pinned cores.
  Mitigation: force `--pin-p-cores` and record affinity status.

## Applicable Anti-Patterns
- [ ] No optimization success claim without before/after benchmark evidence.
- [ ] No high-risk change implementation without explicit user approval.
- [ ] No cProfile claims without structured profiler output evidence.

## Validation / Test Approach
- Benchmark-first validation through route matrix + cProfile integration.
- Unit/integration validation added in implementation tasks after discovery.

## Rollout / Adoption Plan
- Run discovery and baseline.
- Select approved candidates.
- Implement one wave at a time with before/after benchmark capture.

## Open Questions
- How should cProfile output be stored in benchmark JSON for deterministic
  comparison?
- Which hot-path call stacks are primary targets for call-count reduction?

## Decision Log
- Wave-1 medium shortlist selected for implementation:
  `{NR-M1, OR-M1, CC-M2}`.
- Wave-1 implementation lane paused after rollback; next-wave ticket selection
  is now active.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: epic closure

## Notes
- DATETIME: 2026-02-17T15:53:33Z
  TYPE: FACT
  CLAIM: Benchmark runner already supports pinned P-core execution and route
    matrix output for warm and override lanes.
  EVIDENCE:
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:358-362
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:760-799
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1124-1132
  IMPACT: We can start with deterministic pinned-core baseline collection
    without changing benchmark CLI shape.
  NEXT: Create discovery story and per-location tasks with benchmark rubric.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T16:20:08Z
  TYPE: FACT
  CLAIM: Benchmark protocol task closed with pinned-core baseline/comparison
    evidence and weighted 75/25 scoring now in the benchmark schema.
  EVIDENCE:
  - tickets/tasks/completed/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task_completed.md:1-215
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1298-1349
  - benchmarks/testing_other_di/results/codegen_benchmark_after.json:807-853
  IMPACT: Epic can move from benchmark-protocol setup into location discovery
    and risk-ranked optimization option generation.
  NEXT: Execute remaining discovery tasks and produce medium/high-risk option
    synthesis.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T16:48:45Z
  TYPE: PLAN
  CLAIM: Epic discovery execution has resumed with no-overrides task activation
    and first hotspot evidence capture underway.
  EVIDENCE:
  - context_compass/attention_board.md:23-45
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:3-111
  - tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md:108-149
  IMPACT: Milestone 1 work has moved from setup into active per-location
    discovery needed for medium/high-risk option synthesis.
  NEXT: Complete no-overrides discovery deliverables, then route to overrides
    and creation-context tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T16:52:56Z
  TYPE: FACT
  CLAIM: First location discovery lane now has a complete no-overrides option
    package with risk ranking and call-count impact direction.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:53-71
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:148-172
  - tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md:108-164
  IMPACT: Epic Milestone 1 has moved from activation to substantive option
    generation, reducing remaining discovery to overrides and creation-context.
  NEXT: Execute overrides and creation-context discovery tasks, then synthesize
    cross-location medium/high-risk recommendations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T16:55:17Z
  TYPE: FACT
  CLAIM: Discovery progression reached second lane activation: no-overrides is
    in review and overrides has risk-ranked candidates documented.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:3-172
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:3-128
  - context_compass/attention_board.md:23-59
  IMPACT: Epic Milestone 1 now has two location lanes populated, leaving only
    creation-context discovery before cross-lane ranking.
  NEXT: Run creation-context discovery task and produce final synthesis package.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T16:58:00Z
  TYPE: FACT
  CLAIM: Discovery coverage is now complete across all three location tasks with
    documented medium/high candidate tables and benchmark-aligned hotspot anchors.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:53-172
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:53-155
  - tickets/tasks/2026-02-17_creation_context_discovery_task.md:55-155
  - tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md:62-180
  IMPACT: Epic is ready to move from discovery into user-approved implementation
    wave planning with explicit risk-ranked candidate choices.
  NEXT: Present consolidated shortlist and request user approval for wave 1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T17:00:02Z
  TYPE: DECISION_REQUEST
  CLAIM: Epic wave-1 shortlist is prepared for approval with medium set
    {NR-M1, OR-M1, CC-M2} and high set {OR-H1, CC-H1, NR-H2}.
  EVIDENCE:
  - tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md:98-192
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:64-71
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:64-72
  - tickets/tasks/2026-02-17_creation_context_discovery_task.md:64-72
  IMPACT: Milestone 2 can begin immediately after candidate selection without
    additional discovery delay.
  NEXT: User selects approved wave-1 candidate IDs and permitted risk class.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T17:41:37Z
  TYPE: DECISION
  CLAIM: Epic wave execution resumed with medium-risk wave-1
    `{NR-M1, OR-M1, CC-M2}` and deferred high-risk candidates.
  EVIDENCE:
  - tickets/stories/2026-02-17_phase12_creation_context_discovery_and_benchmark_story.md:198-217
  - tickets/tasks/2026-02-17_phase12_no_overrides_executor_discovery_task.md:66-72
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:67-72
  - tickets/tasks/2026-02-17_creation_context_discovery_task.md:68-72
  IMPACT: Milestone 2 can proceed with concrete implementation and targeted
    validation for approved medium candidates.
  NEXT: Execute `TASK-2026-02-17-phase12-wave1-medium-implementation` and log
    before/after evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T18:26:37Z
  TYPE: DECISION
  CLAIM: Wave-1 implementation is paused after rollback; execution now routes
    through a next-wave candidate-selection ticket.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_wave1_medium_implementation_task.md:1-144
  - tickets/tasks/2026-02-17_phase12_wave2_candidate_selection_task.md:1-118
  - benchmarks/testing_other_di/results/codegen_benchmark_after_branch_compare_chat_ref.json:807-844
  IMPACT: Epic stays in Milestone 2 while avoiding stalled execution on a
    reverted lane.
  NEXT: Complete candidate selection and activate the next implementation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-17T18:28:41Z
  TYPE: DECISION
  CLAIM: Next-wave selection is complete, and OR-M1 is activated as the current
    isolated medium-risk implementation lane.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_wave2_candidate_selection_task.md:1-126
  - tickets/tasks/2026-02-17_phase12_or_m1_isolated_implementation_task.md:1-115
  - context_compass/attention_board.md:23-46
  IMPACT: Epic Milestone 2 execution remains active with a narrower
    implementation slice focused on override-route behavior.
  NEXT: Complete OR-M1 implementation and benchmark validation before selecting
    another lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Epic remains in progress with discovery complete across all lanes; wave-1
medium implementation is paused, and active routing is now through
`TASK-2026-02-17-phase12-or-m1-isolated-implementation`.
