# Story: Frame ACL Subsystem Bootstrap
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-04-frame-acl-subsystem-bootstrap
- Epic: EPIC-2026-04-02-rift-profile-surface-and-access-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-04T21:59:53Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As the project owner, I want the first frame-scoped ACL subsystem objects
scaffolded under the Nexus/descriptor boundary, so that the ACL lane can move
from theory into a real implementation surface without overbuilding the system.

## Value / MRP Alignment
This story gives the ACL lane a real runtime foothold. Without a concrete
manager/container/builder/config/validator object shape, later view/codegen
propagation work will keep getting deferred behind handwavy naming arguments.

## Ticket Contract
- ENTRY_GATE: the ACL epic is active, selector prerequisites are already in
  place, and the user has now chosen a concrete frame-scoped subsystem shape.
- EXECUTION_BOUNDARY: scaffold the first placeholder runtime objects and wire
  them under the corrected Nexus/descriptor boundary only; no full ACL
  propagation engine in this story.
- DEPENDENCIES:
  - EPIC-2026-04-02-rift-profile-surface-and-access-model
  - TASK-2026-04-02-design-profile-contracts-and-access-boundaries
  - tickets/artifacts/nexus_acl_builder_and_persistence_model.md
- EXIT_GATE: placeholder Frame ACL subsystem objects exist in code, `Nexus`
  owns the manager, the manager owns frame ACL containers, descriptor creation
  ensures a matching container exists with defaults, and the ticket/patch docs
  reflect the intended ownership chain.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the placeholder slice starts
  pulling in full propagation/runtime policy behavior beyond the agreed
  boundary.

## Requirements (Functional)
- Add `FrameACLManager`
- Add `FrameACLContainer`
- Add `FrameACLBuilder`
- Add `FrameACLConfiguration`
- Add `FrameACLValidator`
- Wire one manager under `Nexus`
- Make the manager own `frame_name -> FrameACLContainer`
- Ensure descriptor creation also creates the matching ACL container with
  defaults
- Make the container the owner of the unique frame-scoped ACL objects
- Make the builder object-singleton per frame container

## Requirements (Non-Functional)
- Thread-safe for one-builder-at-a-time mutation flow
- Small and reviewable
- No fake completeness or giant ACL engine in this slice

## Scope Boundaries
- In scope:
  - placeholder ACL subsystem classes
  - descriptor ownership wiring
  - patch docs and ticket state
- Out of scope:
  - full ACL propagation engine
  - final JSON schema details
  - final Rift/view/codegen consumer integration

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the placeholder ACL classes are landed, the corrected
  Nexus-owned manager / per-frame container split is wired, and the focused ACL
  placeholder plus Nexus unit surfaces passed.

## Dependencies / Related Work
- tickets/epics/2026-04-02_rift_profile_surface_and_access_model_epic.md
- tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
- tickets/tasks/completed/2026-04-04_enforce_root_conduit_name_uniqueness_for_acl_selectors_task.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-04-scaffold-frame-acl-subsystem-placeholders - add the first placeholder classes and descriptor wiring
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `Nexus` owns one `FrameACLManager`
- The manager owns one `FrameACLContainer` per frame target in its dictionary
- The container owns the frame-scoped builder/configuration/validator objects
- The builder is object-singleton per frame container

## Validation / Test Plan
- Focused unit tests for the placeholder object ownership chain and the
  one-builder-per-frame behavior.

## UX / API / Data Notes
- This story defines the internal object shape first.
- Public ACL authoring API details can stay iterative on top of this.

## Risks / Mitigations
- Risk: placeholder work balloons into a full ACL engine.
  Mitigation: keep this story scoped to ownership and placeholder structure.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Exact placeholder method set on `FrameACLBuilder`
- Exact history data shape in the container

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/frame_acl_subsystem_bootstrap/architecture_patch.md
  - system_docs/patches/active/frame_acl_subsystem_bootstrap/component_patch_frame_acl_manager.md
  - system_docs/patches/active/frame_acl_subsystem_bootstrap/component_patch_frame_acl_container.md
  - system_docs/patches/active/frame_acl_subsystem_bootstrap/component_patch_frame_acl_builder.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-04T22:20:26Z
  TYPE: FACT
  CLAIM: The story now has its first runtime result. The placeholder ACL
    subsystem classes exist under `src/melder/aether/nexus/`, `Nexus` owns the
    ACL manager, the manager owns per-frame containers keyed by frame name, and
    descriptor creation ensures the matching container exists with defaults.
    The focused ACL placeholder and Nexus unit surfaces both passed after the
    wire-up.
  EVIDENCE:
  - tickets/tasks/2026-04-04_scaffold_frame_acl_subsystem_placeholders_task.md:1-176
  - src/melder/aether/nexus/frame_acl_manager.py:1-141
  - src/melder/aether/nexus/frame_acl_container.py:1-177
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_subsystem.py
  IMPACT: The ACL lane now has a real placeholder subsystem shape to build on
    instead of only design prose.
  NEXT: review the placeholder object chain and choose the next ACL refinement
    slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T21:59:53Z
  TYPE: FACT
  CLAIM: The first ACL implementation slice should stay structural. The user
    does not want a two-to-three-week god-tier ACL system. They want one
    Nexus-owned ACL manager with per-frame ACL containers and enough real
    runtime shape to hold the builder, config, validator, and bounded history
    without pretending the full propagation story is solved immediately.
  EVIDENCE:
  - user_instruction: "we don't need perfection here"
  - user_instruction: "FrameACLContainer can hold history of different configurations and the builder and anything else we might need to hold in there"
  - user_instruction: "the builder controls the flow and owns the change process"
  IMPACT: The bootstrap story should stop at object ownership and placeholder
    semantics instead of forcing a complete ACL engine into one slice.
  NEXT: scaffold the placeholder classes, keep the manager on `Nexus`, and
    make descriptor creation also ensure the matching ACL container exists.
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
This story exists to give the ACL lane a first real runtime shape under the
Nexus/descriptor boundary without overbuilding the full propagation system.