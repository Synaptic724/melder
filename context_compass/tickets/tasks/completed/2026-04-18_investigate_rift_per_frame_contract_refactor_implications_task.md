# Task: Investigate Rift Per-Frame Contract Refactor Implications
- Completed: 2026-04-18T11:33:52Z
- Summary: Completed the investigate-first pass by mapping the exact aggregate-contract dependencies in `Rift`, `Nexus`, and the focused unit tests before the refactor landed.

## Metadata
- Task ID: TASK-2026-04-18-investigate-rift-per-frame-contract-refactor-implications
- Story: STORY-2026-04-18-investigate-and-refactor-rift-per-frame-contracts
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T11:02:19Z
- Updated: 2026-04-18T11:33:52Z

## Objective
Map the exact `Nexus`, `Rift`, `FrameLinkContract`, and test implications of
changing from one aggregate frame contract to a dict of one-contract-per-frame
before any implementation edits.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested an investigate-first plan before
  implementation.
- EXECUTION_BOUNDARY: investigation and planning only; no runtime/test edits.
- DEPENDENCIES:
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
  - src/melder/utilities/interfaces/interfaces.py
- EXIT_GATE: the exact affected surfaces and the implementation plan are
  explicit enough to propose before code edits.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the aggregate contract shape
  is still required by a deeper runtime assumption.

## Scope Boundaries
- In scope:
  - current aggregate contract shape
  - `Nexus` usage of `Rift` frame contract state
  - `Rift` frame targeting and viewer creation implications
  - visible test contract implications
- Out of scope:
  - actual refactor
  - unrelated event/codegen work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested a staged investigate-first plan.

## Steps / Checklist
- [x] Read the current `Nexus` paths that depend on `Rift` frame contract state.
- [x] Read `Rift` frame-targeting and viewer creation paths.
- [x] Read the current `FrameLinkContract` aggregate shape carefully.
- [x] Identify the visible test/interface implications.
- [x] Produce the implementation plan for approval.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed implication inventory
- concrete implementation plan

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-18_investigate_rift_per_frame_contract_refactor_implications_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Rollback Notes
- Risk: aggregate-frame assumptions are deeper than expected.
  Rollback: keep this task investigation-only and do not edit runtime code
  until the plan is accepted.

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
- DATETIME: 2026-04-18T11:02:19Z
  TYPE: PLAN
  CLAIM: This investigation exists to map the implications of changing
    `FrameLinkContract` from one aggregate object to one-contract-per-frame in
    a dict before any implementation begins.
  EVIDENCE:
  - user_instruction: "make sure its in a dict and the framelinkcontract object just holds a SINGLE frame per contract"
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:31-43
  - src/melder/aether/nexus/rift/rift.py:194-201
  IMPACT: We can now reason from the real `Nexus` and `Rift` code paths instead
    of drifting through old artifact language.
  NEXT: read `Nexus`, `Rift`, and `FrameLinkContract` for the exact runtime
    implications, then return with the implementation plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T11:02:19Z
  TYPE: FACT
  CLAIM: The current aggregate contract shape is deeply assumed by both `Rift`
    and `Nexus`, but in a narrow, identifiable way. `Rift` stores exactly one
    `FrameLinkContract` on `_frame_link_contract`, uses it for:
    - frame membership (`has_frame`)
    - registration (`register_frame`)
    - default frame selection
    - selected view/command/codegen contract lookup
    `Nexus` viewer creation then consumes that aggregate object mainly through:
    - `list_frame_names()`
    - `default_frame_name`
    - `selected_contract_names_by_frame_name`
    - `get_selected_contract_names(frame_name)`
    The unit tests also assert this aggregate surface directly.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:193-201
  - src/melder/aether/nexus/rift/rift.py:430-526
  - src/melder/aether/nexus/nexus.py:1569-1636
  - src/melder/aether/nexus/nexus.py:1640-1689
  - src/melder/aether/nexus/nexus.py:1818-1883
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:31-43
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:120-123
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:208-278
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:342-362
  - tests/unit/melder/aether/test_nexus.py:3585-3757
  IMPACT: The refactor is feasible, but it is not a search-and-replace. We
    must replace one aggregate contract with a dict while preserving these four
    aggregate queries somewhere on `Rift`: assigned frame names, default frame,
    per-frame selected contracts, and per-frame selected-contract lookup.
  NEXT: propose a narrow implementation plan that changes the storage shape
    while keeping the outward behavior for viewer creation and current tests
    comprehensible.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T11:33:52Z
  TYPE: DECISION
  CLAIM: This investigation task is complete. Its deliverable was the live
    dependency map and accepted implementation plan, both of which were used
    directly by the landed refactor and then accepted by the user.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-18_implement_rift_dict_of_per_frame_contracts_task.md:1-133
  - user_instruction: "yeah close the existing epic you did good"
  IMPACT: The investigation task should move to completed status instead of
    staying open after its implementation successor is already landed.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the investigate-first planning pass for the per-frame contract
refactor.
