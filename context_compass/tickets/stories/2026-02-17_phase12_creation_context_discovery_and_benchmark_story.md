# Story: Discover Phase 12 And CreationContext Optimization Paths

## Metadata
- Story ID: STORY-2026-02-17-phase12-creation-context-discovery-and-benchmark
- Epic: EPIC-2026-02-17-phase12-creation-context-codegen-performance
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-17T15:53:33Z
- Updated: 2026-02-17T15:53:33Z

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
- [ ] Task: TASK-2026-02-17-phase12-no-overrides-discovery
- [ ] Task: TASK-2026-02-17-phase12-overrides-discovery
- [ ] Task: TASK-2026-02-17-creation-context-discovery
- [ ] Task: TASK-2026-02-17-codegen-benchmark-pcore-baseline-and-scoring
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

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
- Pending discovery outputs.

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

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Reference child-task notes for evidence.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Story is active with four discovery tasks covering both Phase 12 executors,
`CreationContext`, and benchmark protocol/scoring.
