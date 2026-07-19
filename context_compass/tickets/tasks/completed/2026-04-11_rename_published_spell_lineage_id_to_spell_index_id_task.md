# Task: Rename Published Spell Lineage Id To Spell Index Id
- Completed: 2026-04-13T11:51:25Z
- Summary: Closed the published `spell_index_id` contract rename after later ACL/runtime work treated it as settled substrate.

## Metadata
- Task ID: TASK-2026-04-11-rename-published-spell-lineage-id-to-spell-index-id
- Story: STORY-2026-04-11-design-command-acl-enforcement-for-static-and-capability
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T19:07:44Z
- Updated: 2026-04-13T11:51:25Z

## Objective
Rename the published spell lineage field from `lineage_id` to
`spell_index_id` across the descriptor/viewer/public-contract surface.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested renaming the published field after
  confirming that `SpellRecord` already publishes the stable SpellIndex
  identity under the old `lineage_id` name.
- EXECUTION_BOUNDARY: descriptor spell-record contract, descriptor publication
  path, frame-viewer/view-profile surfaces, focused tests, and system-doc
  references only.
- DEPENDENCIES:
  - tickets/stories/2026-04-11_design_command_acl_enforcement_for_static_and_capability_story.md
  - src/melder/aether/nexus/frame_descriptor/spell_record.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_aetheric_frame_descriptor.py
  - tests/unit/melder/aether/test_frame_viewer_projection.py
  - tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py
  - tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py
- EXIT_GATE: the published contract uses `spell_index_id` consistently and the
  focused descriptor/viewer tests are green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the rename forces broader
  backwards-compat shims instead of a clean contract swap.

## Scope Boundaries
- In scope:
  - `SpellRecord` field rename
  - descriptor-manager publish path rename
  - frame-viewer public output rename
  - focused tests and relevant system-doc references
- Out of scope:
  - unrelated internal lineage variables in dev-ops/runtime
  - ACL semantics beyond this identifier rename
  - backward-compat aliasing

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved renaming the published field
  and requested a sweep so the public surface does not end up mixed.

## Steps / Checklist
- [ ] Record the rename surface and non-goals in `## Notes`.
- [ ] Create patch docs for the public-contract rename.
- [ ] Rename the published contract to `spell_index_id`.
- [ ] Update focused descriptor/viewer tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- renamed published spell-record field
- viewer/output contract updated to `spell_index_id`
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/frame_descriptor/spell_record.py
- src/melder/aether/nexus/frame_descriptor_manager.py
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py
- src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_aetheric_frame_descriptor.py
- tests/unit/melder/aether/test_frame_viewer_projection.py
- tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py
- tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_aetheric_frame_descriptor.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py`

## Risks / Rollback Notes
- Risk: mixed `lineage_id` / `spell_index_id` output survives in the viewer
  surface.
  Rollback: keep the rename scoped to the published/viewer contract and sweep
  every focused viewer/descriptor test before calling it done.

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
  - system_docs/patches/active/published_spell_index_id_contract/architecture_patch.md
  - system_docs/patches/active/published_spell_index_id_contract/component_patch_spell_record.md
  - system_docs/patches/active/published_spell_index_id_contract/component_patch_frame_viewer.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the published spell-record contract rename is
  merged into canonical docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-11T19:14:18Z
  TYPE: FACT
  CLAIM: The published spell-record contract rename is now landed in source.
    `SpellRecord` now carries `spell_index_id`, the descriptor-manager publish
    path constructs the record with that field name, the spell-record protocol
    in `interfaces.py` matches it, and the descriptor/viewer public outputs now
    emit `spell_index_id` instead of `lineage_id`.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:1-167
  - src/melder/aether/nexus/frame_descriptor_manager.py:479-523
  - src/melder/utilities/interfaces/interfaces.py:2686-2703
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1027-1035
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1286-1303
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:174-186
  IMPACT: The stable SpellIndex identity is now published under the correct
    public name, which gives the upcoming ACL compilation work a cleaner target
    identity contract.
  NEXT: run the focused descriptor/viewer suites and confirm the rename sweep
    is green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T19:14:18Z
  TYPE: MEASURE
  CLAIM: The focused descriptor/viewer surface is green after the rename. The
    descriptor record tests, frame-viewer projection tests, Nexus frame-surface
    projection tests, and both viewer matrix suites all pass with the new
    `spell_index_id` contract.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_aetheric_frame_descriptor.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py` -> 394 passed
  IMPACT: The published contract rename is ready for review without mixed
    `lineage_id`/`spell_index_id` state on the viewer/descriptor surface.
  NEXT: review the contract rename and then return to ACL enforcement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T19:07:44Z
  TYPE: FACT
  CLAIM: The stable SpellIndex identity is already published today, but under
    the wrong public name. `SpellRecord` carries `lineage_id`, the descriptor
    manager publishes it from `spell.spell_index.id`, and the frame-viewer
    surfaces read and emit that same field. The rename target is therefore the
    published/viewer contract, not the broader internal lineage terminology
    used across dev-ops and spell-system code.
  EVIDENCE:
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:1-167
  - src/melder/aether/nexus/frame_descriptor_manager.py:479-523
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1051-1051
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_frame.py:1293-1293
  - src/melder/aether/nexus/rift/frame_viewer/profiles/general/view_spell.py:181-181
  IMPACT: We can do a clean public-contract rename without reopening unrelated
    runtime/dev-ops lineage internals.
  NEXT: create the patch docs and rename the public field everywhere on the
    published/viewer surface in one sweep.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:51:25Z
  TYPE: DECISION
  CLAIM: The published `spell_index_id` rename is complete and can move to the
    completed lane. Later precision ACL, runtime lookup, and command ACL work
    all depend on this renamed public contract and no longer treat it as a
    pending review item.
  EVIDENCE:
  - tickets/tasks/2026-04-12_implement_spell_selector_resolution_and_spell_index_acl_compilation_task.md:1-145
  - tickets/tasks/2026-04-12_add_spell_index_runtime_lookup_to_spellbook_and_conduit_task.md:1-131
  IMPACT: This public-contract rename no longer belongs on the active board.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task renames the published spell-record field only. The focused
descriptor/viewer suites are green and the public contract is ready for review
before returning to ACL enforcement.
