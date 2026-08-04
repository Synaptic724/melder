# Task: Scaffold Frame ACL Profile Placeholders

## Metadata
- Task ID: TASK-2026-04-05-scaffold-frame-acl-profile-placeholders
- Story: STORY-2026-04-02-profile-contracts-and-access-boundaries
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T12:55:00Z
- Updated: 2026-04-05T17:50:09Z

## Objective
Add the placeholder ACL profile objects and manager/Nexus registry surface:
- `FrameACLProfile`
- `ViewACLDetails`
- `CodegenACLDetails`
- manager version string `0.0.1`
- manager/Nexus profile registry methods

## Ticket Contract
- ENTRY_GATE: the user explicitly approved a narrow placeholder profile slice
  before deeper ACL configuration work continues.
- EXECUTION_BOUNDARY: placeholder object model and registry/facade only.
- DEPENDENCIES:
  - src/melder/aether/nexus/acl/
  - src/melder/aether/nexus/frame_acl_manager.py
  - src/melder/aether/nexus/nexus.py
- EXIT_GATE: placeholder profile objects exist, manager owns the registry and
  version string, Nexus facades the registry, and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if profile storage semantics
  force deeper application/merge behavior than this slice should own.

## Scope Boundaries
- In scope:
  - placeholder ACL profile objects
  - manager-owned profile registry
  - Nexus façade methods
  - focused tests
- Out of scope:
  - profile application into live ACL configs
  - codegen/view merge semantics
  - deep propagation or validator behavior

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the placeholder profile objects, manager registry/version,
  Nexus facades, and focused tests are landed and green.

## Steps / Checklist
- [ ] Add placeholder profile/detail objects in the ACL package.
- [ ] Add version and profile registry ownership to `FrameACLManager`.
- [ ] Add thin Nexus façade methods for the profile registry.
- [ ] Add focused unit tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- placeholder ACL profile objects
- manager/Nexus profile registry surface
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/
- src/melder/aether/nexus/frame_acl_manager.py
- src/melder/aether/nexus/nexus.py
- tests/unit/melder/aether/
- codex/context_compass/tickets/tasks/2026-04-05_scaffold_frame_acl_profile_placeholders_task.md
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/acl/frame_acl_profile.py src/melder/aether/nexus/frame_acl_manager.py src/melder/aether/nexus/nexus.py tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: the placeholder profile slice quietly hard-codes future merge logic.
  Rollback: keep the objects as storage/registry shapes only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T13:01:00Z
  TYPE: MEASURE
  CLAIM: The placeholder ACL profile slice is landed and green. The new object
    graph is:
    - `FrameACLProfile`
    - `ViewACLDetails`
    - `CodegenACLDetails`
    `FrameACLManager` now also owns a profile registry and version string
    `0.0.1`, and `Nexus` now facades version/register/get/list/remove over
    that registry. The focused unit run over the new objects and the adjacent
    manager/Nexus surfaces passed.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_profile.py:1-465
  - src/melder/aether/nexus/frame_acl_manager.py:1-421
  - src/melder/aether/nexus/nexus.py:1-1995
  - tests/unit/melder/aether/test_frame_acl_profile.py:1-208
  - tests/unit/melder/aether/test_nexus_frame_acl_profiles.py:1-58
  - command:python -m py_compile src/melder/aether/nexus/acl/frame_acl_profile.py src/melder/aether/nexus/frame_acl_manager.py src/melder/aether/nexus/nexus.py tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py
  IMPACT: The ACL subsystem now has a reusable placeholder profile registry
    boundary before deeper configuration and profile-application work starts.
  NEXT: decide how the real `FrameACLConfiguration` object should compose the
    view-side state and how/when those profiles should apply into it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T12:55:00Z
  TYPE: PLAN
  CLAIM: The profile placeholder slice is now well scoped. The user clarified
    that we do not need separate `FrameACLViewProfile` or
    `FrameACLCodegenProfile` classes. Instead, one `FrameACLProfile` should
    own two placeholder detail objects, `ViewACLDetails` and
    `CodegenACLDetails`, where each detail object simply hosts a JSON payload.
    The manager should also carry a version string (`0.0.1`) and own the
    profile registry, with Nexus facading that registry at the root boundary.
  EVIDENCE:
  - user_instruction: "ViewACLDetails hosts a Json and same with CodegenACLDetails"
  - user_instruction: "the FrameACLProfile has those 2 objects the details objects"
  - user_instruction: "we should also have a version attribute in the manager to define the version of this system and just set it to 0.0.1 for now"
  IMPACT: We can add the profile object graph and registry now without locking
    in deeper merge/application semantics too early.
  NEXT: add the placeholder objects plus manager/Nexus registry methods and
    focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to add placeholder ACL profile objects and the manager/Nexus
registry boundary before deeper ACL configuration work continues.
