# Task: Align Command Surface Names To Lower Runtime API
- Completed: 2026-04-13T22:24:59Z
- Summary: Completed the direct command-surface naming-alignment slice after the audited parity renames landed and the focused validation rings passed.

## Metadata
- Task ID: TASK-2026-04-12-align-command-surface-names-to-lower-runtime-api
- Story: STORY-2026-04-12-investigate-capability-rift-space-runtime-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T21:25:38Z
- Updated: 2026-04-13T22:24:59Z

## Objective
Rename drifted command-surface methods so they mirror the real lower Melder
API where the command layer is directly wrapping those runtime seams.

## Ticket Contract
- ENTRY_GATE: the naming/shape audit is complete and the user explicitly told
  me to fix all the command-surface drift before continuing the feature work.
- EXECUTION_BOUNDARY: command system naming alignment, protocol updates,
  focused test/integration updates, patch docs, and board/artifact sync only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py
- EXIT_GATE: drifted command-surface names are aligned to lower runtime API
  names and the focused unit + `rift/` integration rings are green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if full name parity would
  require deeper semantic redesign instead of a bounded rename.

## Scope Boundaries
- In scope:
  - `link_conduits(...)` -> `link(...)`
  - `get_spell_object_by_source_id(...)` -> `get_spell_by_source_id(...)`
  - `get_spell_object_by_index_id(...)` -> `get_spell_by_index_id(...)`
  - `get_spell_object_by_id(...)` -> `get_spell_by_id(...)`
  - protocol/introspection/test/harness updates for those renames
- Out of scope:
  - command-level `meld(...)` helpers
  - deeper semantic redesign of filtered/query surfaces
  - unrelated command-surface expansion

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the audit found concrete naming drift and the user
  explicitly approved fixing all of it before continuing.

## Steps / Checklist
- [x] Stage patch docs and route the task from the board.
- [x] Rename the drifted command-surface methods in base/static command code.
- [x] Update the shared protocol/introspection surface.
- [x] Update focused unit/runtime tests and `rift/` integration harness calls.
- [x] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- aligned command-surface method names
- updated protocol/introspection surface
- updated focused tests and integration harnesses

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/command_system/command_system.py
- src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_nexus.py
- tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py
- tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system/command_system.py src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`
  - `python -m pytest -q tests/integration/melder/aether/rift`

## Risks / Rollback Notes
- Risk: partial rename leaves the command surface inconsistent and breaks the
  JSON harnesses.
  Rollback: patch all direct callsites in one pass and validate both unit and
  integration rings immediately.
- Risk: some names are intentionally room-mediated rather than lower-runtime
  parity.
  Rollback: keep the current slice limited to the audited direct wrappers only.

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
  - system_docs/patches/active/command_surface_name_alignment/architecture_patch.md
  - system_docs/patches/active/command_surface_name_alignment/component_patch_command_system.md
  - system_docs/patches/active/command_surface_name_alignment/component_patch_static_command_system.md
  - system_docs/patches/active/command_surface_name_alignment/component_patch_interfaces.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the naming-alignment behavior is merged into
  canonical docs or intentionally superseded.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T21:25:38Z
  TYPE: FACT
  CLAIM: The naming/shape audit isolated the direct command-surface drift to
    four names that should mirror lower Melder runtime seams:
    `link_conduits(...)`, `get_spell_object_by_source_id(...)`,
    `get_spell_object_by_index_id(...)`, and `get_spell_object_by_id(...)`.
    The real lower API uses `link(...)`, `get_spell_by_source_id` does not
    exist, and the direct lower spell getters are `get_spell_by_id(...)` /
    `get_spell_by_index_id(...)`. This makes the spell-getter rename and the
    link rename the right bounded correction before more helper work lands.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:635-1076
  - src/melder/aether/conduit/conduit.py:1593-1639
  - src/melder/aether/conduit/conduit.py:2874-2930
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:157-180
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:109-119
  IMPACT: We can fix the real naming drift without touching unrelated
    room-mediated helper names yet.
  NEXT: patch the command system, static overrides, interfaces, and direct
    test/harness callsites in one pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T21:34:26Z
  TYPE: MEASURE
  CLAIM: The direct command-surface naming-alignment slice is green on both the
    focused unit/runtime ring and the full shared `rift/` integration folder.
    The live source surface no longer contains the old drifted names; the only
    remaining references are in historical/transition docs that explicitly
    describe the rename set.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system/command_system.py src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> 120 passed
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift` -> 180 passed
  - search_result: live `.py` source search for `get_spell_object_by_*|link_conduits` -> no remaining hits
  IMPACT: The command surface now matches lower Melder names on the audited
    direct wrappers and is safe to build on again.
  NEXT: return to the next feature slice on top of the corrected names:
    command-level `meld(...)` / `meld_existing_spell(...)` helpers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the direct command-surface naming alignment before further
capability helper expansion. The rename slice is now landed and green.
