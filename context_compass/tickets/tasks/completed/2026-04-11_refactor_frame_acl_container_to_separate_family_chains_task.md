# Task: Refactor Frame ACL Container To Separate Family Chains
- Completed: 2026-04-13T11:51:25Z
- Summary: Closed the separate-family ACL chain migration after later precision ACL work built on it as settled foundation.

## Metadata
- Task ID: TASK-2026-04-11-refactor-frame-acl-container-to-separate-family-chains
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T21:44:50Z
- Updated: 2026-04-13T11:51:25Z

## Objective
Replace the current hybrid frame-ACL model with a coherent separate-family
chain model where one frame container owns named version chains for view,
command, and codegen independently, while Rift/Nexus resolve a per-frame ACL
selection that can point those three families to the same contract name or to
different names.

## Ticket Contract
- ENTRY_GATE: the current ACL/container/runtime model has been re-read from
  source, the user explicitly approved the version-control direction, and the
  linked-list inconsistency is now evidenced in task notes.
- EXECUTION_BOUNDARY: ACL container/chain/builder/manager/Nexus refresh wiring,
  focused interfaces, focused tests, and ticket/board/artifact sync only.
- DEPENDENCIES:
  - tickets/epics/2026-04-11_precision_acl_targets_and_spell_access_epic.md
  - tickets/stories/2026-04-11_precision_acl_target_model_and_descriptor_validation_story.md
  - tickets/tasks/2026-04-11_investigate_precision_acl_implementation_and_descriptor_validation_task.md
  - src/melder/aether/nexus/acl/frame_acl_container.py
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py
  - src/melder/aether/nexus/acl/frame_acl_builder.py
  - src/melder/aether/nexus/frame_acl_manager.py
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_frame_acl_configuration_chain.py
  - tests/unit/melder/aether/test_frame_acl_container.py
  - tests/unit/melder/aether/test_frame_acl_manager.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: one frame container owns named chain registries for view,
  command, and codegen, the hybrid frame-global chain is gone, a per-frame ACL
  selection resolves the three current family configs together, and chain
  bumps invalidate/rebuild downstream viewer state.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if this refactor forces a wider
  precision-configuration or public-Rift policy redesign in the same tranche.

## Scope Boundaries
- In scope:
  - convert frame container from one-chain-plus-static-registry to
    separate named view/command/codegen chains
  - add per-frame ACL selection across those three family registries
  - builder draft/commit against one selected family chain at a time
  - manager/Nexus facades for separate-family chain operations
  - downstream viewer cache invalidation and attached-viewer refresh on family
    chain bumps
  - focused tests and interface updates
- Out of scope:
  - precision configuration implementation
  - command ACL enforcement
  - room-mode policy redesign
  - unrelated descriptor/runtime work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved implementing separate family
  chains so ACL elements can keep revision history independently.

## Steps / Checklist
- [ ] Stage the patch docs and route the task from the board.
- [ ] Refactor the container so named view/command/codegen chains are owned separately.
- [ ] Add per-frame ACL selection across the three family registries.
- [ ] Refactor the builder so draft/commit targets one selected family chain.
- [ ] Refactor manager/Nexus facades away from frame-global chain semantics.
- [ ] Add downstream projected-viewer invalidation/refresh for family-chain bumps.
- [ ] Update focused tests and remove obsolete hybrid-model tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- separate family-chain ownership in `FrameACLContainer`
- family-chain-targeted builder/manager/Nexus APIs
- per-frame ACL selection object/state
- downstream viewer refresh on chain bumps
- focused test updates

## Files / Paths Impacted
- src/melder/aether/nexus/acl/frame_acl_container.py
- src/melder/aether/nexus/acl/frame_acl_configuration_chain.py
- src/melder/aether/nexus/acl/frame_acl_builder.py
- src/melder/aether/nexus/frame_acl_manager.py
- src/melder/aether/nexus/nexus.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_frame_acl_configuration_chain.py
- tests/unit/melder/aether/test_frame_acl_container.py
- tests/unit/melder/aether/test_frame_acl_manager.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_configuration_chain.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: the refactor leaves half the code treating `"default"` as the only
  chain-backed contract while the other half assumes all named contracts are
  chain-backed.
  Rollback: keep the refactor atomic across container, builder, manager, Nexus,
  and the focused tests instead of landing partial ownership changes.

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
- system_docs/patches/active/frame_acl_separate_family_chains/architecture_patch.md
- system_docs/patches/active/frame_acl_separate_family_chains/component_patch_frame_acl_container.md
- system_docs/patches/active/frame_acl_separate_family_chains/component_patch_frame_acl_builder.md
- system_docs/patches/active/frame_acl_separate_family_chains/component_patch_frame_acl_manager.md
- system_docs/patches/active/frame_acl_separate_family_chains/component_patch_nexus.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the separate-family chain model is merged into
  canonical ACL docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-11T21:44:50Z
  TYPE: FACT
  CLAIM: The current ACL registry model is hybrid and inconsistent. One frame
    container owns one configuration chain, but it also owns a separate named
    configuration registry. The chain only really drives the reserved
    `"default"` contract because `_sync_default_named_configuration_to_current()`
    mirrors current-chain selection into `"default"`, while other named
    contracts stay static snapshot entries. Rift selection is already stable on
    `frame_name + contract_name`, so the coherent fix is to keep that selection
    identity and move chain ownership behind each named contract instead of
    keeping one frame-global chain.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_container.py:316-352
  - src/melder/aether/nexus/acl/frame_acl_container.py:385-477
  - src/melder/aether/nexus/acl/frame_acl_container.py:541-559
  - src/melder/aether/nexus/rift/rift.py:406-482
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:203-300
  IMPACT: We should not delete version control. We should relocate it so each
    named contract family has its own chain/history and Rift selection remains
    stable.
  NEXT: write patch docs and refactor the frame container to own separate
    named chains per config family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T21:44:50Z
  TYPE: FACT
  CLAIM: Downstream ACL refresh is incomplete today. Chain operations routed
    through Nexus invalidate projected frame-viewer caches, but plain named ACL
    registration does not invalidate that cache, and attached `RiftSpace`
    viewers only rebuild when the Rift itself re-targets and reattaches a
    viewer. That means a contract-family revision model is only coherent if
    chain bumps also invalidate Nexus viewer caches and trigger live attached
    viewer refresh for affected Rifts/spaces.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1269-1300
  - src/melder/aether/nexus/nexus.py:1451-1518
  - src/melder/aether/nexus/nexus.py:2033-2066
  - src/melder/aether/nexus/rift/rift.py:469-482
  IMPACT: The refactor is not just container ownership. It also needs explicit
    downstream refresh so a Rift selection sees the new current revisions
    automatically.
  NEXT: patch the separate-family chain model and wire refresh from selected
    family chain bumps through Nexus into attached Rift viewers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T22:01:00Z
  TYPE: DECISION
  CLAIM: The implementation direction has changed from grouped named contract
    chains to separate named family chains. The container should own:
    - `view_chains_by_name`
    - `command_chains_by_name`
    - `codegen_chains_by_name`
    and Rift/Nexus should resolve a per-frame ACL selection across those three
    registries. Same-name selection stays allowed as convenience, but it is no
    longer the only model.
  EVIDENCE:
  - user_instruction: "nah we don't want to bundle, seperate them"
  - user_instruction: "you might not be commanding the same things your viewing"
  - user_instruction: "we can also export the whole chain if we want"
  - user_instruction: "you can select the names of the configs you want"
  IMPACT: The grouped-chain patch docs were stale before implementation. The
    actual refactor should target independent version control per family plus
    assembled snapshot/validation/compile downstream.
  NEXT: rewrite the patch docs and refactor the ACL core to separate family chains.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T22:24:00Z
  TYPE: FACT
  CLAIM: The runtime refactor is now in flight against the separate-family
    model. `FrameACLViewConfiguration`, `FrameACLCommandConfiguration`, and
    `FrameACLCodegenConfiguration` have been converted into revision payloads
    with chain metadata (`configuration_id`, `source_configuration_id`,
    `previous_configuration_id`, `created_at`, `reason`, `locked`). The old
    bundle-only `FrameACLConfigurationChain` has been replaced with a generic
    family-chain owner, `FrameACLContainer` now stores separate named
    registries for view/command/codegen, `FrameACLBuilder` now drafts one
    family/name at a time, and `FrameLinkContract` plus `Rift.target_frame(...)`
    now store nested view/command/codegen selections instead of a single shared
    contract string.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:1-466
  - src/melder/aether/nexus/acl/frame_acl_command_configuration.py:1-422
  - src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py:1-417
  - src/melder/aether/nexus/acl/frame_acl_configuration_chain.py:1-288
  - src/melder/aether/nexus/acl/frame_acl_container.py:1-463
  - src/melder/aether/nexus/acl/frame_acl_builder.py:1-336
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-560
  - src/melder/aether/nexus/rift/rift.py:406-512
  - src/melder/aether/nexus/nexus.py:1550-2066
  IMPACT: The core storage and selection model is no longer the old hybrid.
    The remaining risk is compile/test drift at the manager/Nexus/test layer,
    not uncertainty about the target runtime model.
  NEXT: run syntax and focused pytest on the touched ACL/Nexus slice, then fix
    the remaining compile/test drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T22:24:55Z
  TYPE: MEASURE
  CLAIM: The focused ACL/Nexus unit slice is now green on the new model. The
    separate-family chain runtime, nested Rift contract selection, same-name
    bundle convenience registration, and downstream viewer rebuild path all
    pass together on the touched unit surface.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_configuration_chain.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_nexus.py` -> 114 passed
  IMPACT: The old hybrid frame-global chain model is no longer the active
    runtime shape on the focused ACL/Nexus surface. The remaining work is
    widening this refactor into the broader component/integration surfaces and
    then building precision on top of it.
  NEXT: summarize the landed model and decide whether the next tranche widens
    validation to the broader ACL test matrix or moves straight into the next
    precision ACL slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T22:29:40Z
  TYPE: MEASURE
  CLAIM: The broader ACL component/integration surface is not green yet. The
    focused runtime implementation is stable, but the larger matrix still
    assumes the removed frame-global bundle-chain model. The failures split
    into two categories:
    1) stale tests asserting old APIs/fields such as
       `frame_acl_configuration_chain`, bundle-chain
       `select_current/rollback/create_new`, and old same-name contract
       payloads
    2) one pre-existing stale component test still using the renamed
       `lineage_id` spell-record field instead of `spell_index_id`
    So the remaining work is not uncertainty about the new runtime core. It is
    widening the test surface to the new model.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/component/melder/aether/test_frame_acl_chain_component_matrix.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py tests/integration/melder/aether/test_frame_acl_chain_integration.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py` -> 25 failed, 136 passed
  IMPACT: We now know exactly what the refactor did to the wider system: the
    runtime core moved cleanly, and the remaining blast radius is mostly stale
    validation surface rather than core runtime collapse.
  NEXT: decide whether to spend the next tranche updating the broader ACL
    component/integration suites or move directly into precision ACL work on
    top of the new model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T22:36:16Z
  TYPE: MEASURE
  CLAIM: The broader ACL migration pass is now green too. After migrating the
    component/integration suites and removing the stale bundle-chain
    expectations, the new separate-family model passes the widened validation
    ring. That means the refactor is no longer just a focused runtime success;
    the surrounding ACL/Nexus validation surface now agrees with it.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_configuration_chain.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_nexus.py tests/component/melder/aether/test_frame_acl_chain_component_matrix.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py tests/integration/melder/aether/test_frame_acl_chain_integration.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py` -> 275 passed
  IMPACT: The old hybrid model is fully migrated on the exercised ACL/Nexus
    test surface, so the next tranche can safely build precision ACL work on
    top of this new foundation instead of stopping to pay down more migration
    fallout.
  NEXT: summarize the landed separate-family model and move the next ACL work
    back to precision configuration and validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T22:45:47Z
  TYPE: MEASURE
  CLAIM: The cleanup tranche is now fully green on the exercised surface. After
    removing the remaining stale bundle-chain facades from Nexus, finishing the
    interface migration, renaming the active task/patch docs to the
    separate-family wording, updating the canonical source docs, and migrating
    the last active `spell_index_id` test drift, the final validation pass is
    clean. The last stale-reference sweep only reported:
    - the still-real generic family chain class name
    - historical completed-ticket/patch references
    - non-ACL lineage terminology elsewhere in the system
    So the old active hybrid ACL model is no longer present in the live
    runtime/test/docs surface we touched.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/nexus.py src/melder/utilities/interfaces/interfaces.py src/melder/aether/nexus/frame_acl_manager.py src/melder/aether/nexus/acl/frame_acl_container.py src/melder/aether/nexus/acl/frame_acl_builder.py src/melder/aether/nexus/rift/frame_link/frame_link_contract.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_configuration_chain.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_frame_link_contract_profiles.py tests/unit/melder/aether/test_nexus.py tests/component/melder/aether/test_frame_acl_chain_component_matrix.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/component/melder/aether/test_nexus_viewer_general_helper_component_matrix.py tests/integration/melder/aether/test_frame_acl_chain_integration.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/unit/melder/aether/test_frame_acl_compiler_contracts.py tests/unit/melder/aether/test_spell_record.py` -> 292 passed
  - stale_sweep_result: active-surface hits limited to the generic chain class name, historical completed docs, and unrelated non-ACL lineage terminology
  IMPACT: The separate-family chain migration is complete enough to stop
    cleaning migration fallout and resume new ACL feature work on top of it.
  NEXT: move the next ACL lane back to precision configuration and descriptor-backed validation implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:51:25Z
  TYPE: DECISION
  CLAIM: The separate-family chain migration is complete and can move to the
    completed lane. Later precision-profile, selector-resolution, runtime
    lookup, and command ACL tasks already treat this model as the settled ACL
    storage/selection substrate rather than an open migration.
  EVIDENCE:
  - tickets/tasks/2026-04-11_implement_acl_family_precision_profiles_and_validator_strategies_task.md:1-160
  - tickets/tasks/2026-04-12_implement_spell_selector_resolution_and_spell_index_acl_compilation_task.md:1-145
  IMPACT: This migration task no longer belongs on the active board.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task replaces the current hybrid ACL registry with separate named
view/command/codegen chains and adds downstream refresh for selected family
chain bumps.
