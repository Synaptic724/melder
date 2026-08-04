# Task: Implement Spell Record Payload Contract
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-05-implement-spell-record-payload-contract
- Story: STORY-2026-04-05-descriptor-payload-contract-implementation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T20:54:09Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Implement the spell-first descriptor payload contract by moving `SpellRecord`
off split spell-profile fields and onto one payload field plus the matching
payload/record interfaces.

## Ticket Contract
- ENTRY_GATE: the proposal task has documented one accepted spell-first
  contract.
- EXECUTION_BOUNDARY: spell payload interfaces, spell-record storage, and the
  direct publish/store/consume path only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-05_propose_descriptor_payload_and_acl_view_contract_task.md
  - src/melder/aether/nexus/frame_descriptor/spell_record.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/utilities/interfaces/interfaces.py
- EXIT_GATE: `SpellRecord` uses one payload field, spell publication stores it,
  and focused validation passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the implementation forces
  conduit/frame payload rollout or larger descriptor aggregate changes.

## Scope Boundaries
- In scope:
  - spell descriptor payload interface(s)
  - spell record contract/interface
  - spell publish/store/consume updates
- Out of scope:
  - conduit/frame payload rollout
  - viewer implementation
  - event bus implementation

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [ ] Implement spell descriptor payload interfaces.
- [ ] Implement spell record interface(s) where needed.
- [ ] Move `SpellRecord` to one payload field.
- [ ] Update spell publish/store/consume code.
- [ ] Add/update focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- spell descriptor payload interface(s)
- spell-first `SpellRecord` payload contract
- focused tests

## Files / Paths Impacted
- src/melder/utilities/interfaces/interfaces.py
- src/melder/aether/nexus/frame_descriptor/spell_record.py
- src/melder/aether/nexus/frame_descriptor_manager.py
- tests/unit/melder/aether/
- tests/component/melder/aether/

## Validation
- Completed:
  - `python -m py_compile src/melder/utilities/interfaces/interfaces.py src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py src/melder/aether/nexus/frame_descriptor/spell_record.py src/melder/aether/nexus/frame_descriptor/frame_descriptor.py src/melder/aether/nexus/frame_descriptor_manager.py src/melder/spellbook/spell_crafter/spell_examiner/profiles/general_profile.py src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py`
  - `python -m pytest -q tests/unit/melder/aether/test_aetheric_frame_descriptor.py tests/component/melder/aether/test_frame_descriptor_manager_component.py tests/unit/melder/aether/test_nexus_passive_ingest.py`

## Risks / Rollback Notes
- Risk: duplicated compatibility fields survive beside the payload.
  Rollback: keep the implementation on one payload field only once this task is active.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/descriptor_payload_spell_first/architecture_patch.md
  - system_docs/patches/active/descriptor_payload_spell_first/component_patch_spell_record.md
  - system_docs/patches/active/descriptor_payload_spell_first/component_patch_frame_descriptor_manager.md
  - system_docs/patches/active/descriptor_payload_spell_first/component_patch_interfaces.md
  - system_docs/patches/active/descriptor_payload_spell_first/code_description_patch_spell_payload_publish.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T20:54:09Z
  TYPE: PLAN
  CLAIM: This task should stay ready until the proposal task locks the spell
    payload contract. Once accepted, the first implementation move is
    `SpellRecord` plus the direct publish/store/consume path, not a wider
    conduit/frame rollout.
  EVIDENCE:
  - tickets/tasks/2026-04-05_investigate_descriptor_payload_and_record_contract_task.md:1-97
  IMPACT: The implementation lane stays narrowly spell-first and reviewable.
  NEXT: wait for the proposal task to define the accepted contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-05T20:54:09Z
  TYPE: DECISION
  CLAIM: The accepted spell-first implementation contract is:
    1) add descriptor payload interfaces using Protocols
    2) define a sanitized spell descriptor payload that at least matches the
       rich spell-facing floor, but strips runtime object references such as the
       nested binding-profile `original_object`
    3) move `SpellRecord` to one `payload` field plus its existing
       identity/ownership fields
    4) update the direct spell publish/store/consume path to use that payload
       field
    5) leave conduit/frame payload rollout for later unless implementation
       pressure proves otherwise
  EVIDENCE:
  - tickets/tasks/2026-04-05_propose_descriptor_payload_and_acl_view_contract_task.md:86-112
  - tickets/tasks/2026-04-05_investigate_descriptor_payload_and_record_contract_task.md:86-111
  - src/melder/aether/nexus/frame_descriptor_manager.py:362-430
  IMPACT: We can start coding the spell-first record/payload cut now without
    widening into conduit/frame payload work or forcing a descriptor aggregate
    redesign.
  NEXT: implement the spell payload interfaces and move `SpellRecord` to one
    payload field first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T20:54:09Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping for this implementation slice is now
    explicit. `architecture_patch.md` maps to the spell-first boundary and the
    non-goals. `component_patch_interfaces.md` maps to the payload and record
    Protocol additions in `interfaces.py`. `component_patch_spell_record.md`
    maps to collapsing `SpellRecord` onto one payload field with fail-fast
    payload requirements. `component_patch_frame_descriptor_manager.md` maps to
    the spell publish/store path rewrite in the manager. The
    `code_description_patch_spell_payload_publish.md` doc maps to the sanitized
    payload export step and the focused publication validation surface.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/descriptor_payload_spell_first/architecture_patch.md:10-26
  - codex/context_compass/system_docs/patches/active/descriptor_payload_spell_first/component_patch_interfaces.md:3-13
  - codex/context_compass/system_docs/patches/active/descriptor_payload_spell_first/component_patch_spell_record.md:3-15
  - codex/context_compass/system_docs/patches/active/descriptor_payload_spell_first/component_patch_frame_descriptor_manager.md:3-15
  - codex/context_compass/system_docs/patches/active/descriptor_payload_spell_first/code_description_patch_spell_payload_publish.md:3-13
  IMPACT: The spell-first implementation can now proceed inside a concrete patch
    contract instead of widening informally.
  NEXT: add the payload/record Protocols and the sanitized spell payload class,
    then cut `SpellRecord` and the direct manager publish path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T21:13:46Z
  TYPE: MEASURE
  CLAIM: The spell-first descriptor payload contract is landed and green on the
    focused descriptor/publication surface. The slice now has:
    - `IDescriptorPayload` / `ISpellDescriptorPayload`
    - `IFrameRecord` / `IConduitRecord` / `ISpellRecord`
    - concrete `SpellDescriptorPayload`
    - `SpellGeneralProfile.to_descriptor_payload()` and
      `SpellDetailedProfile.to_descriptor_payload()`
    - `SpellRecord.payload` replacing the split spell-profile shards
    - spell publication in `FrameDescriptorManager` storing one payload field
    - `FrameDescriptor` typing shifted to record interfaces
    The focused descriptor/publication tests passed.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2161-2278
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py:1-224
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:10-128
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py:1-455
  - src/melder/aether/nexus/frame_descriptor_manager.py:401-430
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/general_profile.py:126-143
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py:209-226
  - command:python -m pytest -q tests/unit/melder/aether/test_aetheric_frame_descriptor.py tests/component/melder/aether/test_frame_descriptor_manager_component.py tests/unit/melder/aether/test_nexus_passive_ingest.py
  IMPACT: The descriptor layer now has a real spell payload contract instead of
    split profile shards, which gives the ACL/view lane one cleaner thing to
    consume and extend later.
  NEXT: review whether we keep the conduit/frame records flat for now and move
    directly into ACL view configuration on top of spell payloads, or whether
    you want conduit/frame payload rollout next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to implement the accepted spell-first descriptor payload
contract once the proposal task is complete.



