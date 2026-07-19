# Task: Implement Conduit And Frame Record Payload Contract
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-05-implement-conduit-and-frame-record-payload-contract
- Story: STORY-2026-04-05-conduit-and-frame-record-payload-rollout
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T21:25:04Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Implement the conduit/frame descriptor payload contract by moving
`ConduitRecord` and `FrameRecord` off flat descriptive fields and onto one
payload field plus the matching payload/record interfaces.

## Ticket Contract
- ENTRY_GATE: the spell-first payload contract is landed, this follow-up task
  is routed from `attention_board.md`, and the new patch-doc set exists and is
  linked below.
- EXECUTION_BOUNDARY: conduit/frame payload interfaces, conduit/frame record
  storage, and the direct publish/store/consume path only.
- DEPENDENCIES:
  - tickets/stories/2026-04-05_conduit_and_frame_record_payload_rollout_story.md
  - tickets/tasks/2026-04-05_implement_spell_record_payload_contract_task.md
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py
  - src/melder/aether/nexus/frame_descriptor/frame_record.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/utilities/interfaces/interfaces.py
- EXIT_GATE: `ConduitRecord` and `FrameRecord` use one payload field, direct
  publication stores that payload, and focused validation passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the implementation forces an
  event abstraction or a larger descriptor aggregate redesign.

## Scope Boundaries
- In scope:
  - conduit descriptor payload interface(s)
  - frame descriptor payload interface(s)
  - conduit/frame record contract/interface updates
  - conduit/frame publish/store/consume updates
- Out of scope:
  - ACL/view implementation
  - spell payload rework
  - event bus implementation
  - `NexusFrameRecord` redesign

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Implement conduit/frame descriptor payload interfaces.
- [x] Implement conduit/frame record interface updates where needed.
- [x] Move `ConduitRecord` to one payload field.
- [x] Move `FrameRecord` to one payload field.
- [x] Update conduit/frame publish/store/consume code.
- [x] Add/update focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- conduit descriptor payload interface(s)
- frame descriptor payload interface(s)
- conduit/frame record payload contract
- focused tests

## Files / Paths Impacted
- src/melder/utilities/interfaces/interfaces.py
- src/melder/aether/nexus/frame_descriptor/conduit_record.py
- src/melder/aether/nexus/frame_descriptor/frame_record.py
- src/melder/aether/nexus/frame_descriptor/frame_descriptor.py
- src/melder/aether/nexus/frame_descriptor_manager.py
- tests/unit/melder/aether/
- tests/component/melder/aether/

## Validation
- Completed:
  - `python -m py_compile src/melder/utilities/interfaces/interfaces.py src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py src/melder/aether/nexus/frame_descriptor/conduit_record.py src/melder/aether/nexus/frame_descriptor/frame_record.py src/melder/aether/nexus/frame_descriptor_manager.py tests/unit/melder/aether/test_aetheric_frame_descriptor.py tests/unit/melder/aether/test_frame_descriptor_manager.py tests/component/melder/aether/test_frame_descriptor_manager_component.py tests/unit/melder/aether/test_nexus_passive_ingest.py`
  - `python -m pytest -q tests/unit/melder/aether/test_aetheric_frame_descriptor.py tests/unit/melder/aether/test_frame_descriptor_manager.py tests/component/melder/aether/test_frame_descriptor_manager_component.py tests/unit/melder/aether/test_nexus_passive_ingest.py`

## Risks / Rollback Notes
- Risk: conduit/frame identity fields get mixed into payload and break current
  index ownership.
  Rollback: keep identity/ownership fields top-level and move only descriptive
  state into payloads.

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
  - system_docs/patches/active/descriptor_payload_conduit_frame_followup/architecture_patch.md
  - system_docs/patches/active/descriptor_payload_conduit_frame_followup/component_patch_conduit_record.md
  - system_docs/patches/active/descriptor_payload_conduit_frame_followup/component_patch_frame_record.md
  - system_docs/patches/active/descriptor_payload_conduit_frame_followup/component_patch_frame_descriptor_manager.md
  - system_docs/patches/active/descriptor_payload_conduit_frame_followup/component_patch_interfaces.md
  - system_docs/patches/active/descriptor_payload_conduit_frame_followup/code_description_patch_record_payload_publish.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T21:25:04Z
  TYPE: PLAN
  CLAIM: The direct next slice is to widen the spell-first payload pattern into
    the two remaining descriptor records that still publish/store flat detail
    fields: `ConduitRecord` and `FrameRecord`. The manager still constructs
    both directly from flattened values, so leaving them untouched would force
    the next ACL/view layer to consume mixed record contracts.
  EVIDENCE:
  - codex/context_compass/attention_board.md:28-28
  - codex/context_compass/tickets/tasks/2026-04-05_implement_spell_record_payload_contract_task.md:201-201
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:29-29
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:29-29
  - src/melder/aether/nexus/frame_descriptor_manager.py:259-259
  - src/melder/aether/nexus/frame_descriptor_manager.py:321-321
  IMPACT: The follow-up should stay on the record lane instead of jumping to ACL
    view config too early.
  NEXT: keep record identity fields stable, move descriptive state into payload
    classes, and update the direct publish/store path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T21:25:04Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping for this follow-up slice is now
    explicit. `architecture_patch.md` defines the non-goals and the fact that
    `FrameDescriptor` stays intact. `component_patch_interfaces.md` maps to the
    new conduit/frame payload and record Protocol additions in `interfaces.py`.
    `component_patch_conduit_record.md` and `component_patch_frame_record.md`
    map to collapsing those records onto one payload field with fail-fast
    payload requirements. `component_patch_frame_descriptor_manager.md` maps to
    the conduit/frame publish path rewrite in the manager. The
    `code_description_patch_record_payload_publish.md` doc maps to payload
    construction plus focused publication validation.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/descriptor_payload_conduit_frame_followup/architecture_patch.md:1-19
  - codex/context_compass/system_docs/patches/active/descriptor_payload_conduit_frame_followup/component_patch_interfaces.md:1-13
  - codex/context_compass/system_docs/patches/active/descriptor_payload_conduit_frame_followup/component_patch_conduit_record.md:1-13
  - codex/context_compass/system_docs/patches/active/descriptor_payload_conduit_frame_followup/component_patch_frame_record.md:1-13
  - codex/context_compass/system_docs/patches/active/descriptor_payload_conduit_frame_followup/component_patch_frame_descriptor_manager.md:1-13
  - codex/context_compass/system_docs/patches/active/descriptor_payload_conduit_frame_followup/code_description_patch_record_payload_publish.md:1-12
  IMPACT: Patch gating is satisfied for the follow-up slice before code edits.
  NEXT: implement the new payload interfaces and record fields, then update the
    publish/store path and focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T21:25:04Z
  TYPE: FACT
  CLAIM: The current flat conduit/frame record fields are mostly consumed by
    the focused descriptor-manager and passive-ingest tests, not by a broad src
    runtime surface. That keeps the rollout local to the record classes, the
    direct manager publish path, and a small focused test slice.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor_manager.py:259-259
  - src/melder/aether/nexus/frame_descriptor_manager.py:321-321
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:39-64
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py:167-172
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:110-118
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:146-152
  - tests/component/melder/aether/test_frame_descriptor_manager_component.py:124-124
  IMPACT: We can keep this slice narrow and avoid widening into unrelated
    runtime consumers while still finishing the record rollout.
  NEXT: add conduit/frame payload classes and wire the records plus manager
    publish path to those payloads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T21:25:04Z
  TYPE: FACT
  CLAIM: The conduit/frame rollout is now implemented in code. The descriptor
    interface family has dedicated conduit/frame payload Protocols, new
    descriptor-safe payload classes exist, both record classes now require a
    non-empty payload and clean it on teardown, and `FrameDescriptorManager`
    now builds payloads before constructing `FrameRecord` and `ConduitRecord`.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2244-2299
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py:9-94
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py:8-116
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:9-89
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:9-85
  - src/melder/aether/nexus/frame_descriptor_manager.py:264-340
  IMPACT: The remaining work in this slice is focused validation plus any
    consumer/test rewiring needed by the new payload access path.
  NEXT: run focused compile and pytest slices for the descriptor manager and
    record tests, then fix any local fallout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T21:32:26Z
  TYPE: MEASURE
  CLAIM: The conduit/frame payload rollout is green on the focused descriptor
    surface. `py_compile` passed on the touched runtime and test files, and the
    focused Aether descriptor-manager/passive-ingest pytest slice passed with
    25 tests. The rollout now has Protocol-based conduit/frame payload
    contracts, concrete `ConduitDescriptorPayload` and `FrameDescriptorPayload`
    classes, payload-backed `ConduitRecord` / `FrameRecord`, manager publication
    rewired to build those payloads, and focused test expectations updated to
    read through `.payload`.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2244-2299
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py:9-94
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py:8-116
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:9-89
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:9-85
  - src/melder/aether/nexus/frame_descriptor_manager.py:264-340
  - command:python -m pytest -q tests/unit/melder/aether/test_aetheric_frame_descriptor.py tests/unit/melder/aether/test_frame_descriptor_manager.py tests/component/melder/aether/test_frame_descriptor_manager_component.py tests/unit/melder/aether/test_nexus_passive_ingest.py
  IMPACT: The descriptor lane no longer mixes one spell payload record with two
    flat legacy records, so the next ACL/view slice can consume a more coherent
    record model.
  NEXT: review the conduit/frame payload contract with the user and decide
    whether the next routed slice is ACL view configuration or another payload
    refinement pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to widen the descriptor payload contract from spell-only into
conduit and frame records once the spell-first slice is in review.



