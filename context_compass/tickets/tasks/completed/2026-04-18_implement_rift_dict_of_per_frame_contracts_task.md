# Task: Implement Rift Dict Of Per-Frame Contracts
- Completed: 2026-04-18T11:33:52Z
- Summary: Completed the per-frame contract refactor after splitting `FrameLinkContract`, updating `Rift` and the direct `Nexus` consumers, and passing the focused validation ring.

## Metadata
- Task ID: TASK-2026-04-18-implement-rift-dict-of-per-frame-contracts
- Story: STORY-2026-04-18-investigate-and-refactor-rift-per-frame-contracts
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T11:02:19Z
- Updated: 2026-04-18T11:33:52Z

## Objective
Replace the aggregate `FrameLinkContract` shape with a dict of one
`FrameLinkContract` per targeted frame after the investigation plan is
accepted.

## Ticket Contract
- ENTRY_GATE: the investigation task is accepted and the implementation plan is
  explicit.
- EXECUTION_BOUNDARY: `Rift` frame-contract storage, `FrameLinkContract`
  single-frame responsibility, and the directly affected test/interface paths.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_investigate_rift_per_frame_contract_refactor_implications_task.md
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
  - src/melder/utilities/interfaces/interfaces.py
- EXIT_GATE: `Rift` holds a dict of per-frame contracts, validation is green,
  and no backward-compat shim was added.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the accepted investigation
  plan proves insufficient once implementation starts.

## Scope Boundaries
- In scope:
  - `Rift` contract storage refactor
  - `FrameLinkContract` single-frame refactor
  - direct interface/tests required by the split
- Out of scope:
  - event-system changes
  - one-space-per-rift changes
  - codegen changes

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the per-frame contract refactor is implemented and the
  focused contract/targeting ring is green without a compatibility shim.

## Steps / Checklist
- [x] Implement the per-frame contract dict on `Rift`.
- [x] Refactor `FrameLinkContract` to one-frame responsibility.
- [x] Update directly affected interfaces/tests.
- [x] Validate the focused contract/targeting ring.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- per-frame contract dict on `Rift`
- one-frame `FrameLinkContract`
- focused validation evidence

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
- src/melder/utilities/interfaces/interfaces.py

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Rollback Notes
- Refactor may ripple through viewer creation and target-frame logic.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

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
- DATETIME: 2026-04-18T11:14:34Z
  TYPE: PLAN
  CLAIM: The implementation will stay small and structural. `FrameLinkContract`
    will become one-frame-only, `Rift` will hold a dict of them keyed by frame
    name, `Rift` will preserve the aggregate query behavior that `Nexus`
    currently needs (`list_assigned_frame_names`, `default_target_frame_name`,
    per-frame selected contract lookup), and the directly affected interface and
    unit tests will be updated in the same pass. There will be no backward-
    compatibility shim.
  EVIDENCE:
  - tickets/tasks/2026-04-18_investigate_rift_per_frame_contract_refactor_implications_task.md:89-113
  IMPACT: The refactor can now proceed without widening into the event system,
    one-space-per-rift, or codegen work.
  NEXT: patch `FrameLinkContract`, then patch `Rift`, then patch the direct
    `Nexus`/interface/test consumers and validate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T11:22:27Z
  TYPE: FACT
  CLAIM: The refactor is now implemented. `FrameLinkContract` is one-frame-
    only, `Rift` holds a dict of per-frame contracts, `Nexus` viewer creation
    consumes `Rift` aggregate queries instead of the old aggregate contract
    object, and the directly affected unit tests were rewritten to the new
    shape. No backward-compat layer was added.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:14-273
  - src/melder/aether/nexus/rift/rift.py:76-92
  - src/melder/aether/nexus/rift/rift.py:184-206
  - src/melder/aether/nexus/rift/rift.py:407-461
  - src/melder/aether/nexus/rift/rift.py:499-566
  - src/melder/aether/nexus/nexus.py:1601-1638
  - src/melder/aether/nexus/nexus.py:1667-1690
  - src/melder/aether/nexus/nexus.py:1848-1886
  - src/melder/utilities/interfaces/interfaces.py:7554-7594
  - tests/unit/melder/aether/test_frame_link_contract_profiles.py:1-205
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:339-363
  - tests/unit/melder/aether/test_nexus.py:3585-3763
  IMPACT: The contract style now matches your intended per-frame shape and the
    aggregate contract object is gone from the live Rift runtime.
  NEXT: record the green validation result and return the lane for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T11:22:27Z
  TYPE: MEASURE
  CLAIM: The focused per-frame contract refactor validation ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/frame_link/frame_link_contract.py src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/nexus.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 134 passed
  IMPACT: The refactor is stable enough to return for acceptance instead of
    widening the lane further.
  NEXT: return the story/task/epic for review and decide whether to close them
    or continue directly into the next Rift structural issue.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T11:33:52Z
  TYPE: DECISION
  CLAIM: This implementation task is complete. The focused validation ring was
    already green, and the user explicitly accepted the result and told us to
    close the lane.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 134 passed
  - user_instruction: "yeah close the existing epic you did good"
  IMPACT: The task can move out of review and into the completed task shelf.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the actual implementation of the per-frame contract split after
the investigation plan is approved.
