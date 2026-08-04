# Task: Add real-world gauntlet GIL mode switch

## Metadata
- Task ID: TASK-2026-05-23-add-real-world-gauntlet-gil-mode-switch
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-23T22:07:04Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Add a simple file-level switch in `test_real_world_gauntlet.py` so the user can
choose `current`, `gil enabled`, or `nogil` from inside the file without
having to remember Python launcher flags.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for a variable inside the shared
  gauntlet file that controls GIL-on vs no-GIL execution.
- EXECUTION_BOUNDARY:
  - `benchmarks/testing_other_di/test_real_world_gauntlet.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - local interpreter supports `-X gil=[0|1]`
- EXIT_GATE: the shared gauntlet file exposes one obvious file-level GIL mode
  variable, and the test can re-exec itself under the selected mode without
  recursive rerun loops.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the file-level switch would
  require a larger benchmark-runner redesign than a bounded subprocess helper.

## Scope Boundaries
- In scope:
  - one file-level GIL mode variable
  - one bounded self-rerun helper for selected mode
  - minimal validation
- Out of scope:
  - benchmark workload changes
  - cProfile changes
  - Melder-only benchmark changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly wants the shared gauntlet file itself
  to expose a GIL on/off switch.

## Steps / Checklist
- [ ] Add the file-level GIL mode variable and normalize its accepted values.
- [ ] Add the bounded subprocess rerun helper using `-X gil=0/1`.
- [ ] Validate the file parses and the switch logic is structurally sound.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one file-level GIL mode switch in `test_real_world_gauntlet.py`
- one bounded rerun path that uses `-X gil=0/1`

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-23_add_real_world_gauntlet_gil_mode_switch_task.md`
- `codex/context_compass/attention_board.md`
- `benchmarks/testing_other_di/test_real_world_gauntlet.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m py_compile benchmarks\testing_other_di\test_real_world_gauntlet.py`

## Risks / Rollback Notes
- Risk: a naive rerun helper would recursively respawn pytest for each
  parametrized library case.
- Rollback: keep the helper bounded to one parent-side trigger library plus an
  explicit child-process guard env var.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No benchmark rerun recursion without an explicit subprocess guard.

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
- Note focus: GIL switch semantics, rerun guard, and one-step continuation.
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
- DATETIME: 2026-05-23T22:07:04Z
  TYPE: FACT
  CLAIM: The local interpreter supports the exact GIL switch surface needed
    for this ask: `-X gil=0` and `-X gil=1`. That means the cleanest bounded
    design is a file-level variable in `test_real_world_gauntlet.py` plus a
    one-shot subprocess rerun helper, not a benchmark rewrite.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe --help-xoptions`
  - user_instruction
  IMPACT: The next edit can stay entirely inside the shared benchmark file and
    give the user a direct in-file switch for current/enabled/disabled GIL
    posture.
  NEXT: patch `test_real_world_gauntlet.py` with the file-level switch and the
    guarded subprocess rerun helper.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T22:12:00Z
  TYPE: FACT
  CLAIM: The shared gauntlet file now exposes a direct file-level switch:
    `REAL_WORLD_GAUNTLET_GIL_MODE = "current"`. Accepted values are
    `"current"`, `"enabled"`, and `"disabled"`. When the selected mode does
    not match the current interpreter, the first parametrized case reruns the
    whole file once under `-X gil=1` or `-X gil=0`, marks the child with an
    explicit env guard, and the remaining parent-side parametrized cases skip
    instead of recursively respawning.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:24-25
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:62-159
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1649-1649
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m py_compile benchmarks\\testing_other_di\\test_real_world_gauntlet.py`
  IMPACT: The user now has an obvious in-file knob for current vs GIL-enabled
    vs no-GIL execution without needing to remember launcher syntax.
  NEXT: surface the exact variable name and accepted values to the user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T22:15:00Z
  TYPE: FACT
  CLAIM: The first no-GIL-only simplification left one stale call site behind.
    The helper was renamed from `_maybe_rerun_under_requested_gil_mode(...)`
    to `_maybe_rerun_under_nogil(...)`, but the test entrypoint at the bottom
    of the file still calls the old name. That is why the shared gauntlet now
    fails immediately with `NameError` before any benchmark work starts.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:68-68
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1628-1628
  - user_failure_report
  IMPACT: The fix is narrow and local: patch the one stale call site and
    re-run a structural compile check.
  NEXT: replace the old helper call with `_maybe_rerun_under_nogil(lib)` and
    verify the file parses cleanly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the shared benchmark file change that adds an in-file GIL mode
switch for `test_real_world_gauntlet.py`.

