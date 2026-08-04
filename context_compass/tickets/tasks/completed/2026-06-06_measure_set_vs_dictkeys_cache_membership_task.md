Completed: 2026-06-12T11:58:04Z
Summary: Closed by user cleanup request with the measurement result retained in
the ticket for later cache-lane reference.

# Task: Measure Set Vs Dict Keys Cache Membership

## Metadata
- Task ID: TASK-2026-06-06-measure-set-vs-dictkeys-cache-membership
- Story: none
- Epic: EPIC-2026-06-06-define-compiler-phase-artifact-directory-cache
- Status: done
- Owner: codex
- Agent Name: compiler_1
- Priority: p1
- Created: 2026-06-06T23:35:28Z
- Updated: 2026-06-12T11:58:04Z

## Objective
Measure whether a direct `set` comparison or a `dict.keys()` view comparison
is faster for the cache-coverage check shape we are discussing.

## Ticket Contract
- ENTRY_GATE: the cache epic is active and the user explicitly requested a
  measurement under `tests/experimentation/`.
- EXECUTION_BOUNDARY:
  - `tests/experimentation/`
  - `codex/context_compass/tickets/tasks/2026-06-06_measure_set_vs_dictkeys_cache_membership_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-06-06_define_compiler_phase_artifact_directory_cache_epic.md`
  - `tickets/tasks/2026-06-06_add_aether_configuration_system_caching_flag_task.md`
- EXIT_GATE:
  - one experiment exists under `tests/experimentation/`
  - it measures `set` vs `dict.keys()` comparisons against another set
  - it runs the comparison 1000 times
  - validation status is recorded truthfully
- FAILURE_ESCALATION: raise `BLOCKER` if the test harness cannot produce a
  stable measurement shape inside repo policy.

## Scope Boundaries
- In scope:
  - one `tests/experimentation` measurement file
  - task/board note sync
- Out of scope:
  - production cache implementation changes
  - broader benchmark framework work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a direct measurement of
  `set` versus `dict.keys()` comparison cost.

## Deliverables
- one experiment file under `tests/experimentation/`
- one recorded measurement result

## Validation
- Ran:
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s tests/experimentation/test_set_vs_dictkeys_cache_membership_experiment.py`
- Result:
  - `1 passed, 1 warning`
- Recommended commands:
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s tests/experimentation/test_set_vs_dictkeys_cache_membership_experiment.py`

## Notes
- DATETIME: 2026-06-06T23:35:28Z
  TYPE: PLAN
  CLAIM: The fastest way to settle the `set` vs `dict_keys` argument is a tiny
    experiment that mirrors the actual cache question: compare one set against
    another set, then compare one `dict.keys()` view against another set,
    repeat both 1000 times, and print the timing.
  EVIDENCE:
  - user_instruction
  IMPACT: This gives the cache lane an empirical answer instead of intuition.
  NEXT: add the experiment file under `tests/experimentation/` and run it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-06T23:37:01Z
  TYPE: MEASURE
  CLAIM: The measurement now exists and it favors the direct set path for the
    exact cache-coverage check shape tested here. Over 1000 iterations with
    300 requested spell ids and 300 cached spell ids:
    - set difference averaged `2218.60 ns/iter`
    - `dict.keys()` difference averaged `5313.20 ns/iter`
    - `dict_keys` was `2.394844x` slower in this run
    Both paths produced identical semantic results.
  EVIDENCE:
  - tests/experimentation/test_set_vs_dictkeys_cache_membership_experiment.py:20-90
  IMPACT: For this exact coverage-check path, keeping the cached spell-id set
    directly is the faster and simpler runtime surface.
  NEXT: use a direct set for cache coverage checks unless a later broader
    benchmark proves the difference disappears in a more realistic bundle flow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns one narrow experiment for the cache lane: measure `set` vs
`dict.keys()` comparison cost for the spell-id coverage check shape.
