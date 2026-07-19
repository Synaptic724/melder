# Task: Expand Nexus Orchestration And Lifecycle Tests
- Completed: 2026-04-25T21:59:28Z
- Summary: Closed after the broader Nexus orchestration/lifecycle seam file
  landed, the restored ACL default-contract seam was validated, and the focused
  mixed unit/component/integration ring passed green.

## Metadata
- Task ID: TASK-2026-04-20-expand-nexus-orchestration-and-lifecycle-tests
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-20T18:06:07Z
- Updated: 2026-04-25T21:59:28Z

## Objective
Add focused tests around the broader Nexus orchestration and lifecycle seams:
Rift registration/removal, projection refresh barriers, target-frame runtime
validation, ACL/profile registry behavior, Aether frame detach handling, and
singleton lifecycle cleanup.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested test expansion for the listed Nexus
  orchestration/lifecycle seams after the Nexus-frame authoring lane.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/nexus.py`
  - directly affected tests under `tests/unit/melder/aether/`,
    `tests/component/melder/aether/`, and `tests/integration/melder/aether/`
  - this task ticket and `attention_board.md`
- DEPENDENCIES:
  - `tests/unit/melder/aether/test_nexus.py`
  - `tests/component/melder/aether/test_frame_acl_component.py`
  - `tests/integration/melder/aether/test_frame_acl_compiler_integration.py`
  - existing active Nexus cleanup and frame-authoring test tasks
- EXIT_GATE: the requested broader Nexus seams have explicit test coverage and
  the focused Nexus validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the new tests require
  widening into unrelated AR/runtime subsystems or force low-value filler.

## Scope Boundaries
- In scope:
  - `create_rift`, `add_rift`, `remove_rift`
  - `_refresh_rift_projection_sets_for_frames`
  - `_validate_target_frame_runtime_requirements` and related helpers
  - ACL profile and named configuration registry surfaces
  - `check_for_aetheric_frame`
  - Nexus singleton lifecycle/reset behavior
- Out of scope:
  - unrelated Nexus-frame authoring object tests
  - lower Melder runtime tests not directly required by the listed seams
  - speculative refactors outside what the tests require

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the user directed closure for finished tickets and this
  task already had the requested seam ring green with the corrective Nexus ACL
  seam restored.

## Steps / Checklist
- [ ] Audit current coverage for each requested seam.
- [ ] Record the seam-by-seam gap set in `## Notes`.
- [ ] Add focused tests for Rift registration/removal atomicity.
- [ ] Add focused tests for projection refresh barrier behavior.
- [ ] Add focused tests for target-frame runtime validation.
- [ ] Add focused tests for ACL profile/configuration registry behavior.
- [ ] Add focused tests for `check_for_aetheric_frame`.
- [ ] Add focused tests for singleton lifecycle/reset behavior.
- [ ] Run focused Nexus validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- expanded Nexus orchestration/lifecycle test surface
- focused validation results for the listed seams

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-20_expand_nexus_orchestration_and_lifecycle_tests_task.md
- codex/context_compass/attention_board.md
- src/melder/aether/nexus/nexus.py
- tests/unit/melder/aether/
- tests/component/melder/aether/
- tests/integration/melder/aether/

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: the seam list is broad enough to spill into unrelated AR behavior.
  Rollback: keep every new case tied directly to one listed seam and stop when
  a required test would widen beyond the requested scope.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-20T18:06:07Z
  TYPE: PLAN
  CLAIM: The next Nexus test lane is broader than frame authoring and should
    stay organized around the exact orchestration/lifecycle seams the user
    listed: Rift registration/removal, projection refresh, target-frame
    validation, ACL registry behavior, Aether frame detach handling, and
    singleton lifecycle.
  EVIDENCE:
  - user_instruction: seam list for `create_rift` / `add_rift` / `remove_rift`, projection refresh, target-frame validation, ACL registry, `check_for_aetheric_frame`, and singleton lifecycle
  IMPACT: The first step is a seam-by-seam gap audit, not blind new tests.
  NEXT: read the current Nexus tests around each requested seam and record the
    first coverage gap set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T18:06:07Z
  TYPE: FACT
  CLAIM: The current `Nexus` test surface already has baseline coverage for
    several requested seams, but it is uneven. Existing tests cover the basic
    `create_rift(...)` gate and success path, projection refresh happy paths,
    named ACL configuration basics, target-frame room-mode eligibility through
    public attach flows, and one managed-frame Aether detach path. The missing
    work is narrower:
    - `create_rift(...)` failure atomicity and gate unregister-on-failure
    - `remove_rift(...)` ordering when ref-count and Nexus-frame cleanup happen together
    - projection refresh failure recovery and `finally` re-enable behavior
    - direct helper-level target-frame runtime validation matrices
    - ACL/profile replacement semantics and per-contract projection selection
    - broader `check_for_aetheric_frame(...)` disposal/no-op matrices
    - singleton lifecycle abuse around re-init, cleanup, and reset
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:58-180
  - tests/unit/melder/aether/test_nexus.py:804-980
  - tests/unit/melder/aether/test_nexus.py:1263-1530
  - tests/unit/melder/aether/test_nexus.py:4320-4510
  - tests/component/melder/aether/test_frame_acl_component.py:1-66
  IMPACT: We should fill the exact regression seams you listed instead of
    duplicating the already-covered happy-path cases.
  NEXT: implement a focused broader `Nexus` unit test file for the missing
    atomicity, failure-recovery, helper-validation, disposal, and singleton
    lifecycle cases first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T18:06:07Z
  TYPE: FACT
  CLAIM: The first broader Nexus regression file is now implemented as a
    focused unit seam file:
    `test_nexus_orchestration_and_lifecycle.py`. The first tranche targets:
    - `create_rift(...)` failure atomicity and gate cleanup
    - `add_rift(...)` gate mismatch atomicity
    - `remove_rift(...)` ordering around ref-count decrement and Nexus-frame cleanup
    - projection refresh failure recovery
    - direct target-frame runtime helper validation
    - ACL profile/config replacement and projection selection
    - `check_for_aetheric_frame(...)` disposal/no-op matrices
    - repeated init / cleanup / `_reset_singleton_for_tests()` lifecycle abuse
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py:1-404
  IMPACT: The broader Nexus seam list is now represented in one bounded test
    file instead of being spread implicitly across the large legacy Nexus test
    file.
  NEXT: run the focused regression file and fix any harness or contract
    mismatches it exposes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T18:06:07Z
  TYPE: FACT
  CLAIM: The broader validation ring exposed one real regression in the
    earlier stale-method cleanup: replacing the active default ACL bundle still
    requires a public Nexus seam. `insert_head_frame_acl_configuration(...)`
    was restored with an honest same-name-contract-install docstring, and the
    integration compiler test now uses it again.
  EVIDENCE:
  - src/melder/aether/nexus/frame_acl_manager.py:457-490
  - src/melder/aether/nexus/nexus.py:1714-1752
  - tests/integration/melder/aether/test_frame_acl_compiler_integration.py:190-210
  IMPACT: The broader test lane corrected a real Nexus regression instead of
    only adding tests.
  NEXT: rerun the focused broader Nexus seam ring and record the final result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T18:06:07Z
  TYPE: MEASURE
  CLAIM: The broader Nexus orchestration/lifecycle seam ring is now green.
    The new focused unit file plus the selected existing unit/component/
    integration cases covering the requested seams pass together.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py tests/component/melder/aether/test_frame_acl_component.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py -k "create_rift or add_rift or remove_rift or refresh_rift_projection_sets or on_frame_acl_changed or target_frame or frame_acl_profile or named_frame_acl or check_for_aetheric_frame or external_aether_frame_cleanup or reset_singleton or cleanup or compiled_surface_projects_directly_into_frame_viewer or runtime_acl_commit_changes_compiled_command_surface"` -> `52 passed, 85 deselected`
  IMPACT: The requested broader Nexus seams are now covered by a mix of new
    and existing tests, and the restored default-contract install seam is
    validated in the same ring.
  NEXT: report the exact new file and the seam-by-seam coverage outcome to the
    user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the broader Nexus orchestration and lifecycle test expansion lane.
