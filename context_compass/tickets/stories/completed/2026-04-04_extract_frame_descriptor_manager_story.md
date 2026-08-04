# Story: Extract Frame Descriptor Manager
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the FrameDescriptorManager extraction story and archived the landed manager-boundary slice.


## Metadata
- Story ID: STORY-2026-04-04-extract-frame-descriptor-manager
- Epic: EPIC-2026-04-04-frame-descriptor-manager-refactor
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-04T20:41:17Z
- Updated: 2026-04-09T21:59:36Z

## User Narrative
As the project owner, I want the frame-scoped descriptor/store machinery moved
out of `Nexus`, so that the public root stays lean and the frame-state
subsystem becomes a clean, thread-safe boundary.

## Value / MRP Alignment
This story protects a foundational internal boundary. If frame-scoped state
continues to accrete inside `Nexus`, ACL systems and future multi-object façade
work will keep building on a confused root object.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved direct migration to a dedicated
  manager and accepted removal of the old in-class descriptor-store paths.
- EXECUTION_BOUNDARY: investigate the exact split, migrate the code, update
  focused tests/docs, and remove the old state paths.
- DEPENDENCIES:
  - EPIC-2026-04-04-frame-descriptor-manager-refactor
  - TASK-2026-04-04-migrate-nexus-frame-state-into-frame-descriptor-manager
  - system_docs/patches/active/nexus_frame_descriptor_manager/architecture_patch.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/component_patch_nexus.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/component_patch_frame_descriptor_manager.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/code_description_patch_frame_descriptor_manager.md
- EXIT_GATE: one thread-safe manager owns the frame-scoped descriptor/store
  state, `Nexus` delegates to it, and the old in-class paths are removed.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the extraction requires a
  broader public API redesign instead of a clean internal migration.

## Requirements (Functional)
- Define the exact method split between `Nexus` and `FrameDescriptorManager`.
- Migrate descriptor/store ownership out of `Nexus`.
- Keep façade-level frame operations coherent from `Nexus`.
- Remove old internal descriptor-store paths after migration.

## Requirements (Non-Functional)
- Thread-safe for multi-step mutations.
- No backward-compat shim.
- Reviewable and explicit about ownership.

## Scope Boundaries
- In scope:
- `Nexus` frame-scoped descriptor/store methods
- new manager class/file
- focused tests/docs required by the migration
- Out of scope:
- final ACL manager systems
- viewer/query implementation
- unrelated Nexus/Rift API redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the child task landed the manager extraction, delegated
  the frame-scoped state flows out of `Nexus`, and passed focused local
  validation, so the story is ready for review.

## Dependencies / Related Work
- tickets/epics/2026-04-04_frame_descriptor_manager_refactor_epic.md
- tickets/tasks/2026-04-04_migrate_nexus_frame_state_into_frame_descriptor_manager_task.md
- tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
- tickets/tasks/2026-03-28_refactor_rift_public_surface_into_nexus_singleton_task.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-04-migrate-nexus-frame-state-into-frame-descriptor-manager - lock split, migrate, and validate
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `Nexus` no longer directly owns the frame-descriptor dictionary.
- Frame-scoped publish/remove/lookup logic lives under the manager.
- The manager is thread-safe and `Nexus` stays the semantic façade/root.

## Validation / Test Plan
- Focused validation of Nexus/frame-scoped record behavior after migration.
- Truthful reporting when tests are not run.

## UX / API / Data Notes
- Public behavior should remain rooted on `Nexus`.
- This is an internal ownership migration, not a new user-facing builder API
  yet.

## Risks / Mitigations
- Risk: the story leaves partial state ownership on both sides.
  Mitigation: remove old paths instead of aliasing them.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Which façade-level frame methods should remain on `Nexus` after the move.

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/nexus_frame_descriptor_manager/architecture_patch.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/component_patch_nexus.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/component_patch_frame_descriptor_manager.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/code_description_patch_frame_descriptor_manager.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-04T20:55:05Z
  TYPE: FACT
  CLAIM: The story now has its first full implementation result. The child task
    introduced `FrameDescriptorManager`, moved the frame-scoped publish/remove
    and descriptor/record helper cluster into it, and left `Nexus` as the
    semantic façade that delegates those operations. Focused Nexus unit
    validation passed after the migration.
  EVIDENCE:
  - tickets/tasks/2026-04-04_migrate_nexus_frame_state_into_frame_descriptor_manager_task.md:1-182
  - src/melder/aether/nexus/frame_descriptor_manager.py:18-595
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py
  IMPACT: The manager extraction is no longer just a design note. The lane is
    now in review on the actual runtime boundary.
  NEXT: review the boundary with the user and either accept it or request one
    more cleanup pass in this slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T20:41:17Z
  TYPE: FACT
  CLAIM: The current extraction target is narrow enough to treat as one story.
    `Nexus` owns the frame-descriptor dictionary, the posture-refresh and
    publishability path, the passive record publication/removal path, and the
    Nexus-managed frame-record helpers. Those frame-scoped responsibilities can
    move together without reopening the broader Rift registry/config/topology
    surface.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:147-149
  - src/melder/aether/nexus/nexus.py:668-969
  - src/melder/aether/nexus/nexus.py:1715-1921
  IMPACT: The migration can stay bounded to the frame-scoped state subsystem
    instead of turning into another broad Nexus redesign.
  NEXT: execute the task that locks the exact method split and performs the
    migration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story exists to migrate the frame-scoped Nexus descriptor/store boundary
into a dedicated manager while keeping `Nexus` as the façade/root. The manager
is now landed and the story is waiting on review/acceptance rather than further
initial implementation.

