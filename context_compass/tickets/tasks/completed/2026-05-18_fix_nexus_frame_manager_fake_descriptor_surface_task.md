# Task: fix nexus frame manager fake descriptor surface

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-nexus-frame-manager-fake-descriptor-surface
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T14:47:01Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the next `nexus`-lane blocker by syncing the `_FakeNexus` test double to the
current descriptor-surface dependency used by `NexusFrameManager`.

## Ticket Contract
- ENTRY_GATE: the next stop-on-first `-k nexus` failure is
  `test_nexus_frame_manager_create_publishes_descriptor_and_acl_state`
  because `_FakeNexus` lacks `_get_or_create_frame_descriptor(...)`.
- EXECUTION_BOUNDARY:
  - `tests/unit/melder/aether/test_nexus_frame_manager.py`
- DEPENDENCIES:
  - current `nexus` test-driving lane
  - `NexusFrameManager._ensure_descriptor_and_acl(...)`
- EXIT_GATE:
  - the targeted frame-manager unit test is green
  - the fake Nexus surface includes the descriptor helper that the real manager now calls
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if runtime evidence shows the
  manager should not depend on `_get_or_create_frame_descriptor(...)`

## Scope Boundaries
- In scope:
  - `_FakeNexus` surface synchronization for descriptor creation
- Out of scope:
  - runtime NexusFrameManager behavior
  - unrelated Nexus failures after this one

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the next live `nexus` blocker is a bounded test-double
  surface drift against the current manager dependency

## Steps / Checklist
- [ ] confirm the fake-surface drift and live manager dependency
- [ ] patch `_FakeNexus` to forward `_get_or_create_frame_descriptor(...)`
- [ ] rerun the targeted frame-manager unit test
- [ ] continue to the next `nexus` blocker only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- a narrow `_FakeNexus` descriptor-surface sync

## Files / Paths Impacted
- `tests/unit/melder/aether/test_nexus_frame_manager.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\aether\test_nexus_frame_manager.py::test_nexus_frame_manager_create_publishes_descriptor_and_acl_state`

## Risks / Rollback Notes
- Low risk. This lane should remain fake-surface only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-18T14:47:01Z
  TYPE: FACT
  CLAIM: The next `nexus` blocker is a fake-surface drift. `NexusFrameManager`
    now uses `_nexus._get_or_create_frame_descriptor(...)` inside
    `_ensure_descriptor_and_acl(...)`, but the unit’s `_FakeNexus` only forwards
    `_get_required_frame_descriptor(...)` even though its owned fake descriptor
    manager already implements both surfaces.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:757-823
  - tests/unit/melder/aether/test_nexus_frame_manager.py:78-100
  - tests/unit/melder/aether/test_nexus_frame_manager.py:175-216
  IMPACT: The `nexus` lane stops on a stale fake before the next real runtime issue.
  NEXT: patch `_FakeNexus` to forward `_get_or_create_frame_descriptor(...)`, then
    rerun the targeted frame-manager unit test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:47:01Z
  TYPE: FACT
  CLAIM: The same fake lane also has a stale conduit-cloud surface. The manager’s
    frame-overview publisher now reads `frame._conduit_cloud.list_conduit_names()`,
    but `_FakeFrame` still installs `_conduit_cloud` as a bare `SimpleNamespace`
    with only `_registry`.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:823-841
  - tests/unit/melder/aether/test_nexus_frame_manager.py:20-37
  IMPACT: Even after fixing the fake Nexus descriptor helper, the unit still
    stops on the stale fake frame cloud shape.
  NEXT: replace the fake conduit-cloud namespace with a tiny fake object that
    implements `list_conduit_names()`, then rerun the targeted unit test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:47:01Z
  TYPE: FACT
  CLAIM: The same fake Nexus surface is also missing the ACL-container removal
    forwarder used by `handle_aether_frame_disposal(...)`. The fake already owns
    `_FakeFrameACLManager`, but it never forwards `_remove_frame_acl_container(...)`
    through the fake Nexus object itself.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:658-663
  - tests/unit/melder/aether/test_nexus_frame_manager.py:92-110
  - tests/unit/melder/aether/test_nexus_frame_manager.py:175-216
  IMPACT: The same fake lane would keep failing on later frame-manager cleanup paths
    even after the descriptor helper and conduit-cloud fixes.
  NEXT: add the `_remove_frame_acl_container(...)` forwarder to `_FakeNexus`, then
    rerun the targeted disposal unit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:47:01Z
  TYPE: MEASURE
  CLAIM: The targeted frame-manager fake-surface lane is green.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus_frame_manager.py:20-37
  - tests/unit/melder/aether/test_nexus_frame_manager.py:175-220
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\unit\melder\aether\test_nexus_frame_manager.py::test_nexus_frame_manager_create_publishes_descriptor_and_acl_state` -> `1 passed`
  IMPACT: This `nexus` blocker is cleared, so the next useful move is another
    stop-on-first `-k nexus` pass.
  NEXT: rerun `pytest -vv -x --tb=long -k nexus` and route the next failure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active `nexus` lane for a narrow frame-manager fake-surface drift. Current
evidence points to a unit-fake update only.
