# Story: Split Rift Creation From Frame Targeting And Program Primary Space
- Completed: 2026-04-09T21:59:36Z
- Summary: Split Rift creation from frame targeting and finished the first primary-space programming cut.


## Metadata
- Story ID: STORY-2026-04-08-split-rift-creation-from-frame-targeting-and-program-primary-space
- Epic: EPIC-2026-04-08-rift-creation-frame-targeting-and-primary-space-split
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-08T11:35:38Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Make `Rift` creation produce a bare live access object, create the primary
space from `space_type`, and move target-frame validation/attachment into a
separate Rift action that refreshes the attached viewer.

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected the next architecture cut away
  from viewer refinement and toward splitting Rift creation from frame
  targeting.
- EXECUTION_BOUNDARY: Rift creation, primary-space programming, and frame
  targeting only.
- DEPENDENCIES:
  - tickets/epics/2026-04-08_rift_creation_frame_targeting_and_primary_space_split_epic.md
  - tickets/tasks/2026-04-08_decouple_rift_configuration_from_target_frame_and_program_primary_space_task.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/configuration/rift_configuration.py
- EXIT_GATE: the Rift lifecycle is split cleanly enough that bare creation,
  primary-space programming, and frame targeting are distinct transitions.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current multi-space Rift
  object model prevents a clean first cut.

## Scope
- In scope:
  - Rift config contract cleanup
  - Rift primary-space creation
  - separate target-frame action
  - viewer refresh on successful targeting
- Out of scope:
  - broad workspace-history features
  - ACL authoring changes

## Steps / Checklist
- [ ] Create patch docs for the lifecycle split.
- [ ] Implement the first task under this story.
- [ ] Validate focused Rift/Nexus/viewer tests.
- [ ] Record findings and results in notes.

## Acceptance Criteria
- Bare Rift creation no longer needs a target frame.
- The chosen `space_type` produces the primary concrete space.
- Targeting a frame becomes a separate validated action.
- Illegal dynamic targeting fails without creating a second fallback workspace.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-08T11:35:38Z
  TYPE: PLAN
  CLAIM: The first story slice is the lifecycle split itself: bare Rift
    creation, primary-space programming from `space_type`, and explicit frame
    targeting that refreshes the attached viewer.
  EVIDENCE:
  - user_instruction: "Create rift, configure it, target a frame, and then enter it"
  - user_instruction: "if the space type selected doesn't match the frame we want to attach to it should reject"
  IMPACT: This story defines the first implementation slice needed to make the
    Rift lifecycle match the intended operational grammar.
  NEXT: create and execute the first implementation task with patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story is the first implementation slice under the new Rift lifecycle epic.
It exists to separate bare Rift creation from later frame targeting and viewer
projection while keeping the chosen space type as a Rift-level concern.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

