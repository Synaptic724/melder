# Task: fix weak data generator materialization

- Completed: 2026-05-22T00:19:54Z
- Summary: Closed during board cleanup after the weak-data materialization slice was accepted and removed from active routing.


## Metadata
- Task ID: TASK-2026-05-21-fix-weak-data-generator-materialization
- Story: none
- Status: done
- Owner: codex
- Agent Name: refactor_1
- Priority: p2
- Created: 2026-05-21T21:45:30Z
- Updated: 2026-05-22T00:19:54Z

## Objective
Replace the four generator-based weak-data iterator/materialization sites
reported by the mypyc checker with explicit realized containers while
preserving the existing snapshot/filter semantics.

## Ticket Contract
- ENTRY_GATE: active board row points at this task and the four warning sites
  plus the direct unit surfaces are recorded in `## Notes` before code edits.
- EXECUTION_BOUNDARY: only
  `src/melder/utilities/data_structures/weak_data_structures/weak_concurrent_dict.py`,
  `src/melder/utilities/data_structures/weak_data_structures/weak_concurrent_list.py`,
  this task, and the routing row/detail in `attention_board.md`.
- DEPENDENCIES: current src-level mypyc checker output and the focused weak
  dict/list unit files.
- EXIT_GATE: the four warning sites use explicit realized containers, the
  focused checker no longer reports those files, and the direct weak dict/list
  unit surfaces stay green.
- FAILURE_ESCALATION: raise `BLOCKER` if the explicit containers change
  snapshot iteration order or map/filter semantics.

## Scope Boundaries
- In scope:
  - `WeakConcurrentDict.__iter__`
  - `WeakConcurrentDict.__reversed__`
  - `WeakConcurrentList.map`
  - `WeakConcurrentList.filter`
  - direct weak dict/list unit files
- Out of scope:
  - broader weak-data refactors
  - unrelated weak-data warnings or errors
  - behavior changes in snapshot ordering or filtering

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the four weak-data sites now use explicit realized
  containers, the focused checker no longer reports those files, and the
  direct weak dict/list unit files are green.

## Steps / Checklist
- [x] Record the four warning sites and the direct unit contract surface in notes.
- [x] Replace the four generator-based sites with explicit realized containers.
- [x] Run focused validation on the warning sites.
- [x] Record the validation result in notes.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- explicit realized iterator/materialization surfaces for the four weak-data sites
- focused validation evidence for the warning outcome

## Files / Paths Impacted
- `src/melder/utilities/data_structures/weak_data_structures/weak_concurrent_dict.py`
- `src/melder/utilities/data_structures/weak_data_structures/weak_concurrent_list.py`
- `codex/context_compass/attention_board.md`
- this task file

## Validation
- Ran:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe tests\experimentation\mypyc\mypy_checker_src.py`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\utilities\data_structures\weak_data_structures\test_weak_concurrent_dict.py tests\unit\melder\utilities\data_structures\weak_data_structures\test_weak_concurrent_list.py`
- Result:
  - focused checker filter: `NO_MATCH_FOR_weak_concurrent_dict_or_list`
  - pytest: `67 passed, 1 warning`

## Risks / Rollback Notes
- Low risk if the explicit containers preserve the same snapshot order and
  live-value filtering behavior.
- Roll back if the focused tests regress or if the checker still reports the
  same warnings.

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
- DATETIME: 2026-05-21T21:45:30Z
  TYPE: FACT
  CLAIM: The reported weak-data warnings come from two direct generator returns
    in `WeakConcurrentDict` snapshot iteration and two generator-fed
    `WeakConcurrentList(...)` constructors in `map`/`filter`. The direct unit
    files already cover dict key iteration, reversed iteration implicitly via
    snapshot order, and list `map`/`filter` behavior.
  EVIDENCE:
  - src/melder/utilities/data_structures/weak_data_structures/weak_concurrent_dict.py:1130-1142
  - src/melder/utilities/data_structures/weak_data_structures/weak_concurrent_list.py:848-858
  - tests/unit/melder/utilities/data_structures/weak_data_structures/test_weak_concurrent_dict.py:112-140
  - tests/unit/melder/utilities/data_structures/weak_data_structures/test_weak_concurrent_dict.py:225-233
  - tests/unit/melder/utilities/data_structures/weak_data_structures/test_weak_concurrent_list.py:174-180
  IMPACT: We can silence the warnings by making the snapshot keys and mapped/
    filtered values explicit before returning, without changing the live-value
    semantics those tests already assert.
  NEXT: patch the four sites and run the focused src checker plus the two weak
    data unit files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-21T21:47:59Z
  TYPE: MEASURE
  CLAIM: The two weak-data files now use explicit realized containers at the
    four reported sites. The focused src-level checker no longer reports either
    file, and the direct weak dict/list unit ring is green.
  EVIDENCE:
  - src/melder/utilities/data_structures/weak_data_structures/weak_concurrent_dict.py:1130-1142
  - src/melder/utilities/data_structures/weak_data_structures/weak_concurrent_list.py:848-858
  - validation_result: focused checker filter -> `NO_MATCH_FOR_weak_concurrent_dict_or_list`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests/unit/melder/utilities/data_structures/weak_data_structures/test_weak_concurrent_dict.py tests/unit/melder/utilities/data_structures/weak_data_structures/test_weak_concurrent_list.py` -> `67 passed, 1 warning`
  IMPACT: The warning slice is cleared without changing the snapshot key
    iteration or weak list `map`/`filter` behavior covered by the direct unit
    files.
  NEXT: wait for user acceptance, then either close this slice or continue to
    the next warning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task is a bounded weak-data mypyc cleanup slice. The intended change is
limited to explicit materialization of snapshot keys and mapped/filtered values
at the four reported warning sites. Focused validation shows both files no
longer appear in the checker output, and the direct weak dict/list unit ring
is green.
