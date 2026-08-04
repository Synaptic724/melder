# Story: Descriptor Payload Contract Implementation

## Metadata
- Story ID: STORY-2026-04-05-descriptor-payload-contract-implementation
- Epic: EPIC-2026-04-05-descriptor-payload-contract-and-acl-view-spine
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-04-05T20:54:09Z
- Updated: 2026-04-05T20:54:09Z

## User Narrative
As the project owner, I want the descriptor record contract implemented on the
spell lane first, so that ACL/view work can consume one coherent payload model
instead of split spell-profile fields.

## Value / MRP Alignment
This story hardens the first real descriptor payload boundary before ACL/view
implementation learns the wrong record semantics.

## Ticket Contract
- ENTRY_GATE: the investigation story has captured the current state and the
  proposal task has documented one accepted contract.
- EXECUTION_BOUNDARY: spell-first record/payload implementation only.
- DEPENDENCIES:
  - STORY-2026-04-05-descriptor-payload-contract-investigation
  - TASK-2026-04-05-propose-descriptor-payload-and-acl-view-contract
  - TASK-2026-04-05-implement-spell-record-payload-contract
- EXIT_GATE: spell descriptor payload interfaces and spell-record storage use
  the accepted payload contract, and focused validation passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the implementation forces
  conduit/frame payload rollout earlier than planned.

## Requirements (Functional)
- add descriptor payload interfaces
- add record interfaces where the code should depend on the contract rather than
  concrete spell-record classes
- move `SpellRecord` off split profile slots and onto one payload field
- update publish/store/consumer code on the spell lane

## Requirements (Non-Functional)
- no lossy spell payload publication
- interface-first, Protocol-based boundaries
- minimal blast radius outside the spell lane

## Scope Boundaries
- In scope:
  - spell descriptor payload interfaces
  - `SpellRecord` contract
  - spell publish/store/consume path
- Out of scope:
  - conduit/frame payload implementation
  - viewer implementation
  - event bus implementation

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: this implementation story is staged behind the
  investigation/proposal lane and is ready once the contract is accepted.

## Dependencies / Related Work
- tickets/epics/2026-04-05_descriptor_payload_contract_and_acl_view_epic.md
- tickets/stories/2026-04-05_descriptor_payload_contract_investigation_story.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-05-implement-spell-record-payload-contract - implement the spell-first payload contract
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- one spell descriptor payload contract exists in code
- `SpellRecord` stores one payload field instead of split profile shards
- focused validation passes

## Validation / Test Plan
- focused descriptor/spell publish/store tests
- focused ACL/view-adjacent spell record tests

## UX / API / Data Notes
- the spell payload contract must at least match the current rich spell-facing
  profile floor

## Risks / Mitigations
- Risk: over-widening into conduit/frame payload rollout.
  Mitigation: keep this story spell-first.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- whether the public publish-event abstraction should remain design-only in this
  story

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-05T20:54:09Z
  TYPE: PLAN
  CLAIM: This story is intentionally staged behind the investigation/proposal
    lane. The spell-first implementation task should only start once the
    descriptor payload contract is accepted.
  EVIDENCE:
  - tickets/tasks/2026-04-05_propose_descriptor_payload_and_acl_view_contract_task.md:1-84
  IMPACT: We can separate the contract decision from the code rollout cleanly.
  NEXT: complete the proposal task and then activate the spell-first
    implementation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story exists to implement the accepted spell-first descriptor payload
contract once the investigation/proposal lane finishes.
