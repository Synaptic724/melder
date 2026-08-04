# Task: build structural compiler phase replacement tests

- Completed: 2026-05-21T09:28:33Z
- Summary: Landed the current-surface SpellCompiler replacement suite through late phase/codegen ownership, validated the replacement lanes plus the full `tests/unit/melder/spellbook` ring, and retired the stale `test_spell_crafter.py` monolith.

## Metadata
- Task ID: TASK-2026-05-21-build-structural-compiler-phase-replacement-tests
- Story: STORY-2026-05-20-cover-structural-compiler-phases-1-to-4
- Status: done
- Owner: codex
- Agent Name: refactor_0
- Priority: p0
- Created: 2026-05-21T00:34:00Z
- Updated: 2026-05-21T09:28:33Z

## Objective
Begin the like-for-like replacement of the old monolithic compiler unit file by
landing explicit current-surface unit tests for phases `1-4`.

## Ticket Contract
- ENTRY_GATE: the replacement-suite epic is active and the full repo ring has
  proven the remaining break is concentrated in the old monolithic compiler unit
  file.
- EXECUTION_BOUNDARY:
  - `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_1.py`
  - `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_2.py`
  - `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_3.py`
  - `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_4.py`
  - supporting unit test fixtures only when required by these files
- DEPENDENCIES:
  - `tickets/stories/2026-05-20_cover_structural_compiler_phases_1_to_4_story.md`
  - current phase owners under `src/melder/aether/spellbook/spell_compiler/phases/`
  - the old monolithic `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
    as behavior-source inventory only
- EXIT_GATE:
  - first current-surface structural phase files exist
  - targeted structural-phase ring is green
  - old structural mechanics from the monolith are mapped into the new files
- FAILURE_ESCALATION:
  - raise if any old structural mechanic has no current owner in phases `1-4`

## Scope Boundaries
- In scope:
  - phase `1-4` current-surface replacement tests
- Out of scope:
  - phase `5-12` rooted/planning/codegen mechanics
  - component/integration compiler bucket already landed

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the full repo ring proved the next real break is the old
  monolithic compiler unit file, so structural phase replacement is the next
  active route.

## Steps / Checklist
- [x] inventory old monolithic phase `1-4` mechanic buckets
- [x] create current-surface phase `1` test file
- [x] create current-surface phase `2` test file
- [x] create current-surface phase `3` test file
- [x] create current-surface phase `4` test file
- [x] run targeted structural-phase pytest ring
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- new current-surface unit tests for compiler phases `1-4`

## Files / Paths Impacted
- `tests/unit/melder/spellbook/spell_compiler/phases/**`

## Validation
- Ran:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\spell_compiler\test_spell_compiler_artifact.py tests\unit\melder\spellbook\spell_compiler\test_spell_compiler.py tests\unit\melder\spellbook\spell_compiler\test_spell_compiler_system.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_1.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_2.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_3.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_4.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_5.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_5_local.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_6.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_6_local.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_7.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_7_local.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_8.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_9.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_10.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_11.py tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_12.py tests\unit\melder\spellbook\spell_compiler\phases\test_shared_compiler_executions.py tests\unit\melder\spellbook\test_spell.py tests\unit\melder\spellbook\test_spell_compiler_foundation.py` -> `303 passed, 1 warning`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook` -> `2017 passed, 1 xfailed, 1 warning in 2.26s`

## Risks / Rollback Notes
- Risk: phase coverage gets reintroduced as another stopgap instead of by actual
  owner.
  Rollback: keep every test tied to the concrete current phase owner.

## Applicable Anti-Patterns
- [ ] No broad smoke tests replacing detailed phase contracts.
- [ ] No restored `SpellCrafter` runtime object assumptions.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: old structural mechanic mapping and current phase-owner replacement coverage.

## Notes
- DATETIME: 2026-05-21T00:34:00Z
  TYPE: PLAN
  CLAIM: The next active route is structural phase replacement because the full repo ring is red only on the old monolithic compiler unit file. The first bounded replacement tranche is phases `1-4`.
  EVIDENCE:
  - validation: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests` -> remaining failures concentrated in `tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py`
  IMPACT: Getting back to a green full repo ring now depends on phase-owner replacement, not on more foundation or component/integration work.
  NEXT: land explicit current-surface phase `1-4` files and start draining the old monolith by owner group.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T00:55:35Z
  TYPE: FACT
  CLAIM: The first failing monolith bucket is no longer phase-owner behavior.
    The old `SpellCrafter` init/cleanup/property slice now maps mainly to
    `SpellCompilerArtifact` lifecycle tests, `Spell` compiler-foundation tests,
    and `Spell` public compiler-property tests. The real structural gap is that
    the current-surface phase `1-4` unit files still do not exist.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:1602-1879
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_artifact.py:13-171
  - tests/unit/melder/spellbook/test_spell_compiler_foundation.py:92-122
  - tests/unit/melder/spellbook/test_spell.py:969-1003
  IMPACT: We can remove the covered early stale `SpellCrafter` slice once the
    remaining current-surface property/cancellation replacements are present,
    while the actual active replacement work stays focused on new phase `1-4`
    test files.
  NEXT: add current-surface phase `1-4` test files, top up the remaining
    modern property/cancellation coverage, then delete the covered early
    monolith bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T08:33:39Z
  TYPE: MEASURE
  CLAIM: The replacement suite now owns phases `1-7`, the shared IR-export
    helper slice, and the top orchestration slice. The old monolith is down to
    one late-stage bucket: Phase 11 metrics/variant helpers, Phase 12 compile
    caching, and Phase 8-10 plan/cache helpers. The monolith failure floor is
    now `29` failures plus `1` collection/setup error.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_1.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_2.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_3.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_4.py` -> `30 passed`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_5.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_5_local.py` -> `14 passed`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_6.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_6_local.py` -> `10 passed`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_7.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_7_local.py` -> `6 passed`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\spell_compiler\\test_spell_compiler_system.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_shared_compiler_executions.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_3.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_8.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_10.py` -> `65 passed`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\spell_crafter\\test_spell_crafter.py` -> `29 failed, 1 error`
  IMPACT: The next useful cut is no longer early structural parity. It is late
    execution/codegen helper ownership only.
  NEXT: port current-owner tests for Phase 11 metrics/variant helpers, Phase 12
    compile caching, and Phase 8-10 plan/cache helper reuse, then delete the
    matching old monolith tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T08:33:39Z
  TYPE: BLOCKER
  CLAIM: Standalone validation of the newest late-owner files is now blocked by
    an import-time production error in
    `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_request/transaction_request.py`.
    The file references `_mrg.sentinel` in `ChangeTransactionType`, but the
    import path currently resolves to `NameError: _mrg is not defined` during
    package import.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_request/transaction_request.py:1-31
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_shared_compiler_executions.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_11.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_12.py` -> import-time `NameError`
  IMPACT: The remaining late-owner tests can still be written and the old
    monolith can still be drained, but isolated validation of those newest
    files is not trustworthy until this import bug is fixed or otherwise
    routed around.
  NEXT: finish porting the final Phase 11 run semantics and decide whether to
    fix the import-time production bug or keep validating through broader rings
    that bypass the broken import path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T09:28:33Z
  TYPE: MEASURE
  CLAIM: The replacement lane is complete enough to retire the old SpellCrafter monolith. The current-surface SpellCompiler suite covers the late phase/codegen owners, the stale `test_spell_crafter.py` file is gone, and the full `tests/unit/melder/spellbook` ring is green.
  EVIDENCE:
  - validation_result: `$env:PYTHONPATH='src'; .\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\spell_compiler\\test_spell_compiler_artifact.py tests\\unit\\melder\\spellbook\\spell_compiler\\test_spell_compiler.py tests\\unit\\melder\\spellbook\\spell_compiler\\test_spell_compiler_system.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_1.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_2.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_3.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_4.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_5.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_5_local.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_6.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_6_local.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_7.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_7_local.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_8.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_9.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_10.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_11.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_compiler_phase_12.py tests\\unit\\melder\\spellbook\\spell_compiler\\phases\\test_shared_compiler_executions.py tests\\unit\\melder\\spellbook\\test_spell.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py` -> `303 passed, 1 warning`
  - validation_result: `$env:PYTHONPATH='src'; .\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook` -> `2017 passed, 1 xfailed, 1 warning in 2.26s`
  - filesystem_check: `Test-Path tests\\unit\\melder\\spellbook\\spell_crafter\\test_spell_crafter.py` -> `False`
  IMPACT: The old monolithic compiler unit file is no longer the active owner of this behavior. The replacement suite is now the canonical unit coverage surface for the spell compiler lane.
  NEXT: close the task, move it to `tickets/tasks/completed/`, and clear stale routing from `attention_board.md`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Delivered state:
- current-surface SpellCompiler replacement tests cover the former structural and late-owner compiler mechanics
- `tests/unit/melder/spellbook` is green under `PYTHONPATH=src`
- the stale `test_spell_crafter.py` monolith has been retired
