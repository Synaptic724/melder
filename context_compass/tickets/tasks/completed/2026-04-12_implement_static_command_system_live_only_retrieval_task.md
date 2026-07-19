# Task: Implement Static Command System Live Only Retrieval
- Completed: 2026-04-13T11:51:25Z
- Summary: Archived the historical static live-only retrieval slice after its capability assumptions and retrieval-layer approach were superseded.

## Metadata
- Task ID: TASK-2026-04-12-implement-static-command-system-live-only-retrieval
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T11:34:20Z
- Updated: 2026-04-13T11:51:25Z

## Objective
Replace the current blanket raw-object denial in `StaticCommandSystem` with
true live-only spell retrieval so the existing command getters return a spell
runtime object only when it already exists and fail otherwise without creating
anything.

## Ticket Contract
- ENTRY_GATE: the mode-specific command-system composition refactor is landed
  and green, and the user explicitly asked to keep the same command methods but
  make static mode use live-only behavior instead of a separate static API.
- EXECUTION_BOUNDARY: static command system, supporting conduit/creation live
  retrieval helpers, focused tests, patch docs, and board/artifact routing
  only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-12_refactor_rift_space_to_mode_specific_command_systems_task.md
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py
  - src/melder/aether/conduit/conduit.py
  - src/melder/aether/conduit/creations/creation.py
  - src/melder/aether/conduit/creations/creations.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: `StaticCommandSystem` uses the existing command getters but only
  returns spell runtime objects when a live creation already exists, and the
  focused runtime ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if static live-only retrieval
  requires a broader handle/capability design instead of a narrow live-creation
  probe plus retrieval helper.

## Scope Boundaries
- In scope:
  - static spell getter behavior on the existing command methods
  - supporting internal live-creation retrieval helper(s)
  - focused tests
- Out of scope:
  - capability handle design
  - workstation-bound object policing
  - broad conduit/runtime API redesign
  - many-creation ambiguity redesign beyond fail-fast behavior

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the current static command surface is too coarse; the user
  explicitly wants the existing command methods to behave in a static live-only
  way instead of exposing a separate static-only API.

## Steps / Checklist
- [x] Stage patch docs and route the new task from the board.
- [x] Add an internal live-spell-runtime retrieval helper over existing conduit/creation truth.
- [x] Override static spell getters to return only already-live spell runtime objects.
- [x] Update focused tests for live vs not-live static behavior.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- static live-only spell retrieval on existing command methods
- supporting internal live retrieval helper
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py
- src/melder/aether/conduit/conduit.py
- src/melder/aether/conduit/creations/creations.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/conduit/conduit.py src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: we accidentally route static retrieval through a creation path and fake
  “live-only” semantics.
  Rollback: keep the implementation on top of current live creation storage and
  fail when no live creation exists.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/static_command_system_live_only_retrieval/architecture_patch.md
  - system_docs/patches/active/static_command_system_live_only_retrieval/component_patch_static_command_system.md
  - system_docs/patches/active/static_command_system_live_only_retrieval/component_patch_conduit.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until static live-only retrieval is merged into
  canonical runtime docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T11:34:20Z
  TYPE: FACT
  CLAIM: The current static substrate is still missing the actual live-object
    retrieval half of the static contract. `Meld.describe_live_creation_status`
    can already tell whether a resolved spell has a live creation, but
    `Creations` still does not expose a clean retrieval helper for the existing
    object in the non-spellspace singleton/owner-creations paths. That is why
    the first static cut only blocked raw spell getters. The next narrow move is
    to add an internal live-retrieval helper on top of the current
    spell/owner-creations truth and then make `StaticCommandSystem` use the
    existing spell getter names with live-only semantics.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:434-520
  - src/melder/aether/conduit/meld/meld.py:634-766
  - src/melder/aether/conduit/creations/creations.py:279-376
  - src/melder/aether/conduit/creations/creations.py:519-542
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:1-42
  IMPACT: We can keep the same command methods for static mode, but we need one
    more internal runtime helper before those methods can do true live-only
    retrieval instead of blanket denial.
  NEXT: stage the patch docs and implement the internal live-retrieval helper
    plus the static command-system override.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T11:37:21Z
  TYPE: FACT
  CLAIM: The static live-only slice is now landed in source. `Conduit` now owns
    one narrow internal helper for returning the already-live spell runtime
    object by `spell_index_id` from current creation storage, and
    `StaticCommandSystem` now uses the existing spell getter names with
    live-only behavior instead of blanket denial. The static room now:
    - still allows frame/conduit runtime access
    - returns a spell runtime object only when a live creation already exists
    - fails fast when the spell is published but not live
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1634-1709
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:1-140
  - tests/unit/melder/aether/test_nexus.py:1667-1837
  IMPACT: Static mode is no longer just a blanket raw-spell denial. It now has
    real live-only spell semantics on the existing command getters.
  NEXT: validate the focused and nearby runtime rings and record the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T11:37:21Z
  TYPE: MEASURE
  CLAIM: The static live-only retrieval slice is green on the focused and
    nearby ACL/Nexus/runtime rings. The updated static frame/conduit/spell
    behavior tests pass, and the nearby ACL/viewer/compiler ring still passes
    with the new live-only retrieval path.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/conduit/conduit.py src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py` -> 88 passed
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py tests/unit/melder/aether/test_frame_viewer_projection.py tests/unit/melder/aether/test_nexus.py` -> 167 passed
  IMPACT: The static command surface now has a meaningful live-only retrieval
    behavior and is ready for review or for the next capability-surface step.
  NEXT: summarize the landed static behavior and decide whether the next slice
    is capability handles or another static/runtime boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T12:39:23Z
  TYPE: CONFLICT
  CLAIM: The live-only static slice was implemented on the wrong layer. The
    existing `get_spell_by_id(...)` and `get_spell_by_index_id(...)` contract
    returns `ISpell` definitions, not created runtime instances, and the added
    `_get_live_spell_runtime_object_by_index_id(...)` helper on `Conduit`
    introduced new lookup/runtime behavior in a layer the user does not want
    carrying more spell-lookup duplication. The clean recovery is to back out
    the static live-only retrieval slice and return to the last known-good
    boundary:
    mode-specific command-system composition without the added conduit helper.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1593-1668
  - src/melder/spellbook/spellbook.py:1092-1198
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:1-140
  - user_direction: "finding a spell doesn't return the object it returns the spell object"
  IMPACT: We should revert the last static live-only retrieval tranche before
    doing more design work, while preserving the earlier `RiftSpace` command
    composition refactor.
  NEXT: remove the added conduit helper and restore `StaticCommandSystem` plus
    the focused tests to the last known-good state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:51:25Z
  TYPE: DECISION
  CLAIM: This task is historical rather than current. Its own notes already
    record that the live-only retrieval slice was implemented on the wrong
    layer and conflicted with the intended spell/runtime contract. Later static
    and capability work moved the room model forward without treating this task
    as the settled boundary.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-12_implement_static_command_system_live_only_retrieval_task.md:125-138
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:125-301
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py:6-23
  IMPACT: The task should not remain on the active board because it is no
    longer the live direction for room-mode runtime behavior.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task turns `StaticCommandSystem` from blanket raw-object denial into
live-only spell retrieval on the existing command surface.
