# Task: fix alias default attribute warnings

- Completed: 2026-05-22T00:19:54Z
- Summary: Closed during board cleanup after the routed slice was accepted and removed from active routing.


## Metadata
- Task ID: TASK-2026-05-21-fix-alias-default-attribute-warnings
- Story: none
- Status: done
- Owner: codex
- Agent Name: refactor_1
- Priority: p2
- Created: 2026-05-21T22:10:11Z
- Updated: 2026-05-22T00:19:54Z

## Objective
Replace the six class-body alias/default attribute sites in `weak_ref_node.py`,
`sync_weak_ref.py`, and `safe_logger.py` with explicit properties or wrapper
methods so the mypyc checker stops warning without changing the exposed API.

## Ticket Contract
- ENTRY_GATE: active board row points at this task and the six alias sites plus
  direct unit coverage are recorded in `## Notes` before code edits.
- EXECUTION_BOUNDARY: only
  `src/melder/utilities/data_structures/weak_data_structures/weak_ref_node.py`,
  `src/melder/utilities/synchronization/sync_weak_ref.py`,
  `src/melder/utilities/logger/safe_logger.py`, this task, and the routing
  row/detail in `attention_board.md`.
- DEPENDENCIES: current src-level mypyc checker output and the focused direct
  unit files for weak ref node, sync weak ref, and safe logger.
- EXIT_GATE: the alias/default attribute warnings are gone from the focused
  checker, and the direct unit surfaces for those three files stay green.
- FAILURE_ESCALATION: raise `BLOCKER` if explicit wrappers change the public
  alias semantics (`snapshot`, `map`, `warn`, `fatal`) or if the focused checker
  still reports the same warnings.

## Scope Boundaries
- In scope:
  - `WeakRefNode.snapshot`
  - `WeakRefNode.map`
  - `SyncWeakRef.snapshot`
  - `SyncWeakRef.map`
  - `SafeLogger.warn`
  - `SafeLogger.fatal`
  - direct unit files for those surfaces
- Out of scope:
  - broader weak-ref or logging refactors
  - unrelated warnings/errors
  - behavior changes outside the alias surface

## State Transition Event
- from_state: in_progress
- to_state: blocked
- transition_reason: the alias wrappers are implemented and the direct unit
  ring is green, but the focused src checker is still blocked by an unrelated
  pre-existing `sync_weak_ref.py:19` multiple-inheritance error in the same
  file, so the task cannot honestly claim a checker-clean exit.

## Steps / Checklist
- [x] Record the six alias sites and the direct unit surface in notes.
- [x] Replace the six class-body alias/default assignments with explicit wrappers.
- [x] Run focused validation on the warning sites.
- [x] Record the validation result in notes.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- explicit wrappers for the six alias/default attribute sites
- focused validation evidence for the warning outcome

## Files / Paths Impacted
- `src/melder/utilities/data_structures/weak_data_structures/weak_ref_node.py`
- `src/melder/utilities/synchronization/sync_weak_ref.py`
- `src/melder/utilities/logger/safe_logger.py`
- `codex/context_compass/attention_board.md`
- this task file

## Validation
- Ran:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe tests\experimentation\mypyc\mypy_checker_src.py`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\data_structures\weak_data_structures\test_weak_ref_node.py tests\unit\melder\utilities\synchronization\test_sync_weak_ref.py tests\unit\melder\utilities\logger\test_safe_logger.py`
- Result:
  - direct unit ring: `55 passed, 1 warning`
  - focused checker remains blocked by unrelated file-level error:
    `src\\melder\\utilities\\synchronization\\sync_weak_ref.py:19: error: Multiple inheritance is not supported (except for traits)`

## Risks / Rollback Notes
- Low risk if the wrappers preserve the same call/property surface.
- Roll back if alias behavior changes or if the focused unit ring regresses.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-21T22:10:11Z
  TYPE: FACT
  CLAIM: The reported warnings are all class-body alias/default attribute sites:
    `snapshot = property(get)` and `map = transform` on weak-ref wrappers, plus
    `warn = warning` and `fatal = critical` on `SafeLogger`. The direct unit
    files already exercise `map`, `warn`, and `fatal`, so explicit wrapper
    methods/properties can preserve behavior while removing the unsupported
    default-attribute pattern.
  EVIDENCE:
  - src/melder/utilities/data_structures/weak_data_structures/weak_ref_node.py:237-238
  - src/melder/utilities/data_structures/weak_data_structures/weak_ref_node.py:325-328
  - src/melder/utilities/synchronization/sync_weak_ref.py:338-343
  - src/melder/utilities/synchronization/sync_weak_ref.py:418-421
  - src/melder/utilities/logger/safe_logger.py:341-348
  - src/melder/utilities/logger/safe_logger.py:428-435
  - tests/unit/melder/utilities/data_structures/weak_data_structures/test_weak_ref_node.py:145-176
  - tests/unit/melder/utilities/synchronization/test_sync_weak_ref.py:67-82
  - tests/unit/melder/utilities/logger/test_safe_logger.py:98-116
  IMPACT: We can clear the warnings by replacing alias assignments with
    explicit wrappers while preserving the public surface the tests already use.
  NEXT: patch the six sites and run the focused checker plus the three direct
    unit files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-21T22:12:58Z
  TYPE: BLOCKER
  CLAIM: The alias/default-wrapper patch is in place and the direct unit ring is
    green, but the focused src checker cannot prove the warning slice fully
    clean because `sync_weak_ref.py` still has an older file-level multiple
    inheritance error at line 19. That error is upstream of the alias sites and
    stops this task from claiming a checker-clean exit.
  EVIDENCE:
  - src/melder/utilities/data_structures/weak_data_structures/weak_ref_node.py:237-238
  - src/melder/utilities/data_structures/weak_data_structures/weak_ref_node.py:325-328
  - src/melder/utilities/synchronization/sync_weak_ref.py:343-343
  - src/melder/utilities/synchronization/sync_weak_ref.py:421-421
  - src/melder/utilities/logger/safe_logger.py:348-348
  - src/melder/utilities/logger/safe_logger.py:435-435
  - validation_result: `.\.venv_new\Scripts\python.exe tests\experimentation\mypyc\mypy_checker_src.py` -> `src\\melder\\utilities\\synchronization\\sync_weak_ref.py:19: error: Multiple inheritance is not supported (except for traits)`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests/unit/melder/utilities/data_structures/weak_data_structures/test_weak_ref_node.py tests/unit/melder/utilities/synchronization/test_sync_weak_ref.py tests/unit/melder/utilities/logger/test_safe_logger.py` -> `55 passed, 1 warning`
  IMPACT: `weak_ref_node.py` and `safe_logger.py` aliasing is fixed and `sync_weak_ref.py` alias wrappers are in, but checker-level closure for the shared task is blocked until the broader `sync_weak_ref` class-shape issue is addressed.
  NEXT: if you want full checker closure on this slice, the next task must fix
    the `sync_weak_ref.py:19` multiple-inheritance problem.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task is a bounded alias/default-attribute warning slice. The intended
change is limited to replacing six class-body alias assignments with explicit
wrappers while preserving the same public surface. The direct unit ring is
green, but checker-level closure is blocked by the older
`sync_weak_ref.py:19` multiple-inheritance error.
