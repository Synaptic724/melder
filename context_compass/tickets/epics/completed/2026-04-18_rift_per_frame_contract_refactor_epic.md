# Epic: Refactor Rift To Per-Frame Contracts
- Completed: 2026-04-18T11:33:52Z
- Summary: Completed the bounded Rift contract-shape refactor after splitting `FrameLinkContract` to one frame per object, moving `Rift` to a dict of contracts, and proving the focused Rift/Nexus validation ring.

## Metadata
- Epic ID: EPIC-2026-04-18-rift-per-frame-contract-refactor
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T11:02:19Z
- Updated: 2026-04-18T11:33:52Z
- Target Window: 2026-04
- Related Program/Initiative: Rift runtime finishing pass

## Problem / Opportunity
Current `Rift` owns one aggregate `FrameLinkContract` that carries multiple
frame names plus per-frame selected ACL contract names. That shape conflicts
with the established contract style in the rest of the system and does not
match the intended architecture where one frame should have one contract and
the Rift should own a simple dictionary of those contracts.

## MRP Alignment (Most Reasonable Product)
The right MRP is not a broad Rift rewrite. It is one coherent contract shape:
- `Rift` holds a dict of per-frame contracts.
- each `FrameLinkContract` holds exactly one frame
- follow-on behavior can build from that simpler, more consistent base

This keeps the change structural and bounded instead of over-expanding the
Rift refactor.

## Ticket Contract
- ENTRY_GATE: the user explicitly directed a per-frame contract refactor lane
  and requested a staged investigate-first flow before any implementation.
- EXECUTION_BOUNDARY: investigate and later refactor the `Rift` frame-contract
  model only; no unrelated event/codegen/space changes in this lane.
- DEPENDENCIES:
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
  - src/melder/utilities/interfaces/interfaces.py
- EXIT_GATE: the story and tasks for the per-frame contract refactor are
  accepted and the board reflects the surviving live lane cleanly.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current `Nexus` or test
  contracts still require the aggregate contract shape.

## Goals (Outcomes)
- Understand the exact implications of moving from one aggregate frame contract
  to a dict of one-contract-per-frame.
- Produce a bounded implementation plan before code edits.
- Later land the refactor without hidden compatibility sludge.

## Non-Goals (Explicit Exclusions)
- one-space-per-rift refactor
- event-system redesign
- codegen-system implementation
- general `Rift` API cleanup beyond the contract split

## Scope Boundaries
- In scope:
  - `Rift` frame-contract storage model
  - `FrameLinkContract` responsibility shape
  - `Nexus` / viewer / test implications of the split
- Out of scope:
  - non-contract ownership shifts
  - unrelated room/workstation/codegen work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested an explicit epic/story/task lane and
  investigate-first plan before implementation.

## Success Metrics
- one evidence-backed implementation plan
- no hidden dependency on the aggregate contract shape

## Requirements (Functional + Non-Functional)
- Investigation must identify all code/test dependencies on the current
  aggregate contract shape.
- The plan must preserve truthful migration boundaries and avoid implicit
  backward compatibility.

## Constraints / Assumptions
- `FrameLinkContract` is currently aggregate by design and may have deeper
  dependencies in `Nexus` and tests.

## Dependencies / External References
- tickets/tasks/2026-04-14_investigate_codegen_rift_space_implementation_task.md

## Milestones (Track Progress)
- [x] Milestone 1: investigation and plan accepted
- [x] Milestone 2: per-frame contract refactor implemented and validated

## Stories (Required to Complete)
- [x] Story: STORY-2026-04-18-investigate-and-refactor-rift-per-frame-contracts
      - investigate and then implement the split to one contract per frame

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-04-18-investigate-and-refactor-rift-per-frame-contracts
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The investigation plan is accepted before implementation.
- The aggregate frame contract is replaced by a dict of per-frame contracts.
- The focused validation ring is green.

## Risks / Mitigations
- Risk: `Nexus` viewer/materialization logic assumes the aggregate contract.
  Mitigation: investigate those dependencies first and keep the refactor plan
  explicit before edits.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- focused unit/integration ring around Rift contracts and frame targeting

## Rollout / Adoption Plan
- investigate first
- propose plan
- implement after approval

## Open Questions
- Does `Nexus.create_frame_viewer_for_rift(...)` need a new contract access
  path once contracts become per-frame objects?

## Decision Log
- 2026-04-18T11:02:19Z: create a dedicated investigate-first lane instead of
  starting the contract split ad hoc.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-18T11:02:19Z
  TYPE: PLAN
  CLAIM: This epic exists to turn the frame-contract shape complaint into a
    bounded refactor lane instead of continuing to debate it from memory.
  EVIDENCE:
  - user_instruction: "the framelinkcontract object just holds a SINGLE frame per contract"
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:16-18
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:120-123
  IMPACT: We can now investigate the real `Nexus`/`Rift` implications before
    implementing anything.
  NEXT: stage the story/task, route the investigation on the board, and read
    the current code paths that depend on the aggregate contract shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T11:33:52Z
  TYPE: DECISION
  CLAIM: This epic is complete. The per-frame contract lane landed cleanly:
    `FrameLinkContract` is now one-frame-only, `Rift` owns a dict of those
    contracts, the direct `Nexus` consumers were updated, and the user accepted
    the result and explicitly told us to close the epic.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-18_investigate_rift_per_frame_contract_refactor_implications_task.md:1-112
  - tickets/tasks/completed/2026-04-18_implement_rift_dict_of_per_frame_contracts_task.md:1-133
  - user_instruction: "yeah close the existing epic you did good"
  IMPACT: The per-frame contract refactor no longer belongs in the active Rift
    lane and should move to the completed epic shelf.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the per-frame contract refactor lane for `Rift`.
