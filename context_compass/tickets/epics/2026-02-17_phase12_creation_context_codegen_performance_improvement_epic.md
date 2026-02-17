# Epic: Improve Phase 12 And CreationContext Codegen Performance

## Metadata
- Epic ID: EPIC-2026-02-17-phase12-creation-context-codegen-performance
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-17T15:53:33Z
- Updated: 2026-02-17T15:53:33Z
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

## Milestones (Track Progress)
- [ ] Milestone 1: Discovery and baseline complete.
- [ ] Milestone 2: Approved optimization candidates and implementation plan.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-17-phase12-creation-context-discovery-and-benchmark -
      discovery, baseline, and risk-ranked options.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-02-17-phase12-no-overrides-discovery
- [ ] Task: TASK-2026-02-17-phase12-overrides-discovery
- [ ] Task: TASK-2026-02-17-creation-context-discovery
- [ ] Task: TASK-2026-02-17-codegen-benchmark-pcore-baseline-and-scoring

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
- Pending discovery.

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

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Epic started to structure Phase 12 and `CreationContext` optimization work with
mandatory pinned-core before/after benchmarking and weighted cProfile+time
scoring.
