# Task: Migrate Nexus Frame State Into FrameDescriptorManager

## Metadata
- Task ID: TASK-2026-04-04-migrate-nexus-frame-state-into-frame-descriptor-manager
- Story: STORY-2026-04-04-extract-frame-descriptor-manager
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-04T20:41:17Z
- Updated: 2026-04-05T17:50:09Z

## Objective
Extract the frame-scoped descriptor/store mechanics out of `Nexus` into a
dedicated thread-safe `FrameDescriptorManager`, migrate the live call sites,
and remove the old in-class state paths with no backward-compat shim.

## Ticket Contract
- ENTRY_GATE: active board row and patch-doc lane exist, and the user
  explicitly approved direct migration.
- EXECUTION_BOUNDARY: exact method split, manager introduction, call-site
  migration, cleanup of old in-class paths, and focused validation only.
- DEPENDENCIES:
  - tickets/epics/2026-04-04_frame_descriptor_manager_refactor_epic.md
  - tickets/stories/2026-04-04_extract_frame_descriptor_manager_story.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/architecture_patch.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/component_patch_nexus.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/component_patch_frame_descriptor_manager.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/code_description_patch_frame_descriptor_manager.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/frame_descriptor.py
- EXIT_GATE: manager owns the frame-descriptor dictionary and frame-scoped
  publish/remove/lookup flows, `Nexus` delegates cleanly, and old paths are
  removed.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the extraction requires a
  broader API redesign beyond the frame-scoped boundary.

## Scope Boundaries
- In scope:
  - `src/melder/aether/nexus/nexus.py`
  - new manager file under `src/melder/aether/nexus/`
  - focused tests/docs needed by the migration
  - active tickets/board/artifact-board state
- Out of scope:
  - final ACL system implementation
  - unrelated Nexus/Rift API redesign
  - backward-compat aliases

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: `FrameDescriptorManager` is landed, `Nexus` now delegates
  the frame-scoped descriptor/store methods to it, the old direct descriptor
  dictionary ownership is gone, and focused Nexus validation passed.

## Steps / Checklist
- [x] Lock the exact method split between `Nexus` and `FrameDescriptorManager`.
- [x] Add `FrameDescriptorManager` with explicit `RLock` ownership.
- [x] Move frame-scoped descriptor/store methods into the manager.
- [x] Delegate façade-level frame work from `Nexus` into the manager.
- [x] Remove the old direct descriptor-store fields and methods from `Nexus`.
- [x] Update focused tests.
- [x] Validate syntax and targeted runtime behavior.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- thread-safe `FrameDescriptorManager`
- leaner `Nexus` delegation boundary
- removal of old in-class descriptor-store paths

## Files / Paths Impacted
- src/melder/aether/nexus/nexus.py
- src/melder/aether/nexus/frame_descriptor.py
- src/melder/aether/nexus/
- tests/unit/melder/aether/
- tests/component/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/tickets/tasks/2026-04-04_migrate_nexus_frame_state_into_frame_descriptor_manager_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/nexus.py src/melder/aether/nexus/frame_descriptor_manager.py src/melder/aether/nexus/frame_descriptor.py`
  - `python -m py_compile src/melder/aether/nexus/nexus.py tests/unit/melder/aether/test_nexus.py`
  - `python -m py_compile tests/unit/melder/aether/test_frame_descriptor.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_descriptor.py`
  - `python -m py_compile tests/unit/melder/aether/test_nexus_passive_ingest.py tests/unit/melder/aether/test_frame_descriptor_manager.py tests/component/melder/aether/test_frame_descriptor_manager_component.py tests/integration/melder/aether/test_aether_integration_nexus_passive_ingest.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus_passive_ingest.py tests/unit/melder/aether/test_frame_descriptor_manager.py tests/component/melder/aether/test_frame_descriptor_manager_component.py tests/integration/melder/aether/test_aether_integration_nexus_passive_ingest.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_passive_ingest.py tests/unit/melder/aether/test_frame_descriptor_manager.py tests/unit/melder/aether/test_frame_descriptor.py tests/component/melder/aether/test_frame_descriptor_manager_component.py tests/integration/melder/aether/test_aether_integration_nexus_passive_ingest.py`

## Risks / Rollback Notes
- Risk: state ownership stays split between `Nexus` and the manager.
  Rollback: stop before partial dual-ownership ships and keep the split
  documented in the task notes.
- Risk: lock ordering becomes ambiguous.
  Rollback: keep `Nexus` registry work and manager frame-state work delegated in
  one direction only.

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
  - system_docs/patches/active/nexus_frame_descriptor_manager/architecture_patch.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/component_patch_nexus.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/component_patch_frame_descriptor_manager.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/code_description_patch_frame_descriptor_manager.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-04T21:09:51Z
  TYPE: FACT
  CLAIM: The `Nexus` faÃ§ade now has one smaller control-flow cleanup on top of
    the manager extraction: `_allocate_default_rift_name()` no longer uses an
    open-ended `while True` loop. It now performs a bounded deterministic probe
    from `_next_default_rift_number`, advances the stored incrementer on
    success, and raises a clear `RuntimeError` if the bounded name window is
    unexpectedly exhausted. The focused Nexus unit surface now covers both the
    collision-skip path and the fail-fast path.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1455-1477
  - tests/unit/melder/aether/test_nexus.py:299-336
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py
  IMPACT: One more low-quality edge is removed from the live root object, and
    the default-name allocator no longer relies on an unbounded loop.
  NEXT: keep the lane in review unless you want more small faÃ§ade cleanups of
    this kind before acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-04T21:09:51Z
  TYPE: FACT
  CLAIM: One smaller `Nexus` faÃ§ade cleanup is still worth doing in this slice.
    `_allocate_default_rift_name()` still uses an open-ended `while True` loop
    even though the class already carries an explicit deterministic name
    incrementer (`_next_default_rift_number`). The behavior should stay the
    same in normal operation, but the implementation should become bounded and
    fail-fast if the default-name namespace is unexpectedly exhausted or badly
    drifted.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1455-1468
  IMPACT: This is not a major architecture change, but it is the kind of
    faÃ§ade cleanup that removes a low-quality edge from the live root object.
  NEXT: replace the open-ended loop with a bounded probe over deterministic
    default Rift names and add a collision-path unit test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-04T21:09:51Z
  TYPE: MEASURE
  CLAIM: The aggregate narrow lane is now green after the extra coverage pass.
    The combined façade, passive-ingest, manager, descriptor, component, and
    integration surfaces all passed together in one run, which is a stronger
    signal than separate green subsets. The direct descriptor and manager unit
    files now cover the core lifecycle/index branches instead of only the happy
    paths.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_passive_ingest.py tests/unit/melder/aether/test_frame_descriptor_manager.py tests/unit/melder/aether/test_frame_descriptor.py tests/component/melder/aether/test_frame_descriptor_manager_component.py tests/integration/melder/aether/test_aether_integration_nexus_passive_ingest.py
  IMPACT: The refactor lane now has professional, multi-layered coverage for
    the new boundary instead of a thin happy-path wrapper surface.
  NEXT: keep the lane in review unless you want a full-repo test sweep beyond
    this boundary-focused set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T21:02:33Z
  TYPE: PLAN
  CLAIM: The current added tests are materially better than the stale baseline,
    but they still do not saturate the new manager boundary. The next coverage
    pass should target the obvious remaining branch holes directly:
    manager cleanup, posture-refresh failure branches, required-get failure
    branches, existing-vs-create Nexus frame-record paths, direct list/count
    behavior, and descriptor no-op/error edges. This is the right place to add
    coverage because the refactor introduced a new internal owner, and leaving
    those branches untested would undercut confidence in the extraction.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor_manager.py:18-595
  - tests/unit/melder/aether/test_frame_descriptor_manager.py:1-131
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:1-267
  IMPACT: The lane should stay active until the manager coverage looks
    professional rather than merely non-embarrassing.
  NEXT: add direct tests for the uncovered manager/descriptor branches, then
    rerun the narrow suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T21:02:33Z
  TYPE: FACT
  CLAIM: The direct `FrameDescriptor` unit surface is now stronger than
    the original three-test baseline. Additional tests now cover conduit record
    replacement/removal cleanup, spell record replacement with index refresh,
    spell record removal with index teardown, and `detach_nexus_frame_record()`
    semantics. That gives the descriptor aggregate its own meaningful lifecycle
    and index-ownership coverage instead of relying on manager tests as a proxy.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_descriptor.py:1-301
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_descriptor.py
  IMPACT: The frame-descriptor aggregate now has direct unit coverage for the
    owned cleanup/index behaviors that the manager and Nexus layers depend on.
  NEXT: keep the lane in review unless you want yet more targeted coverage in a
    broader full-suite pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T21:02:33Z
  TYPE: FACT
  CLAIM: The test surface for this lane is now broader than the original
    focused Nexus wrapper test. The stale passive-ingest unit file was repaired
    to stop reaching into the removed Nexus-owned descriptor dictionary, and
    three additional tests now lock the new boundary directly:
    one unit file for `FrameDescriptorManager`,
    one component test for manager + real Aether frame posture + mixed record
    publication,
    and one integration test proving real `Spellbook.conjure()` still drives
    passive Nexus population through the manager-owned path.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:1-267
  - tests/unit/melder/aether/test_frame_descriptor_manager.py:1-131
  - tests/component/melder/aether/test_frame_descriptor_manager_component.py:1-101
  - tests/integration/melder/aether/test_aether_integration_nexus_passive_ingest.py:1-88
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus_passive_ingest.py tests/unit/melder/aether/test_frame_descriptor_manager.py tests/component/melder/aether/test_frame_descriptor_manager_component.py tests/integration/melder/aether/test_aether_integration_nexus_passive_ingest.py
  IMPACT: The refactor is now covered at the faÃ§ade, direct manager, component,
    and integration layers instead of only by the original wrapper test file.
  NEXT: keep the lane in review unless you want another cleanup pass inside the
    `Nexus` faÃ§ade surface itself.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T20:55:05Z
  TYPE: FACT
  CLAIM: The focused `test_nexus.py` surface passed, but the passive-ingest unit
    surface still carries direct assertions against the removed
    `nexus._frame_descriptors_by_name` field. That means the refactor is
    behaviorally fine at the focused façade layer but the narrower passive-ingest
    tests are stale and must be rewritten to assert through the new manager-owned
    state boundary instead of the deleted in-class store field.
  EVIDENCE:
  - user_report: tests/unit/melder/aether/test_nexus_passive_ingest.py failures referencing nexus._frame_descriptors_by_name
  IMPACT: The lane is not actually review-clean yet. We need to repair the stale
    unit surface and add direct manager coverage so the new ownership split is
    tested where it really lives.
  NEXT: inspect the passive-ingest tests and update them against
    `FrameDescriptorManager`, then decide which extra component/integration cases
    are worth adding in this slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T20:55:05Z
  TYPE: MEASURE
  CLAIM: The manager extraction is mechanically stable in the focused local
    Nexus surface. Syntax compilation passed for the migrated Nexus files, and
    the focused Nexus unit suite passed after the frame-scoped store ownership
    moved into `FrameDescriptorManager`.
  EVIDENCE:
  - command:python -m py_compile src/melder/aether/nexus/nexus.py src/melder/aether/nexus/frame_descriptor_manager.py src/melder/aether/nexus/frame_descriptor.py
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py
  IMPACT: The lane is ready for review on behavior and boundary quality rather
    than still being blocked on syntax or the focused Nexus unit surface.
  NEXT: review the new ownership split with the user and decide whether any
    remaining façade/helper cleanup should happen in this slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T20:55:05Z
  TYPE: FACT
  CLAIM: The migration landed in the bounded form we planned. A new
    `FrameDescriptorManager` now owns the descriptor dictionary and the moved
    frame-scoped publish/remove/record methods, while `Nexus` keeps the façade
    methods and delegates into the manager. The old direct descriptor-store
    ownership field is gone from `Nexus`, and `check_for_aetheric_frame(...)`
    now detaches Nexus frame-record state through the manager rather than
    reaching into the descriptor dictionary directly.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor_manager.py:18-595
  - src/melder/aether/nexus/nexus.py:70-80
  - src/melder/aether/nexus/nexus.py:134-145
  - src/melder/aether/nexus/nexus.py:274-301
  - src/melder/aether/nexus/nexus.py:668-812
  - src/melder/aether/nexus/nexus.py:1005-1018
  - src/melder/aether/nexus/nexus.py:1575-1729
  IMPACT: The frame-scoped store is no longer embedded as raw Nexus-owned
    state, which makes the root class smaller in responsibility even though the
    façade surface remains available for callers that already speak to `Nexus`.
  NEXT: leave the lane in review until you confirm the boundary and any further
    cleanup you want in this slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T20:41:17Z
  TYPE: DECISION
  CLAIM: The method split is now concrete enough to implement. The
    `FrameDescriptorManager` should own:
    `_frame_descriptors_by_name`,
    `_refresh_frame_posture_cache(...)`,
    `_get_publishable_frame_posture(...)`,
    `_publish_frame_record(...)`,
    `_publish_conduit_record(...)`,
    `_remove_conduit_record(...)`,
    `_publish_spell_record(...)`,
    `_remove_spell_record(...)`,
    `_get_required_frame_descriptor(...)`,
    `_get_or_create_frame_descriptor(...)`,
    `_get_nexus_frame_record(...)`,
    `_list_nexus_frame_names(...)`,
    `_count_nexus_frame_records(...)`,
    `_get_required_nexus_frame_record(...)`,
    `_get_or_create_nexus_frame_record(...)`,
    and `_create_nexus_frame_record(...)`.
    `Nexus` should keep the façade/root surfaces that apply topology or Rift
    registry policy:
    `get_nexus_frame_for_rift(...)`,
    `create_nexus_frame_for_rift(...)`,
    `list_accessible_nexus_frame_names(...)`,
    `_attach_rift_to_nexus_frames(...)`,
    `_detach_rift_from_nexus_frames(...)`,
    `_dispose_nexus_frame(...)`,
    and `check_for_aetheric_frame(...)`,
    with those methods delegating frame-scoped record/descriptor work into the
    manager instead of mutating the store directly.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:668-969
  - src/melder/aether/nexus/nexus.py:983-1152
  - src/melder/aether/nexus/nexus.py:1643-1713
  - src/melder/aether/nexus/nexus.py:1715-1921
  IMPACT: The migration can preserve a clean semantic root on `Nexus` while
    moving the actual frame-scoped store mechanics into one dedicated
    thread-safe subsystem.
  NEXT: implement `FrameDescriptorManager`, re-home the moved methods, and
    retarget `Nexus` call sites to delegate through it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T20:41:17Z
  TYPE: FACT
  CLAIM: The frame-scoped extraction target is already visible in one coherent
    `Nexus` method cluster. The class owns `_frame_descriptors_by_name`,
    posture refresh and publishability checks, passive frame/conduit/spell
    record publication/removal, and Nexus-managed frame-record lookup/create.
    That means the migration can move one real subsystem instead of trying to
    slice scattered helpers out of unrelated Rift registry logic.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:147-149
  - src/melder/aether/nexus/nexus.py:668-969
  - src/melder/aether/nexus/nexus.py:1715-1921
  IMPACT: The manager boundary can be locked before code edits without
    reopening the wider Nexus design.
  NEXT: define which façade methods stay on `Nexus` and which frame-scoped
    methods move fully into the manager.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to migrate the frame-scoped Nexus descriptor/store subsystem
into a dedicated manager and remove the old in-class ownership paths. The
manager is now landed and validated in the focused Nexus unit surface, so the
lane is in review pending user acceptance or further cleanup direction.
