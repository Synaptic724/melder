# Task: remove aether cluster and cloud surface

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction after validation handoff. Latest lane state and validation notes remain below.


## Metadata
- Task ID: TASK-2026-05-18-remove-aether-cluster-and-cloud-surface
- Epic: EPIC-2026-05-18-recompose-conduit-aether-spellbook-runtime-ownership
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p0
- Created: 2026-05-18T23:36:43Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Remove the old `Aether` cloud/cluster helper surface, reroute live callers to
the real frame/cloud owners, and update the stale tests that were still
asserting the deleted helper seam.

## Ticket Contract
- ENTRY_GATE: user explicitly redirected work back to the deferred `Aether`
  cleanup and asked to remove the conduit-cloud / conduit-cluster helper
  surface from `Aether`.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aether.py`
  - `src/melder/utilities/interfaces/iaether.py`
  - `src/melder/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/nexus/rift/command_system/capability_command_system.py`
  - `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
  - `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
  - directly implicated test files only
- EXIT_GATE:
  - `Aether` no longer exposes the old cloud/cluster helper methods
  - bounded runtime callers resolve the frame/cloud owner directly
  - stale test buckets now target the cloud-owned seam
  - focused validation confirms the helper-removal slice
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one runtime caller still
  needs a new owner-facing seam instead of the removed helper surface

## Scope Boundaries
- In scope:
  - removal of the old `Aether` cloud/cluster helper methods
  - rerouting bounded runtime callers to frame/cloud owners
  - stale Aether/cluster test migration
- Out of scope:
  - broader conduit public API redesign
  - unrelated runtime or mypy lanes outside the collection blockers surfaced
    during validation

## Steps / Checklist
- [x] remove the old `Aether` cloud/cluster helper surface
- [x] reroute bounded runtime callers to frame/cloud owners
- [x] update stale Aether cluster tests to the cloud seam
- [x] run focused validation and record the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- Aether helper-surface removal for conduit-cloud / conduit-cluster
- bounded caller reroutes to the frame/cloud owner path
- focused validation evidence for the helper-removal slice

## Files / Paths Impacted
- `src/melder/aether/aether.py`
- `src/melder/utilities/interfaces/iaether.py`
- `src/melder/spellbook/spellbook_creation_system.py`
- `src/melder/aether/nexus/rift/command_system/capability_command_system.py`
- `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
- `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py`
- `src/melder/utilities/interfaces/iconduitresolutionstate.py`
- `src/melder/utilities/interfaces/ispell.py`
- `src/melder/aether/conduit/meld/meld.py`
- `tests/unit/melder/aether/test_aether.py`
- `tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py`
- `tests/integration/melder/aether/test_aether_integration_core.py`
- `tests/integration/melder/aether/test_aether_integration_cluster_sharing_internal.py`
- `tests/integration/melder/aether/test_aether_integration_clusters_membership.py`
- `tests/integration/melder/aether/test_aether_integration_frame_cleanup.py`
- `tests/integration/melder/aether/test_aether_integration_registry_ops.py`
- `tests/integration/melder/conduit/test_conduit_integration_cluster_sharing_edges.py`

## Validation
- Ran:
  - `python -m pytest -q tests\unit\melder\aether\test_aether.py -k cluster`
  - `python -m pytest -q tests\integration\melder\aether\test_aether_integration_core.py tests\integration\melder\aether\test_aether_integration_cluster_sharing_internal.py tests\integration\melder\aether\test_aether_integration_clusters_membership.py tests\integration\melder\aether\test_aether_integration_frame_cleanup.py tests\integration\melder\aether\test_aether_integration_registry_ops.py tests\integration\melder\conduit\test_conduit_integration_cluster_sharing_edges.py`
  - `python -m pytest -q tests\unit\melder\aether\conduit\conduit_ward\transfer\test_transfer_of_ownership.py tests\unit\melder\aether\conduit\conduit_ward\transfer\test_transfer_of_ownership_contracts.py`
- Results:
  - `19 passed, 108 deselected`
  - `27 passed`
  - `134 passed`

## Risks / Rollback Notes
- Medium risk. The helper removals are straightforward, but the danger was
  leaving one old Aether helper expectation alive in runtime callers or tests.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/remove_aether_cluster_and_cloud_surface/architecture_patch.md`
  - `system_docs/patches/active/remove_aether_cluster_and_cloud_surface/component_patch_aether.md`
  - `system_docs/patches/active/remove_aether_cluster_and_cloud_surface/component_patch_runtime_callers.md`
  - `system_docs/patches/active/remove_aether_cluster_and_cloud_surface/component_patch_cluster_tests.md`
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: remove patch docs after the owner-surface removal is merged
  into canonical system docs and the task is accepted

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step
  continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-19T01:51:07Z
  TYPE: FACT
  CLAIM: The old Aether cloud/cluster helper surface is removed. `IAether`
    now exposes `_get_existing_frame(...)` instead of the old cloud/cluster
    helper family, and the bounded runtime callers now resolve the frame-owned
    `ConduitCloud` directly instead of routing through `Aether`.
  EVIDENCE:
  - src/melder/aether/aether.py:30-1253
  - src/melder/aether/aether.py:853-868
  - src/melder/utilities/interfaces/iaether.py:1-120
  - src/melder/spellbook/spellbook_creation_system.py:180-180
  - src/melder/spellbook/spellbook_creation_system.py:359-377
  - src/melder/aether/nexus/rift/command_system/capability_command_system.py:91-115
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:144-168
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:518-561
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1067-1122
  IMPACT: Cluster/cloud ownership is now truthful all the way up the live
    caller path. `Aether` is no longer the fake manager for that surface.
  NEXT: verify the stale test ring now targets the cloud seam and rerun the
    focused integration slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T01:51:07Z
  TYPE: FACT
  CLAIM: The stale Aether cluster unit file was still asserting deleted helper
    methods and a frame-owned cluster store. The fix was to move the test seam
    onto a cloud-owned cluster stub and explicitly assert that the removed
    helper methods are no longer exposed on `Aether`.
  EVIDENCE:
  - tests/unit/melder/aether/test_aether.py:21-85
  - tests/unit/melder/aether/test_aether.py:1146-1368
  IMPACT: The unit ring now locks the new owner story instead of forcing the
    old compatibility behavior back into Aether.
  NEXT: rerun the focused Aether cluster unit slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T01:51:07Z
  TYPE: FACT
  CLAIM: Focused validation was initially blocked by unrelated import-surface
    regressions, not by the Aether owner move itself. A missing `Dict` import,
    an undefined creation-context return type, an undefined spellbook surface
    annotation, and a stale transfer fake cluster were all small collection
    blockers that had to be corrected before the owner-removal ring could run.
  EVIDENCE:
  - src/melder/utilities/interfaces/iconduitresolutionstate.py:1-24
  - src/melder/utilities/interfaces/ispell.py:208-208
  - src/melder/aether/conduit/meld/meld.py:970-995
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:389-430
  IMPACT: The extra edits were bounded collection repairs. They were not
    architectural reversions of the Aether cloud/cluster removal.
  NEXT: record the final focused validation results and move the task to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T01:51:07Z
  TYPE: MEASURE
  CLAIM: The helper-removal slice is green in the focused rings. The stale
    Aether cluster unit file, the integration files directly touched by the
    owner move, and the transfer unit files all pass against the new direct
    frame/cloud seam.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests\unit\melder\aether\test_aether.py -k cluster` -> `19 passed, 108 deselected, 2 warnings`
  - validation_result: `python -m pytest -q tests\integration\melder\aether\test_aether_integration_core.py tests\integration\melder\aether\test_aether_integration_cluster_sharing_internal.py tests\integration\melder\aether\test_aether_integration_clusters_membership.py tests\integration\melder\aether\test_aether_integration_frame_cleanup.py tests\integration\melder\aether\test_aether_integration_registry_ops.py tests\integration\melder\conduit\test_conduit_integration_cluster_sharing_edges.py` -> `27 passed, 2 warnings`
  - validation_result: `python -m pytest -q tests\unit\melder\aether\conduit\conduit_ward\transfer\test_transfer_of_ownership.py tests\unit\melder\aether\conduit\conduit_ward\transfer\test_transfer_of_ownership_contracts.py` -> `134 passed, 2 warnings`
  IMPACT: This Aether cleanup stage is ready for user review. The old
    cluster/cloud helper surface is gone and the focused fallout rings are
    stable.
  NEXT: report the completed owner-surface removal to the user and wait for
    the next lane decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-19T02:01:00Z
  TYPE: FACT
  CLAIM: The next surfaced regressions were stale tests, not runtime owner
    drift. Capability/codegen command-system tests were still mocking the old
    `Aether.get_conduit_cloud(...)` seam, and a small Aether/unit/integration
    bucket was still asserting the deleted `_register/_unregister_conduit_cloud`
    helpers.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:2134-2146
  - tests/unit/melder/aether/test_nexus.py:4666-4672
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:318-342
  - tests/unit/melder/aether/test_aether.py:651-660
  - tests/integration/melder/aether/test_aether_integration_error_paths.py:128-141
  - validation_result: `python -m pytest -q tests\unit\melder\aether\test_nexus.py -k "codegen_command_system_can_delegate_selected_runtime_helpers or capability_room_can_access_conduit_cloud_on_dynamic_frame"` -> `2 passed`
  - validation_result: `python -m pytest -q tests\unit\melder\aether\test_rift_runtime_contracts.py -k capability_rift_spaces_expose_conduit_discovery_through_command_system` -> `1 passed`
  - validation_result: `python -m pytest -q tests\unit\melder\aether\test_aether.py -k "register_conduit_cloud or unregister_conduit_cloud or removed_cluster_helpers_are_not_exposed_on_aether"` -> `3 passed`
  - validation_result: `python -m pytest -q tests\integration\melder\aether\test_aether_integration_error_paths.py -k conduit_cloud_register_unregister_missing_frame_raises` -> `1 passed`
  IMPACT: The Aether helper-removal runtime stays intact; the failure class was
    old doubles and deleted-helper expectations only.
  NEXT: report this cleanup with the focused passing commands and wait for the
    next failure bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This stage finishes the deferred Aether cleanup from the conduit/cloud owner
move. `ConduitCloud` remains the real owner, live callers resolve the frame
owner directly, and the remaining stale tests were updated to that seam.
