# Task: Pin every-declared-disposal-method behaviour in Creations with unit tests

## Metadata
- Task ID: TASK-2026-08-07-creations-disposal-all-methods
- Story:
- Status: done
- Owner: cowork
- Agent Name: melder_0
- Priority: p2
- Created: 2026-08-07T11:06:16Z
- Updated: 2026-09-27T13:03:47Z
- Completed: 2026-09-27T13:03:47Z
- Closure Basis: owner acceptance and turn-in in chat (2026-09-27): "yeah accepted turn in everything call it all
  and stay signed in but finish off your work".
- Summary: The disposal-methods regression file (all declared methods invoked in order, `many` lane, pinned
  stop-at-first-failure posture) passes on 3.14t (GIL 0 and 1) and the GIL build, agent-run; per-method error
  aggregation stays an open owner decision, not taken at turn-in.

## Objective
Add unit coverage proving `Creations` invokes EVERY declared disposal method for
an entry, in declared order, on both the singleton and `many` lanes - and pin the
current first-failure posture explicitly so a later change to error aggregation
is a deliberate edit rather than a silent behaviour drift.

## Ticket Contract
- ENTRY_GATE: active `attention_board.md` row routing to this task; owner-reported
  source fix to `_attempt_cleanup` already applied.
- EXECUTION_BOUNDARY: `tests/unit/melder/aether/conduit/creations/` only. No `src/`
  edits in this task - the source change was made by the owner.
- DEPENDENCIES: owner's removal of the success-path `return None` in
  `Creations._attempt_cleanup`.
- EXIT_GATE: owner runs the new test file on 3.14t and reports GREEN. Until then
  validation stays `Not run.`
- FAILURE_ESCALATION: if the failure-posture test reds, record a DECISION_REQUEST
  rather than editing the assertion - a red there means the error contract
  changed and the owner must rule on aggregate-vs-first-error.

## Scope Boundaries
- In scope: one new unit test module covering the disposal-method invocation contract.
- Out of scope: changing `_attempt_cleanup`; changing error aggregation; the
  `list(disposal_methods)` per-creation copy; any perf work.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner directed the test to be written and placed in unit tests;
  source fix already applied upstream, so the test is the remaining deliverable.
- from_state: in_progress
- to_state: done
- transition_reason: Owner turn-in of every melder_0 ticket (chat, 2026-09-27T13:03:47Z); the file is green today.

## Steps / Checklist
- [x] Read the sibling regression modules for naming and style conventions
- [x] Write the regression module
- [x] Owner runs the file on 3.14t (agent-run instead on 2026-09-27; owner turned the task in)
- [x] Record the result in `## Notes`
- [x] Ask owner to confirm acceptance criteria before closure

## Deliverables
- `tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py`

## Files / Paths Impacted
- tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py

## Validation
- Run 2026-09-27 (agent, VM worktree byte-equal to the device file): 4 passed on 3.14.7t
  PYTHON_GIL=0 and =1 and on the 3.14.7 GIL build; also inside the whole-tree run.
- Recommended commands:
  - `pytest tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py -q`
  - `pytest tests/unit/melder/aether/conduit/creations -q`

## Risks / Rollback Notes
- The failure-posture test encodes CURRENT behaviour (stop at first raising
  method). It is expected to red if error aggregation is introduced later; that
  red is the signal, not a defect. Rollback is deleting one file.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off (authoring)
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed
- [x] Notes quality maintained
- [x] Applicable anti-pattern checks are clear or escalated with evidence
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.

## Notes
- DATETIME: 2026-08-07T11:06:16Z
  TYPE: FACT
  CLAIM: `_attempt_cleanup` could never reach a second loop iteration - both
    branches of its `try` returned inside iteration one (`return None` on
    success, `return RuntimeError(...)` on failure), so only `method_names[0]`
    was ever invoked. Owner has removed the success-path `return None`; the
    first-failure return is deliberately retained for now.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:197-219
  - src/melder/aether/conduit/creations/creations.py:221-263
  IMPACT: A creation declaring more than one disposal method silently skipped
    every method after the first, with no exception and no log. The entry still
    left the registry, so an undisposed resource was indistinguishable from a
    disposed one.
  NEXT: Owner runs the new module on 3.14t and reports the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-08-07T11:06:16Z
  TYPE: DECISION
  CLAIM: The first-failure posture is pinned in a separately named test rather
    than left unasserted, so a future move to per-method error aggregation
    fails one clearly-named test instead of silently changing behaviour.
    `_dispose_disposable_registry` already aggregates per-ENTRY failures into an
    `ExceptionGroup`, so returning a list from `_attempt_cleanup` would compose
    with existing machinery if that change is wanted.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:251-263
  IMPACT: Makes the error contract an explicit owner decision rather than an
    accident of control flow.
  NEXT: Owner rules whether to aggregate per-method failures.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T13:03:47Z
  TYPE: MEASURE
  CLAIM: The regression file runs green today: 4 passed on 3.14.7t PYTHON_GIL=0 and =1 and on the 3.14.7 GIL
    build (VM worktree copy, byte-equal to the device file), and it sits inside today's whole-tree run. The
    per-method error-aggregation question (DECISION note above) was not ruled; the owner turned the task in.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/creations/test_creations_disposal_all_methods_regression.py:1-211
  - context_compass/artifacts/aether_conduit_lookup_api_impl_20260927/suites_final_0279_vm.txt:1-38
  IMPACT: The exit gate's green run exists (agent-run); the task closes on the owner's turn-in.
  NEXT: none (closed).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Closed 2026-09-27T13:03:47Z by owner turn-in; the file is green on 3.14t and GIL (agent-run).
Owner fixed `_attempt_cleanup` after the loop-never-iterates finding. This task
adds the unit coverage that pins the fix: all declared methods invoked, declared
order preserved, `many` lane covered, and the current stop-at-first-failure
posture asserted separately. Nothing under `src/` was touched here. Awaiting an
owner 3.14t run - validation is `Not run.`

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
