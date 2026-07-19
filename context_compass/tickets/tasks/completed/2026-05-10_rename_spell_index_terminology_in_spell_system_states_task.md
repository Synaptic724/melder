# Completed: 2026-05-10T12:04:09Z
# Summary: Renamed the SpellSystemStates spell-index API and internal map vocabulary from `lineage` to `index`, then validated the focused runtime/test caller surface.
# Task: Rename Spell Index Terminology In Spell System States

## Metadata
- Task ID: TASK-2026-05-10-rename-spell-index-terminology-in-spell-system-states
- Story: STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T11:03:00Z
- Updated: 2026-05-10T11:09:32Z

## Objective
Rename the SpellIndex-derived `lineage` vocabulary in the SpellSystemStates
family to `index` where the keys are really `SpellIndex.id` values, while
keeping true conduit lineage and mutation-lineage semantics out of scope.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved the next rename target after the
  creation-gate slice and the direct caller map now shows the SpellSystemStates
  cluster is the next high-signal surface.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
  - `src/melder/utilities/interfaces/ispellsystemstates.py`
  - direct source callers broken by the API rename
  - focused tests that encode the current SpellSystemStates spell-index
    terminology
- DEPENDENCIES:
  - STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
  - the prior SpellIndex investigation notes for SpellSystemStates coupling
- EXIT_GATE: the SpellSystemStates family uses `index` wording consistently for
  SpellIndex-derived identities, callers/tests compile, and conduit-lineage
  semantics remain untouched.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the rename collides with a
  real mutation-lineage or conduit-lineage meaning rather than a SpellIndex key.

## Scope Boundaries
- In scope:
  - `register_lineage` / `unregister_lineage` family
  - dirty-lineage/index worklist naming
  - SpellSystemStates internal owner/collection/contract maps keyed by
    `SpellIndex.id`
  - direct callers and tests that break because of those renames
- Out of scope:
  - real conduit lineage
  - spell-crafter validation strategies that model true lineage conflicts
  - viewer `describe_spell_lineage(...)`
  - broader SpellIndex ownership redesign

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the SpellSystemStates rename is landed and the focused
  compile/pytest ring is green.

## Steps / Checklist
- [x] Rename SpellSystemStates public API and internal field names from
      SpellIndex-derived `lineage` to `index`.
- [x] Update `ispellsystemstates.py` to match the new index terminology.
- [x] Update direct runtime callers broken by the API rename.
- [x] Update the focused unit/component/integration tests in this cluster.
- [x] Run focused validation for the touched source/test ring.

## Deliverables
- SpellSystemStates spell-index API renamed to `index`
- interface contract updated to match
- direct callers and focused tests updated

## Files / Paths Impacted
- src/melder/aether/dev_ops/spell_system_states/spell_system_states.py
- src/melder/utilities/interfaces/ispellsystemstates.py
- src/melder/spellbook/spellbook.py
- src/melder/spellbook/spell.py
- src/melder/spellbook/spell_crafter/spell_crafter.py
- src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py
- focused SpellSystemStates test surfaces under `tests/unit/melder/aether/dev_ops/spell_system_states/`
- direct stubbed caller tests that mirror the renamed API

## Validation
- Executed:
  - `python -m py_compile src/melder/aether/dev_ops/spell_system_states/spell_system_states.py src/melder/utilities/interfaces/ispellsystemstates.py src/melder/spellbook/spellbook.py src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py tests/component/melder/aether/dev_ops/change_control_manager/test_change_control_manager_component.py tests/component/melder/aether/dev_ops/spell_system_states/test_spell_system_states_component.py tests/component/melder/aether/dev_ops/test_dev_ops_manager_component.py tests/component/melder/spellbook/spell_crafter/dag/test_spellbook_component_dag_targeting.py tests/component/melder/spellbook/spell_crafter/system/test_spellbook_component_spell_system_adjacency_builder.py tests/component/melder/spellbook/spell_crafter/system/test_spellbook_component_spell_system_adjacency_snapshot.py tests/component/melder/spellbook/spell_crafter/system/test_spellbook_component_spell_system_index.py tests/component/melder/spellbook/spell_crafter/system/test_spellbook_component_spell_system_node.py tests/component/melder/spellbook/spell_crafter/system/test_spellbook_component_spell_system_root_blueprint_builder.py tests/component/melder/spellbook/spell_crafter/system/test_spellbook_component_spell_system_validation_state.py tests/component/melder/spellbook/spell_crafter/system/test_spellbook_component_system_diagnostic.py tests/component/melder/spellbook/spell_crafter/system/validation/test_spellbook_component_system_validation_graph_consistency.py tests/component/melder/spellbook/spell_crafter/system/validation/test_spellbook_component_system_validation_system.py tests/component/melder/spellbook/test_spellbook_component_spell.py tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py tests/component/melder/spellbook/test_spellbook_component_spellbook.py tests/integration/melder/aether/test_aether_integration_devops.py tests/integration/melder/spellbook/test_spellbook_integration_post_conjure_bind_snapshot.py tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py tests/unit/melder/spellbook/test_spellbook.py`
  - `python -m pytest -q -p no:cacheprovider tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py tests/component/melder/aether/dev_ops/spell_system_states/test_spell_system_states_component.py tests/integration/melder/aether/test_aether_integration_devops.py tests/component/melder/spellbook/test_spellbook_component_spell.py tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py tests/component/melder/spellbook/test_spellbook_component_spellbook.py tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py`
- Result:
  - compile validation passed
  - focused pytest ring passed (`387 passed`)

## Risks / Rollback Notes
- Risk: the rename bleeds into true lineage semantics in system validation or
  mutation work and creates a false cleanup.
  Rollback: keep this slice constrained to SpellSystemStates and its direct
  SpellIndex-derived caller surface only.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No conduit-lineage drift.
- [ ] No broad repo-wide lineage rewrite outside the bounded SpellSystemStates family.

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
- DATETIME: 2026-05-10T11:03:00Z
  TYPE: FACT
  CLAIM: The next rename surface is not just two files. `SpellSystemStates`
    still encodes SpellIndex-derived `lineage` vocabulary in its API,
    docstrings, and internal maps, and that API is called directly from
    `spellbook.py`, `spell.py`, `spell_crafter.py`,
    `transfer_of_ownership.py`, and a broad focused test ring.
  EVIDENCE:
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:24-58
  - src/melder/utilities/interfaces/ispellsystemstates.py:15-52
  - src/melder/spellbook/spellbook.py:389-389
  - src/melder/spellbook/spellbook.py:2776-2777
  - src/melder/spellbook/spell.py:1527-1644
  - src/melder/spellbook/spell_crafter/spell_crafter.py:3804-4084
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:384-1137
  IMPACT: This slice needs an explicit task boundary because it is a real API
    rename with direct source callers and test fallout, not just a docstring
    cleanup.
  NEXT: patch the SpellSystemStates family and its direct caller/test ring,
  then validate it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T11:09:32Z
  TYPE: MEASURE
  CLAIM: The SpellSystemStates rename is now landed through the bounded API
    and direct caller surface. The core file now uses `register_index`,
    `unregister_index`, `consume_dirty_indexes`, and the matching internal
    `*_index_*` map names; `ispellsystemstates.py` matches that contract; and
    the direct runtime callers plus the focused SpellSystemStates/spellbook/
    transfer test surfaces were updated and validated.
  EVIDENCE:
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:24-58
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:206-263
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:576-593
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:682-746
  - src/melder/utilities/interfaces/ispellsystemstates.py:15-52
  - src/melder/spellbook/spellbook.py:389-389
  - src/melder/spellbook/spellbook.py:2776-2777
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:534-660
  - validation_result:
    `python -m pytest -q -p no:cacheprovider tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py tests/component/melder/aether/dev_ops/spell_system_states/test_spell_system_states_component.py tests/integration/melder/aether/test_aether_integration_devops.py tests/component/melder/spellbook/test_spellbook_component_spell.py tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py tests/component/melder/spellbook/test_spellbook_component_spellbook.py tests/unit/melder/spellbook/test_spellbook.py tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py` -> `387 passed`
  IMPACT: The next SpellIndex cleanup can move outward from SpellSystemStates
    without this family still teaching the old lineage-first vocabulary.
  NEXT: return the slice for review and decide whether the next rename target
    should be `spellbook.py` / `ispellbook.py` or the outward AR/viewer
    exposure layer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded SpellSystemStates `lineage -> index` rename where
the keys are really `SpellIndex.id` values. Real conduit lineage and
mutation-lineage semantics stay out of scope.
