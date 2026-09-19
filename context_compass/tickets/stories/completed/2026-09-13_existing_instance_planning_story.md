# Story: Keep existing instances opaque during dependency planning

- Completed: 2026-09-19T14:51:36Z
- Closure Basis: explicit owner request to turn in all delivered updater_0 work.
- Summary: Accepted the delivered existing-instance injection repair; downstream Iris cleanup and broader object-policy questions are explicitly deferred rather than claimed repaired.
- Deferred work: tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md.
  Historical unchecked redesign/downstream items are deferred, not an implementation claim.


## Metadata
- Story ID: STORY-2026-09-13-existing-instance-planning
- Epic: EPIC-2026-09-13-provider-artifact-ownership-and-existing-instance-planning
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-13T18:14:07Z
- Updated: 2026-09-19T14:51:36Z

## User Narrative
As a caller supplying an existing logger or other object, I need Melder to inject that exact object
without inspecting it for constructor contracts or treating it as a factory.

## Value / MRP Alignment
The supported existing-instance binding contract must hold throughout transitive planning, not only at roots.

## Ticket Contract
- ENTRY_GATE: owner-assigned epic and linked reproduction task exist.
- EXECUTION_BOUNDARY: existing-object contract discovery in the Phase-8 and Phase-9 iterators.
- DEPENDENCIES: accepted consultation and the original dedicated Iris logger ActivityBootstrap proof.
- EXIT_GATE: both iterators are corrected, native controls pass and the real downstream logger proof passes.
- FAILURE_ESCALATION: raise incompatible class/factory or ownership semantics before changing them.

## Requirements
- Existing non-callable and callable objects retain identity at root and dependency positions.
- Existing instances yield no constructor contract-default requests.
- Cover both planning iterators; preserve ordinary class/factory contract discovery and overrides.
- Preserve real ChannelLogger input, ActivityBuilder/GeneralActivity assertions and teardown.

## Scope Boundaries
- In scope: existing-creation planning, regression tests and original downstream validation.
- Out of scope: wrappers, fake acceptance loggers, Optional/default policy, Iris redesign and releases.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: owner accepts turn-in of delivered scope and explicitly backlogs unperformed user-created-object work.

## Tasks
- [x] TASK-2026-09-13-repair-deferred-annotation-acquisition:
  tickets/tasks/completed/2026-09-13_repair_deferred_annotation_acquisition_task.md
- [ ] TASK-2026-09-13-repair-existing-instance-planning:
  tickets/tasks/completed/2026-09-13_repair_existing_instance_planning_task.md

## Acceptance Criteria
- Native non-callable/callable existing objects pass roots and transitive dependency planning unchanged.
- Both iterators avoid signature inspection for existing creations.
- Ordinary class/factory and explicit contract override controls pass.
- Original dedicated Iris logger bootstrap and cleanup assertions pass without weakening the test.

## Validation / Test Plan
Record a native failing reproduction, fix both contract-default iterators and run scoped controls.
Coordinate the original CommandOps scenario against the resulting local package.

## Risks / Mitigations
A first-stage fix can mask the same defect in Phase 9; test both entry points explicitly.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: record unresolved design questions in the linked task.

## Notes
- DATETIME: 2026-09-13T18:14:07Z
  TYPE: FACT
  CLAIM: Both iterator source hashes match the accepted installed-0.2.40 consultation.
  EVIDENCE:
  - tickets/epics/completed/2026-09-13_provider_artifact_ownership_and_existing_instance_planning_epic.md:134-143
  IMPACT: No known drift in the diagnosed branches; reproduce before selecting the patch.
  NEXT: Run the linked task after the provider reproduction is recorded.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-13T19:15:40Z
  TYPE: MEASURE
  CLAIM: The task now records 66 stock/diagnostic observations and 21 stock regressions (14 red,
    seven green). Correcting only both existing-instance scanners in memory unblocks 14 injection
    scenarios. A separate deferred-annotation NameError, type-frame admission asymmetry and
    class-only disposal policy are recorded with controls. Production changes remain paused.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-13_repair_existing_instance_planning_task.md
  - artifacts/existing_instance_planning_20260913/gap_analysis.md
  IMPACT: Existing instances remain injectable providers. New admission/cleanup policy must be
    selected explicitly, and the callable-object factory classification is not changed by this work.
  NEXT: Review the expanded evidence with the owner before selecting a production repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T14:51:36Z
  TYPE: DECISION
  CLAIM: Owner accepts turn-in of this delivered record. Accepted the delivered existing-instance injection repair; downstream Iris cleanup and broader object-policy questions are explicitly deferred rather than claimed repaired.
  EVIDENCE:
  - Owner instruction to backlog user-created-object ideas and turn in all work done.
  - artifacts/updater_0_turn_in_20260919/closure_manifest.json
  IMPACT: Record closed with its historical evidence retained. Deferred requirements remain visible
    in the backlog epic; no new runtime, test, installation or release result is implied.
  NEXT: Resume deferred work only on a new explicit owner request.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
CLOSED BY OWNER: delivered scope is turned in; see the completion summary at the top. Any earlier
review/resume instructions below are historical. Deferred user-created-object work is parked in the
backlog epic and does not request continued implementation.

Annotation work is accepted and turned in under its completed task. The owner then selected the
existing-instance planning repair: both guards now preserve existing providers as leaves, and
138 native cases pass. The original Iris test reaches successful construction and then fails its
builder-cleanup assertion; full downstream acceptance remains incomplete. See the task's latest
notes and original JUnit artifact. Frame/disposal policy changes remain parked.
