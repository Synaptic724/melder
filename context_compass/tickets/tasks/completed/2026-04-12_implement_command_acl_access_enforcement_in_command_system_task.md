# Task: Implement Command ACL Access Enforcement In Command System
- Completed: 2026-04-13T11:51:25Z
- Summary: Closed the first command ACL access-enforcement slice after later command/runtime work built on it as settled access substrate.

## Metadata
- Task ID: TASK-2026-04-12-implement-command-acl-access-enforcement-in-command-system
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T10:17:27Z
- Updated: 2026-04-13T11:51:25Z

## Objective
Implement real command ACL enforcement on command-system access/fetch paths by
compiling command enablement into the ACL surface and making `CommandSystem`
honor that compiled state for frames, conduits, and spells keyed by
`spell_index_id`.

## Ticket Contract
- ENTRY_GATE: the selector-aware precision ACL tranche and the runtime
  `spell_index_id` lookup tranche are landed and green, and the user explicitly
  approved moving into command-system enforcement.
- EXECUTION_BOUNDARY: compiled ACL surface, ACL compiler, command-system
  access/fetch paths, focused tests, patch docs, and ticket/board/artifact sync
  only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-12_implement_spell_selector_resolution_and_spell_index_acl_compilation_task.md
  - tickets/tasks/2026-04-12_add_spell_index_runtime_lookup_to_spellbook_and_conduit_task.md
  - tickets/tasks/2026-04-11_design_command_acl_enforcement_plan.md
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py
  - src/melder/aether/nexus/acl/frame_acl_compiler.py
  - src/melder/aether/nexus/rift/rift_space/command_system.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: command enablement is compiled into the ACL surface, command access
  paths enforce frame/conduit/spell ACL state, and the focused ACL/Nexus/runtime
  slice is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if enforcing workstation-bound
  objects would require a provenance/wrapper model beyond the agreed access/fetch
  boundary.

## Scope Boundaries
- In scope:
  - compiled command enablement for frame/conduit/spell
  - command-system enforcement on selected-target and direct fetch paths
  - `spell_index_id`-based spell gating
  - focused tests
- Out of scope:
  - workstation-bound object policing after bind
  - room-mode policy changes beyond access gating
  - viewer projection redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved implementing command ACL
  access enforcement on top of the new precision and runtime lookup substrate.

## Steps / Checklist
- [ ] Stage patch docs and route the task from the board.
- [ ] Extend the compiled ACL surface with command enablement outputs.
- [ ] Extend the compiler to derive frame/conduit/spell command enablement.
- [ ] Enforce command ACL on `CommandSystem` selected-target and direct getter paths.
- [ ] Update focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- compiled command enablement outputs
- command-system ACL checks on access/fetch paths
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py
- src/melder/aether/nexus/acl/frame_acl_compiler.py
- src/melder/aether/nexus/rift/rift_space/command_system.py
- tests/unit/melder/aether/test_nexus.py
- tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py
- tests/unit/melder/aether/test_frame_acl_compiler_contracts.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py tests/unit/melder/aether/test_frame_acl_compiler_contracts.py`

## Risks / Rollback Notes
- Risk: we accidentally try to enforce ACL on already-bound workstation objects
  even though the agreed model only gates access/fetch paths.
  Rollback: keep enforcement limited to selected-target/direct getter paths and
  leave workstation-bound objects alone after bind.

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
  - system_docs/patches/active/command_system_acl_access_enforcement/architecture_patch.md
  - system_docs/patches/active/command_system_acl_access_enforcement/component_patch_frame_acl_compiler.md
  - system_docs/patches/active/command_system_acl_access_enforcement/component_patch_command_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until command ACL access enforcement is merged into
  canonical ACL/runtime docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T10:17:27Z
  TYPE: FACT
  CLAIM: The command ACL/runtime seam is now clear. The compiler still emits
    only broad `allowed_commands` plus view visibility, while `CommandSystem`
    still performs no ACL checks on selected-target or direct getter paths.
    The agreed boundary is also clear now:
    - enforce ACL on access/fetch paths
    - do not police already-bound workstation objects after bind
    So the clean next slice is compiled command enablement plus command-system
    access gating keyed by frame/conduit/spell identities and `spell_index_id`
    for spell targets.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:35-40
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:73-170
  - src/melder/aether/nexus/rift/rift_space/command_system.py:1-520
  - user_direction: "ACLs gate access before bind"
  - user_direction: "once bound, the object is just a Python object in local workspace"
  IMPACT: We can implement real command ACL behavior now without inventing a
    provenance/wrapper system for workstation-bound objects.
  NEXT: extend the compiled surface for command enablement and wire those checks
    into `CommandSystem`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T10:28:00Z
  TYPE: FACT
  CLAIM: The compiled command-enablement substrate already exists in source, so
    this task no longer needs new surface/compiler fields as its main work.
    `CompiledFrameACLAccessSurface` already carries:
    - `command_frame_enabled`
    - `enabled_conduit_ids`
    - `enabled_spell_index_ids`
    and `FrameACLCompiler._compile_command_enablement(...)` already derives
    them. The real remaining runtime gap is `CommandSystem`, which still does
    no ACL checks on selected-target or direct getter paths. There is also one
    supporting bug in `FrameViewer`: `_clone_compiled_access_surface(...)`
    currently drops the command enablement fields when cloning a compiled ACL
    surface, which would silently strip command state from viewer clones.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:30-57
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:138-148
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:381-438
  - src/melder/aether/nexus/rift/rift_space/command_system.py:20-24
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:3281-3310
  IMPACT: The implementation should stay narrow:
    - patch runtime gating in `CommandSystem`
    - patch the viewer clone helper so command ACL state survives clone paths
    - update focused tests
    and not waste the tranche on already-landed compiler work.
  NEXT: patch the task-bound runtime files and focused tests around command ACL
    access denial and cloned compiled-surface preservation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T10:33:07Z
  TYPE: FACT
  CLAIM: The implementation slice is now landed in source. `CommandSystem`
    enforces compiled command ACL state on:
    - selected-target access
    - conduit fetch by id/name
    - spell fetch by source id / spell id / spell_index_id
    while still leaving already-bound workstation targets outside post-bind ACL
    policing. The spell-source-id path now resolves through stable
    `spell_index_id`, and `FrameViewer._clone_compiled_access_surface(...)`
    now preserves the compiled command fields instead of dropping them during
    clone paths.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system.py:1-608
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:3281-3319
  - tests/unit/melder/aether/test_nexus.py:143-220
  - tests/unit/melder/aether/test_nexus.py:1306-1471
  IMPACT: The first real command ACL runtime boundary now exists on access/fetch
    paths, and viewer clones no longer silently lose command enablement state.
  NEXT: validate the focused ACL/Nexus/runtime ring and record the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T10:33:07Z
  TYPE: MEASURE
  CLAIM: The focused command ACL access ring is green. The touched runtime,
    viewer-clone path, and focused ACL contract tests all pass after the
    command-gating patch.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_acl_compiled_access_surface.py tests/unit/melder/aether/test_frame_acl_compiler_contracts.py` -> 97 passed
  IMPACT: The task is ready for user review or for a deliberate widen to the
    next runtime/ACL slice instead of more local stabilization.
  NEXT: summarize the landed command ACL enforcement behavior and ask for the
    next direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:51:25Z
  TYPE: DECISION
  CLAIM: The first command ACL access-enforcement slice is complete and can
    move to the completed lane. Later command-system composition, shared
    manual-runtime expansion, and capability-room work all build on this access
    gating as settled substrate.
  EVIDENCE:
  - tickets/tasks/2026-04-12_refactor_rift_space_to_mode_specific_command_systems_task.md:1-153
  - tickets/tasks/2026-04-12_expand_shared_command_system_manual_runtime_surface_task.md:1-170
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:132-2111
  IMPACT: This command ACL enforcement task no longer belongs on the active
    board.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the first real command ACL runtime enforcement slice on
top of the new precision and spell-index runtime substrate.
