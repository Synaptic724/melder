# Task: Update compiler and meld test drift

## Metadata
- Task ID: TASK-2026-05-30-update-compiler-and-meld-test-drift
- Story: none
- Status: done
- Owner: codex
- Agent Name: spellspace_0
- Priority: p0
- Created: 2026-05-30T19:57:27Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Update the stale tests that drifted after the recent compiler shape-profile
collection, Phase 13 rename, and abstract `Meld` split, without reintroducing
compatibility logic into production code.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested test updates after the recent
  runtime/compiler surface changes and the active board routes this narrow test
  slice before edits begin.
- EXECUTION_BOUNDARY:
  - `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_1.py`
  - `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_8.py`
  - `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_9.py`
  - `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_10.py`
  - `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_11.py`
  - `tests/unit/melder/spellbook/test_spell_compiler_foundation.py`
  - directly implicated `tests/unit/melder/aether/conduit/meld/test_meld.py`
  - directly implicated `tests/unit/melder/aether/conduit/meld/test_meld_2.py`
  - this task ticket
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-30_collect_execution_strategy_shape_profiles_task.md`
  - `tickets/tasks/2026-05-30_rename_current_phase12_backend_to_phase13_task.md`
- EXIT_GATE:
  - stale tests match the new compiler-profile and abstract-meld surfaces
  - focused pytest ring passes
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any remaining failures appear
  to be real production regressions instead of stale tests.

## Scope Boundaries
- In scope:
  - updating stale test stubs and assertions
  - updating tests that instantiate abstract `Meld`
  - focused validation
- Out of scope:
  - production compatibility code
  - broad suite cleanup

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested the stale tests be updated
  instead of reintroducing compatibility logic.

## Steps / Checklist
- [ ] Patch stale phase 1/8/9/10/11 test stubs and assertions.
- [ ] Patch stale abstract `Meld` instantiations in foundation and direct meld tests.
- [ ] Run a focused pytest ring over the touched files.
- [ ] Summarize whether any failures still look like runtime regressions.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- one bounded test-drift fix
- one focused validation result

## Files / Paths Impacted
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_1.py`
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_8.py`
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_9.py`
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_10.py`
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_11.py`
- `tests/unit/melder/spellbook/test_spell_compiler_foundation.py`
- `tests/unit/melder/aether/conduit/meld/test_meld.py`
- `tests/unit/melder/aether/conduit/meld/test_meld_2.py`
- `codex/context_compass/tickets/tasks/2026-05-30_update_compiler_and_meld_test_drift_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -q <touched test files>`

## Risks / Rollback Notes
- Risk: some failures may still indicate a real runtime regression instead of
  stale tests.
- Rollback: keep changes test-only and surface production regressions instead of
  masking them.

## Applicable Anti-Patterns
- [ ] No production compatibility code for stale tests.
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
- Note focus: stale test assumptions, exact drift cause, and focused validation.
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
- DATETIME: 2026-05-30T20:08:40Z
  TYPE: MEASURE
  CLAIM: The stale test surface is now aligned to the upgraded compiler and
    meld runtime. The fixes were test-only:
    - Phase 1/8/9/10 rebuild/cache tests now stub the new profile helpers when
      the test intent is about cache/rebuild behavior rather than profile
      contents.
    - Phase 11 helper tests now pass the new `artifact` argument into
      `_cache_execution_plan_metrics(...)` and assert moved metric ownership on
      the artifact instead of `Spell`, while still asserting
      `execution_plan_dispatch_route` on `Spell`.
    - foundation and direct meld tests now use `ConduitMeld` instead of trying
      to instantiate abstract `Meld`.
    - direct meld helper tests now use the current `ConduitCreations` /
      spellspace-owned `Creations` model rather than the removed hybrid
      spellspace APIs on conduit-owned creations.
    - `SpellSpaceMeld` coverage now owns the spellspace-specific reuse/probe/status
      assertions instead of forcing old conduit-owned spellspace behavior back
      into `ConduitMeld`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_1.py:49-95
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_8.py:238-333
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_9.py:41-99
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_10.py:76-161
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_11.py:77-381
  - tests/unit/melder/spellbook/test_spell_compiler_foundation.py:1-136
  - tests/unit/melder/aether/conduit/meld/test_meld.py:703-2570
  - tests/unit/melder/aether/conduit/meld/test_meld_2.py:181-614
  - tests/unit/melder/aether/conduit/meld/test_meld_gate_controller.py:1-157
  IMPACT: The current failure cluster was stale-test drift, not a reason to put
    compatibility back into production code.
  NEXT: if more suite drift appears, classify it the same way: stale test vs
    real regression, and only touch production code for real regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T20:08:40Z
  TYPE: MEASURE
  CLAIM: The focused stale-test validation ring is green.
    `.\.venv_new\Scripts\python.exe -m pytest -q
    tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_1.py
    tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_8.py
    tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_9.py
    tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_10.py
    tests\unit\melder\spellbook\spell_compiler\phases\test_compiler_phase_11.py
    tests\unit\melder\spellbook\test_spell_compiler_foundation.py
    tests\unit\melder\aether\conduit\meld\test_meld.py
    tests\unit\melder\aether\conduit\meld\test_meld_2.py
    tests\unit\melder\aether\conduit\meld\test_meld_gate_controller.py`
    passed with `143 passed, 1 warning`.
  EVIDENCE:
  - validation_result: focused pytest ring above
  IMPACT: The direct drift from the recent compiler-profile, Phase 13 rename,
    and abstract `Meld` changes is resolved in the touched test surface.
  NEXT: if broader validation is wanted, widen from this green ring outward
    instead of jumping straight to the whole suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T19:57:27Z
  TYPE: FACT
  CLAIM: The current failure cluster is stale-test drift, not a reason to add
    compatibility back into runtime code. The direct failures are:
    - Phase 1 test stubs returning raw dicts without `.parameters`
    - Phase 8/9/10 tests building bare `object()` plan/map stubs that no longer
      satisfy the new profile collectors
    - Phase 11 tests calling `_cache_execution_plan_metrics(...)` with the old
      signature and asserting the old `Spell` metric fields
    - compiler foundation test still instantiating abstract `Meld`
  EVIDENCE:
  - user_pasted_failure_cluster
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_1.py:49-79
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_8.py:238-333
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_9.py:41-99
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_10.py:76-161
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_11.py:77-381
  - tests/unit/melder/spellbook/test_spell_compiler_foundation.py:122-127
  IMPACT: The next step is to patch the stale tests, not the production code.
  NEXT: update the direct failing tests and run a focused pytest ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to update the stale tests after the recent compiler-profile,
Phase 13 rename, and abstract `Meld` changes.

