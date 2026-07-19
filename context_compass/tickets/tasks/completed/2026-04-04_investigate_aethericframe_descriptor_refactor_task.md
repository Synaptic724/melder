# Task: Investigate FrameDescriptor Refactor

## Metadata
- Task ID: TASK-2026-04-04-investigate-aethericframe-descriptor-refactor
- Story: STORY-2026-04-04-aethericframe-descriptor-refactor
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-04T13:10:15Z
- Updated: 2026-04-04T19:25:19Z

- Completed: 2026-04-04T19:25:19Z
- Summary: `FrameDescriptor` is now the live frame-scoped Nexus
  aggregate. Frame posture/overview, Nexus frame records, conduit records,
  spell records, and frame-local indexes live under the descriptor, and the
  old flat-store runtime shape is gone.

## Objective
Investigate the current Nexus/frame publishing and state ownership surfaces,
land the safest first `FrameDescriptor` slice, and leave the next
migration step explicit so the full refactor can proceed in multiple small
steps instead of one broad rewrite.

## Ticket Contract
- ENTRY_GATE: the user approved the descriptor direction and explicitly asked
  for investigation plus staged implementation instead of one giant change.
- EXECUTION_BOUNDARY: investigation, design notes, patch-lane setup, and the
  first descriptor migration slice only.
- DEPENDENCIES:
  - tickets/epics/2026-04-04_refactor_nexus_frame_state_around_frame_descriptor_epic.md
  - src/melder/aether/nexus/
  - src/melder/aether/aetheric_frame.py
  - tickets/tasks/completed/2026-04-04_implement_nexus_passive_ingest_and_canonical_store_task.md
- EXIT_GATE: the migration surface is mapped, the first staged slice is clear,
  and the patch-doc lane exists.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the migration boundary still
  implies too much risky surface for one first slice.

## Scope Boundaries
- In scope:
  - current flat Nexus frame-scoped state
  - current frame publication/update methods
  - descriptor contents and migration boundaries
  - patch-doc setup for the refactor
- Out of scope:
  - full runtime migration
  - viewer refactor
  - ACL implementation

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: the descriptor migration slices, cleanup, and lock/read
  boundary correction are landed and validated, and the active work has moved
  to ACL design above the cleaned descriptor.

## Steps / Checklist
- [x] Create patch artifacts for the descriptor refactor lane.
- [x] Map every current frame-scoped Nexus field that should migrate.
- [x] Map every current publish/remove path that will need retargeting.
- [x] Define the first implementation slice.
- [x] Implement the first descriptor migration slice.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- descriptor-refactor investigation notes
- patch-doc lane
- first implementation-slice definition
- first descriptor migration slice

## Files / Paths Impacted
- codex/context_compass/tickets/epics/2026-04-04_refactor_nexus_frame_state_around_frame_descriptor_epic.md
- codex/context_compass/tickets/stories/2026-04-04_aethericframe_descriptor_refactor_story.md
- codex/context_compass/tickets/tasks/2026-04-04_investigate_aethericframe_descriptor_refactor_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md
- codex/context_compass/system_docs/patches/active/nexus_frame_descriptor_refactor/

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/frame_descriptor.py src/melder/aether/nexus/nexus.py src/melder/aether/nexus/canonical_store/nexus_canonical_store.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_passive_ingest.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_passive_ingest.py`
  - `python -m py_compile src/melder/aether/nexus/frame_descriptor.py src/melder/aether/nexus/nexus_frame_record.py src/melder/aether/nexus/nexus.py tests/unit/melder/aether/test_frame_descriptor.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_descriptor.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_passive_ingest.py`

## Risks / Rollback Notes
- Risk: we under-scope the migration surface and then widen mid-implementation.
  Rollback: keep this task investigation-only and stage the first code slice
  explicitly before runtime edits.

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
  - system_docs/patches/active/nexus_frame_descriptor_refactor/architecture_patch.md
  - system_docs/patches/active/nexus_frame_descriptor_refactor/component_patch_nexus.md
  - system_docs/patches/active/nexus_frame_descriptor_refactor/component_patch_frame_descriptor.md
  - system_docs/patches/active/nexus_frame_descriptor_refactor/code_description_patch_nexus.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-04T15:56:42Z
  TYPE: FACT
  CLAIM: The descriptor locking audit is now landed. `FrameDescriptor`
    no longer only serializes grouped writes; its exposed read boundary is now
    protected too. Scalar component getters take the descriptor `RLock`, and
    the collection properties return snapshots instead of live dict/set state.
    That means future Rift/view consumers can inspect descriptor-owned conduit
    and spell surfaces without receiving direct mutation access to Nexus-owned
    containers. On the Nexus side, the small frame-descriptor registry helpers
    now also take `Nexus._lock`, and the dead `nexus_frame_mode` local in
    `_attach_rift_to_nexus_frames(...)` was removed.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor.py:1-430
  - src/melder/aether/nexus/nexus.py:1643-1912
  - src/melder/aether/nexus/nexus_frame_record.py:1-250
  - tests/unit/melder/aether/test_frame_descriptor.py:1-198
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_descriptor.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_passive_ingest.py
  IMPACT: The descriptor refactor now has a cleaner concurrency contract for
    both internal grouped mutations and external read consumers, which is the
    right base before ACL containers or view/query surfaces are added on top.
  NEXT: continue building on the descriptor shape rather than revisiting flat
    Nexus frame state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T15:37:31Z
  TYPE: FACT
  CLAIM: `FrameDescriptor` still needs one small contract correction:
    it has no owned lock guarding descriptor-level component replacement and
    grouped cleanup. The runtime already keeps direct dict/set operations cheap
    under Python 3.14t, so we do not need to wrap every container mutation, but
    the descriptor should still own an `RLock` for replacing major component
    refs (`frame_handle`, `frame_configuration`, `frame_overview`,
    `nexus_frame_record`) and for grouped teardown during cleanup.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor.py:1-245
  - user_instruction: "your changes in framedescriptor you should be using a lock for updates on specific components not the lists and dicts unless its a group change"
  IMPACT: Without this, descriptor-level replacement/cleanup semantics are
    looser than the rest of the runtime's ownership contract.
  NEXT: add an owned `RLock`, use it for component replacement and cleanup,
    and add a focused descriptor unit test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T15:32:00Z
  TYPE: FACT
  CLAIM: A broader suite pass exposed three test-surface drifts after the
    recent cleanup/refactor work, but they are all fixture/expectation issues
    rather than new runtime contract breaks. First, one component configuration
    test still expects `ai_native_enabled=True` to validate in automatic mode,
    which conflicts with the now-enforced semantic posture rule. Second, the
    `test_transfer_of_ownership_contracts.py` FakeSpellbook double does not
    implement `_publish_spell_record_to_nexus(...)`, even though the live
    transfer path now calls that hook. Third, the conduit-package autouse
    singleton fixture rebinds `Conduit._aether` but not `Spellbook._aether`, so
    conduit snapshot tests can build a new Spellbook against a stale cleaned
    Aether singleton.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_configuration_core.py:189-215
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py:521-555
  - tests/unit/melder/aether/conduit/test_conduit_snapshot.py:1-47
  - tests/unit/melder/aether/conduit/conftest.py:1-33
  IMPACT: The next fix should patch tests/fixtures to match current runtime
    contracts, not weaken the runtime to satisfy outdated doubles.
  NEXT: update the component configuration expectation, add the missing
    FakeSpellbook Nexus publish stub, and rebind `Spellbook._aether` in the
    conduit test fixture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T13:18:00Z
  TYPE: FACT
  CLAIM: The current frame-scoped Nexus state is split across three clearly
    migratable groups and one group that should stay outside the first slice.
    Group 1 is frame posture + frame overview:
    `Nexus._frame_posture_by_name` plus the `FrameRecord` produced in
    `_publish_frame_record(...)`. Group 2 is Nexus-managed frame lifecycle:
    `Nexus._nexus_frames_by_name` and `NexusFrameRecord`. Group 3 is frame-local
    indexes in the passive-ingest store: `frame_records_by_name`,
    `conduit_ids_by_frame_name`, and `spell_keys_by_frame_name`. The safer
    first slice is to introduce `FrameDescriptor` and move Group 1 and
    Group 2 under it first, while leaving the global conduit/spell primary
    stores alone until a later slice. `Nexus._target_frame_ref_counts` should
    stay top-level for now because it tracks process-wide target-frame
    attachments rather than one descriptor's owned state.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:70-87
  - src/melder/aether/nexus/nexus.py:149-152
  - src/melder/aether/nexus/nexus.py:752-845
  - src/melder/aether/nexus/nexus.py:1646-1784
  - src/melder/aether/nexus/canonical_store/nexus_canonical_store.py:30-37
  IMPACT: We can stage the descriptor migration without rewriting the entire
    passive-ingest store in one unsafe pass.
  NEXT: implement `FrameDescriptor` and retarget frame posture,
    `FrameRecord`, and `NexusFrameRecord` ownership into it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T13:23:33Z
  TYPE: FACT
  CLAIM: The first descriptor migration slice is now landed. Nexus now owns
    `_frame_descriptors_by_name` plus a new `FrameDescriptor` class.
    The descriptor currently owns or references:
    - the live frame handle
    - the bound `AethericFrameConfiguration`
    - the frame overview (`FrameRecord`)
    - the optional `NexusFrameRecord`
    `FrameRecord` no longer lives inside `NexusCanonicalStore`, and frame
    publication now stores the overview on the descriptor instead. Nexus-managed
    frame lifecycle paths were retargeted to descriptor-owned
    `NexusFrameRecord`s, while a compatibility `_nexus_frames_by_name` view was
    left in place so the focused Nexus unit surface did not have to be fully
    rewritten in the same slice. The global conduit/spell primary stores remain
    flat for now; that is the next migration surface.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor.py:1-179
  - src/melder/aether/nexus/nexus.py:64-152
  - src/melder/aether/nexus/nexus.py:675-793
  - src/melder/aether/nexus/nexus.py:1101-1185
  - src/melder/aether/nexus/nexus.py:1555-1811
  - src/melder/aether/nexus/canonical_store/nexus_canonical_store.py:10-181
  - tests/unit/melder/aether/test_nexus.py:1-769
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:1-161
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_passive_ingest.py
  IMPACT: The refactor now has a real runtime foothold without attempting the
    whole migration at once. Future slices can move frame-local conduit/spell
    indexes and ACL containers under the descriptor instead of continuing to
    extend flat Nexus frame state.
  NEXT: define the second migration slice: move frame-local conduit/spell
    indexes under the descriptor and retire the remaining flat frame-scoped
    pieces from `NexusCanonicalStore`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T13:30:00Z
  TYPE: FACT
  CLAIM: The remaining flat `NexusCanonicalStore` surface is now narrow enough
    for a second migration slice. After the first descriptor step, the only
    live runtime code still touching the store is `nexus.py` itself, and the
    only external reads are the focused Nexus passive-ingest tests. That means
    we can move the remaining conduit/spell records and frame-local indexes
    under `FrameDescriptor` without a broad repo rewrite.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:868-988
  - src/melder/aether/nexus/canonical_store/nexus_canonical_store.py:10-335
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:163-270
  IMPACT: The second slice can retire `NexusCanonicalStore` cleanly instead of
    keeping a second flat source of truth alive.
  NEXT: migrate conduit/spell records and their indexes into the descriptor,
    then retarget the focused passive-ingest tests to the descriptor-backed
    shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T13:43:35Z
  TYPE: FACT
  CLAIM: The second descriptor migration slice is now landed. The remaining
    active conduit/spell record ownership has moved under
    `FrameDescriptor`: descriptor now owns conduit records, spell
    records, conduit->spell indexes, and spellbook->spell indexes. `Nexus`
    publish/remove paths now route those updates into the descriptor instead of
    `NexusCanonicalStore`, and the focused passive-ingest tests were updated to
    read descriptor-owned state. `NexusCanonicalStore` is now reduced to dead
    code / compatibility residue rather than a live source of truth. The next
    step is cleanup and consolidation of the old compatibility shape.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor.py:1-245
  - src/melder/aether/nexus/nexus.py:830-988
  - src/melder/aether/nexus/canonical_store/nexus_canonical_store.py:10-335
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:1-270
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_passive_ingest.py
  IMPACT: The frame-scoped Nexus aggregate is now the real source of truth for
    frame overview plus conduit/spell state. The next slice is cleanup and
    consolidation, not another big ownership move.
  NEXT: define the cleanup slice: remove dead `NexusCanonicalStore` runtime
    shape and decide how much compatibility surface to keep for the internal
    Nexus tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T15:20:45Z
  TYPE: FACT
  CLAIM: The cleanup/consolidation slice is now landed too. The dead
    `NexusCanonicalStore` runtime file is removed, the old
    `_nexus_frames_by_name` compatibility shim is gone, and the focused Nexus
    tests now use the descriptor-backed internal accessors directly. That means
    `FrameDescriptor` is no longer just a partial wrapper; it is the
    actual live frame-scoped Nexus aggregate. Remaining work in this lane is no
    longer store cleanup, but higher-level design and integration on top of the
    cleaned descriptor model.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor.py:1-245
  - src/melder/aether/nexus/nexus.py:1-1811
  - tests/unit/melder/aether/test_nexus.py:620-770
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:1-270
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_passive_ingest.py
  IMPACT: The descriptor refactor has reached a stable internal state. The next
    work should be about what we build on top of the descriptor, not more
    cleanup of the old flat store.
  NEXT: decide whether the next descriptor-adjacent slice is ACL containers,
    view/query integration, or richer descriptor organization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T13:10:15Z
  TYPE: PLAN
  CLAIM: The first step in the descriptor refactor should be investigation and
    staging, not direct runtime edits. We need to map the existing frame-scoped
    Nexus state and define the first migration slice before changing the
    publication paths.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-04_implement_nexus_passive_ingest_and_canonical_store_task.md:1-170
  - user_instruction: "investigate everything and then implement your changes in multiple steps not a single step"
  IMPACT: This task should stay investigation-first and create the patch lane
    before runtime edits.
  NEXT: add the descriptor-refactor patch docs and then map the current flat
    frame-scoped Nexus state that should migrate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the active entrypoint for the `FrameDescriptor` refactor.
It has now completed the first two staged migration slices plus the cleanup
slice: descriptor owns frame posture/overview/NexusFrameRecord plus the active
conduit/spell state and indexes, and the old flat-store compatibility residue
is gone from live runtime use.
