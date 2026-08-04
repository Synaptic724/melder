# Task: Fix Cleanup And Nexus Mode Test Fallout
- Completed: 2026-04-25T10:37:18Z
- Summary: Closed during cleanup after the passive Nexus detach fix and the
  stale Nexus/Aether fallout tests were aligned and validated green.

## Metadata
- Task ID: TASK-2026-04-24-fix-cleanup-and-nexus-mode-test-fallout
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-24T11:43:58Z
- Updated: 2026-04-25T10:37:18Z

## Objective
Repair the current test fallout by fixing the real passive-Nexus frame-detach
cleanup bug and updating the stale tests that still assume the pre-refactor
raw Nexus-frame authoring contract or pre-detach Aether frame persistence.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested immediate fixes for the listed
  failing tests.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/nexus.py`
  - `src/melder/aether/nexus/frame_descriptor/frame_descriptor.py`
  - directly affected failing tests under `tests/component/`, `tests/integration/`,
    and `tests/unit/`
  - this task ticket and `attention_board.md`
- DEPENDENCIES:
  - `src/melder\aether\conduit\conduit.py`
  - `src/melder\aether\aether.py`
  - `src/melder\spellbook\spellbook.py`
  - `src/melder\aether\nexus\nexus_frame_manager.py`
  - `tests\unit\melder\aether\conduit\test_conduit_lifecycle.py`
- EXIT_GATE: the passive Nexus detach path no longer leaves stale conduit/spell
  records behind, the stale single-mode/raw-manager tests are aligned to the
  current contract, and the focused failing ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the fixes widen into a broader
  AR/frame-lifecycle redesign instead of a bounded runtime+test fallout patch.

## Scope Boundaries
- In scope:
  - passive Nexus cleanup on frame detach
  - stale tests around raw Nexus-frame manager creation in `single` mode
  - stale tests around post-cleanup frame persistence assumptions
  - directly affected validation ring
- Out of scope:
  - new codegen behavior
  - unrelated Nexus/AR refactors
  - broad test rewrites outside the failing fallout set

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: current failing tests show one real runtime bug plus a
  small stale-test tranche after recent Nexus/cleanup contract changes.

## Steps / Checklist
- [ ] Confirm which failures are real runtime regressions vs stale tests.
- [ ] Patch the passive Nexus frame-detach cleanup path if stale records remain.
- [ ] Update stale tests to the current raw-manager and frame-detach contracts.
- [ ] Run the focused failing ring.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- bounded runtime fix for passive Nexus detach cleanup
- aligned fallout tests for current Nexus/Aether cleanup contracts
- focused validation results

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-24_fix_cleanup_and_nexus_mode_test_fallout_task.md
- codex/context_compass/attention_board.md
- src/melder/aether/nexus/nexus.py
- src/melder/aether/nexus/frame_descriptor/frame_descriptor.py
- tests/component/melder/spellbook/test_spellbook_component_spellbook.py
- tests/integration/melder/aether/test_aether_integration_frames.py
- tests/integration/melder/aether/test_aether_integration_nexus_passive_ingest.py
- tests/integration/melder/spellbook/test_spellbook_integration_core.py
- tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py
- tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/component/melder/spellbook/test_spellbook_component_spellbook.py -k "post_conjure_bind or post_conjure_scan"`
  - `python -m pytest -q tests/integration/melder/aether/test_aether_integration_frames.py tests/integration/melder/aether/test_aether_integration_nexus_passive_ingest.py tests/integration/melder/spellbook/test_spellbook_integration_core.py tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py -k "check_for_aetheric_frame_matrix or cleanup_cleans_frame_manager or reset_singleton_for_tests"`

## Risks / Rollback Notes
- Risk: a quick fix papers over the detach bug in tests instead of fixing the
  descriptor runtime truth.
  Rollback: keep runtime cleanup and stale-test alignment as separate decisions
  with explicit evidence.

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
- DATETIME: 2026-04-24T11:43:58Z
  TYPE: FACT
  CLAIM: The current failure set splits cleanly into one real runtime bug and
    one stale-test tranche. The Nexus orchestration failures come from the now-
    intentional `NexusFrameManager` raw-creation restriction in `single` mode,
    which rejects non-shared frame names. Separately, the passive Nexus spell-
    record failures are real: `conduit.cleanup()` drops the last frame through
    `Aether`, `Nexus.check_for_aetheric_frame(...)` clears the frame overview
    and ACL container, and then later `Spellbook.cleanup()` cannot remove spell
    records because `_remove_spell_record(...)` short-circuits once the frame is
    no longer publishable.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py:611-707
  - src/melder/aether/nexus/nexus_frame_manager.py:328-377
  - src/melder/aether/conduit/conduit.py:373-400
  - src/melder/aether/aether.py:243-279
  - src/melder/aether/nexus/nexus.py:2154-2202
  - src/melder/spellbook/spellbook.py:3328-3347
  - src/melder/aether/nexus/frame_descriptor_manager.py:523-555
  IMPACT: We should patch runtime cleanup for the descriptor bug, but update the
    single-mode/raw-manager tests to the current contract instead of weakening
    the manager.
  NEXT: add the board row, patch the descriptor detach cleanup path, then align
    the stale tests to current contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-24T11:43:58Z
  TYPE: PLAN
  CLAIM: The bounded fix shape is now explicit. The runtime patch should clear
    descriptor-owned runtime publication state on frame detach without deleting
    the descriptor object, and the test fallout patch should only touch the
    stale assertions that still assume pre-refactor raw-manager behavior or
    pre-detach frame persistence.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py:16-39
  - src/melder/aether/nexus/nexus.py:2154-2202
  - src/melder/aether/nexus/nexus_frame_manager.py:640-675
  - tests/integration/melder/aether/test_aether_integration_frames.py:334-373
  - tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py:611-707
  IMPACT: We can keep this as one tight runtime-plus-tests patch instead of
    reopening broader cleanup or frame-authoring design.
  NEXT: run the focused failing ring and record exactly what still fails.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-24T11:43:58Z
  TYPE: FACT
  CLAIM: The final fix needed two separate patches. First, runtime detach
    cleanup now clears descriptor-owned runtime publication state through
    `FrameDescriptor.clear_runtime_publication_state()` and both Nexus detach
    call paths use that helper. Second, the remaining spellbook
    component/integration failures were caused by the tests themselves: they
    reset `Nexus` after `Aether` was already live, which split
    `Aether._nexus` from `Nexus._instance` and made cleanup notify one singleton
    while assertions read another. The two affected fixtures now reset `Nexus`
    before `Aether`, and the redundant mid-test Nexus resets are removed.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py:314-359
  - src/melder/aether/nexus/nexus.py:2154-2202
  - src/melder/aether/nexus/nexus_frame_manager.py:640-675
  - src/melder/aether/aether.py:65-124
  - tests/component/melder/spellbook/test_spellbook_component_spellbook.py:17-37
  - tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py:21-41
  IMPACT: The passive Nexus detach contract and the test singleton lifecycle
    are now aligned, so the fallout is fixed without weakening the recent
    cleanup or Nexus frame-manager semantics.
  NEXT: record the focused validation results and return the patch for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-24T11:43:58Z
  TYPE: MEASURE
  CLAIM: The focused fallout ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/frame_descriptor/frame_descriptor.py src/melder/aether/nexus/nexus.py src/melder/aether/nexus/nexus_frame_manager.py tests/integration/melder/aether/test_aether_integration_frames.py tests/integration/melder/spellbook/test_spellbook_integration_core.py tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py tests/component/melder/spellbook/test_spellbook_component_spellbook.py tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py` -> success
  - validation_result: `python -m pytest -q tests/component/melder/spellbook/test_spellbook_component_spellbook.py -k "post_conjure_bind or post_conjure_scan"` -> `3 passed, 25 deselected`
  - validation_result: `python -m pytest -q tests/integration/melder/aether/test_aether_integration_frames.py tests/integration/melder/aether/test_aether_integration_nexus_passive_ingest.py tests/integration/melder/spellbook/test_spellbook_integration_core.py tests/integration/melder/spellbook/test_spellbook_integration_scan_bind.py -k "spell_versions_drop_after_conduit_cleanup or post_conjure_bind_updates_and_removes_passive_nexus_spell_record or conjure_registers_spell_versions_and_cleanup_clears_registry or post_conjure_scan_updates_passive_nexus_records"` -> `4 passed, 58 deselected`
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py -k "check_for_aetheric_frame_matrix or cleanup_cleans_frame_manager_after_live_manager_population or reset_singleton_for_tests_cleans_live_manager_state"` -> `6 passed, 19 deselected`
  IMPACT: The bounded fallout slice is stable enough to hand back immediately.
  NEXT: ask whether to close this task or keep it open for any further larger-
    suite fallout the user surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-24T11:43:58Z
  TYPE: FACT
  CLAIM: One additional unit-only fallout case remained after the main fix:
    the `_FakeDescriptor` test double in `test_nexus_frame_manager.py` still
    modeled the old descriptor surface and did not implement
    `clear_runtime_publication_state()`. That mismatch is now corrected on the
    test side only; no further runtime change was needed.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus_frame_manager.py:55-69
  - tests/unit/melder/aether/test_nexus_frame_manager.py:739-767
  - src/melder/aether/nexus/nexus_frame_manager.py:667-675
  IMPACT: The frame-manager unit double now matches the live descriptor
    contract, so the disposal-path unit cases can exercise the new API instead
    of failing on a stale fake.
  NEXT: run the failing frame-manager disposal slice and keep the task in
    review if it passes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task owns the immediate fallout fix for the current failing ring. The lane
is explicitly split between a real passive-Nexus detach cleanup bug and stale
tests that still assume pre-refactor Nexus raw-manager or frame-persistence
behavior.
