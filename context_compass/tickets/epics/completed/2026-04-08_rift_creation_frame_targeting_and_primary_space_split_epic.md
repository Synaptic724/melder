# Epic: Rift Creation Frame Targeting And Primary Space Split
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the first Rift lifecycle split epic and archived the retained access-mode artifact under the finished lane.


## Metadata
- Epic ID: EPIC-2026-04-08-rift-creation-frame-targeting-and-primary-space-split
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-08T11:35:38Z
- Updated: 2026-04-09T21:59:36Z
- Target Window: 2026-Q2
- Related Program/Initiative: Rift lifecycle and primary workspace programming

## Problem / Opportunity
The current Rift lifecycle is still collapsed:
- `RiftConfiguration` carries `target_frame_name`
- `Nexus.create_rift(...)` validates and binds the target frame immediately
- `Rift` is born already frame-targeted
- primary space creation and viewer attachment are not part of one explicit
  programming step

This blurs three distinct phases:
- configuring a Rift
- targeting or engaging frames
- creating the primary room/workspace and attaching the descriptor viewer

We want the lifecycle to be explicit:
- configure Nexus
- create/configure a Rift
- create the primary space from the chosen `space_type`
- target frames later through the Rift itself
- let frame targeting validate legality through Nexus and update the attached
  viewer from descriptor + current ACL state

## MRP Alignment (Most Reasonable Product)
The reasonable product is not more hidden magic inside `create_rift(...)`.
It is a clean phased lifecycle:
- a bare Rift can exist without any target frames
- a primary space can exist without a viewer yet
- target-frame selection is explicit and validated
- viewer projection is derived from descriptor truth plus the current ACL state

## Ticket Contract
- ENTRY_GATE: the viewer is already good enough that the next architecture lane
  can move down one layer into Rift lifecycle/programming.
- EXECUTION_BOUNDARY: split Rift creation from frame targeting and primary-space
  programming only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_implement_actionable_viewer_profile_tool_compositions.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/configuration/rift_configuration.py
  - src/melder/aether/nexus/rift/rift_space/
  - system_docs/patches/active/rift_creation_targeting_primary_space_split/architecture_patch.md
  - tickets/stories/2026-04-08_split_rift_creation_from_frame_targeting_and_program_primary_space_story.md
- EXIT_GATE: Rift creation no longer depends on target-frame selection, primary
  space creation is explicit and space-type driven, and frame targeting becomes
  the separate validated action that updates the attached viewer.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one-primary-space semantics
  conflict with other live Rift ownership assumptions.

## Goals (Outcomes)
- Remove target-frame selection from `RiftConfiguration`.
- Make `Nexus.create_rift(...)` produce a bare Rift.
- Create the primary concrete space from `space_type`.
- Make frame targeting a separate validated Rift action.
- Update viewer attachment so targeting refreshes the space-attached viewer.

## Non-Goals (Explicit Exclusions)
- Reworking the ACL subsystem itself.
- Changing descriptor publication contracts.
- Introducing a new generic tooling frame.
- Broad multi-space redesign beyond what is required for the primary-space flow.

## Scope Boundaries
- In scope:
  - Rift configuration contract
  - Nexus Rift-creation flow
  - Rift primary-space creation/programming
  - target-frame validation split
  - viewer refresh/attachment after targeting
- Out of scope:
  - mutation work
  - ingest/persistence subsystem work
  - broad workspace history/event model work

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created to hold the Rift lifecycle split as its own
  governed architecture lane instead of burying it in the viewer task.

## Success Metrics
- Bare Rifts can be created without target frames.
- Primary space type is chosen from Rift config and instantiated correctly.
- Frame targeting is explicit and rejects illegal static/dynamic combinations.
- Targeting refreshes the attached viewer using descriptor + current ACL state.

## Requirements (Functional + Non-Functional)
- Functional:
  - remove `target_frame_name` from `RiftConfiguration`
  - validate frame legality during targeting rather than during bare Rift creation
  - instantiate `StaticRiftSpace` or `DynamicRiftSpace` from the chosen config
  - attach/update the `FrameViewer` after successful targeting
- Non-functional:
  - keep lifecycle phases explicit
  - fail fast on illegal dynamic targeting
  - avoid fallback creation of a second workspace when the chosen space type is incompatible

## Constraints / Assumptions
- `space_type` remains a Rift-level preference/identity choice.
- Static targeting is the broad mode; dynamic targeting is the restrictive mode.
- Viewer projection must stay derived from descriptor truth plus current ACL.

## Dependencies / External References
- Current viewer/runtime proving ground.
- Existing RiftSpace artifacts under `tickets/artifacts/` for historical context.

## Milestones (Track Progress)
- [ ] Milestone 1: Split Rift configuration from target-frame selection
- [ ] Milestone 2: Program primary space from Rift config
- [ ] Milestone 3: Rewire targeting to refresh the viewer

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-08-split-rift-creation-from-frame-targeting-and-program-primary-space

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: create and execute the first implementation task for the lifecycle split
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The Rift lifecycle is phased cleanly and the primary space/viewer flow is explicit.

## Risks / Mitigations
- Risk: changing Rift creation breaks current tests and downstream assumptions.
  Mitigation: stage the split with focused unit coverage around config, creation,
  targeting, and viewer attachment.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Focus on unit tests first around Rift/Nexus lifecycle behavior.
- Expand to component/integration only if the split crosses a real runtime seam
  unit tests cannot prove.

## Rollout / Adoption Plan
- First land the split with backward-compatible semantics where possible.
- Then re-evaluate whether one-primary-space should become a stricter invariant.

## Open Questions
- Should one-primary-space become a hard runtime invariant now or later?
- Should viewer refresh happen automatically on every successful target or
  through a separate explicit program step?

## Decision Log
- Created after clarifying that ACL truth is Nexus-owned and frame targeting
  should therefore be a separate action from bare Rift creation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the Rift access-mode model is either implemented
  and merged into canonical docs or intentionally retired.

## Notes
- DATETIME: 2026-04-08T11:35:38Z
  TYPE: PLAN
  CLAIM: The Rift lifecycle needs to be split into creation, primary-space
    programming, and frame targeting. The current code still collapses target
    frame selection into `create_rift(...)`, which is the wrong place because
    ACL truth and target legality live at Nexus/frame level.
  EVIDENCE:
  - user_instruction: "configuring the rift is a seperate and isolated situation outside of targetting a frame"
  - user_instruction: "targetting a frame should happen as a seperate action"
  IMPACT: This epic preserves the architecture lane so the split can be
    implemented intentionally instead of as scattered edits.
  NEXT: create the story/task and patch docs for the first implementation cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-08T23:36:22Z
  TYPE: PLAN
  CLAIM: The lifecycle split now has one retained design artifact for the
    three Rift access modes. The current best direction is:
    - `static` for already-live published access only
    - `capability` for restrictive pre-published execution without codegen
    - `dynamic` for the full workspace mode
  EVIDENCE:
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md:1-1
  IMPACT: The access-mode semantics now have a durable home inside the same
    epic instead of staying trapped in chat-only discussion.
  NEXT: use this artifact to guide the next access-mode implementation choices
    after the first lifecycle split cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic isolates the Rift lifecycle split from the now-mostly-finished viewer
lane. The goal is to make Rift creation bare, primary space creation explicit,
and frame targeting the separate validated action that drives viewer refresh.

