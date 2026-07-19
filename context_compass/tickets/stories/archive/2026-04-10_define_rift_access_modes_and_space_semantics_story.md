# Story: Define Rift Access Modes And Space Semantics

## Metadata
- Story ID: STORY-2026-04-10-define-rift-access-modes-and-space-semantics
- Epic: EPIC-2026-04-10-rift-access-modes-static-capability-dynamic
- Status: draft
- Owner: codex
- Priority: p0
- Created: 2026-04-10T00:50:25Z
- Updated: 2026-04-10T00:50:25Z

## User Narrative
As the Rift runtime designer, I want `static`, `capability`, and `dynamic`
to have explicit space semantics, so that later implementation does not blur
their contracts or force dynamic behavior back into every mode.

## Value / MRP Alignment
This story turns the retained access-mode artifact into a real execution lane.
Without it, the next implementation work will keep re-litigating what each
mode means.

## Ticket Contract
- ENTRY_GATE: the new access-mode epic exists and the retained access-mode
  artifact is available as the current semantic source.
- EXECUTION_BOUNDARY: define and sequence the mode semantics only; do not
  implement runtime behavior in this story.
- DEPENDENCIES:
  - tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
  - tickets/tasks/2026-04-10_stage_rift_access_modes_lane_from_retained_artifact.md
- EXIT_GATE: the mode boundaries and next implementation slices are explicit
  enough to start static/capability runtime work cleanly.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the retained access-mode artifact
  still leaves multiple materially different runtime interpretations plausible.

## Requirements (Functional)
- define static space semantics
- define capability space semantics
- define dynamic-space boundary relative to the other two
- define the first implementation order

## Requirements (Non-Functional)
- clear
- non-overlapping
- durable under compaction/handoff

## Scope Boundaries
- In scope:
  - mode semantics
  - sequencing
  - re-homing retained design context
- Out of scope:
  - runtime implementation
  - test creation
  - public endpoint packaging

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created to anchor the access-mode implementation lane
  beneath the new epic before runtime work starts.

## Dependencies / Related Work
- tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-10-stage-rift-access-modes-lane-from-retained-artifact
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The story documents one clear static/capability/dynamic split.
- The first runtime implementation steps are explicit.

## Validation / Test Plan
- Design/sequence validation only in this story.

## UX / API / Data Notes
- Static stays non-codegen.
- Capability stays pre-published execution without codegen.
- Dynamic remains the open workspace mode.

## Risks / Mitigations
- Risk: capability semantics get treated as "dynamic lite" without a clear contract.
  Mitigation: keep the story centered on explicit boundaries and operation classes.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should static first-cut support only singleton-like lifecycle postures?
- How much capability-mode handle management belongs inside Rift vs a later endpoint layer?

## Decision Log
- Created after the completed lifecycle/probe work made the access-mode lane
  explicit enough to stage independently.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the access-mode runtime model settles.

## Notes
- DATETIME: 2026-04-10T00:50:25Z
  TYPE: PLAN
  CLAIM: The story is intentionally staging-only. The runtime already has the
    capability placeholder and the live-creation probe, so the remaining gap is
    to lock the semantics and the implementation order before adding new behavior.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-09_add_capability_rift_space_placeholder.md:1-159
  - tickets/tasks/completed/2026-04-09_implement_meld_owned_has_live_creation_probe.md:1-182
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md:1-202
  IMPACT: This keeps the next runtime slice from drifting into a half-defined
    access-mode implementation.
  NEXT: stage the child task and re-home the retained artifact under this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

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
This story stages the access-mode semantics lane so static/capability/dynamic
can be implemented from one explicit contract instead of scattered retained notes.
