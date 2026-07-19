# Task: Implement View And Command ACL Fluent Builders
- Completed: 2026-04-25T20:01:52Z
- Summary: Closed after the view and command ACL fluent builders landed green,
  bringing the three major ACL families onto the same family-specific builder
  pattern.

## Metadata
- Task ID: TASK-2026-04-25-implement-view-and-command-acl-fluent-builders
- Story: STORY-2026-04-25-implement-view-and-command-acl-fluent-builders
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T19:44:00Z
- Updated: 2026-04-25T20:01:52Z

## Objective
Add family-specific fluent builders for the `view` and `command` ACL families,
wire them into `FrameACLBuilder`, and validate them with focused unit tests.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to begin the other ACL fluent APIs
  after the codegen slice.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py`
  - `src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py`
  - `src/melder/aether/nexus/acl/builder/frame_acl_builder.py`
  - focused unit tests
- DEPENDENCIES:
  - `codex/context_compass/system_docs/patches/active/view_and_command_acl_fluent_builders/architecture_patch.md`
  - `codex/context_compass/system_docs/patches/active/view_and_command_acl_fluent_builders/component_patch_frame_acl_builder.md`
  - `codex/context_compass/system_docs/patches/active/view_and_command_acl_fluent_builders/component_patch_frame_acl_view_builder.md`
  - `codex/context_compass/system_docs/patches/active/view_and_command_acl_fluent_builders/component_patch_frame_acl_command_builder.md`
- EXIT_GATE: the view/command fluent builders land green and the builder lane
  is coherently routed.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the family-specific helpers
  widen into a broader ACL redesign.

## Scope Boundaries
- In scope:
  - view fluent builder
  - command fluent builder
  - generic builder entrypoints
  - focused tests
- Out of scope:
  - codegen builder redesign
  - new ACL runtime/compiler semantics

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py src/melder/aether/nexus/acl/builder/frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/view_and_command_acl_fluent_builders/architecture_patch.md`
  - `system_docs/patches/active/view_and_command_acl_fluent_builders/component_patch_frame_acl_builder.md`
  - `system_docs/patches/active/view_and_command_acl_fluent_builders/component_patch_frame_acl_view_builder.md`
  - `system_docs/patches/active/view_and_command_acl_fluent_builders/component_patch_frame_acl_command_builder.md`
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: merge into canonical docs or explicit supersession

## Notes
- DATETIME: 2026-04-25T19:44:00Z
  TYPE: PLAN
  CLAIM: The next family-specific builders should stay bounded and mirror the
    live profile vocabularies. `view` needs visibility/payload/member helpers,
    and `command` needs enablement/member-operation helpers.
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/profiles/view/safe_profile.py:1-58
  - src/melder/aether/nexus/acl/configurations/profiles/command/permissive_profile.py:1-38
  IMPACT: The implementation should be family-shaped rather than a generic
    "set any rule" abstraction only.
  NEXT: add the new builders, entrypoints, and focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T19:53:10Z
  TYPE: FACT
  CLAIM: The view and command builder slice is now landed. The generic builder
    exposes `begin_view_change(...)` and `begin_command_change(...)`, and the
    new family-specific builders mirror the live family vocabularies instead of
    generic placeholder methods:
    - `FrameACLViewBuilder` for visibility/payload/member rules
    - `FrameACLCommandBuilder` for enablement and member-operation rules
  EVIDENCE:
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-400
  - src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py:1-390
  - src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py:1-329
  IMPACT: The ACL authoring surface is now consistent across the three major
    families without changing the underlying container/configuration model.
  NEXT: return the slice for review and decide whether the fluent-builder
    program should stop here or widen further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T19:53:10Z
  TYPE: MEASURE
  CLAIM: The focused and broader builder rings are green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/acl/builder/frame_acl_view_builder.py src/melder/aether/nexus/acl/builder/frame_acl_command_builder.py src/melder/aether/nexus/acl/builder/frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py` -> `10 passed, 2 warnings`
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_profile_builder.py tests/unit/melder/aether/test_frame_acl_codegen_builder.py tests/unit/melder/aether/test_frame_acl_view_builder.py tests/unit/melder/aether/test_frame_acl_command_builder.py` -> `37 passed, 2 warnings`
  IMPACT: The new builders are stable enough to move to review immediately.
  NEXT: review the landed slice and decide whether to close this lane or add
    more fluent authoring surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
