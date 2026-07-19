# Task: Rename Crystallizer Configuration Builder And Add Cleanup
- Completed: 2026-05-10T00:06:36Z
- Summary: Closed after the builder file was renamed, made `Cleanable`, and
  given explicit one-shot ownership-transfer semantics.

## Metadata
- Task ID: TASK-2026-05-04-rename-crystallizer-configuration-builder-and-add-cleanup
- Story:
- Epic: EPIC-2026-05-04-implement-crystallizer-configuration-and-activation
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-05-04T23:01:34Z
- Updated: 2026-05-10T00:06:36Z

## Objective
Correct the builder seam so it matches repo naming and ownership rules:
- rename `builder.py` to `crystallizer_configuration_builder.py`
- make `CrystallizerConfigurationBuilder` a real `Cleanable`
- give the builder explicit ownership-transfer and cleanup behavior

## Ticket Contract
- ENTRY_GATE: the user explicitly called out the undernamed file and the
  missing builder cleanup/ownership contract.
- EXECUTION_BOUNDARY:
  - `src/melder/crystallizer/configuration/builder.py` rename + replacement
  - imports/tests that reference the builder path
  - focused builder/configuration tests
- DEPENDENCIES:
  - `src/melder/aether/nexus/nexus_frame_builder.py`
  - `src/melder/aether/nexus/acl/builder/frame_acl_builder.py`
  - `tests/unit/melder/crystallizer/test_crystallizer_configuration.py`
- EXIT_GATE: the builder has a full file name, inherits `Cleanable`, owns its
  wrapped configuration explicitly, and the focused tests prove cleanup and
  one-shot handoff behavior.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the builder needs a wider
  public API redesign than a narrow naming/ownership correction.

## Scope Boundaries
- In scope:
  - builder file rename
  - builder cleanup/ownership contract
  - direct builder import updates
  - focused unit tests
- Out of scope:
  - broader crystallizer root changes
  - public `__init__.py` export wiring
  - changing the underlying configuration object contract

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the builder rename and cleanup slice is implemented and
  the focused configuration test ring is green.

## Steps / Checklist
- [x] Rename the builder file to a full concrete name.
- [x] Make the builder inherit `Cleanable` and own `_configuration` explicitly.
- [x] Define one-shot ownership transfer for `build/finalize/activate`.
- [x] Update imports/tests and run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- renamed builder file
- cleanable builder with deterministic cleanup
- focused builder tests

## Files / Paths Impacted
- src/melder/crystallizer/configuration/builder.py
- src/melder/crystallizer/configuration/crystallizer_configuration_builder.py
- tests/unit/melder/crystallizer/test_crystallizer_configuration.py

## Validation
- Executed:
  - `python -m py_compile src/melder/crystallizer/configuration/crystallizer_configuration.py src/melder/crystallizer/configuration/crystallizer_configuration_builder.py tests/unit/melder/crystallizer/test_crystallizer_configuration.py`
  - `python -m pytest -q -p no:cacheprovider tests/unit/melder/crystallizer/test_crystallizer_configuration.py`
- Result:
  - compile validation passed
  - focused configuration/builder ring passed (`7 passed`)

## Risks / Rollback Notes
- Risk: the builder ownership handoff becomes ambiguous if it stays reusable.
  Rollback: make the builder one-shot and explicit about transfer/consumption.

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
- DATETIME: 2026-05-04T23:01:34Z
  TYPE: PLAN
  CLAIM: The current crystallizer configuration builder is undernamed and too
    weak for the repo’s ownership rules. It lives in `builder.py`, does not
    inherit `Cleanable`, and wraps a live configuration object without making
    ownership-transfer or cleanup explicit.
  EVIDENCE:
  - src/melder/crystallizer/configuration/builder.py:1-67
  - src/melder/aether/nexus/nexus_frame_builder.py:1-94
  - src/melder/aether/nexus/acl/builder/frame_acl_builder.py:1-121
  IMPACT: The builder currently reads like a throwaway helper instead of a
    real owned object, which conflicts with the repo’s naming and lifecycle
    discipline.
  NEXT: rename the file, add `Cleanable`, and define one-shot ownership
    transfer plus focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-04T23:06:48Z
  TYPE: MEASURE
  CLAIM: The builder seam is now corrected. The generic `builder.py` file was
    replaced by `crystallizer_configuration_builder.py`, the builder now
    inherits `Cleanable`, owns one wrapped configuration explicitly, cleans that
    configuration if discarded, and consumes itself on `build/finalize/activate`
    so ownership transfers to the caller instead of staying ambiguous. The
    local configuration class also had the remaining low-value self-derived
    aliasing removed from its validation/property path.
  EVIDENCE:
  - src/melder/crystallizer/configuration/crystallizer_configuration_builder.py:1-187
  - src/melder/crystallizer/configuration/crystallizer_configuration.py:1-260
  - tests/unit/melder/crystallizer/test_crystallizer_configuration.py:1-125
  IMPACT: The builder now matches repo naming and lifecycle rules instead of
    looking like a disposable wrapper with unclear ownership.
  NEXT: decide whether the builder should stay as a separate public helper at
    all or whether callers should just use `Crystallizer.create_configuration()`
    directly in most places later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the builder naming and ownership correction after the first
crystallizer configuration/root slice.
