# Task: Implement Codegen ACL Fluent Builder
- Completed: 2026-04-25T20:01:52Z
- Summary: Closed after the codegen-family ACL fluent builder landed green,
  kept the existing frame/container draft lifecycle intact, and synced the
  builder lane ticket/patch state.

## Metadata
- Task ID: TASK-2026-04-25-implement-codegen-acl-fluent-builder
- Story: STORY-2026-04-25-implement-codegen-acl-fluent-builder
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T19:09:44Z
- Updated: 2026-04-25T20:01:52Z

## Objective
Add a dedicated codegen-family ACL fluent builder under
`src/melder/aether/nexus/acl/builder/`, wire it into the existing
`FrameACLBuilder` lifecycle, and validate it with focused unit tests.

## Ticket Contract
- ENTRY_GATE: the active board routes to this builder lane and the user
  explicitly asked to start with the codegen ACL fluent builder first.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py`
  - `src/melder/aether/nexus/acl/builder/frame_acl_builder.py`
  - directly affected typed ACL configuration/profile surfaces
  - focused unit tests for the builder lane
- DEPENDENCIES:
  - `codex/context_compass/system_docs/patches/active/codegen_acl_fluent_builder/architecture_patch.md`
  - `codex/context_compass/system_docs/patches/active/codegen_acl_fluent_builder/component_patch_frame_acl_builder.md`
  - `codex/context_compass/system_docs/patches/active/codegen_acl_fluent_builder/component_patch_codegen_acl_fluent_builder.md`
  - `codex/context_compass/system_docs/patches/active/codegen_acl_fluent_builder/code_description_patch_codegen_acl_fluent_builder_flow.md`
- EXIT_GATE: the codegen fluent builder lands green and the routing/patch-doc
  state is coherent.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a passing fluent builder
  requires redesigning the generic builder lifecycle or widening into other ACL
  families.

## Scope Boundaries
- In scope:
  - codegen-family fluent builder
  - generic-builder entrypoint for codegen drafts
  - focused builder tests
  - routing/artifact sync required for this lane
- Out of scope:
  - view/command fluent builders
  - new codegen validation features
  - broader ACL storage redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly directed the next ACL authoring lane
  to start with the codegen fluent builder.

## Steps / Checklist
- [x] Repair missing ticket/patch-doc state for this lane.
- [x] Inspect the current staged builder implementation against the typed ACL
      configuration contract.
- [x] Finish or correct the codegen fluent builder.
- [x] Run focused builder validation.
- [x] Sync board/artifact state to the landed builder lane.

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py src/melder/aether/nexus/acl/builder/frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_codegen_builder.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_codegen_builder.py`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/codegen_acl_fluent_builder/architecture_patch.md`
  - `system_docs/patches/active/codegen_acl_fluent_builder/component_patch_frame_acl_builder.md`
  - `system_docs/patches/active/codegen_acl_fluent_builder/component_patch_codegen_acl_fluent_builder.md`
  - `system_docs/patches/active/codegen_acl_fluent_builder/code_description_patch_codegen_acl_fluent_builder_flow.md`
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: merge into canonical docs or explicit supersession

## Notes
- DATETIME: 2026-04-25T19:09:44Z
  TYPE: FACT
  CLAIM: The active routing pointed at a missing codegen fluent-builder
    task/story/epic lane, so the first required repair is restoring those files
    and the matching patch-doc lane before further implementation or validation.
  EVIDENCE:
  - codex/context_compass/attention_board.md:24-33
  - filesystem_check: missing `codex/context_compass/tickets/tasks/2026-04-25_implement_codegen_acl_fluent_builder_task.md`
  IMPACT: Ticket/patch gating had to be repaired before this lane could resume
    honestly after re-onboarding.
  NEXT: recreate the missing task/story/epic and patch-doc files, then validate
    the staged builder code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T19:44:00Z
  TYPE: FACT
  CLAIM: The live worktree already contained the bulk of the codegen fluent
    builder implementation in untracked form. The actual code work in this pass
    was bounded: restore the missing ticket/patch-doc lane, confirm the staged
    builder shape, and correct the focused builder tests so they author
    permissive-only operations under a permissive or full-access profile rather
    than the default safe profile.
  EVIDENCE:
  - src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py:1-446
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-400
  - tests/unit/melder/aether/test_frame_acl_codegen_builder.py:1-154
  IMPACT: The builder lane stayed narrow and honest instead of inventing a
    second ACL authoring model or weakening validator semantics.
  NEXT: return the landed builder slice for review and decide whether the next
    ACL authoring lane should widen to view/command families.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T19:44:00Z
  TYPE: MEASURE
  CLAIM: The focused codegen ACL fluent-builder ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/acl/builder/frame_acl_codegen_builder.py src/melder/aether/nexus/acl/builder/frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_codegen_builder.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_codegen_builder.py` -> `7 passed, 2 warnings`
  IMPACT: The first codegen-family fluent builder is stable enough to return
    instead of staying in implementation state.
  NEXT: review the landed builder and decide whether to close this task or
    branch into the next ACL-family fluent builder.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first codegen-family ACL fluent builder slice.
