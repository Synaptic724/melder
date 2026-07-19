# Completed: 2026-05-10T12:04:09Z
# Summary: Renamed the outward spell-facing viewer/static-command SpellIndex API and payload wording from `lineage` to `index` and validated the focused aether viewer/test ring.
# Task: Rename Spell Index Terminology In Viewer And Static Command

## Metadata
- Task ID: TASK-2026-05-10-rename-spell-index-terminology-in-viewer-and-static-command
- Story: STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T11:51:42Z
- Updated: 2026-05-10T11:59:29Z

## Objective
Rename the outward spell-facing `lineage` vocabulary in the
viewer/descriptor/static-command layer to `index` where it is really exposing
SpellIndex semantics, without touching real conduit lineage information.

## Ticket Contract
- ENTRY_GATE: the user explicitly said to finish the leftovers and keep real
  conduit lineage intact.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/frame_viewer/`
  - `src/melder/aether/nexus/rift/command_system/static_command_system.py`
  - `src/melder/aether/nexus/frame_descriptor/spell_record.py`
  - the matching outward spell-facing tests under `tests/unit/melder/aether/`
    and `tests/component/melder/aether/`
- DEPENDENCIES:
  - the internal rename slices already landed in creation-context,
    SpellSystemStates, and Spellbook
- EXIT_GATE: the outward spell-facing API uses `index` wording consistently
  where it is exposing SpellIndex semantics, and conduit lineage semantics are
  left untouched.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one of these outward names is
  actually encoding a real lineage concept that should remain separate from
  SpellIndex.

## Scope Boundaries
- In scope:
  - spell-facing viewer methods like `describe_spell_lineage`
  - spell-facing grouping/listing names like `list_lineage_ids`
  - static-command error/doc wording for SpellIndex ids
  - spell-record doc wording
- Out of scope:
  - conduit lineage depth or root-conduit lineage fields
  - ConduitWard lineage semantics
  - `spell_index.py` semantic redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the outward spell-facing rename is landed and the focused
  compile/pytest ring is green.

## Steps / Checklist
- [x] Rename outward spell-facing viewer/static-command method names and docs
      from `lineage` to `index`.
- [x] Update outward spell-facing payload keys where they are clearly
      SpellIndex-derived.
- [x] Update the focused outward tests that depend on those names.
- [x] Run focused validation for the touched ring.

## Deliverables
- outward spell-facing viewer/static-command surface aligned to `index`

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_viewer/view_spell.py
- src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py
- src/melder/aether/nexus/rift/frame_viewer/view_frame.py
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- src/melder/aether/nexus/rift/command_system/static_command_system.py
- src/melder/aether/nexus/frame_descriptor/spell_record.py

## Validation
- Executed:
  - `python -m py_compile src/melder/aether/nexus/frame_descriptor/spell_record.py src/melder/aether/nexus/rift/command_system/command_system.py src/melder/aether/nexus/rift/command_system/static_command_system.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py src/melder/aether/nexus/rift/frame_viewer/view_frame.py src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py src/melder/aether/nexus/rift/frame_viewer/view_spell.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py tests/unit/melder/aether/test_static_command_system_direct.py`
  - `python -m pytest -q -p no:cacheprovider tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py tests/unit/melder/aether/test_static_command_system_direct.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py`
- Result:
  - compile validation passed
  - focused pytest ring passed (`670 passed`)

## Risks / Rollback Notes
- Risk: broad viewer renames accidentally touch real conduit lineage meanings.
  Rollback: keep the slice limited to spell-facing SpellIndex names only and
  leave conduit-lineage structures unchanged.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No conduit-lineage drift.
- [ ] No blind repo-wide lineage rename outside the bounded viewer/static-command layer.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-10T11:51:42Z
  TYPE: FACT
  CLAIM: The remaining outward spell-facing rename surface is concentrated in
    the viewer/static-command layer. Those files expose methods like
    `describe_spell_lineage`, `list_lineage_ids`, and
    `list_spells_by_lineage_id`, plus spell-facing error/doc strings about
    “Spell lineage”, even though the payload field is already `spell_index_id`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/view_spell.py:532-577
  - src/melder/aether/nexus/rift/frame_viewer/view_spell.py:1012-1039
  - src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py:937-961
  - src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py:1514-1537
  - src/melder/aether/nexus/rift/frame_viewer/view_frame.py:1055-1075
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:570-592
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:999-1019
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:3344-3367
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:3692-3710
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:45-123
  IMPACT: This is the clean outward-facing leftover to finish before deciding
    whether `spell_index.py` itself is still a safe same-turn semantic cleanup.
  NEXT: patch the bounded outward spell-facing surface and validate it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T11:59:29Z
  TYPE: MEASURE
  CLAIM: The outward spell-facing SpellIndex rename is now landed. The viewer
    and static-command helper names were shifted from `lineage` to `index`
    where they are really exposing `spell_index_id`, spell-facing payload keys
    like `lineage_groups` / `lineage_ids` / `lineage_count` were shifted to
    `index_*`, and the focused outward aether test ring passed after the API
    change.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_viewer/view_spell.py:532-577
  - src/melder/aether/nexus/rift/frame_viewer/view_spell.py:1012-1039
  - src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py:655-656
  - src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py:937-961
  - src/melder/aether/nexus/rift/frame_viewer/view_multiframe.py:1514-1537
  - src/melder/aether/nexus/rift/frame_viewer/view_frame.py:638-672
  - src/melder/aether/nexus/rift/frame_viewer/view_frame.py:1055-1075
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:570-592
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:999-1019
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:2061-2077
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:3344-3367
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:3692-3710
  - src/melder/aether/nexus/rift/command_system/command_system.py:1275-1285
  - src/melder/aether/nexus/rift/command_system/static_command_system.py:45-123
  - src/melder/aether/nexus/frame_descriptor/spell_record.py:82-95
  - validation_result:
    `python -m pytest -q -p no:cacheprovider tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_viewer_descriptor_host_matrix.py tests/unit/melder/aether/test_nexus_viewer_extended_helper_matrix.py tests/unit/melder/aether/test_static_command_system_direct.py tests/component/melder/aether/test_nexus_viewer_extended_surface_component_matrix.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py` -> `670 passed`
  IMPACT: The outward spell-facing layer now matches the internal SpellIndex
    rename work instead of reintroducing lineage-first vocabulary at the AR
    surface.
  NEXT: decide whether to turn in the completed rename tickets now and whether
    `spell_index.py` / `ispellindex.py` should be treated as a final semantic
    cleanup or a separate design decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the outward spell-facing SpellIndex wording cleanup in the
viewer/descriptor/static-command layer. Real conduit lineage stays out of
scope.
