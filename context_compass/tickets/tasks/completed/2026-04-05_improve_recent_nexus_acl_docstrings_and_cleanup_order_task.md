# Task: Improve Recent Nexus ACL Docstrings And Cleanup Order

## Metadata
- Task ID: TASK-2026-04-05-improve-recent-nexus-acl-docstrings-and-cleanup-order
- Story: none
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T11:20:00Z
- Updated: 2026-04-05T17:50:09Z

## Objective
Improve the public-library docstrings on the recently added Nexus/ACL classes
and normalize class layout so `cleanup()` appears directly below `__init__`
in the touched classes.

## Ticket Contract
- ENTRY_GATE: the recent Nexus/ACL chain/bootstrap work is already landed and
  the user explicitly requested a documentation-quality pass over those new
  objects.
- EXECUTION_BOUNDARY: targeted docstring and class-layout polish only.
- DEPENDENCIES:
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/frame_acl_manager.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py
  - src/melder/aether/nexus/acl/*
- EXIT_GATE: touched classes have materially better rich docstrings, parameter
  contracts are documented, and `cleanup()` is moved directly below `__init__`
  in the touched classes where practical.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the docstring/layout pass
  reveals a deeper API/behavior contract conflict that should not be silently
  normalized.

## Scope Boundaries
- In scope:
  - rich class and method docstrings for the recent Nexus/ACL objects
  - cleanup ordering directly below `__init__`
  - focused compile/tests for touched files
- Out of scope:
  - behavioral refactors
  - API redesign
  - broad repo-wide documentation rewrites

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the targeted Nexus/ACL docstring and cleanup-order pass
  is landed and the focused compile/test surface passed.

## Steps / Checklist
- [ ] Investigate the recently added Nexus/ACL classes and identify docstring/layout gaps.
- [ ] Improve rich docstrings on the targeted classes/methods.
- [ ] Move `cleanup()` directly below `__init__` in the touched classes.
- [ ] Run focused compile/tests on the touched files.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- improved rich docstrings on the recent Nexus/ACL classes
- normalized cleanup ordering in the touched classes

## Files / Paths Impacted
- src/melder/aether/nexus/nexus.py
- src/melder/aether/nexus/frame_acl_manager.py
- src/melder/aether/nexus/frame_descriptor_manager.py
- src/melder/aether/nexus/frame_descriptor/frame_descriptor.py
- src/melder/aether/nexus/acl/
- codex/context_compass/tickets/tasks/2026-04-05_improve_recent_nexus_acl_docstrings_and_cleanup_order_task.md
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/nexus.py src/melder/aether/nexus/frame_acl_manager.py src/melder/aether/nexus/frame_descriptor_manager.py src/melder/aether/nexus/frame_descriptor/frame_descriptor.py src/melder/aether/nexus/acl/frame_acl_configuration.py src/melder/aether/nexus/acl/frame_acl_configuration_chain.py src/melder/aether/nexus/acl/frame_acl_container.py src/melder/aether/nexus/acl/frame_acl_builder.py src/melder/aether/nexus/acl/frame_acl_validator.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_configuration_chain.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_aetheric_frame_descriptor.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: the pass turns into behavioral churn instead of staying a
  documentation-quality improvement.
  Rollback: keep the work strictly to docstrings/comments/class ordering.

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
- DATETIME: 2026-04-05T11:43:00Z
  TYPE: MEASURE
  CLAIM: The targeted documentation-quality pass is mechanically clean in the
    touched Nexus/ACL files and the focused unit surface is green. The compile
    step passed on all touched files, and the focused Nexus/ACL/descriptor unit
    tranche passed with 89 tests. The only test reroute needed was using the
    live `test_aetheric_frame_descriptor.py` filename instead of the older
    stale `test_frame_descriptor.py` path.
  EVIDENCE:
  - command:python -m py_compile src/melder/aether/nexus/nexus.py src/melder/aether/nexus/frame_acl_manager.py src/melder/aether/nexus/frame_descriptor_manager.py src/melder/aether/nexus/frame_descriptor/frame_descriptor.py src/melder/aether/nexus/acl/frame_acl_configuration.py src/melder/aether/nexus/acl/frame_acl_configuration_chain.py src/melder/aether/nexus/acl/frame_acl_container.py src/melder/aether/nexus/acl/frame_acl_builder.py src/melder/aether/nexus/acl/frame_acl_validator.py
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_configuration_chain.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_aetheric_frame_descriptor.py tests/unit/melder/aether/test_nexus.py
  IMPACT: The docstring/layout pass did not destabilize the recent Nexus/ACL
    boundary and is ready for review instead of still being an in-progress
    cleanup.
  NEXT: review the new docstring quality and decide whether you want one more
    tightening pass on any specific class or method cluster.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T11:38:00Z
  TYPE: FACT
  CLAIM: The first documentation-quality pass is now implemented across the
    recent Nexus/ACL boundary. The targeted classes were upgraded from thin
    placeholder docstrings to richer contract-first docstrings that now spell
    out purpose, ownership, lifecycle, threading, parameter meaning, and
    failure expectations. The class layout was also normalized so `cleanup()`
    now sits directly below `__init__` in the touched recent classes, including
    `Nexus`, `FrameACLManager`, `FrameDescriptorManager`, `FrameDescriptor`,
    and the recent ACL builder/configuration/chain/container/validator types.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:38-1111
  - src/melder/aether/nexus/frame_acl_manager.py:12-374
  - src/melder/aether/nexus/frame_descriptor_manager.py:18-547
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py:14-430
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:10-388
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py:10-382
  - src/melder/aether/nexus/acl/frame_acl_container.py:13-231
  - src/melder/aether/nexus/acl/frame_acl_builder.py:10-186
  - src/melder/aether/nexus/acl/frame_acl_validator.py:9-111
  IMPACT: The recent Nexus/ACL surface is much closer to the repo's public
    library standard, and the next reader can understand construction,
    teardown, and facade behavior without reverse-engineering it from code
    shape alone.
  NEXT: run focused compile/tests against the touched Nexus/ACL files and then
    decide whether one more docstring tightening pass is still needed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T11:20:00Z
  TYPE: PLAN
  CLAIM: The recent Nexus/ACL classes are behaviorally in place, but the
    docstrings still read like placeholder/internal notes instead of public
    library contracts. The most obvious gaps are thin parameter docs, weak
    lifecycle/concurrency language, and inconsistent class layout where
    `cleanup()` is not kept directly below `__init__`.
  EVIDENCE:
  - src/melder/aether/nexus/frame_acl_manager.py:12-310
  - src/melder/aether/nexus/frame_descriptor_manager.py:18-547
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py:13-380
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:10-353
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py:10-332
  - src/melder/aether/nexus/acl/frame_acl_container.py:12-190
  - src/melder/aether/nexus/acl/frame_acl_builder.py:10-137
  - src/melder/aether/nexus/acl/frame_acl_validator.py:8-90
  - src/melder/aether/nexus/nexus.py:38-1083
  IMPACT: This is the right moment to improve the public-library contract
    surface before more ACL/view work piles on top of these classes.
  NEXT: patch the targeted classes with richer docstrings and cleanup ordering,
    then run focused validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to improve the documentation quality of the recent Nexus/ACL
classes without changing their behavior.
