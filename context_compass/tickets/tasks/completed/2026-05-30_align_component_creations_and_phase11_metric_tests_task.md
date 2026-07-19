# Task: Align component creations and phase11 metric tests

## Metadata
- Task ID: TASK-2026-05-30-align-component-creations-and-phase11-metric-tests
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-30T22:52:00Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Update the directly failing component tests so they match the current
`Creations` raw-object storage/disposal contract and the current Phase 11
execution-plan metric ownership on `SpellCompilerArtifact`.

## Ticket Contract
- ENTRY_GATE: the user provided two new failing clusters and asked for test repair.
- EXECUTION_BOUNDARY:
  - `tests/component/melder/aether/conduit/test_conduit_component_creations.py`
  - `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`
  - `tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py`
  - directly implicated runtime references for evidence only:
    - `src/melder/aether/conduit/creations/creations.py`
    - `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-30_move_creation_extract_restore_contract_to_base_task.md`
  - `tickets/tasks/2026-05-30_move_execution_plan_metrics_to_spell_compiler_artifact_task.md`
- EXIT_GATE:
  - the directly failing component tests match the current runtime contracts
  - focused validation is green
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any failing assertion proves
  runtime behavior contradicts the new storage or artifact-ownership contract.

## Scope Boundaries
- In scope:
  - raw-object `Creations` storage expectation drift
  - disposal-order expectation drift
  - Phase 11 metric ownership drift
  - focused validation of the directly implicated component files
- Out of scope:
  - runtime redesign
  - broader component-suite churn unless a direct contradiction is proven

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the new failures are bounded component-test drift against
  current creations and compiler-artifact contracts.

## Steps / Checklist
- [ ] Read the current runtime contract at the failing seams.
- [ ] Patch the directly failing component test assertions.
- [ ] Run focused validation on the touched component files.
- [ ] Summarize the resulting alignment and any remaining drift.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- aligned component creations tests
- aligned phase11 metric component tests
- focused validation result

## Files / Paths Impacted
- `tests/component/melder/aether/conduit/test_conduit_component_creations.py`
- `tests/component/melder/spellbook/test_phase_component_cprofile_harness.py`
- `tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Ran:
  - `.venv_new\Scripts\python.exe -m py_compile tests/component/melder/aether/conduit/test_conduit_component_creations.py tests/component/melder/spellbook/test_phase_component_cprofile_harness.py tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py`
  - `.venv_new\Scripts\python.exe -m pytest -q tests/component/melder/aether/conduit/test_conduit_component_creations.py tests/component/melder/spellbook/test_phase_component_cprofile_harness.py tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py`
- Result:
  - `24 passed, 1 warning`

## Risks / Rollback Notes
- Risk: the disposal-order assertion might expose a genuine runtime contract
  dispute instead of simple drift.
- Rollback: keep the patch test-only and stop if source evidence becomes ambiguous.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No runtime edits unless a direct contradiction is proven.

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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: one runtime contract seam at a time.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-30T22:52:00Z
  TYPE: FACT
  CLAIM: The new failures are two bounded component-test drift families. First,
    `test_conduit_component_creations.py` is still asserting the old
    `Creation.value` wrapper shape in `_creations` and the old LIFO disposal
    order, even though current `Creations` stores raw objects in `_creations`
    and detached disposal metadata in `_disposable_creations`. Second, the two
    spellbook component tests still read `execution_plan_*` metrics from
    `Spell`, but those metrics now live on `SpellCompilerArtifact` as
    `_execution_plan_*_phase11`.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:281-283
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:309-311
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:337-339
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:419-421
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:456-456
  - src/melder/aether/conduit/creations/creations.py:237-246
  - src/melder/aether/conduit/creations/creations.py:380-391
  - tests/component/melder/spellbook/test_phase_component_cprofile_harness.py:439-443
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1324-1335
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:147-152
  IMPACT: The next step is a localized component-test alignment pass; no runtime
    contradiction is evidenced yet.
  NEXT: patch the creations assertions to raw-object storage/current cleanup
    order, patch the phase11 metric assertions to read compiler-artifact fields,
    then run a focused component ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T22:57:00Z
  TYPE: FACT
  CLAIM: The bounded component-test patch is landed. The creations tests now
    assert raw object storage in `_creations` plus the current insertion-order
    disposal walk, and the two Phase 11 metric tests now read the
    `_execution_plan_*_phase11` fields from `SpellCompilerArtifact` while
    leaving `execution_plan_dispatch_route` on `Spell`.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:266-456
  - tests/component/melder/spellbook/test_phase_component_cprofile_harness.py:423-447
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1324-1335
  IMPACT: The remaining step is focused validation of those three component files.
  NEXT: run `.venv_new\\Scripts\\python.exe -m py_compile` and a focused pytest
    ring for the three touched component files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T22:58:00Z
  TYPE: MEASURE
  CLAIM: The focused component drift ring is green. The creations storage/order
    assertions and the Phase 11 metric ownership assertions all passed together
    under `.venv_new` after the test-only alignment.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:266-456
  - tests/component/melder/spellbook/test_phase_component_cprofile_harness.py:423-447
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1324-1335
  IMPACT: This lane is ready for user review; no runtime patch was needed.
  NEXT: report the aligned component surfaces and focused `24 passed` result to
    the user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task exists to repair the current component-test drift after creations
storage changes and the Phase 11 metric ownership move.

