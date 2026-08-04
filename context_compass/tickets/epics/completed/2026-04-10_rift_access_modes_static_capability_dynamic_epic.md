# Epic: Rift Access Modes Static Capability Dynamic
- Completed: 2026-05-16T16:41:00Z
- Summary: Closed at user direction as a retained umbrella reference for the
  static, capability, and dynamic room-mode split.

## Metadata
- Epic ID: EPIC-2026-04-10-rift-access-modes-static-capability-dynamic
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-10T00:50:25Z
- Updated: 2026-05-16T16:41:00Z
- Target Window: 2026-Q2
- Related Program/Initiative: Rift access-mode semantics and execution boundaries

## Problem / Opportunity
The runtime now has the first enabling pieces for the next Rift lane:
- `capability` now exists as a live non-codegen room type, but this epic still
  carries older pre-implementation semantics that need to stay aligned with the
  newer capability lane
- `Meld` and `Conduit` expose a no-create live-creation probe
- the retained access-mode artifact already defines the best current split:
  - `static`
  - `capability`
  - `dynamic`

What is still missing is a dedicated architecture lane that turns those ideas
into first-class Rift runtime behavior instead of leaving them split across:
- the closed Rift lifecycle epic
- the retained access-mode artifact
- recent chat-only design discussion

## MRP Alignment (Most Reasonable Product)
The MRP outcome is not "more room types." It is one coherent access model:
- `static` means already-live published access only
- `capability` means broad manual runtime access without codegen
- `dynamic` currently shares the same broad manual-runtime posture as
  capability and remains the future codegen-oriented room

If we do not isolate and implement this now as its own lane, the next Rift
changes will keep smearing static/capability/dynamic concerns together.

## Ticket Contract
- ENTRY_GATE: the first Rift lifecycle split is complete, the capability space
  placeholder exists, and the live-creation probe is landed.
- EXECUTION_BOUNDARY: access-mode semantics, ACL/runtime integration, and
  space-specific behavior for `static`, `capability`, and `dynamic`.
- DEPENDENCIES:
  - tickets/epics/completed/2026-04-08_rift_creation_frame_targeting_and_primary_space_split_epic.md
  - tickets/epics/completed/2026-04-09_live_creation_visibility_probe_for_static_access_epic.md
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
  - src/melder/aether/nexus/configuration/rift_space_type.py
  - src/melder/aether/nexus/rift/rift_space/
- EXIT_GATE: the access-mode model is implemented clearly enough that static,
  capability, and dynamic are separate, explainable, and testable runtime lanes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if static/capability semantics
  require a broader endpoint/publication redesign than Rift should own alone.

## Goals (Outcomes)
- Give `static`, `capability`, and `dynamic` one dedicated implementation lane.
- Keep `static` strict and non-codegen.
- Define and implement the middle `capability` mode properly.
- Preserve `dynamic` as the open workspace mode.
- Align ACL/view/runtime behavior with the three-mode split.

## Non-Goals (Explicit Exclusions)
- Broad UI/HUD product work.
- CommandOps orchestration changes.
- MutationResearch/runtime evolution work.
- Reopening the completed Rift lifecycle split.

## Scope Boundaries
- In scope:
  - mode semantics
  - space-type behavior boundaries
  - static live-access behavior
  - capability broad manual-runtime behavior
  - runtime/ACL integration for those modes
- Out of scope:
  - unrelated viewer expansion
  - unrelated Nexus publication refactors
  - raw product endpoint packaging

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created to give the static/capability/dynamic split its
  own durable architecture lane after the prerequisite lifecycle/probe work landed.

## Success Metrics
- One dedicated epic owns the access-mode model.
- `static`, `capability`, and `dynamic` no longer depend on chat memory.
- Future implementation can target this lane directly.

## Requirements (Functional + Non-Functional)
- Functional:
  - define final static contract
  - define final capability contract
  - define dynamic boundary relative to the other two
  - sequence implementation work cleanly
- Non-functional:
  - no fake static implemented by hidden dynamic tricks
  - no codegen leakage into static/capability
  - clear retained documentation and board hygiene

## Constraints / Assumptions
- The retained access-mode artifact is historical context, but the
  2026-04-12 capability runtime model supersedes it where the semantics differ.
- `capability` already exists in runtime as a live room type.
- `has_live_creation(...)` and `describe_live_creation_status(...)` are the
  canonical backend primitives for static/live checks.

## Dependencies / External References
- tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md

## Milestones (Track Progress)
- [ ] Milestone 1: Lock final access-mode semantics and sequencing
- [ ] Milestone 2: Implement static access behavior
- [ ] Milestone 3: Implement capability execution behavior

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-10-define-rift-access-modes-and-space-semantics

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: stage the access-mode lane from the retained artifact
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Rift access modes are governed by one clear epic, the implementation sequence
  is explicit, and the three-mode split is no longer trapped in retained notes only.

## Risks / Mitigations
- Risk: static and capability get blurred back into dynamic.
  Mitigation: keep each mode tied to a distinct contract and runtime surface.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Start with design/sequence validation.
- Later target focused unit and integration slices per mode.

## Rollout / Adoption Plan
- Stage the lane.
- Lock semantics.
- Implement static.
- Implement capability.

## Open Questions
- How strict should static lifecycle gating be in the first cut?
- What additional non-codegen distinction, if any, should capability keep from
  dynamic once the room-mode foundation is fully settled?

## Decision Log
- Created after the completed Rift lifecycle/probe work made the access-mode
  lane concrete enough to stand on its own.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the access-mode runtime model is implemented and
  merged into canonical docs or intentionally retired.

## Notes
- DATETIME: 2026-04-10T00:50:25Z
  TYPE: PLAN
  CLAIM: The completed lifecycle/probe lanes left one obvious next architecture
    hole: the static/capability/dynamic split now has enough substance to need
    its own epic instead of living as a retained note under a closed lifecycle lane.
  EVIDENCE:
  - tickets/epics/completed/2026-04-08_rift_creation_frame_targeting_and_primary_space_split_epic.md:1-187
  - tickets/epics/completed/2026-04-09_live_creation_visibility_probe_for_static_access_epic.md:1-157
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md:1-202
  IMPACT: Future work can now target access-mode behavior directly without reopening
    the wrong parent epic.
  NEXT: create the story/task lane and re-home the retained access-mode artifact to it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T00:24:24Z
  TYPE: FACT
  CLAIM: The umbrella access-mode lane is still valid, but its capability
    semantics drifted behind the live runtime. The newer capability lane and
    retained artifact now define capability as broad manual runtime access
    without codegen, strong refs allowed, and no handle/proxy theater, while
    `dynamic` currently shares that manual-runtime posture and reserves the
    later codegen distinction.
  EVIDENCE:
  - tickets/epics/2026-04-12_capability_rift_space_runtime_model_epic.md:13-37
  - tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md:32-45
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:15-31
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py:6-23
  - src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py:13-27
  IMPACT: New onboarding should still read this epic as the umbrella room-mode
    lane, but it should no longer inherit the older restrictive capability
    framing from the April 8 artifact.
  NEXT: keep the umbrella epic language aligned with the live capability lane
    so future doc and ticket refreshes do not regress.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic exists to isolate the Rift access-mode model into its own lane after
the prerequisite lifecycle split and live-creation probe work landed.
