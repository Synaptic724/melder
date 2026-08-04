# Story: Investigate And Refactor Rift Per-Frame Contracts
- Completed: 2026-04-18T11:33:52Z
- Summary: Completed the investigate-first per-frame contract story after mapping the live `Nexus`/`Rift` implications, landing the dict-backed Rift contract model, and getting explicit user acceptance.

## Metadata
- Story ID: STORY-2026-04-18-investigate-and-refactor-rift-per-frame-contracts
- Epic: EPIC-2026-04-18-rift-per-frame-contract-refactor
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T11:02:19Z
- Updated: 2026-04-18T11:33:52Z

## User Narrative
As the maintainer of Rift, I want one contract per frame instead of one
aggregate contract holding all frames, so that the contract style stays
consistent and the per-frame wiring is easier to reason about.

## Value / MRP Alignment
This strengthens the finishing-pass structural coherence of Rift without
expanding into unrelated event/codegen/space refactors.

## Ticket Contract
- ENTRY_GATE: the epic is active and the user explicitly requested an
  investigate-first plan before implementation.
- EXECUTION_BOUNDARY: investigate then refactor only the frame-contract shape
  on `Rift`; no unrelated surface changes.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_investigate_rift_per_frame_contract_refactor_implications_task.md
  - tickets/tasks/2026-04-18_implement_rift_dict_of_per_frame_contracts_task.md
- EXIT_GATE: the investigation is accepted, the refactor lands, and the
  focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current `Nexus` or tests
  still require the aggregate shape in a way that changes the plan.

## Requirements (Functional)
- Investigate all current dependencies on the aggregate `FrameLinkContract`.
- Produce an explicit plan before implementation.
- Refactor `Rift` to hold a dict of per-frame contracts and keep frame-targeting
  behavior working.

## Requirements (Non-Functional)
- No backward-compat layer.
- Keep the change bounded and reviewable.

## Scope Boundaries
- In scope:
  - `Rift` frame contract storage
  - `FrameLinkContract` single-frame responsibility
  - `Nexus`/test implications directly related to the split
- Out of scope:
  - one-space-per-rift
  - event system
  - codegen system

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the investigate-first refactor lane is explicitly staged.

## Dependencies / Related Work
- tickets/tasks/2026-04-14_investigate_codegen_rift_space_implementation_task.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-18-investigate-rift-per-frame-contract-refactor-implications
      - map current code/test implications before edits
- [x] Task: TASK-2026-04-18-implement-rift-dict-of-per-frame-contracts
      - perform the contract split after plan approval
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The investigation plan is accepted before runtime edits.
- `Rift` uses a dict of per-frame contracts.
- The focused validation ring is green.

## Validation / Test Plan
- focused Rift/Nexus contract ring after implementation

## UX / API / Data Notes
- This is structural runtime cleanup, not a user-facing feature.

## Risks / Mitigations
- Risk: hidden reliance on aggregate default-frame behavior.
  Mitigation: investigate `Nexus` and tests first.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Where should the default target frame live once contracts are split:
  on `Rift` only, or inside the per-frame contract map plus a default key?

## Decision Log
- 2026-04-18T11:02:19Z: treat this as a strict investigate-then-implement
  story, not an ad hoc runtime edit.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-18T11:02:19Z
  TYPE: PLAN
  CLAIM: The story is intentionally narrow: per-frame contract shape only.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:16-18
  - src/melder/aether/nexus/rift/rift.py:194-201
  IMPACT: We can investigate the current contract dependencies without mixing
    them with the event-system or one-space-per-rift discussions.
  NEXT: activate the investigation task and map the `Nexus` and test
    implications first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T11:33:52Z
  TYPE: DECISION
  CLAIM: This story is complete. The investigation task mapped the live
    dependency surface, the implementation task landed the per-frame contract
    shape with no backward-compat shim, and the user approved closing the lane.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-18_investigate_rift_per_frame_contract_refactor_implications_task.md:1-112
  - tickets/tasks/completed/2026-04-18_implement_rift_dict_of_per_frame_contracts_task.md:1-133
  - user_instruction: "yeah close the existing epic you did good"
  IMPACT: The story can leave the active Rift finishing queue and move to the
    completed shelf.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story owns the investigate-first refactor from one aggregate frame
contract to one contract per frame.
