# Task: Investigate Descriptor Payload And Record Contract
- Completed: 2026-04-09T21:59:36Z
- Summary: Captured the descriptor payload and record-contract current state that fed the later proposal and implementation lanes.


## Metadata
- Task ID: TASK-2026-04-05-investigate-descriptor-payload-and-record-contract
- Story: STORY-2026-04-05-descriptor-payload-contract-investigation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T19:35:48Z
- Updated: 2026-04-09T21:59:36Z

## Objective
Investigate the current live state of:
- descriptor record composition
- publish event paths
- spell profile publication
- ACL/view consumption needs

and document the current constraints clearly before writing the proposed
contract.

## Ticket Contract
- ENTRY_GATE: the new story is routed and the SpellExaminer/profile substrate
  lane is already complete enough to support descriptor-contract investigation.
- EXECUTION_BOUNDARY: investigation only across current records, events, and
  ACL/view contract surfaces.
- DEPENDENCIES:
  - src/melder/aether/nexus/frame_descriptor/
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/utilities/interfaces/interfaces.py
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/
- EXIT_GATE: one evidence-backed current-state picture exists for the records,
  events, and ACL/view consumption boundary.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the current code still
  supports multiple contradictory contract readings after direct source review.

## Scope Boundaries
- In scope:
  - spell/conduit/frame record shapes
  - current publish paths
  - profile interface needs
  - ACL/view consumer constraints
- Out of scope:
  - runtime implementation edits
  - viewer implementation
  - event bus implementation

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a proper investigate ->
  propose -> implement sequence for this lane.

## Steps / Checklist
- [ ] Inspect current record classes and manager publish paths.
- [ ] Inspect current event-style publication boundaries.
- [ ] Inspect current ACL/view consumer assumptions.
- [ ] Write current-state findings in `## Notes`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- evidence-backed current-state summary for descriptor payload work

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-05_investigate_descriptor_payload_and_record_contract_task.md
- codex/context_compass/attention_board.md

## Validation
- Not run.
- Recommended commands:
  - `Get-Content src/melder/aether/nexus/frame_descriptor/spell_record.py`
  - `Get-Content src/melder/aether/nexus/frame_descriptor_manager.py`

## Risks / Rollback Notes
- Risk: the investigation accidentally locks implementation decisions too early.
  Rollback: keep findings factual and move proposals into the proposal task only.

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
  CLAIM: The immediate work is to inspect the live descriptor records and
    publication path and separate what is actual code truth from what we have
    only been discussing conceptually.
  EVIDENCE:
  - user_instruction: "make an epic, investigate, then propose and then implement please go do that stuff"
  IMPACT: The next note should be a concrete current-state finding, not another
    design opinion.
  NEXT: inspect the current record classes, manager publication path, and ACL
    consumer assumptions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T19:35:48Z
  TYPE: FACT
  CLAIM: The current descriptor layer is still asymmetric. `SpellRecord` is
    already half-transitioned toward payload thinking because it stores rich
    spell-facing data in three profile-shaped slots:
    `binding_profile`, `resolution_profile`, and `detailed_profile`.
    But `ConduitRecord` and `FrameRecord` still store only flattened direct
    fields with no generalized payload concept at all. `FrameDescriptorManager`
    currently publishes those records directly, with spell publication already
    normalizing through the spell profile interfaces while conduit/frame
    publication still constructs the older field-only record objects. That
    means the cleanest next proposal is likely:
    - keep the record classes and `FrameDescriptor` aggregate in place
    - introduce a generalized `payload` concept on records
    - convert `SpellRecord` first from split profile slots to one payload field
    - leave conduit/frame payloads as design targets unless we explicitly widen
      scope
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:10-131
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:10-91
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:10-124
  - src/melder/aether/nexus/frame_descriptor_manager.py:256-270
  - src/melder/aether/nexus/frame_descriptor_manager.py:318-328
  - src/melder/aether/nexus/frame_descriptor_manager.py:401-430
  IMPACT: We do not need to rebuild `FrameDescriptor` itself to move forward.
    The more surgical contract move is to generalize the record payload shape,
    starting with spells where the rich profile payload already exists.
  NEXT: write the proposal task around record payload generalization, spell-first
    payload storage, and the event envelope/interface contract that should sit
    above it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T20:54:09Z
  TYPE: FACT
  CLAIM: The rich spell-facing profile is not yet fully descriptor-safe for
    direct storage. Even after removing the `Spell` back-reference from
    `SpellDetailedProfile`, the nested binding profile still carries
    `original_object`, which is a live class/function/object reference. So the
    current `SpellDetailedProfile` can define the minimum descriptor contract
    shape, but publishing/storing it directly would still leak runtime object
    references into the descriptor layer. That means the spell-first
    implementation likely needs either:
    - a sanitized descriptor payload class that matches the detailed-profile
      shape, or
    - a detached-copy path that strips runtime references from the binding side
      before publication.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/binding_profile.py:22-37
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/binding_profile.py:63-93
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py:27-384
  IMPACT: We should not implement `SpellRecord.payload = spell.profile` as a raw
    object assignment. The spell-first implementation needs one sanitized payload
    step first.
  NEXT: update the proposal task so the spell-first payload contract includes a
    descriptor-safe sanitized spell payload rather than direct raw
    `SpellDetailedProfile` storage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to inspect the current descriptor/event/payload/ACL surfaces
before we propose the contract.


## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

