# Story: Implement Codegen ACL Fluent Builder
- Completed: 2026-04-25T20:01:52Z
- Summary: Closed after the bounded codegen-family builder slice landed and
  validated green on the focused builder ring.

## Metadata
- Story ID: STORY-2026-04-25-implement-codegen-acl-fluent-builder
- Epic: EPIC-2026-04-25-implement-codegen-acl-fluent-builder
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T19:09:44Z
- Updated: 2026-04-25T20:01:52Z

## User Narrative
As an engineer, I want a readable codegen ACL fluent builder so that authoring
codegen rules does not require hand-editing low-level rulesets or bypassing the
existing frame/container lifecycle.

## Value / MRP Alignment
The codegen ACL family is now specific enough that a fluent builder adds real
value instead of hiding vague architecture. The builder should reduce ceremony
without replacing the current typed configuration system.

## Ticket Contract
- ENTRY_GATE: the codegen ACL validation/profile slice is complete enough to
  support authoring ergonomics.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/acl/builder/`
  - directly affected typed configuration/profile surfaces
  - focused builder tests
- DEPENDENCIES:
  - `tickets/tasks/2026-04-25_implement_codegen_acl_fluent_builder_task.md`
- EXIT_GATE: the codegen ACL builder exists, is reachable through
  `FrameACLBuilder`, and is validated with focused tests.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current generic builder
  contract is too rigid for the fluent layer.

## Requirements (Functional)
- Provide a dedicated `FrameACLCodegenBuilder`.
- Add a generic-builder entrypoint for codegen drafts.
- Support fluent profile and common rule authoring.
- Commit and discard through the existing builder lifecycle.

## Requirements (Non-Functional)
- Keep typing strict.
- Keep cleanup deterministic and lock-disciplined.
- Do not widen into command/view fluent builders yet.

## Acceptance Criteria
- `FrameACLBuilder.begin_codegen_change(...)` returns a fluent codegen builder.
- The fluent builder can author the common codegen ACL operations.
- The resulting configuration remains a normal typed
  `FrameACLCodegenConfiguration`.
- Focused builder tests are green.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-25T19:09:44Z
  TYPE: PLAN
  CLAIM: The story should stay bounded to one family-specific fluent builder.
    The generic builder/container/configuration model already exists and should
    remain the source of truth.
  EVIDENCE:
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-220
  - src/melder/aether/nexus/acl/configurations/frame_acl_codegen_configuration.py:1-120
  IMPACT: The implementation can stay small and reviewable.
  NEXT: implement the task that lands the file, wiring, and tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T19:44:00Z
  TYPE: FACT
  CLAIM: The first codegen-family fluent builder is now landed and green. The
    story stayed bounded to the existing frame/container draft lifecycle:
    `FrameACLBuilder.begin_codegen_change(...)` returns
    `FrameACLCodegenBuilder`, the fluent builder mutates the active typed
    codegen draft, and commit/discard still flow through the generic builder.
  EVIDENCE:
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-400
  - src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py:1-446
  - tests/unit/melder/aether/test_frame_acl_codegen_builder.py:1-154
  IMPACT: The next ACL authoring discussion can move from "can we do this" to
    "which family should get the next fluent layer."
  NEXT: return the story for review and decide whether to close it or widen the
    fluent-builder program.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owns the first family-specific ACL fluent builder: codegen only.
