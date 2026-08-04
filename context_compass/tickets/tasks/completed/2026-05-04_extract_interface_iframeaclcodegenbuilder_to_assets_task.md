# Task: Extract Interface IFrameACLCodegenBuilder To Assets

## Metadata
- Task ID: TASK-2026-05-04-extract-interface-iframeaclcodegenbuilder-to-assets
- Story:
- Epic: EPIC-2026-05-04-split-interfaces-py-into-assets
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p2
- Created: 2026-05-04T23:22:58Z
- Updated: 2026-05-04T23:41:13Z

## Objective
Extract IFrameACLCodegenBuilder into src/melder/utilities/interfaces/assets/iframeaclcodegenbuilder.py while keeping interfaces.py as the
stable aggregator import lane.

## Ticket Contract
- ENTRY_GATE: the interfaces-split epic is active and IFrameACLCodegenBuilder is queued
  behind earlier dependency-safe extractions.
- EXECUTION_BOUNDARY:
  - src/melder/utilities/interfaces/interfaces.py
  - src/melder/utilities/interfaces/assets/iframeaclcodegenbuilder.py
  - focused import/validation updates needed for this one interface move
- DEPENDENCIES:
  - tickets/epics/2026-05-04_split_interfaces_py_into_assets_epic.md
  - current IFrameACLCodegenBuilder definition in interfaces.py
- EXIT_GATE: IFrameACLCodegenBuilder lives in its own asset file, interfaces.py
  re-exports it cleanly, and focused validation proves downstream imports still
  work.
- FAILURE_ESCALATION: raise DECISION_REQUEST if IFrameACLCodegenBuilder has an import
  or inheritance seam that makes isolated extraction unsafe at this stage.

## Scope Boundaries
- In scope:
  - IFrameACLCodegenBuilder extraction
  - aggregator import update for this one class
  - focused validation
- Out of scope:
  - extracting unrelated interfaces
  - broader interface semantic changes
  - __init__.py export wiring

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: the bulk interface-assets split landed and the shared import validation ring passed.
  under the interfaces split epic.

## Steps / Checklist
- [ ] Move IFrameACLCodegenBuilder into src/melder/utilities/interfaces/assets/iframeaclcodegenbuilder.py.
- [ ] Update interfaces.py to aggregate IFrameACLCodegenBuilder from the new file.
- [ ] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document.
- [ ] Document each meaningful finding immediately in ## Notes before further investigation.

## Deliverables
- src/melder/utilities/interfaces/assets/iframeaclcodegenbuilder.py
- updated interfaces.py aggregator entry for IFrameACLCodegenBuilder
- focused validation proof

## Files / Paths Impacted
- src/melder/utilities/interfaces/interfaces.py
- src/melder/utilities/interfaces/assets/iframeaclcodegenbuilder.py

## Validation
- Executed:
  - python -m py_compile src/melder/utilities/interfaces/interfaces.py src/melder/utilities/interfaces/assets/iframeaclcodegenbuilder.py
  - python -m pytest -q -p no:cacheprovider tests/unit/melder/utilities/interfaces/test_interface_inheritance.py
- Result:
  - interface aggregator compile passed
  - focused interfaces import/inheritance ring passed (23 passed)

## Risks / Rollback Notes
- Risk: IFrameACLCodegenBuilder depends on other interfaces strongly enough that the
  extraction order must change.
  Rollback: postpone the task behind whichever prerequisite interface class is
  actually required.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from UNKNOWN or HYPOTHESIS.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (UNKNOWN promoted to FACT only with evidence)
- [ ] Notes quality maintained (SCORE_0_TO_10 >=
      workflow.ticket_microcycle.minimum_note_score)
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
- Add a ## Notes entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote UNKNOWN to FACT only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-04T23:22:58Z
  TYPE: PLAN
  CLAIM: IFrameACLCodegenBuilder is mapped as one explicit extraction unit under the
    interfaces split epic.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py
  IMPACT: The large interfaces refactor can proceed one class at a time instead
    of as one opaque monolithic rewrite.
  NEXT: extract IFrameACLCodegenBuilder when its dependency order comes up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
This task owns the isolated extraction of IFrameACLCodegenBuilder into the interfaces
assets folder while keeping the aggregator stable.

- DATETIME: 2026-05-04T23:41:13Z
  TYPE: MEASURE
  CLAIM: This interface now exists as its own lower-case asset file under the interfaces assets folder, and the shared interfaces aggregator import ring passed after the full split.
  EVIDENCE:
  - src/melder/utilities/interfaces/assets/iframeaclcodegenbuilder.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/utilities/interfaces/test_interface_inheritance.py
  IMPACT: The interface surface is no longer trapped in the giant monolithic file for this contract.
  NEXT: none
  REREAD: REQUIRED
  SCORE_0_TO_10: 8


