# Task: Harden Rift Space And Workstation Locking
- Completed: 2026-04-13T11:34:18Z
- Summary: Closed the room/workstation lock-hardening slice after the locked runtime posture and its no-change decisions were incorporated into the settled AR model.

## Metadata
- Task ID: TASK-2026-04-11-harden-rift-space-and-workstation-locking
- Story: STORY-2026-04-11-add-workstation-to-rift-space
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T18:46:59Z
- Updated: 2026-04-13T11:34:18Z

## Objective
Add explicit `RLock` ownership to `RiftSpace` and `Workstation`, use those
locks in grouped mutation and cleanup paths, and explicitly review the nearby
runtime/ACL surfaces so we do not widen locking blindly.

## Ticket Contract
- ENTRY_GATE: the workstation and queue slices are landed, the user explicitly
  asked for stronger locking discipline on mutable room/runtime objects, and
  the current code review already confirmed the live lock posture of Rift,
  RiftSpace, Workstation, CommandSystem, and the recent ACL objects.
- EXECUTION_BOUNDARY: `RiftSpace`, `Workstation`, focused tests, ticket/board/
  artifact sync, and explicit no-change review conclusions for nearby runtime/
  ACL surfaces only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-11_add_workstation_to_rift_space_task.md
  - tickets/tasks/2026-04-11_add_workstation_reference_modes_to_rift_space_task.md
  - tickets/tasks/2026-04-11_add_rift_space_event_queue_and_weak_binding_events_task.md
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift_space/workstation.py
  - src/melder/aether/nexus/rift/rift_space/command_system.py
  - src/melder/aether/nexus/acl/frame_acl_container.py
  - src/melder/aether/nexus/acl/frame_acl_command_configuration.py
  - src/melder/aether/nexus/acl/frame_acl_set_compatibility_validator.py
  - src/melder/aether/nexus/acl/frame_acl_validator.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/unit/melder/aether/test_frame_acl_container.py
- EXIT_GATE: `RiftSpace` and `Workstation` own `RLock`s, grouped mutation and
  cleanup paths use them, focused tests are green, and the no-change decisions
  for `CommandSystem` and the reviewed ACL objects are captured.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if making the room/workstation
  locking coherent requires widening into broader ACL/runtime refactors.

## Scope Boundaries
- In scope:
  - `RiftSpace` lock ownership
  - `Workstation` lock ownership
  - cleanup and multistep mutation serialization
  - focused Rift/Nexus tests
  - explicit review notes for nearby runtime/ACL objects
- Out of scope:
  - queue API redesign
  - ACL enforcement
  - adding locks everywhere “just because”

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested stronger lock discipline on
  these mutable runtime objects and asked for the nearby ACL surfaces to be
  reviewed as part of the same pass.

## Steps / Checklist
- [ ] Record the current lock posture and no-change decisions in `## Notes`.
- [ ] Create patch docs for the locking slice.
- [ ] Add `RLock` ownership plus grouped mutation/cleanup locking to `RiftSpace`.
- [ ] Add `RLock` ownership plus grouped mutation/cleanup locking to `Workstation`.
- [ ] Update or add focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- locked `RiftSpace`
- locked `Workstation`
- explicit no-change review decisions for `CommandSystem` and reviewed ACL objects
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/aether/nexus/rift/rift_space/workstation.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: this turns into lock cargo-culting and widens beyond the two objects
  that actually own mutable grouped state here.
  Rollback: keep the slice limited to `RiftSpace` and `Workstation` and record
  explicit no-change decisions for `CommandSystem` and the reviewed ACL objects.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/rift_space_lock_hardening/architecture_patch.md
  - system_docs/patches/active/rift_space_lock_hardening/component_patch_rift_space.md
  - system_docs/patches/active/rift_space_lock_hardening/component_patch_workstation.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the room/workstation lock model is merged into
  canonical docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-11T18:55:09Z
  TYPE: FACT
  CLAIM: The runtime-hardening slice is now landed in source. `RiftSpace`,
    `Workstation`, and `CommandSystem` now all own per-instance `RLock`s, and
    the grouped cleanup/mutation/getter paths that depend on consistent owned
    state now serialize through those locks. In the reviewed ACL slice,
    `FrameACLContainer` and `FrameACLCommandConfiguration` already had the
    right lock posture, and `FrameACLValidator` plus
    `FrameACLSetCompatibilityValidator` now also serialize cleanup and the
    mutable “last validated/report” state they own.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:1-118
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-612
  - src/melder/aether/nexus/rift/rift_space/workstation.py:1-602
  - src/melder/aether/nexus/rift/rift_space/command_system.py:1-320
  - src/melder/aether/nexus/acl/frame_acl_container.py:1-149
  - src/melder/aether/nexus/acl/frame_acl_command_configuration.py:1-199
  - src/melder/aether/nexus/acl/frame_acl_validator.py:1-253
  - src/melder/aether/nexus/acl/frame_acl_set_compatibility_validator.py:1-171
  IMPACT: The mutable room/runtime surfaces now align better with the no-GIL
    runtime assumptions without blindly widening locking across every nearby
    class.
  NEXT: run the focused runtime and ACL validator test slices and confirm the
    hardening pass stays green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T18:55:09Z
  TYPE: MEASURE
  CLAIM: The lock-hardening slice is green on both touched surfaces. The
    focused Rift/Nexus slice and the focused ACL container/validator slices
    both pass after adding the new lock usage.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py` -> 74 passed
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_set_compatibility_validator.py` -> 41 passed
  IMPACT: The room/workstation locking model is ready for review before we go
    back to ACL enforcement or another runtime slice.
  NEXT: review the lock-hardening cut and choose whether the next lane returns
    to ACL enforcement or continues runtime hardening.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T18:46:59Z
  TYPE: FACT
  CLAIM: The reopened runtime surfaces split cleanly into “needs locking” and
    “reviewed no-change”. `Rift` already owns an `RLock` and uses it in
    cleanup. `RiftSpace` and `Workstation` currently own mutable grouped state
    and multistep mutation paths but still have no lock. `CommandSystem` does
    not yet own enough mutable coordinated state to justify adding one in the
    same pass. In the recent ACL slice, `FrameACLContainer` and
    `FrameACLCommandConfiguration` already own locks and use them in grouped
    cleanup, while the reopened validators are mostly immutable review surfaces
    with no grouped setter behavior in this slice.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:1-131
  - src/melder/aether/nexus/rift/rift.py:207-249
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-612
  - src/melder/aether/nexus/rift/rift_space/workstation.py:1-597
  - src/melder/aether/nexus/rift/rift_space/command_system.py:1-320
  - src/melder/aether/nexus/acl/frame_acl_container.py:1-149
  - src/melder/aether/nexus/acl/frame_acl_command_configuration.py:1-199
  - src/melder/aether/nexus/acl/frame_acl_set_compatibility_validator.py:1-104
  - src/melder/aether/nexus/acl/frame_acl_validator.py:1-111
  IMPACT: The patch target is narrower than “lock everything”. We should harden
    the two room/runtime objects that actually need it and explicitly leave the
    rest alone in this tranche.
  NEXT: add the task/patch docs and then patch `RiftSpace` and `Workstation`
    only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:34:18Z
  TYPE: DECISION
  CLAIM: The room/workstation lock-hardening slice is complete and can move to
    the completed lane. The locked posture is now part of the settled runtime
    foundation and is already reflected in the canonical AR docs.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:1-612
  - src/melder/aether/nexus/rift/rift_space/workstation.py:1-597
  - codex/context_compass/system_docs/src_architecture.md:464-468
  IMPACT: This lock-hardening task no longer needs active review state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task hardens the mutable room/runtime lock posture only. The focused
runtime and ACL validator slices are green and the no-change decisions for the
broader nearby surfaces are captured in the notes.
