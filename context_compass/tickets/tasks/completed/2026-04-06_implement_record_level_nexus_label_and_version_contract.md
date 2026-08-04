# Task: Implement Record-Level Nexus Label And Version Contract
- Completed: 2026-04-09T11:31:39Z
- Summary: Moved Nexus dataset identity to the record layer and aligned ACL/viewer validation to it.


## Metadata
- Task ID: TASK-2026-04-06-implement-record-level-nexus-label-and-version-contract
- Story: STORY-2026-04-06-split-nexus-record-contract-from-payload-detail
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T19:39:52Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Add `nexus_label` and `nexus_version` to the published record/event contract,
publish all current frame/conduit/spell records as `default:0.0.1`, and wire
the ACL/viewer validation path to that deterministic record contract.

## Ticket Contract
- ENTRY_GATE: the investigation task documented the contract split and the user
  explicitly approved implementation.
- EXECUTION_BOUNDARY: record/event contract identity, spell payload detail
  typing, descriptor-manager publication, ACL validation, and viewer-side label
  wiring only.
- DEPENDENCIES:
  - src/melder/utilities/interfaces/interfaces.py
  - src/melder/aether/nexus/frame_descriptor/frame_record.py
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py
  - src/melder/aether/nexus/frame_descriptor/spell_record.py
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/aether/nexus/acl/frame_acl_validator.py
  - src/melder/aether/nexus/acl/profiles/frame_acl_view_profile.py
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py
- EXIT_GATE: published records carry `nexus_label` / `nexus_version`, spell
  payload detail uses `payload_type`, ACL matching uses the record-level Nexus
  contract, and the viewer binding path can validate against the same label
  cycle.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if record-level contract fields
  are insufficient and a separate published-event envelope is actually
  required.

## Scope
- record interfaces
- frame/conduit/spell record classes
- descriptor payload classes
- descriptor-manager publish path
- ACL validation contract fields
- viewer profile label wiring
- focused tests

## Validation
- `python -m py_compile src/melder/utilities/interfaces/interfaces.py src/melder/aether/nexus/frame_descriptor/frame_record.py src/melder/aether/nexus/frame_descriptor/conduit_record.py src/melder/aether/nexus/frame_descriptor/spell_record.py src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py src/melder/aether/nexus/frame_descriptor_manager.py src/melder/aether/nexus/acl/profiles/frame_acl_view_profile.py src/melder/aether/nexus/acl/profiles/view/safe_profile.py src/melder/aether/nexus/acl/profiles/view/hybrid_profile.py src/melder/aether/nexus/acl/profiles/view/permissive_profile.py src/melder/aether/nexus/acl/frame_acl_view_configuration.py src/melder/aether/nexus/acl/frame_acl_validator.py src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py`
- `python -m pytest -q tests/unit/melder/aether/test_aetheric_frame_descriptor.py tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_frame_acl_chain_matrix.py tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py tests/unit/melder/aether/test_frame_acl_compiler_contracts.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_nexus_passive_ingest.py`
- `python -m pytest -q tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_frame_descriptor_manager_component.py tests/component/melder/aether/test_frame_acl_chain_component_matrix.py`
- `python -m pytest -q tests/integration/melder/aether/test_frame_acl_chain_integration.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py`

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/nexus_record_contract_payload_type/architecture_patch.md
  - system_docs/patches/active/nexus_record_contract_payload_type/component_patch_record_contracts.md
  - system_docs/patches/active/nexus_record_contract_payload_type/component_patch_descriptor_manager.md
  - system_docs/patches/active/nexus_record_contract_payload_type/component_patch_frame_acl_validator.md
  - system_docs/patches/active/nexus_record_contract_payload_type/component_patch_frame_viewer.md
  - system_docs/patches/active/nexus_record_contract_payload_type/code_description_patch_record_contract_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: merge into canonical docs or explicitly retire after the
  record-level Nexus publication contract settles

## Notes
- DATETIME: 2026-04-06T19:50:41Z
  TYPE: PLAN
  CLAIM: The implementation will be executed as one bounded tranche even though
    it spans the two ready follow-up tasks. The user explicitly asked to
    implement the full contract split now, including the viewer-side label
    wiring. The runtime order is: add record-level Nexus contract fields, split
    spell payload detail into `payload_type`, then rewire descriptor-manager,
    ACL, and viewer matching to the new contract.
  EVIDENCE:
  - user_instruction: "go ahead and implement all that and also wire the FrameViewer into it too"
  - tickets/tasks/2026-04-06_investigate_record_level_nexus_label_and_payload_type_split.md:1-90
  IMPACT: The active implementation task needs to cover the whole bounded
    contract migration instead of only the first half.
  NEXT: add patch docs and artifact links, then inspect the affected tests and
    implement the contract migration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T19:52:03Z
  TYPE: PLAN
  CLAIM: Patch-to-implementation mapping is now explicit. `architecture_patch`
    maps to the full contract split, `component_patch_record_contracts`
    maps to interface/record edits, `component_patch_descriptor_manager` maps
    to publish-path and ingest validation edits, `component_patch_frame_acl_validator`
    maps to ACL-side contract rewiring, and `component_patch_frame_viewer`
    maps to viewer-profile binding checks against the new record-level Nexus
    label cycle.
  EVIDENCE:
  - system_docs/patches/active/nexus_record_contract_payload_type/architecture_patch.md:1-18
  - system_docs/patches/active/nexus_record_contract_payload_type/component_patch_record_contracts.md:1-12
  - system_docs/patches/active/nexus_record_contract_payload_type/component_patch_descriptor_manager.md:1-10
  - system_docs/patches/active/nexus_record_contract_payload_type/component_patch_frame_acl_validator.md:1-9
  - system_docs/patches/active/nexus_record_contract_payload_type/component_patch_frame_viewer.md:1-9
  - system_docs/patches/active/nexus_record_contract_payload_type/code_description_patch_record_contract_flow.md:1-6
  IMPACT: Code edits can now proceed without violating the patch gating rules.
  NEXT: edit the record interfaces/classes and payload classes first, then
    rewire manager/validator/viewer and fix the focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T20:07:30Z
  TYPE: MEASURE
  CLAIM: The record-level Nexus contract migration is now green on the targeted
    runtime, component, and integration slices. Published records now carry
    `nexus_label` / `nexus_version`, payloads no longer carry dataset identity,
    spell payload detail is represented by `payload_type`, descriptor-manager
    publish validation checks record contracts separately from payload detail,
    ACL validation now matches record-level Nexus labels plus spell payload
    detail floors, and `FrameViewerProfile` binding validates against the same
    Nexus label cycle.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2223-2278
  - src/melder/utilities/interfaces/interfaces.py:2407-2418
  - src/melder/aether/nexus/frame_descriptor/frame_record.py:8-85
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py:8-86
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:9-134
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py:8-108
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py:8-80
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py:80-256
  - src/melder/aether/nexus/frame_descriptor_manager.py:63-76
  - src/melder/aether/nexus/frame_descriptor_manager.py:274-294
  - src/melder/aether/nexus/frame_descriptor_manager.py:340-355
  - src/melder/aether/nexus/frame_descriptor_manager.py:434-454
  - src/melder/aether/nexus/frame_descriptor_manager.py:796-890
  - src/melder/aether/nexus/acl/profiles/frame_acl_view_profile.py:12-354
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:13-508
  - src/melder/aether/nexus/acl/frame_acl_validator.py:24-731
  - src/melder/aether/nexus/rift/frame_viewer/profiles/frame_viewer_profile.py:13-685
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:462-490
  - tests/unit/melder/aether/test_frame_acl_validator.py:1-431
  - tests/unit/melder/aether/test_frame_viewer_projection.py:1-363
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:1-313
  IMPACT: The active implementation task exit gate is satisfied and the slice
    can move to user review instead of staying in implementation.
  NEXT: review the record-level Nexus contract tranche and either accept it or
    direct the next Nexus viewer/dataset step.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T20:12:26Z
  TYPE: FACT
  CLAIM: The stale-code sweep for this contract lane is clean. There are no
    remaining live `src/` or `tests/` references to the old payload-side
    contract field names; the only obvious leftovers are generated
    `__pycache__` directories under the workspace.
  EVIDENCE:
  - src/: stale-field scan returned no `.py` hits
  - tests/: stale-field scan returned no `.py` hits
  IMPACT: Cleanup can stay narrow and mechanical: remove generated caches
    without touching runtime code again.
  NEXT: delete workspace `__pycache__` directories under `src/` and `tests/`.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This is the active implementation task for the full bounded contract migration.
It moves dataset identity to the record/event layer, keeps spell detail inside
the payload, and rewires ACL/viewer matching to the new Nexus contract.

