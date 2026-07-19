# Task: fix aether singleton native new support

- Completed: 2026-05-22T00:19:54Z
- Summary: Closed during board cleanup after the bounded singleton-construction slice was accepted and removed from active routing.


## Metadata
- Task ID: TASK-2026-05-21-fix-aether-singleton-native-new-support
- Story: none
- Status: done
- Owner: codex
- Agent Name: refactor_1
- Priority: p1
- Created: 2026-05-21T21:54:51Z
- Updated: 2026-05-22T00:19:54Z

## Objective
Clear the mypyc `object.__new__()` unsupported errors on the two remaining
native singleton roots that still implement custom `__new__()`: `Aether` and
`AetherUtilitySystem`.

## Ticket Contract
- ENTRY_GATE: active board row points at this task and the singleton root shape
  evidence is recorded in `## Notes` before code edits.
- EXECUTION_BOUNDARY: only `src/melder/aether/aether.py`,
  `src/melder/aether/aether_utility_system.py`, this task, and the routing
  row/detail in `attention_board.md`.
- DEPENDENCIES: current `object.__new__()` mypyc errors plus the existing
  singleton tests for `Aether` and `AetherUtilitySystem`.
- EXIT_GATE: the focused src checker no longer reports those two `__new__`
  errors and the direct singleton tests remain green.
- FAILURE_ESCALATION: raise `BLOCKER` if clearing the native-construction error
  forces broader lifecycle or singleton-behavior changes beyond these two
  classes.

## Scope Boundaries
- In scope:
  - `Aether` singleton construction surface
  - `AetherUtilitySystem` singleton construction surface
  - direct singleton/reset test coverage for those classes
- Out of scope:
  - `Nexus`, `MutationResearch`, or `Crystallizer` behavior
  - broader lifecycle or cleanup refactors
  - unrelated singleton/type issues

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the local cleanable replacement cleared the native
  singleton construction errors, and the focused singleton tests for both
  classes remain green.

## Steps / Checklist
- [x] Record the native-singleton construction mismatch and direct test surface.
- [x] Patch `Aether` and `AetherUtilitySystem` so custom singleton `__new__()`
      no longer relies on unsupported native-class allocation semantics.
- [x] Run focused validation on both files.
- [x] Record the validation result in notes.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- cleared `object.__new__()` mypyc errors for `Aether` and `AetherUtilitySystem`
- focused validation evidence for the result

## Files / Paths Impacted
- `src/melder/aether/aether.py`
- `src/melder/aether/aether_utility_system.py`
- `codex/context_compass/attention_board.md`
- this task file

## Validation
- Ran:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe tests\experimentation\mypyc\mypy_checker_src.py`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_aether.py -k "singleton or reset_singleton_for_tests or cleanup_clears_state"`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_aether_utility_system.py`
- Result:
  - focused checker filter: `NO_MATCH_FOR_aether_or_utility_system`
  - pytest (`test_aether.py` subset): `6 passed, 121 deselected, 1 warning`
  - pytest (`test_aether_utility_system.py`): `20 passed, 1 warning`

## Risks / Rollback Notes
- Low risk if the change stays on class decoration/construction shape only.
- Roll back if singleton identity or reset behavior regresses.

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
- DATETIME: 2026-05-21T21:54:51Z
  TYPE: FACT
  CLAIM: The current mypyc complaint is no longer about singleton storage
    typing. It is about native-class construction: `Aether` and
    `AetherUtilitySystem` are still marked `native_class=True` and both call
    `super(...).__new__(cls)` in custom singleton `__new__()` methods. `Nexus`
    and `Crystallizer` already live as plain Python singleton roots, which is
    why they do not hit this native-construction error.
  EVIDENCE:
  - src/melder/aether/aether.py:31-32
  - src/melder/aether/aether.py:97-113
  - src/melder/aether/aether_utility_system.py:9-11
  - src/melder/aether/aether_utility_system.py:56-75
  - src/melder/nexus/nexus.py:53-55
  - src/melder/crystallizer/crystallizer.py:17-18
  IMPACT: The bounded fix is to align these two singleton roots with the
    already-non-native singleton pattern instead of keeping unsupported native
    `__new__()` allocation semantics.
  NEXT: drop `Aether` and `AetherUtilitySystem` out of native-class mode, then
    rerun the focused checker and singleton tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-21T21:54:51Z
  TYPE: DECISION
  CLAIM: Dropping `native_class=True` was not sufficient because both classes
    still hit the same `object.__new__()` complaint as plain classes while
    inheriting `Cleanable`. The workable path was to remove the `Cleanable`
    base entirely and inline the small cleaned-state contract these two classes
    actually use.
  EVIDENCE:
  - validation_result: focused checker after decorator removal -> `src\\melder\\aether\\aether.py:110: error: \"object.__new__()\" not supported for classes inheriting from non-native classes`
  - validation_result: focused checker after decorator removal -> `src\\melder\\aether\\aether_utility_system.py:71: error: \"object.__new__()\" not supported for classes inheriting from non-native classes`
  - src/melder/aether/aether.py:360-392
  - src/melder/aether/aether_utility_system.py:119-139
  IMPACT: The fix stays bounded to the two singleton roots while preserving
    `_cleaned`, `cleaned`, `is_cleaned`, and `check_cleaned()` for existing code
    and tests.
  NEXT: rerun the focused checker and both singleton test surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-21T21:54:51Z
  TYPE: MEASURE
  CLAIM: `Aether` and `AetherUtilitySystem` no longer inherit `Cleanable`, but
    they now expose the same local cleaned-state contract needed by their code
    and tests. The focused checker no longer reports either construction error,
    and both singleton test surfaces are green.
  EVIDENCE:
  - src/melder/aether/aether.py:1-140
  - src/melder/aether/aether_utility_system.py:1-110
  - validation_result: focused checker filter -> `NO_MATCH_FOR_aether_or_utility_system`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests/unit/melder/aether/test_aether.py -k "singleton or reset_singleton_for_tests or cleanup_clears_state"` -> `6 passed, 121 deselected, 1 warning`
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests/unit/melder/aether/test_aether_utility_system.py` -> `20 passed, 1 warning`
  IMPACT: The native singleton construction errors are cleared without changing
    the observed singleton identity/reset behavior.
  NEXT: wait for user acceptance, then either close this slice or continue to
    the next issue.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task is a narrow singleton-construction slice for `Aether` and
`AetherUtilitySystem`. The intended change is limited to their native-class
construction posture, not their singleton behavior. The final fix was local
cleaned-state replacement instead of `Cleanable` inheritance; focused checker
and singleton tests are green.
