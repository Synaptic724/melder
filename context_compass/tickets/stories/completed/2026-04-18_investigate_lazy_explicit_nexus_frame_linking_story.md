# Story: Investigate Lazy Explicit Nexus Frame Linking
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after downstream lazy-linking implementation landed.

## Metadata
- Story ID: STORY-2026-04-18-investigate-lazy-explicit-nexus-frame-linking
- Epic: EPIC-2026-04-18-lazy-explicit-nexus-frame-linking
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T12:41:23Z
- Updated: 2026-04-19T16:54:36Z

## User Narrative
As the Rift/Nexus runtime maintainer, I want Rift creation to be frame-free and
Nexus-frame realization to happen only on explicit request, so the topology
policy stays in Nexus without forcing eager attachment/default state into Rift.

## Value / MRP Alignment
This keeps the next refactor narrow:
- remove eager/default frame state
- keep topology ownership in Nexus
- do not try to solve the full future space-open/link design yet

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected to this frame/default cleanup lane
  and requested an epic plus a proposed plan.
- EXECUTION_BOUNDARY: investigate the current eager/default model and define
  the exact no-backward-compat refactor cut.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_investigate_lazy_explicit_nexus_frame_linking_task.md
- EXIT_GATE: the lazy-linking refactor plan is concrete enough to approve
  before implementation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a larger frame-opening design
  is required first.

## Acceptance Criteria
- The exact eager/default call paths are mapped with source evidence.
- The no-compat refactor plan is concrete enough to implement.
- The user can approve/reject the plan without another investigation loop.

## Notes
- DATETIME: 2026-04-18T12:41:23Z
  TYPE: PLAN
  CLAIM: This story is intentionally limited to removing eager/default
    Nexus-frame state from Rift and applying topology only at explicit request
    time. It is not a full target-opening redesign.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:691-706
  - src/melder/aether/nexus/nexus.py:736-755
  - src/melder/aether/nexus/rift/rift.py:102-189
  IMPACT: We can cut the eager model cleanly without mixing it with the later
    space-owned target-opening work.
  NEXT: finish the task-level blast-radius map and propose the implementation sequence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Context / Handoff Summary
This story owns the investigate-first pass for lazy explicit Nexus-frame
linking and Rift default-frame state removal.
