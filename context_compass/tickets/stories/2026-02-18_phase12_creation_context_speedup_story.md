# Story: Phase 12 and Creation Context Speedup

## Metadata
- Story ID: STORY-2026-02-18-phase12-creation-context-speedup
- Epic: EPIC-2026-02-18-codegen-phase8-12-creation-context-speedup
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-18T18:54:05Z
- Updated: 2026-02-18T18:54:05Z

## User Narrative
As a performance-focused maintainer, I want Phase 12 and creation_context
execution to be faster on fast and override routes, so end-to-end codegen
throughput improves where workloads spend most time.

## Value / MRP Alignment
Phase 12 + creation_context is the primary target for this lane. Improvements
here directly influence weighted benchmark outcomes and user-visible speed.

## Ticket Contract
- ENTRY_GATE: discovery task documents Phase 12 and creation_context hotspots.
- EXECUTION_BOUNDARY: Phase 12 executor and creation_context execution surfaces.
- DEPENDENCIES: TASK-2026-02-18-phase8-12-holistic-codegen-discovery.
- EXIT_GATE: optimization task accepted and weighted pass criteria met.
- FAILURE_ESCALATION: raise DECISION_REQUEST if route contracts diverge.

## Requirements (Functional)
- Identify and rank hotspots in:
  - Phase 12 no-overrides executor path
  - Phase 12 overrides executor path
  - creation_context execute helpers
- Preserve behavior parity across fast and override routes.
- Produce implementation plan without executing code changes in this tranche.

## Requirements (Non-Functional)
- Enforce weighted scoring policy (0.75 cProfile / 0.25 time).
- Capture and compare means and medians for fast/override route metrics.
- Keep changes phase-local and reviewable.

## Scope Boundaries
- In scope:
  - `phase12_no_overrides_executor.py`
  - `phase12_overrides_executor.py`
  - `creation_context.py`
  - benchmark route/profile reports for fast/override lanes
- Out of scope:
  - unrelated scheduler or DI subsystem rewrites

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user requested primary focus on phase12 + creation_context.

## Dependencies / Related Work
- `tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md`
- `tickets/tasks/2026-02-18_phase12_creation_context_optimization_task.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-18-phase12-creation-context-optimization
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Discovery includes evidence-backed hotspot ranking for phase12/creation_context.
- Execution plan task is approved and scoped.
- Weighted benchmark policy and mean/median reporting requirements are explicit.

## Validation / Test Plan
- Not run.
- Execution task will run benchmark comparisons with weighted score gates.

## UX / API / Data Notes
- No public API shape changes allowed.

## Risks / Mitigations
- Risk: fast-route gains could regress override route behavior.
  - Mitigation: route-level weighted validation on both fast and override lanes.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should weighted routes remain default (`warm_root_ns` + override routes) or
  expand to spellspace/mixed?
- Should mean metrics be added as first-class report keys?

## Decision Log
- 2026-02-18T18:54:05Z: Story marked in-progress as primary target lane.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: story closure

## Notes
- DATETIME: 2026-02-18T18:54:05Z
  TYPE: FACT
  CLAIM: Current benchmark route matrix tracks fast and override lanes and
    weighted score defaults to 75% cProfile and 25% time.
  EVIDENCE:
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:353-359
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1100-1229
  IMPACT: Story can enforce user-required scoring policy directly.
  NEXT: complete holistic discovery and isolate phase12/creation_context hotspots.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Primary focus story is active; discovery findings will drive phase12 and
creation_context optimization sequencing.
