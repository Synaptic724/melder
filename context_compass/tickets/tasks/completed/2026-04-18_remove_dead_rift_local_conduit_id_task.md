# Task: Remove Dead Rift Local Conduit Id Surface
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-remove-dead-rift-local-conduit-id
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T12:12:27Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Remove the dead `local_conduit_id` surface from `Rift`, `Nexus`, and the
public interfaces now that the field is only stored/exposed and does not drive
any live runtime behavior.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to strip out `local_conduit_id` first,
  and the investigation confirmed it is dead surface rather than active runtime
  state.
- EXECUTION_BOUNDARY: `Rift`, `Nexus`, interfaces, and the directly affected
  unit test only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/nexus.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
- EXIT_GATE: `local_conduit_id` is gone from the live runtime surface with no
  backward-compat shim and the focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a hidden runtime use appears
  during implementation and widens the blast radius beyond this bounded slice.

## Scope Boundaries
- In scope:
  - `Rift` storage/property removal
  - `Nexus.create_rift(...)` signature cleanup
  - interface cleanup
  - directly affected unit assertion
- Out of scope:
  - default-frame cleanup
  - event-system replacement
  - source-doc rewrites unless required by compile/test fallout

## Steps / Checklist
- [ ] Remove `local_conduit_id` from `Rift`.
- [ ] Remove `local_conduit_id` from `Nexus.create_rift(...)`.
- [ ] Remove `local_conduit_id` from the public interfaces.
- [ ] Update the directly affected test.
- [ ] Validate the focused ring.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- cleaned dead-field runtime surface
- focused validation evidence

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: a hidden consumer still expects the dead field even though no live
  behavior was found during investigation.
- Rollback: keep the slice bounded and fail fast instead of adding a
  compatibility alias.

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
- DATETIME: 2026-04-18T12:12:27Z
  TYPE: FACT
  CLAIM: `local_conduit_id` is dead surface in the current live model. It is
    accepted by `Nexus.create_rift(...)`, stored on `Rift`, exposed by
    `Rift.local_conduit_id`, and asserted once in a unit test, but no live
    runtime path uses it for frame targeting, viewer creation, workstation
    behavior, or command behavior.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:636-705
  - src/melder/aether/nexus/rift/rift.py:109-201
  - src/melder/aether/nexus/rift/rift.py:388-397
  - src/melder/utilities/interfaces/interfaces.py:7563-7567
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:408-414
  IMPACT: We can remove it cleanly without widening into other Rift design
    questions.
  NEXT: patch the runtime surface and direct test, then validate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T12:41:23Z
  TYPE: FACT
  CLAIM: The dead field removal is now implemented with no compatibility
    layer. `local_conduit_id` is removed from `Rift`, from
    `Nexus.create_rift(...)`, from the public interface surface, and from the
    one direct unit assertion that still mentioned it.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:102-203
  - src/melder/aether/nexus/rift/rift.py:352-410
  - src/melder/aether/nexus/nexus.py:631-707
  - src/melder/utilities/interfaces/interfaces.py:7536-7563
  - src/melder/utilities/interfaces/interfaces.py:7806-7822
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:408-414
  IMPACT: The Rift surface is cleaner and the remaining discussion about frame
    defaults is no longer mixed with a fake conduit-hosting field.
  NEXT: record the focused validation result and return the task for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T12:41:23Z
  TYPE: MEASURE
  CLAIM: The focused dead-field removal ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/nexus.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 124 passed
  IMPACT: The removal is stable enough to review immediately without widening
    the lane.
  NEXT: return the task for acceptance and then continue the frame-default
    discussion cleanly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the small bounded runtime cleanup for removing the dead
`local_conduit_id` surface from the live Rift model.