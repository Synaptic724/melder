# Task: Expand Codegen Command Surface With Selected Runtime Helpers
- Completed: 2026-04-24T01:03:27Z
- Summary: Closed during the 2026-04-24 cleanup after the selected codegen helper set landed green and became the current codegen command baseline.

## Metadata
- Task ID: TASK-2026-04-24-expand-codegen-command-surface-with-selected-runtime-helpers
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-24T00:19:28Z
- Updated: 2026-04-24T01:03:27Z

## Objective
Expand `CodegenCommandSystem` from placeholder-only seams to the explicit
runtime-helper subset the user selected, while keeping codegen separate from
capability inheritance.

## Ticket Contract
- ENTRY_GATE: codegen foundation epic is active, command-surface ownership work
  is complete for base/capability/static, and the user explicitly selected the
  first runtime-helper set for codegen.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/command_system/codegen_command_system.py`
  - directly affected tests in `tests/unit/melder/aether/test_nexus.py`
  - directly affected docs/ticket/board state
- DEPENDENCIES:
  - tickets/epics/2026-04-22_investigate_codegen_foundation_acl_and_validation_strategy_epic.md
  - tickets/tasks/2026-04-23_refactor_command_system_base_and_room_owned_surfaces_task.md
- EXIT_GATE: `CodegenCommandSystem` exposes the selected runtime-helper subset
  plus `validate_codegen(...)` / `execute_codegen(...)`, the helper methods are
  explicitly owned on the codegen class, and the focused codegen/unit ring is
  green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if adding the selected helpers
  cleanly requires a broader codegen architecture or another base-command
  ownership refactor instead of a bounded codegen class patch.

## Scope Boundaries
- In scope:
  - selected runtime helper methods on `CodegenCommandSystem`
  - supported-method discovery for codegen
  - directly affected unit coverage
- Out of scope:
  - AST validation implementation
  - compile/exec implementation
  - codegen history/logging implementation
  - another base/capability/static ownership refactor

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly selected the first nontrivial
  codegen-helper set and asked for implementation now.

## Steps / Checklist
- [x] Stage and link minimal patch artifacts for the codegen command-surface expansion.
- [x] Lock the selected helper matrix in `## Notes`.
- [x] Add the explicitly selected runtime helper methods to `CodegenCommandSystem`.
- [x] Update codegen supported-method discovery to match the selected helper set.
- [x] Add or update focused unit tests.
- [x] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- expanded `CodegenCommandSystem` runtime helper surface
- updated supported-method discovery
- focused unit validation results

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-24_expand_codegen_command_surface_with_selected_runtime_helpers_task.md
- codex/context_compass/attention_board.md
- src/melder/aether/nexus/rift/command_system/codegen_command_system.py
- tests/unit/melder/aether/test_nexus.py

## Validation
- Executed:
  - `python -m py_compile src/melder/aether/nexus/rift/command_system/codegen_command_system.py src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "codegen"`
- Result:
  - `13 passed, 105 deselected, 2 warnings`

## Risks / Rollback Notes
- Risk: `CodegenCommandSystem` supported-method discovery drifts from the actual
  helper methods the class owns.
  Rollback: make the helper tuple explicit on the class and test the exact
  method names.

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
  - system_docs/patches/active/codegen_command_surface_runtime_helpers/architecture_patch.md
  - system_docs/patches/active/codegen_command_surface_runtime_helpers/component_patch_codegen_command_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the codegen command-surface contract is merged
  into canonical docs or intentionally superseded.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-24T00:19:28Z
  TYPE: FACT
  CLAIM: The selected first codegen helper set is explicit. The user wants
    `CodegenCommandSystem` to own a slim runtime-helper surface centered on
    conduit lookup, limited contract/read helpers, target helpers, and the two
    codegen placeholders, without inheriting the full capability surface.
  EVIDENCE:
  - user_instruction: selected method list for codegen helper surface
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:1-123
  IMPACT: The patch can stay bounded to one codegen-class ownership expansion
    instead of reopening base/capability/static command ownership.
  NEXT: stage patch docs and add the selected helpers directly onto
    `CodegenCommandSystem`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-24T00:19:28Z
  TYPE: PLAN
  CLAIM: Patch artifact consumption is now mapped for this codegen surface
    expansion. The architecture patch fixes the public-surface boundary and the
    component patch fixes the exact helper ownership list for
    `CodegenCommandSystem`.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/codegen_command_surface_runtime_helpers/architecture_patch.md:1-23
  - codex/context_compass/system_docs/patches/active/codegen_command_surface_runtime_helpers/component_patch_codegen_command_system.md:1-31
  IMPACT: The implementation can stay bounded to one codegen class plus focused
    tests instead of widening into base/capability/static ownership again.
  NEXT: patch `CodegenCommandSystem`, then update the focused codegen tests and
    validate the selected surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-24T00:19:28Z
  TYPE: FACT
  CLAIM: The selected helper set is now landed directly on
    `CodegenCommandSystem`. The class now explicitly owns:
    `get_conduit_cloud`, `get_conduit_by_id`, `get_conduit_by_name`,
    `list_conduit_ids`, `list_conduit_names`, `count_conduits`,
    `find_conduit_id_by_name`, `list_clusters`, `get_links`,
    `get_contracted_conduits`, `get_spell_in_contracts`,
    `get_spells_in_contract_by_conduit_name`, plus the selected inherited
    helper names in its supported-method discovery:
    `describe_spells_in_conduit`, `find_spell_id`, `find_spell_key`,
    `get_spell_permissions`, `get_target_attribute`, `get_target_method`, and
    `execute_target_method`, together with `validate_codegen` and
    `execute_codegen`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:1-451
  - src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py:13-27
  IMPACT: Codegen now has the slim runtime-helper surface you selected instead
    of a placeholder-only shell or a full capability-grade manual surface.
  NEXT: return the landed codegen helper set for review and decide whether any
    further codegen helper pruning/expansion is wanted before AST work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-24T00:19:28Z
  TYPE: MEASURE
  CLAIM: The selected codegen helper expansion is green on the focused codegen
    unit ring. The updated tests now assert the curated supported-method list,
    placeholder behavior, and one real helper-dispatch slice over the selected
    conduit/runtime helper set.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:1571-1712
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/command_system/codegen_command_system.py src/melder/aether/nexus/rift/rift_space/codegen_rift_space.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "codegen"` -> `13 passed, 105 deselected, 2 warnings`
  IMPACT: The first codegen runtime-helper expansion is stable enough to review
    without widening into AST validation or compile/exec work yet.
  NEXT: let the user decide whether the helper surface is complete enough for
    the next codegen layer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first codegen command-surface expansion beyond the two
placeholders. The selected runtime-helper set is user-chosen and should land as
direct codegen-class ownership, not capability inheritance.
