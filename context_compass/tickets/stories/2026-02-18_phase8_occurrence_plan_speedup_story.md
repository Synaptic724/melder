# Story: Phase 8 Occurrence Plan Speedup

## Metadata
- Story ID: STORY-2026-02-18-phase8-occurrence-plan-speedup
- Epic: EPIC-2026-02-18-codegen-phase8-12-creation-context-speedup
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-18T18:54:05Z
- Updated: 2026-02-18T18:54:05Z

## User Narrative
As a performance-focused maintainer, I want Phase 8 occurrence plan compilation
to run faster, so that downstream phase execution starts from a lower baseline.

## Value / MRP Alignment
Phase 8 is an early gate in the phase8-12 pipeline. Stabilizing and reducing
its overhead improves total throughput without changing public behavior.

## Ticket Contract
- ENTRY_GATE: holistic discovery identifies Phase 8 hotspots and cache behavior.
- EXECUTION_BOUNDARY: Phase 8 compile path and related IR dirtiness signals.
- DEPENDENCIES: TASK-2026-02-18-phase8-12-holistic-codegen-discovery.
- EXIT_GATE: accepted implementation task + benchmark validation complete.
- FAILURE_ESCALATION: raise DECISION_REQUEST on contract or cache invalidation risks.

## Requirements (Functional)
- Identify Phase 8 compile hotspots and repeated work.
- Define candidate optimizations that preserve deterministic signatures.
- Implement only within declared phase8 surfaces in execution task.

## Requirements (Non-Functional)
- Preserve behavior and IR correctness.
- Keep cleanup/lifecycle invariants unchanged.
- Demonstrate no regression in weighted benchmark gates.

## Scope Boundaries
- In scope:
  - Phase 8 compile methods and input signatures
  - phase8_11 IR dirty-mark interactions
- Out of scope:
  - Phase 9-12 behavior changes outside declared interfaces

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: story scaffold created for phase-scoped execution.

## Dependencies / Related Work
- `tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md`
- `tickets/tasks/2026-02-18_phase8_occurrence_plan_optimization_task.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-18-phase8-occurrence-plan-optimization
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Phase 8 hotspot evidence is recorded in task notes.
- Optimization approach is approved before code edits.
- Weighted benchmark comparison passes post-implementation.

## Validation / Test Plan
- Not run.
- Execution task will run weighted benchmark comparisons against baseline.

## UX / API / Data Notes
- No public API changes allowed in this story.

## Risks / Mitigations
- Risk: cache invalidation mistakes.
  - Mitigation: preserve signature checks and IR dirty semantics.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Are there phase8-only call-count hotspots or mostly downstream amplification?

## Decision Log
- 2026-02-18T18:54:05Z: Story created from new codegen speedup epic.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: story closure

## Notes
- DATETIME: 2026-02-18T18:54:05Z
  TYPE: PLAN
  CLAIM: Phase 8 optimization execution is deferred until holistic discovery
    ranks hotspots across all phases.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md:1-109
  IMPACT: Avoids local improvements that regress total pipeline performance.
  NEXT: wait for discovery task hotspot ranking.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

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
Phase 8 story is staged and waiting on discovery outputs before implementation.
