# Task: Extract Interface ICLEANABLE To Assets

## Metadata
- Task ID: TASK-2026-05-04-extract-interface-icleanable-to-assets
- Story:
- Epic: EPIC-2026-05-04-split-interfaces-py-into-assets
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-04T23:22:58Z
- Updated: 2026-05-04T23:41:13Z

## Objective
Extract `ICleanable` into `src/melder/utilities/interfaces/assets/icleanable.py`
and keep `interfaces.py` as the stable aggregator import lane.

## Ticket Contract
- ENTRY_GATE: the interfaces-split epic is active and `ICleanable` is the
  root base protocol that many other interfaces inherit from.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/interfaces/interfaces.py`
  - `src/melder/utilities/interfaces/assets/icleanable.py`
  - one focused import/validation test surface if needed
- DEPENDENCIES:
  - `tickets/epics/2026-05-04_split_interfaces_py_into_assets_epic.md`
  - current `ICleanable` definition in `interfaces.py`
- EXIT_GATE: `ICleanable` lives in its own asset file, `interfaces.py`
  re-exports it cleanly, and focused validation proves downstream imports still
  work.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if even the base protocol
  extraction exposes a stronger import-cycle problem than the current split
  plan expects.

## Scope Boundaries
- In scope:
  - `ICleanable` extraction
  - `assets/` folder usage
  - aggregator import update
  - focused validation
- Out of scope:
  - extracting other interfaces in this task
  - broader interface semantic changes
  - `__init__.py` export wiring

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: the bulk interface-assets split landed and the shared import validation ring passed.
  the common base protocol for the rest of the interface surface.

## Steps / Checklist
- [ ] Create `assets/` under the interfaces folder if still missing.
- [ ] Move `ICleanable` into `assets/icleanable.py`.
- [ ] Update `interfaces.py` to aggregate `ICleanable` from the new file.
- [ ] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `assets/icleanable.py`
- updated `interfaces.py` aggregator
- focused validation proof

## Files / Paths Impacted
- src/melder/utilities/interfaces/interfaces.py
- src/melder/utilities/interfaces/assets/icleanable.py

## Validation
- Executed:
  - python -m py_compile src/melder/utilities/interfaces/interfaces.py src/melder/utilities/interfaces/assets/icleanable.py
  - python -m pytest -q -p no:cacheprovider tests/unit/melder/utilities/interfaces/test_interface_inheritance.py
- Result:
  - interface aggregator compile passed
  - focused interfaces import/inheritance ring passed (23 passed)

## Risks / Rollback Notes
- Risk: even the first extraction triggers unexpected downstream import behavior.
  Rollback: keep `ICleanable` in the aggregator until the import seam is
  better understood.

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
- DATETIME: 2026-05-04T23:22:58Z
  TYPE: PLAN
  CLAIM: `ICleanable` is the right first extraction because it is the shared
    base protocol for most of the rest of the interface surface. If that seam
    fails, the broader split plan is wrong; if it works, it gives the rest of
    the split a clean root dependency.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:1-67
  - class_inventory: `ICleanable` is the first shared base protocol in the file
  IMPACT: This is the lowest-risk first real split step and the fastest way to
    prove whether the assets-folder approach is viable.
  NEXT: create the `assets/` folder, move `ICleanable`, and validate the
    aggregator import seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first actual extraction in the interfaces split: move the
base `ICleanable` protocol out of the giant file while keeping the aggregator
stable.

- DATETIME: 2026-05-04T23:41:13Z
  TYPE: MEASURE
  CLAIM: This interface now exists as its own lower-case asset file under the interfaces assets folder, and the shared interfaces aggregator import ring passed after the full split.
  EVIDENCE:
  - src/melder/utilities/interfaces/assets/icleanable.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/utilities/interfaces/test_interface_inheritance.py
  IMPACT: The interface surface is no longer trapped in the giant monolithic file for this contract.
  NEXT: none
  REREAD: REQUIRED
  SCORE_0_TO_10: 8


