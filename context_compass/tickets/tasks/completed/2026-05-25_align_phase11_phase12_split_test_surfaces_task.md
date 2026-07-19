# Task: Align Phase 11 / 12 Split Test Surfaces

## Metadata
- Task ID: TASK-2026-05-25-align-phase11-phase12-split-test-surfaces
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-25T05:26:21Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Update the directly implicated `Spellbook` and
`SpellbookCreationSystem` tests so they match the live compiler contract where
Phase 11 planning and Phase 12 executor compilation are separate registered
phase surfaces.

## Ticket Contract
- ENTRY_GATE: the user provided the failing test output and explicitly
  requested test updates for the separated Phase 11/12 compiler model.
- EXECUTION_BOUNDARY:
  - `tests/unit/melder/spellbook/test_spellbook.py`
  - `tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py`
  - directly implicated runtime references in
    `src/melder/aether/spellbook/spellbook_creation_system.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-24_investigate_phase_scheduler_and_spell_compiler_pipeline_task.md`
- EXIT_GATE: the affected tests assert the live `executor_compile` /
  `executor_compile_local` phase surfaces correctly, stub spellbooks expose the
  runtime shape those helpers now require, and focused validation is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any failing assertion proves
  the runtime phase split itself is inconsistent rather than just the tests.

## Scope Boundaries
- In scope:
  - update expected phase-key sets and registered-phase lists
  - update stub spellbook shape for executor-compile unit creation
  - focused validation of the directly implicated test files
- Out of scope:
  - runtime behavior changes
  - broader compiler/scheduler redesign
  - unrelated test cleanup

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the directly implicated unit-test surfaces are aligned to
  the separated Phase 11/12 contract and focused validation is green.

## Steps / Checklist
- [ ] Read the failing `Spellbook` and `SpellbookCreationSystem` test surfaces.
- [ ] Read the current `executor_compile` registration/runtime contract in
      `spellbook_creation_system.py`.
- [ ] Update the directly implicated assertions and stubs only.
- [ ] Run focused validation on the touched test files.
- [ ] Summarize the alignment and any remaining drift.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      implementation.

## Deliverables
- aligned unit-test expectations for split Phase 11/12 registration
- aligned stub spellbook shape for executor compile phase units
- focused validation result

## Files / Paths Impacted
- `tests/unit/melder/spellbook/test_spellbook.py`
- `tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py`
- `codex/context_compass/attention_board.md`
- `codex/context_compass/tickets/tasks/2026-05-25_align_phase11_phase12_split_test_surfaces_task.md`

## Validation
- Not run.
- Recommended commands:
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\test_spellbook.py -k "run_resolution_phases"`
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\test_spellbook_creation_system_resolution_fastpath.py -k "resolution_phases or executor_compile"`

## Risks / Rollback Notes
- Risk: some failures may indicate runtime contract drift rather than stale
  assertions.
  Rollback: stop at the first runtime contradiction and surface it instead of
  mass-editing tests.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: failing assertion drift, concrete runtime-test mismatches, and
  one-step continuation.
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
- DATETIME: 2026-05-25T05:26:21Z
  TYPE: PLAN
  CLAIM: The current failures are bounded test-surface drift around the split
    Phase 11 / 12 registration model. The directly implicated tests still
    expect plan phases to end at `execution_plan`, but the runtime now
    registers a separate `executor_compile` phase and the per-spell phase-unit
    helper now requires `_spells` on stub spellbooks.
  EVIDENCE:
  - user_provided_failure_output
  - src/melder/aether/spellbook/spellbook_creation_system.py:1202-1203
  - src/melder/aether/spellbook/spellbook_creation_system.py:1689-1691
  - src/melder/aether/spellbook/spellbook_creation_system.py:2179-2208
  IMPACT: The next step is direct test alignment, not runtime redesign.
  NEXT: read the failing test sections and patch their expected phase keys plus
    stub shape only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-25T05:26:21Z
  TYPE: FACT
  CLAIM: The direct drift points are now explicit. Runtime registration adds a
    separate `"executor_compile"` phase after `"execution_plan"` for conduit
    resolution, and a separate `"executor_compile_local"` phase after
    `"execution_plan_local"` for target-local plan reruns. The phase-factory
    implementation uses the same `_build_per_spell_phase_units(...)` helper as
    other per-spell phases, so any stub spellbook that reaches this path now
    needs a minimal `_spells` map. The currently failing tests still assert the
    old pre-split phase key sets and do not provide that stub shape.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1201-1205
  - src/melder/aether/spellbook/spellbook_creation_system.py:1687-1693
  - src/melder/aether/spellbook/spellbook_creation_system.py:2179-2210
  - src/melder/aether/spellbook/spellbook_creation_system.py:1816-1870
  - tests/unit/melder/spellbook/test_spellbook.py:2573-2585
  - tests/unit/melder/spellbook/test_spellbook.py:3270-3280
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:75-109
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:343-367
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:1245-1250
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:1402-1415
  IMPACT: The fix is test-only and narrow: extend expected phase names, extend
    stub installer coverage for `executor_compile`, and give `_StubSpellbook`
    a minimal `_spells` surface.
  NEXT: patch the two failing test files, then run the focused unit rings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-25T05:26:21Z
  TYPE: FACT
  CLAIM: The direct test alignment cut is in. The broad `Spellbook` unit file
    now treats `executor_compile` as part of the expected conduit-resolution
    phase key set. The fastpath resolution tests now install a stub
    `phase_executor_compile_factory`, expect `executor_compile` /
    `executor_compile_local` in the registered phase surfaces, and give the
    stub spellbook a minimal `_spells` map so the real per-spell phase-unit
    helper contract is satisfied when the executor-compile factory is not
    monkeypatched away.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spellbook.py:2573-2587
  - tests/unit/melder/spellbook/test_spellbook.py:3270-3284
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:104-109
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:277-284
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:345-367
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:441-460
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:525-536
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:1245-1250
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:1308-1318
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:1410-1415
  IMPACT: The remaining question is validation only: whether the targeted
    failing rings are now green without introducing any new stale assumptions.
  NEXT: run the focused `Spellbook` and `SpellbookCreationSystem` unit rings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-25T05:26:21Z
  TYPE: MEASURE
  CLAIM: The directly failing nodes from the pasted full-suite output are now
    green after the split-surface alignment. The two `Spellbook` phase-key
    assertions and the five `SpellbookCreationSystem` scheduler/wrapper tests
    all passed together in one focused run: `7 passed, 1 warning`.
  EVIDENCE:
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\test_spellbook.py::test_run_resolution_phases_success tests\unit\melder\spellbook\test_spellbook.py::test_run_resolution_phases_with_multiple_spells tests\unit\melder\spellbook\test_spellbook_creation_system_resolution_fastpath.py::test_run_resolution_phases_for_conduit_uses_one_scheduler_lifecycle tests\unit\melder\spellbook\test_spellbook_creation_system_resolution_fastpath.py::test_run_resolution_phases_for_conduit_skips_plan_group_when_foundational_errors_exist tests\unit\melder\spellbook\test_spellbook_creation_system_resolution_fastpath.py::test_run_resolution_phases_for_conduit_skips_plan_group_when_jit_mode_is_enabled tests\unit\melder\spellbook\test_spellbook_creation_system_resolution_fastpath.py::test_run_target_foundational_and_plan_resolution_phase_wrappers_register_expected_phases tests\unit\melder\spellbook\test_spellbook_creation_system_resolution_fastpath.py::test_run_conduit_foundational_and_plan_resolution_phase_wrappers_register_expected_phases`
  IMPACT: The split-contract alignment is directionally correct. The remaining
    step is confidence on the full local test surfaces, not just the exact
    failed nodes.
  NEXT: run the full two touched unit files and confirm no additional local
    drift remains.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-25T05:30:51Z
  TYPE: MEASURE
  CLAIM: The full local surface for the two touched unit files is green after
    the split-surface test alignment. Full result:
    `179 passed, 1 warning`.
  EVIDENCE:
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\test_spellbook.py tests\unit\melder\spellbook\test_spellbook_creation_system_resolution_fastpath.py`
  IMPACT: The direct Phase 11/12 split test drift in these two files is
    resolved without touching runtime code.
  NEXT: get user review on the aligned test surface and only widen if the full
    suite shows a different remaining seam elsewhere.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is a narrow test-alignment slice for the separated Phase 11/12
compiler contract. It should stay limited to the directly failing tests and
their immediate stubs.

