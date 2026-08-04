# Task: Rename Dynamic Rift Room To Codegen
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-13-rename-dynamic-rift-room-to-codegen
- Epic: EPIC-2026-04-13-investigate-april-11-12-aethericrift-history-and-next-steps
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-13T23:54:10Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Rename the AR room/type layer from `dynamic` to `codegen` while preserving the
lower Melder runtime convention that still uses `SystemState.dynamic`.

## Ticket Contract
- ENTRY_GATE: the rename investigation concluded that an AR-layer rename is
  semantically honest if it stays above the lower frame/conduit convention.
- EXECUTION_BOUNDARY: AR room/type/config/interface/doc/test rename only, plus
  compatibility handling for legacy AR `dynamic` inputs.
- DEPENDENCIES:
  - codex/context_compass/tickets/tasks/2026-04-13_investigate_renaming_dynamic_rift_space_to_codegen_task.md
  - codex/context_compass/system_docs/patches/active/codegen_room_rename/architecture_patch.md
  - codex/context_compass/system_docs/patches/active/codegen_room_rename/component_patch_room_type_and_configuration.md
  - codex/context_compass/system_docs/patches/active/codegen_room_rename/component_patch_rift_space_and_command_system.md
  - codex/context_compass/system_docs/patches/active/codegen_room_rename/component_patch_interfaces_and_tests.md
- EXIT_GATE: AR room/type names use `codegen`, legacy AR `dynamic` inputs are
  handled explicitly, source/docs/tests are aligned, and the lower runtime
  `SystemState.dynamic` convention is untouched.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the code changes reveal a
  hidden lower-runtime dependency on AR room names that breaks the bounded
  rename boundary.

## Scope Boundaries
- In scope:
  - `RiftSpaceType`
  - AR room classes/command-system classes
  - AR-facing interfaces
  - Nexus/Rift room selection and target-frame gating language
  - AR docs/tests
  - compatibility handling for AR `dynamic` config inputs
- Out of scope:
  - lower `SystemState.dynamic`
  - conduit dynamic-environment semantics
  - mutationresearch or lower runtime naming

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the feasibility investigation showed a bounded AR-room
  rename is coherent and the user explicitly requested the rename.

## Steps / Checklist
- [ ] Create and link patch artifacts for the rename.
- [ ] Rename AR room/type/config names from `dynamic` to `codegen`.
- [ ] Add compatibility handling for legacy AR `dynamic` room inputs.
- [ ] Update AR interfaces, docs, and tests.
- [ ] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- renamed AR room/type layer
- compatibility handling for legacy AR `dynamic` inputs
- aligned tests/docs

## Files / Paths Impacted
- src/melder/aether/nexus/configuration/
- src/melder/aether/nexus/nexus.py
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/rift/rift_space/
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/
- codex/context_compass/system_docs/
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Rollback Notes
- Risk: AR rename leaks into lower runtime semantics and creates conceptual or
  compatibility confusion.
  Rollback: keep the change bounded to AR room/type naming and preserve the
  lower `dynamic` convention untouched.

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
  - system_docs/patches/active/codegen_room_rename/architecture_patch.md
  - system_docs/patches/active/codegen_room_rename/component_patch_room_type_and_configuration.md
  - system_docs/patches/active/codegen_room_rename/component_patch_rift_space_and_command_system.md
  - system_docs/patches/active/codegen_room_rename/component_patch_interfaces_and_tests.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the rename is merged into canonical docs or intentionally superseded.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-13T23:54:10Z
  TYPE: PLAN
  CLAIM: The implementation boundary is now clear: rename the AR room/type
    layer to `codegen`, preserve the lower `dynamic` substrate convention, and
    carry a compatibility path for legacy AR `dynamic` inputs at the AR config
    boundary.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-04-13_investigate_renaming_dynamic_rift_space_to_codegen_task.md:1-144
  IMPACT: The rename can proceed as a bounded AR migration instead of an
    uncontrolled global sweep.
  NEXT: author the patch docs, map patch sections to code edits, then apply the
    source/doc/test rename.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T23:54:10Z
  TYPE: PLAN
  CLAIM: Patch-artifact consumption is complete for the bounded AR rename. The
    implementation mapping is:
    - `architecture_patch.md` -> keep rename above lower `SystemState.dynamic`
      and conduit dynamic-environment semantics
    - `component_patch_room_type_and_configuration.md` -> update
      `RiftSpaceType`, `RiftConfiguration`, and Nexus target-frame gating
      language while preserving legacy AR `"dynamic"` input compatibility
    - `component_patch_rift_space_and_command_system.md` -> rename the final
      room and room-specific command classes plus Rift primary-space mapping
    - `component_patch_interfaces_and_tests.md` -> rename AR-facing protocols,
      unit tests, and canonical docs
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/codegen_room_rename/architecture_patch.md:1-32
  - codex/context_compass/system_docs/patches/active/codegen_room_rename/component_patch_room_type_and_configuration.md:1-18
  - codex/context_compass/system_docs/patches/active/codegen_room_rename/component_patch_rift_space_and_command_system.md:1-18
  - codex/context_compass/system_docs/patches/active/codegen_room_rename/component_patch_interfaces_and_tests.md:1-17
  IMPACT: Source edits can now stay bounded and traceable to the patch gate.
  NEXT: apply the AR-layer source rename and then update the focused AR docs
    and tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T23:54:10Z
  TYPE: FACT
  CLAIM: The first source tranche is in place. The canonical AR room/type is
    now `codegen` in the enum/configuration/Nexus/Rift path, the final room and
    room-specific command classes have been renamed to `CodegenRiftSpace` and
    `CodegenCommandSystem`, and Nexus target-frame gating language now talks
    about "Codegen AR" while still enforcing the same lower
    `SystemState.dynamic` requirement. Legacy AR string input `"dynamic"` now
    normalizes to the new room type at the `RiftConfiguration` boundary.
  EVIDENCE:
  - src/melder/aether/nexus/configuration/rift_space_type.py:6-28
  - src/melder/aether/nexus/configuration/rift_configuration.py:332-349
  - src/melder/aether/nexus/configuration/rift_configuration.py:428-447
  - src/melder/aether/nexus/nexus.py:2370-2425
  - src/melder/aether/nexus/rift/rift.py:1059-1119
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:13-85
  - src/melder/aether/nexus/rift/rift_space/command_system/codegen_command_system.py:6-20
  IMPACT: The rename now exists in the main AR construction path, so the next
    tranche is to align interfaces, docs, and focused AR tests.
  NEXT: patch interfaces, canonical docs, and unit tests to the new canonical
    `codegen` room name and then run focused validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T23:54:10Z
  TYPE: FACT
  CLAIM: The second source tranche is in place too. AR-facing interfaces now
    expose `ICodegenRiftSpace`, the canonical source docs now describe
    `CodegenRiftSpace` / `CodegenCommandSystem`, and the focused AR tests now
    assert `codegen` as the canonical room name while keeping legacy string
    `"dynamic"` as a compatibility input at the configuration boundary.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:7493-7495
  - codex/context_compass/system_docs/src_architecture.md:475-491
  - codex/context_compass/system_docs/src_components.md:519-588
  - tests/unit/melder/aether/test_rift_space_type.py:1-22
  - tests/unit/melder/aether/test_rift_configuration.py:95-108
  - tests/unit/melder/aether/test_nexus_configuration.py:111-127
  - tests/unit/melder/aether/test_nexus.py:786-818
  - tests/unit/melder/aether/test_nexus.py:3946-4033
  IMPACT: The remaining question is no longer source alignment. It is whether
    the focused AR validation ring passes cleanly with the bounded rename.
  NEXT: run the focused AR unit ring covering Rift configuration, Nexus room
    creation, and runtime contract behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-14T00:24:55Z
  TYPE: MEASURE
  CLAIM: The bounded AR rename is green on the focused AR validation ring. The
    renamed room/type/configuration path compiles, the focused AR unit ring
    passes, and a final live-surface search shows no remaining
    `DynamicRiftSpace` / `DynamicCommandSystem` / `RiftSpaceType.dynamic`
    references in current source, tests, or canonical system docs outside
    historical artifacts and active patch docs.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/configuration/rift_space_type.py src/melder/aether/nexus/configuration/rift_configuration.py src/melder/aether/nexus/configuration/nexus_configuration.py src/melder/aether/nexus/nexus.py src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py src/melder/aether/nexus/rift/rift_space/command_system/codegen_command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_space_type.py tests/unit/melder/aether/test_rift_configuration.py tests/unit/melder/aether/test_nexus_configuration.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_space_type.py tests/unit/melder/aether/test_rift_configuration.py tests/unit/melder/aether/test_nexus_configuration.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 151 passed
  - search_result: live source/test/system-doc search for `DynamicRiftSpace|DynamicCommandSystem|IDynamicRiftSpace|RiftSpaceType.dynamic` -> no hits outside historical artifacts/patch docs
  IMPACT: The rename is implemented and validated. The remaining step is user
    acceptance and any decision about whether to also refresh historical
    artifact language.
  NEXT: return the bounded AR rename for review and ask whether to close the
    task or continue into the next DynamicSpace/codegen lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded AR-room rename from `dynamic` to `codegen`.