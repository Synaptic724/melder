# Epic: Descriptor Payload Contract And ACL View Spine
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the descriptor payload contract investigation/proposal epic and handed the work off to downstream implementation epics.


## Metadata
- Epic ID: EPIC-2026-04-05-descriptor-payload-contract-and-acl-view-spine
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T19:35:48Z
- Updated: 2026-04-09T21:59:36Z
- Target Window: 2026-Q2
- Related Program/Initiative: ACL / Descriptor / Viewer contract stabilization

## Problem / Opportunity
The spell-profile substrate is now stable enough to support a stronger contract
spine, but the upper layers still do not have one clean generalized model for:
- descriptor-safe payload publication
- event transport
- record storage
- ACL/view consumption

Today the runtime is close, but not locked:
- `SpellRecord` still reflects older field-splitting decisions
- descriptor/event/profile contracts are still being reasoned about informally
- ACL view design is blocked on what payload/record contract it should consume

If we do not lock this now, the descriptor, ACL, and viewer systems will each
start inventing their own near-duplicate contract language.

## MRP Alignment (Most Reasonable Product)
This is MRP-critical because the descriptor/payload/event/ACL/view spine is a
core system boundary. If the contract is weak now, every later consumer will
inherit drift and the cleanup cost will compound.

## Ticket Contract
- ENTRY_GATE: the spell-profile substrate lane is closed and the user has
  explicitly redirected focus to the descriptor/event/payload/ACL contract
  spine.
- EXECUTION_BOUNDARY: descriptor payload interfaces, record contract design,
  event transport design, and the ACL/view consumption model.
- DEPENDENCIES:
  - tickets/tasks/completed/2026-04-05_implement_spell_examiner_registry_rebuild_task.md
  - tickets/epics/2026-04-02_rift_profile_surface_and_access_model_epic.md
  - tickets/stories/2026-04-02_profile_contracts_and_access_boundaries_story.md
- EXIT_GATE: one accepted contract model exists for runtime profile export,
  event transport, record storage, and ACL/view consumption.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the contract boundary still
  has multiple plausible ownership models after investigation.

## Goals (Outcomes)
- Define a clean descriptor payload contract family.
- Define how spell/conduit/frame publication events carry payloads.
- Define how record classes store payloads without flattening them into
  duplicated top-level fields.
- Define the minimum descriptor baseline that ACL/view consumers can rely on.
- Define the concrete next implementation sequence for the descriptor payload
  and ACL view lane.

## Non-Goals (Explicit Exclusions)
- Full viewer implementation.
- Full conduit/frame payload implementation.
- Event bus/scheduler redesign.
- MutationResearch changes.

## Scope Boundaries
- In scope:
  - spell descriptor payload contract
  - conduit/frame payload contract direction
  - record interface direction
  - event transport contract
  - ACL/view consumption boundary
- Out of scope:
  - final UI rendering
  - workstation behavior
  - broad repo-wide refactors outside the descriptor/payload lane

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the spell-profile substrate is now strong enough that the
  next system-level contract problem is the descriptor/event/payload/ACL spine.

## Success Metrics
- One accepted spell payload contract exists.
- The descriptor/record/event/ACL relationship can be explained without
  ambiguity.
- Follow-up implementation tasks are concrete and scoped.

## Requirements (Functional + Non-Functional)
- Functional:
  - descriptor payload interfaces
  - record storage model
  - event envelope model
  - ACL/view consumption contract
- Non-functional:
  - no lossy spell payload publication
  - extensible for future conduit/frame payloads
  - low duplication
  - interface-first, Protocol-based boundaries

## Constraints / Assumptions
- `SpellDetailedProfile` is the current rich spell-facing baseline.
- `general` remains a thinner runtime profile and may not publish.
- Descriptor records should remain in place as the canonical storage objects.
- Payloads should stay descriptor-safe and avoid live runtime back-references.

## Dependencies / External References
- `src/melder/aether/nexus/frame_descriptor/`
- `src/melder/aether/nexus/frame_descriptor_manager.py`
- `src/melder/spellbook/spell_crafter/spell_examiner/profiles/`
- `src/melder/utilities/interfaces/interfaces.py`

## Milestones (Track Progress)
- [ ] Milestone 1: Investigate current payload/event/record usage and lock the contract options.
- [ ] Milestone 2: Propose and accept the descriptor payload + ACL view consumption model.
- [ ] Milestone 3: Implement the accepted record/payload contract changes.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-05-descriptor-payload-contract-investigation - investigate and propose the contract
- [ ] Story: STORY-2026-04-05-descriptor-payload-contract-implementation - implement the accepted contract
- [ ] Story: STORY-2026-04-05-conduit-and-frame-record-payload-rollout - widen the payload contract into conduit/frame records

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-04-05-descriptor-payload-contract-investigation
- [ ] Task: Complete story STORY-2026-04-05-descriptor-payload-contract-implementation
- [ ] Task: Complete story STORY-2026-04-05-conduit-and-frame-record-payload-rollout
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- One accepted contract exists for:
  - payload interfaces
  - event transport
  - record storage
  - ACL/view consumption
- The implementation lane is completed and accepted.

## Risks / Mitigations
- Risk: records, events, and ACLs each invent separate payload models.
  - Mitigation: make the payload contract explicit before more implementation.
- Risk: spell payload publication becomes lossy again.
  - Mitigation: keep the rich spell profile shape as the baseline floor.

## Validation / Test Approach
- Investigation phase: source-evidence review and contract proposal.
- Implementation phase: focused runtime, record, and descriptor tests.

## Rollout / Adoption Plan
- Investigate current state.
- Propose contract.
- Implement spell-first payload/record changes.
- Return to ACL view configuration on top of that contract.

## Open Questions
- Whether `SpellRecord` should store only `payload` or keep some duplicated
  core top-level profile fields.
- Whether conduit/frame payloads should land in the same implementation slice
  or remain design-only for now.

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-05T19:35:48Z
  TYPE: PLAN
  CLAIM: The next coherent contract lane is the descriptor/event/payload/ACL
    spine. The spell-profile substrate is now strong enough that the record and
    ACL layers can stop guessing and instead lock one export/store/consume
    model.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-05_implement_spell_examiner_registry_rebuild_task.md:1-196
  - codex/context_compass/attention_board.md:25-64
  IMPACT: We can now turn the recent discussion into one real program lane
    instead of continuing with ad hoc contract talk.
  NEXT: create the investigation story/task and route the active ACL row down
    into that investigation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T21:25:04Z
  TYPE: DECISION
  CLAIM: The epic now has a second implementation story. The spell-first
    payload contract is landed, but the remaining flat `ConduitRecord` and
    `FrameRecord` shapes would force the next ACL/view lane to consume mixed
    contracts. The follow-up path is to widen the same payload model into those
    records before ACL/view implementation.
  EVIDENCE:
  - codex/context_compass/attention_board.md:28-28
  - codex/context_compass/tickets/tasks/2026-04-05_implement_spell_record_payload_contract_task.md:201-201
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:29-29
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:29-29
  IMPACT: The epic sequence is now:
    spell-first payload contract -> conduit/frame record payload rollout ->
    ACL/view configuration.
  NEXT: route the new rollout story/task and implement the follow-up slice.
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
This epic exists to lock the descriptor/event/payload/ACL contract spine before
the ACL view implementation hardens around the wrong model.

