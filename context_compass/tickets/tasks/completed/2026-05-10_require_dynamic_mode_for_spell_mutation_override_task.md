Completed: 2026-06-06T18:18:17Z
Summary: Closed as historical completed work. The bounded dynamic-mode guard slice landed, and later mutation-override redesign moved the lane beyond this narrower setter gate.

# Task: Require Dynamic Mode For Spell Mutation Override

## Metadata
- Task ID: TASK-2026-05-10-require-dynamic-mode-for-spell-mutation-override
- Story:
- Epic: EPIC-2026-05-10-implement-mutation-contract-runtime-socket-management
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T20:18:16Z
- Updated: 2026-06-06T18:18:17Z

## Objective
Make the spell-level mutation-override API require dynamic mode before it can
apply or clear runtime mutation overlays.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested that `Spell.apply_mutation_override(...)`
  and `Spell.clear_mutation_override(...)` require dynamic mode and throw when
  the spell is not running in a dynamic environment.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spell.py`
  - `src/melder/utilities/interfaces/ispell.py`
  - `tests/unit/melder/spellbook/test_spell.py`
  - `tests/component/melder/spellbook/test_spellbook_component_spell.py`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-10_investigate_mutation_contract_runtime_socket_feature_task.md`
- EXIT_GATE: spell-level mutation-override writes fail fast outside dynamic
  mode and the focused unit/component rings prove the new contract.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if enforcing the dynamic
  gate breaks a wider runtime surface than the bounded spell mutation-override
  API.

## Scope Boundaries
- In scope:
  - dynamic-mode guard on spell mutation-override setters
  - matching interface/docstring updates
  - focused unit/component test updates
- Out of scope:
  - MutationContract runtime enablement
  - new mutation socket getters/setters
  - broader MutationResearch redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested a bounded runtime change before any
  other MutationContract work continues.

## Steps / Checklist
- [ ] Add a dynamic-mode guard to `apply_mutation_override(...)`.
- [ ] Add a dynamic-mode guard to `clear_mutation_override(...)`.
- [ ] Update the `ISpell` contract/docstrings to match.
- [ ] Update the focused spell unit/component tests.
- [ ] Run targeted validation.

## Deliverables
- dynamic-mode-only spell mutation-override setter behavior
- focused passing tests proving the guard

## Files / Paths Impacted
- src/melder/spellbook/spell.py
- src/melder/utilities/interfaces/ispell.py
- tests/unit/melder/spellbook/test_spell.py
- tests/component/melder/spellbook/test_spellbook_component_spell.py

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: some current tests or internal paths assume mutation-override writes
  are valid before conduit ownership/runtime mode stamping.
  Rollback: keep the guard but tighten the affected tests to reflect the
  runtime contract, not constructor-only spell state.

## Applicable Anti-Patterns
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into MutationContract enablement in this task.
- [ ] No silent runtime gating change without matching tests.

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
- DATETIME: 2026-05-10T20:18:16Z
  TYPE: PLAN
  CLAIM: The bounded runtime fix is now isolated from the larger
    MutationContract investigation. Current source shows that spells do carry a
    runtime `_dynamic_environment` bool, but `apply_mutation_override(...)` and
    `clear_mutation_override(...)` do not enforce it. The first implementation
    slice is therefore just to align those setters with the existing dynamic-mode
    posture already used by conduit-level mutation access.
  EVIDENCE:
  - src/melder/spellbook/spell.py:356-356
  - src/melder/spellbook/spell.py:507-509
  - src/melder/spellbook/spell.py:1574-1646
  - src/melder/aether/conduit/conduit.py:3971-4005
  IMPACT: This keeps the edit narrowly scoped and avoids drifting into the
    larger MutationContract runtime-enablement feature.
  NEXT: patch the spell/interface methods and update the focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-10T20:25:23Z
  TYPE: MEASURE
  CLAIM: The dynamic-mode guard is now landed for the spell-side
    mutation-override API. `Spell.apply_mutation_override(...)` and
    `Spell.clear_mutation_override(...)` now raise outside dynamic mode,
    `ISpell` documents the same runtime contract, the focused spell unit tests
    now stamp dynamic mode explicitly when they expect success, and two new
    negative tests prove the non-dynamic failure path. The focused unit and
    component rings are green.
  EVIDENCE:
  - src/melder/spellbook/spell.py:1574-1653
  - src/melder/utilities/interfaces/ispell.py:227-264
  - tests/unit/melder/spellbook/test_spell.py:128-179
  - tests/unit/melder/spellbook/test_spell.py:563-586
  - tests/unit/melder/spellbook/test_spell.py:804-833
  - tests/unit/melder/spellbook/test_spell.py:1000-1072
  - tests/component/melder/spellbook/test_spellbook_component_spell.py:1-16
  - tests/component/melder/spellbook/test_spellbook_component_spell.py:244-287
  - validation_result:
    `python -m py_compile src/melder/spellbook/spell.py src/melder/utilities/interfaces/ispell.py tests/unit/melder/spellbook/test_spell.py tests/component/melder/spellbook/test_spellbook_component_spell.py`
  - validation_result:
    `python -m pytest -q -p no:cacheprovider tests/unit/melder/spellbook/test_spell.py tests/component/melder/spellbook/test_spellbook_component_spell.py` -> `81 passed`
  IMPACT: The spell-side mutation overlay path now matches the existing
    dynamic-mode posture used by conduit-level mutation access instead of being
    a broader always-writable setter.
  NEXT: return the bounded fix for acceptance before widening back into
    MutationContract runtime enablement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded spell-side runtime contract change requiring dynamic
mode for mutation-override writes.
