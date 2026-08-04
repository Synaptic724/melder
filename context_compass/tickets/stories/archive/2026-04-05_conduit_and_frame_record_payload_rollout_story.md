# Story: Conduit And Frame Record Payload Rollout

## Metadata
- Story ID: STORY-2026-04-05-conduit-and-frame-record-payload-rollout
- Epic: EPIC-2026-04-05-descriptor-payload-contract-and-acl-view-spine
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-04-05T21:25:04Z
- Updated: 2026-04-05T21:25:04Z

## User Narrative
As the project owner, I want the remaining descriptor records moved onto the
same payload model, so ACL/view work does not consume one spell payload record
shape and two flat legacy record shapes.

## Value / MRP Alignment
This is MRP-critical cleanup on the descriptor boundary. If conduit/frame stay
flat while spell moves to payloads, the upper layers will harden around mixed
contracts and the next ACL/view work will drift immediately.

## Ticket Contract
- ENTRY_GATE: the spell-first descriptor payload task is landed and in review,
  and the user has explicitly asked to continue the record-contract lane.
- EXECUTION_BOUNDARY: conduit/frame payload interfaces, record storage, and
  direct publish/store updates only.
- DEPENDENCIES:
  - STORY-2026-04-05-descriptor-payload-contract-implementation
  - TASK-2026-04-05-implement-spell-record-payload-contract
  - TASK-2026-04-05-implement-conduit-and-frame-record-payload-contract
- EXIT_GATE: `ConduitRecord` and `FrameRecord` both store one required payload
  field, the publish/store path uses those payloads, and focused validation
  passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the rollout forces a
  descriptor aggregate redesign or event-bus implementation.

## Requirements (Functional)
- add descriptor payload interfaces for conduit/frame payloads
- add record interface fields where code should depend on payload contracts
- move `ConduitRecord` and `FrameRecord` off flat detail fields and onto one
  payload field
- update the direct publish/store path in `FrameDescriptorManager`

## Requirements (Non-Functional)
- keep `FrameDescriptor` as the canonical aggregate
- no event-bus redesign
- no ACL/view implementation in this story
- keep identity/ownership keys stable while moving descriptive detail into
  payloads

## Scope Boundaries
- In scope:
  - conduit descriptor payload contract
  - frame descriptor payload contract
  - `ConduitRecord` and `FrameRecord` storage model
  - direct publish/store updates
- Out of scope:
  - ACL/view implementation
  - viewer runtime implementation
  - event bus implementation
  - `NexusFrameRecord` redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the spell-first payload contract is landed and the next
  accepted descriptor step is widening the same pattern into conduit/frame
  records.

## Dependencies / Related Work
- tickets/epics/2026-04-05_descriptor_payload_contract_and_acl_view_epic.md
- tickets/stories/2026-04-05_descriptor_payload_contract_implementation_story.md
- tickets/tasks/2026-04-05_implement_spell_record_payload_contract_task.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-05-implement-conduit-and-frame-record-payload-contract - implement the conduit/frame payload rollout
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- one conduit descriptor payload contract exists in code
- one frame descriptor payload contract exists in code
- `ConduitRecord` and `FrameRecord` store one payload field instead of flat
  descriptive fields
- focused validation passes

## Validation / Test Plan
- focused frame-descriptor record tests
- focused descriptor-manager publication tests
- no full-repo suite in this story by default

## UX / API / Data Notes
- keep record identity fields stable
- move descriptive conduit/frame state into payloads
- fail fast when a record payload is empty

## Risks / Mitigations
- Risk: widening this slice mutates `FrameDescriptor` ownership semantics.
  Mitigation: keep the aggregate intact and only change record payload shape.
- Risk: raw runtime references leak into conduit/frame payloads.
  Mitigation: keep payloads descriptor-safe and value-oriented.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- whether frame/conduit payload classes should expose only current flat fields
  or add profile-name/version metadata now

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-05T21:25:04Z
  TYPE: DECISION
  CLAIM: The spell-first payload slice is no longer the full record contract
    lane. `ConduitRecord` and `FrameRecord` still hold flat descriptive fields,
    `FrameDescriptorManager` still constructs those records directly from
    flattened values, and the active board already captured the next decision as
    "move into ACL view configuration or widen into conduit/frame payload
    rollout." The user has now chosen to continue the record rollout.
  EVIDENCE:
  - codex/context_compass/attention_board.md:28-28
  - codex/context_compass/tickets/tasks/2026-04-05_implement_spell_record_payload_contract_task.md:30-30
  - codex/context_compass/tickets/tasks/2026-04-05_implement_spell_record_payload_contract_task.md:38-38
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:29-29
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:29-29
  - src/melder/aether/nexus/frame_descriptor_manager.py:259-259
  - src/melder/aether/nexus/frame_descriptor_manager.py:321-321
  IMPACT: The descriptor lane now needs a second implementation story rather
    than widening the spell-first story past its stated contract.
  NEXT: create the follow-up implementation task plus patch-doc set, then move
    the conduit/frame records onto payloads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

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
This story exists to widen the descriptor payload rollout from spell-only into
conduit/frame records without redesigning the descriptor aggregate or jumping to
ACL/view implementation too early.
