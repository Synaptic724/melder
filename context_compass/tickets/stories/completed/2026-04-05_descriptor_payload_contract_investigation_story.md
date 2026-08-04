# Story: Descriptor Payload Contract Investigation
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the descriptor payload contract investigation/proposal lane and handed it off to later implementation slices.


## Metadata
- Story ID: STORY-2026-04-05-descriptor-payload-contract-investigation
- Epic: EPIC-2026-04-05-descriptor-payload-contract-and-acl-view-spine
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T19:35:48Z
- Updated: 2026-04-09T21:59:36Z

## User Narrative
As the project owner, I want the descriptor payload and record contract
investigated properly, so that the ACL/view layer can be built on one stable
contract instead of multiple overlapping guesses.

## Value / MRP Alignment
This story protects the next MRP boundary for ACL/view work. If the descriptor
payload spine is vague, the viewer and ACL layers will drift immediately.

## Ticket Contract
- ENTRY_GATE: the new epic is routed and the spell-profile substrate lane is
  complete enough to support contract investigation.
- EXECUTION_BOUNDARY: investigation and proposal only; no runtime contract
  implementation in this story.
- DEPENDENCIES:
  - EPIC-2026-04-05-descriptor-payload-contract-and-acl-view-spine
  - TASK-2026-04-05-investigate-descriptor-payload-and-record-contract
  - TASK-2026-04-05-propose-descriptor-payload-and-acl-view-contract
- EXIT_GATE: the current state is investigated and one evidence-backed proposed
  contract is documented for user review.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if multiple materially different
  contract models remain plausible after investigation.

## Requirements (Functional)
- Investigate current spell/conduit/frame record composition.
- Investigate current publish event paths.
- Investigate how ACL/view consumers should read the payloads.
- Produce one proposed contract model.

## Requirements (Non-Functional)
- Evidence-first.
- No premature implementation.
- Interface-first with Protocol boundaries where appropriate.

## Scope Boundaries
- In scope:
  - current descriptor records
  - publish event paths
  - payload interface needs
  - ACL/view contract consumption needs
- Out of scope:
  - full implementation
  - conduit/frame payload rollout

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the descriptor payload contract lane now needs a bounded
  investigation slice before implementation starts.

## Dependencies / Related Work
- tickets/epics/2026-04-05_descriptor_payload_contract_and_acl_view_epic.md
- tickets/tasks/completed/2026-04-05_implement_spell_examiner_registry_rebuild_task.md
- tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-05-investigate-descriptor-payload-and-record-contract - inspect the live state
- [ ] Task: TASK-2026-04-05-propose-descriptor-payload-and-acl-view-contract - write the proposed contract
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The current state is investigated with evidence.
- One concrete proposed contract exists for user review.
- The next implementation task is explicit.

## Validation / Test Plan
- Investigation and proposal only.

## UX / API / Data Notes
- Spell payload should remain rich enough for later ACL/view work.
- Descriptor records should not be flattened thoughtlessly.

## Risks / Mitigations
- Risk: proposal drifts into implementation by habit.
  Mitigation: keep this story investigation/proposal only.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether records store one `payload` or keep any duplicated profile shards.
- How far conduit/frame payloads should be formalized in the first cut.

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
  CLAIM: This story should stay on investigation/proposal only. The next task
    is to inspect the live descriptor records, event publication paths, and ACL
    consumer needs, then return one proposed contract before implementation.
  EVIDENCE:
  - user_instruction: "make an epic, investigate, then propose and then implement please go do that stuff"
  IMPACT: We can separate thinking from implementation cleanly instead of
    mixing design and code edits again.
  NEXT: create and route the investigation task.
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
This story exists to investigate and propose the descriptor/event/payload
contract before implementation starts.

