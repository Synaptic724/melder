# Task: Propose Descriptor Payload And ACL View Contract
- Completed: 2026-04-09T21:59:36Z
- Summary: Turned the descriptor payload investigation into a concrete contract proposal for the later implementation lanes.


## Metadata
- Task ID: TASK-2026-04-05-propose-descriptor-payload-and-acl-view-contract
- Story: STORY-2026-04-05-descriptor-payload-contract-investigation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T19:35:48Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Turn the investigation findings into one concrete proposed contract for:
- descriptor payload interfaces
- event transport
- record storage
- ACL/view consumption

## Ticket Contract
- ENTRY_GATE: the investigation task has documented the current state with
  evidence.
- EXECUTION_BOUNDARY: proposal only; no runtime implementation in this task.
- DEPENDENCIES:
  - tickets/tasks/2026-04-05_investigate_descriptor_payload_and_record_contract_task.md
- EXIT_GATE: one evidence-backed contract proposal exists for user review.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if multiple materially different
  proposals still appear equally valid after investigation.

## Scope Boundaries
- In scope:
  - proposed payload interfaces
  - proposed event envelope contract
  - proposed record storage model
  - proposed ACL/view consumption model
- Out of scope:
  - implementation
  - broad viewer rewrite

## State Transition Event
- from_state: ready
- to_state: review
- transition_reason: the current-state investigation is now strong enough that
  one concrete proposal can be written for review.

## Steps / Checklist
- [ ] Read the investigation findings.
- [ ] Write one concrete contract proposal.
- [ ] Record risks and implementation implications.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one proposed descriptor/event/payload/ACL contract

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-05_propose_descriptor_payload_and_acl_view_contract_task.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content codex/context_compass/tickets/tasks/2026-04-05_investigate_descriptor_payload_and_record_contract_task.md`

## Risks / Rollback Notes
- Risk: proposal widens into implementation or drifts from the investigation evidence.
  Rollback: keep proposal lines tied directly to investigation evidence.

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
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T19:35:48Z
  TYPE: PLAN
  CLAIM: This task should not start until the current-state investigation is
    documented. Once that exists, this task becomes the place for one coherent
    proposal rather than another mixed investigation/implementation pass.
  EVIDENCE:
  - tickets/tasks/2026-04-05_investigate_descriptor_payload_and_record_contract_task.md:1-84
  IMPACT: The lane can stay disciplined: investigate first, then propose.
  NEXT: wait for the investigation task to produce the current-state findings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-05T20:54:09Z
  TYPE: DECISION
  CLAIM: The clean spell-first proposal is:
    1) keep `FrameDescriptor`, `SpellRecord`, `ConduitRecord`, and `FrameRecord`
       as the canonical descriptor storage objects instead of rebuilding the
       whole descriptor aggregate;
    2) add descriptor payload interfaces using Protocols, with a spell-first
       floor:
       - `IDescriptorPayload`
       - `ISpellDescriptorPayload`
       - later `IConduitDescriptorPayload` / `IFrameDescriptorPayload` when those
         richer payloads are actually needed;
    3) define the spell descriptor baseline so it matches at least the current
       rich spell-facing profile floor, but treat the runtime detailed profile
       as the *source shape*, not the raw stored object, because the nested
       binding profile still carries `original_object`;
    4) add a sanitized spell descriptor payload contract and concrete
       spell-first payload implementation that strips runtime object references
       while preserving the current rich spell-facing shape;
    5) change `SpellRecord` from split profile shards
       (`binding_profile`, `resolution_profile`, `detailed_profile`) to one
       `payload` field plus its existing identity/ownership fields;
    6) leave `ConduitRecord` and `FrameRecord` structurally flat for now and
       introduce payload fields there only when richer conduit/frame publication
       is actually needed;
    7) treat the current direct manager publication calls as the effective
       synchronous event boundary for now instead of introducing real event
       classes in the same slice;
    8) let ACL/view consume record payloads from the descriptor, not raw spell
       objects and not split profile shards.
  EVIDENCE:
  - tickets/tasks/2026-04-05_investigate_descriptor_payload_and_record_contract_task.md:86-97
  - tickets/tasks/2026-04-05_investigate_descriptor_payload_and_record_contract_task.md:98-111
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:10-131
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:10-91
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:10-124
  - src/melder/aether/nexus/frame_descriptor_manager.py:256-270
  - src/melder/aether/nexus/frame_descriptor_manager.py:318-328
  - src/melder/aether/nexus/frame_descriptor_manager.py:401-430
  - tickets/tasks/completed/2026-04-05_implement_spell_examiner_registry_rebuild_task.md:66-140
  IMPACT: This keeps the change set surgical and extensible without leaking live
    runtime object references into the descriptor layer. We get one strong spell
    payload spine immediately, we do not overbuild conduit/frame payloads before
    they are needed, and ACL/view work gets one clean thing to consume.
  NEXT: activate the spell-first implementation task and cut `SpellRecord` to a
    payload-based contract first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to hold the proposed descriptor/event/payload/ACL contract
once the investigation is complete.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

