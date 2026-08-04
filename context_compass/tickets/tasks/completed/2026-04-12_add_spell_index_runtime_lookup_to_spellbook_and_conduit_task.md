# Task: Add Spell Index Runtime Lookup To Spellbook And Conduit
- Completed: 2026-04-13T11:51:25Z
- Summary: Closed the first runtime consumer path for compiled `spell_index_id` outputs after later command ACL/runtime work built on it as settled substrate.

## Metadata
- Task ID: TASK-2026-04-12-add-spell-index-runtime-lookup-to-spellbook-and-conduit
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T08:53:53Z
- Updated: 2026-04-13T11:51:25Z

## Objective
Add a runtime lookup path that resolves a spell by stable `spell_index_id`
through `Spellbook`, then facade that lookup on `Conduit` so the new ACL
compiled spell-index outputs have a real runtime consumer path.

## Ticket Contract
- ENTRY_GATE: the selector-aware ACL/compiler tranche is landed and the user
  explicitly approved adding a runtime lookup method keyed by `spell_index_id`.
- EXECUTION_BOUNDARY: Spellbook lookup, Conduit facade, interfaces, focused
  tests, patch docs, and ticket/board/artifact sync only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-12_implement_spell_selector_resolution_and_spell_index_acl_compilation_task.md
  - src/melder/spellbook/spellbook.py
  - src/melder/aether/conduit/conduit.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/spellbook/test_spellbook.py
  - tests/unit/melder/aether/conduit/test_conduit_facade.py
- EXIT_GATE: Spellbook can resolve a spell by `spell_index_id`, Conduit facades
  that lookup, and the focused runtime slice is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if adding stable lineage lookup
  forces a broader public-runtime lookup redesign than this tranche should own.

## Scope Boundaries
- In scope:
  - Spellbook lookup by `spell_index_id`
  - Conduit facade lookup by `spell_index_id`
  - focused tests and interface updates
- Out of scope:
  - command-system integration
  - ACL/compiler changes
  - broader runtime lookup redesign

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the runtime lookup path is landed and the focused runtime
  plus nearby ACL/viewer slice are green.

## Steps / Checklist
- [x] Stage patch docs and route the task from the board.
- [x] Add Spellbook lookup by stable `spell_index_id`.
- [x] Add Conduit facade lookup by stable `spell_index_id`.
- [x] Update interfaces and focused tests.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Spellbook `spell_index_id` lookup
- Conduit `spell_index_id` facade lookup
- focused tests

## Files / Paths Impacted
- src/melder/spellbook/spellbook.py
- src/melder/aether/conduit/conduit.py
- src/melder/utilities/interfaces/interfaces.py
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- tests/_nexus_viewer_matrix_support.py
- tests/unit/melder/spellbook/test_spellbook.py
- tests/unit/melder/aether/conduit/test_conduit_facade.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/aether/conduit/test_conduit_facade.py`
  - `python -m pytest -q tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/aether/conduit/test_conduit_facade.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_compiler_contracts.py tests/unit/melder/aether/test_frame_viewer_projection.py`

## Risks / Rollback Notes
- Risk: a lineage lookup path could bounce back through current `spell_id` and
  reintroduce version-id coupling.
  Rollback: keep the implementation on top of `SpellIndex` attachment scans and
  `_find_spell/_find_contracted_spell` instead of a second spell-id hop.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
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
  - system_docs/patches/active/spell_index_runtime_lookup/architecture_patch.md
  - system_docs/patches/active/spell_index_runtime_lookup/component_patch_spellbook.md
  - system_docs/patches/active/spell_index_runtime_lookup/component_patch_conduit.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the spell-index runtime lookup model is merged
  into canonical runtime docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T08:53:53Z
  TYPE: FACT
  CLAIM: The current runtime already has the right lower-level seam for a
    stable lineage lookup, but no public API for it. Spellbook can already:
    - find a lineage object by logical signature via `find_spell_index(...)`
    - resolve a local spell from a `SpellIndex` via `_find_spell(...)`
    - resolve a contracted spell from a `SpellIndex` via `_find_contracted_spell(...)`
    and `SpellIndex` already exposes both:
    - stable lineage id via `.id`
    - current version id via `.current`
    So the clean next runtime API is a direct lookup by `spell_index_id`, not a
    second spell-id hop once the `SpellIndex` is found.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:1092-1188
  - src/melder/spellbook/bind/spell_index.py:101-139
  - src/melder/spellbook/bind/spell_index.py:320-329
  - src/melder/aether/conduit/conduit.py:1593-1700
  IMPACT: The implementation can stay narrow and align directly with the new
    ACL compiled spell-index outputs.
  NEXT: add the Spellbook lookup by stable lineage id and then facade it on
    Conduit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T08:58:01Z
  TYPE: FACT
  CLAIM: The runtime consumer path is now landed in source. `Spellbook` now has
    direct stable-lineage lookup by `spell_index_id`, implemented by scanning
    local and contracted `SpellIndex` attachments and then resolving the spell
    directly through `_find_spell(...)` / `_find_contracted_spell(...)`. The
    `Conduit` facade now exposes the same lookup on top of the owned
    Spellbook, and the public interfaces were updated to match.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:1118-1193
  - src/melder/aether/conduit/conduit.py:1640-1678
  - src/melder/utilities/interfaces/interfaces.py:1666-1680
  - src/melder/utilities/interfaces/interfaces.py:4896-4908
  IMPACT: The new ACL compiled `spell_index_id` outputs now have a direct
    runtime consumer path instead of stopping at design/runtime mismatch.
  NEXT: review the landed spell-index runtime lookup tranche and decide whether
    the next step is to consume it in CommandSystem or another higher runtime
    surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T08:58:01Z
  TYPE: MEASURE
  CLAIM: The focused runtime and nearby ACL/viewer slice are green after adding
    the spell-index runtime lookup path. The new Spellbook/Conduit tests pass,
    and the nearby ACL validator/compiler/viewer tests still pass with the
    recent spell-index compiled surface changes.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/aether/conduit/test_conduit_facade.py` -> 191 passed
  - validation_result: `python -m pytest -q tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/aether/conduit/test_conduit_facade.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_compiler_contracts.py tests/unit/melder/aether/test_frame_viewer_projection.py` -> 299 passed
  IMPACT: This runtime consumer slice is ready for review rather than more
    stabilization work.
  NEXT: present the landed lookup path and validation result to the user and
    wait for direction on the next consumer integration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:51:25Z
  TYPE: DECISION
  CLAIM: The stable-lineage runtime lookup slice is complete and can move to
    the completed lane. Later command ACL access enforcement and capability
    command/runtime work now depend on this lookup path as settled runtime
    substrate.
  EVIDENCE:
  - tickets/tasks/2026-04-12_implement_command_acl_access_enforcement_in_command_system_task.md:1-146
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:1258-1380
  IMPACT: This runtime-lookup task no longer belongs on the active board.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task adds the first runtime consumer path for compiled `spell_index_id`
ACL outputs.
