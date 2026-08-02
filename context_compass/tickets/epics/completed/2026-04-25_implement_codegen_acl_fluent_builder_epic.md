# Epic: Implement Codegen ACL Fluent Builder
- Completed: 2026-04-25T20:01:52Z
- Summary: Closed after the first ACL authoring ergonomics slice landed one
  dedicated codegen fluent builder on top of the existing generic builder
  lifecycle.

## Metadata
- Epic ID: EPIC-2026-04-25-implement-codegen-acl-fluent-builder
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T19:09:44Z
- Updated: 2026-04-25T20:01:52Z
- Target Window: 2026-Q2

## Problem / Opportunity
The codegen ACL family is now real enough that authoring it through detached
profile factories and raw ruleset edits is too indirect. The current system has
the right runtime pieces:
- `FrameACLManager`
- `FrameACLContainer`
- `FrameACLBuilder`
- typed codegen configuration/profile objects

What is missing is an ergonomic authoring layer that keeps those existing
ownership boundaries but gives users and later schema surfaces a readable
fluent API for codegen ACL changes.

## MRP Alignment (Most Reasonable Product)
The MRP is not a new ACL subsystem and not a second persistence path.

The MRP is:
- one dedicated codegen-family fluent builder
- layered over the existing generic builder draft/commit lifecycle
- able to choose profiles and common codegen validation/import/meta settings
- returning normal typed `FrameACLCodegenConfiguration` revisions

## Ticket Contract
- ENTRY_GATE: the projection-driven codegen ACL validation slice is complete
  enough to make authoring ergonomics worth building.
- EXECUTION_BOUNDARY: codegen-family ACL authoring ergonomics only.
- DEPENDENCIES:
  - `src/melder/aether/nexus/acl/builder/frame_acl_builder.py`
  - `src/melder/aether/nexus/acl/configurations/frame_acl_codegen_configuration.py`
  - `src/melder/aether/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py`
  - `src/melder/aether/nexus/acl/frame_acl_container.py`
- EXIT_GATE: one usable codegen ACL fluent builder exists, is routed through
  the existing frame/container draft lifecycle, and is covered by focused unit
  tests.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the generic builder lifecycle
  cannot support the fluent layer without a broader ACL authoring redesign.

## Goals (Outcomes)
- Add a dedicated fluent builder for codegen ACL drafts.
- Keep projection/config/profile/container ownership intact.
- Make the common codegen authoring operations readable:
  - profile selection
  - precision profile selection
  - imports
  - builtin allow/deny
  - unsafe reflection
  - dunder access
  - recursive codegen
- Keep commit/discard flowing through the generic frame ACL builder.

## Non-Goals (Explicit Exclusions)
- A full fluent builder for view and command families in this slice.
- Replacing `FrameACLBuilder`.
- Replacing typed ACL configuration objects.
- Changing compiled ACL behavior.

## Milestones (Track Progress)
- [ ] Milestone 1: Restore coherent ticket and patch-doc routing for the
      builder lane.
- [ ] Milestone 2: Land `FrameACLCodegenBuilder` on top of the current draft
      lifecycle.
- [ ] Milestone 3: Green focused builder validation ring.

## Stories (Required to Complete)
- [ ] Story: implement the codegen ACL fluent builder over the current
      frame/container lifecycle

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: create the dedicated codegen builder file
- [ ] Task: wire the generic builder entrypoint
- [ ] Task: add focused builder tests
- [ ] Task: verify patch-doc and artifact-board sync

## Acceptance Criteria (Epic Done)
- The codegen fluent builder exists and is usable.
- The active routing/ticket/patch state is coherent.
- The focused builder ring is green.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-25T19:09:44Z
  TYPE: DECISION
  CLAIM: The current codegen ACL lane is past validator semantics and into
    authoring ergonomics. The next useful move is a codegen-family fluent
    builder layered over the existing `FrameACLBuilder` draft/commit model.
  EVIDENCE:
  - codex/context_compass/attention_board.md:24-33
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-220
  - src/melder/aether/nexus/acl/frame_acl_container.py:1-120
  IMPACT: The builder lane can stay bounded and useful instead of expanding
    into another ACL architecture discussion.
  NEXT: implement the story and task for the codegen fluent builder.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T19:44:00Z
  TYPE: MEASURE
  CLAIM: The first codegen ACL fluent-builder slice is implemented and green.
    The lane now has coherent ticket/patch-doc routing, a family-specific
    builder layered over the generic draft lifecycle, and focused unit
    validation.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-04-25_implement_codegen_acl_fluent_builder_task.md:1-136
  - src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py:1-446
  - tests/unit/melder/aether/test_frame_acl_codegen_builder.py:1-154
  IMPACT: This epic can move to review while we decide whether the broader ACL
    fluent-builder program should continue into command and view families.
  NEXT: review this codegen-first slice and decide whether to close it or stage
    the next family-specific builder.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic owns the first ACL authoring ergonomics slice after the
projection-driven codegen ACL validation work.
