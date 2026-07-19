# Task: Experiment Runtime Test Frameworks Against Synthetic Modules

## Metadata
- Task ID: TASK-2026-05-02-experiment-pytest-against-synthetic-modules
- Story:
- Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: review
- Owner: codex
- Agent Name: codex_01
- Priority: p1
- Created: 2026-05-02T10:52:26Z
- Updated: 2026-05-02T12:21:14Z

## Objective
Build a focused experimentation bench under `tests/experimentation/` that tests
whether a lighter in-process test framework can use synthetic modules directly
at runtime without the process-ownership baggage we hit with `pytest`.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested runtime test experiments against
  synthetic modules and later redirected the lane toward `unittest`-style
  in-process mechanics.
- EXECUTION_BOUNDARY:
  - `tests/experimentation/`
  - this task ticket
  - `attention_board.md`
- DEPENDENCIES:
  - existing synthetic module import experiment
  - runtime `unittest` availability
- EXIT_GATE: one experiment bench exists, runs, and reports results for
  multiple synthetic-module / `unittest` interaction ideas.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if `pytest` requires far more
  invasive collection/plugin machinery than a bounded experiment bench should
  own.

## Scope Boundaries
- In scope:
  - runtime `unittest` experiments
  - synthetic module / importlib / module-object ideas
- Out of scope:
  - production testing framework integration
  - crystallizer implementation changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested runtime test experiments
  against synthetic modules and later redirected the lane to use `unittest`
  instead of `pytest`.

## Steps / Checklist
- [ ] Build a runtime-oriented `unittest` experiment bench.
- [ ] Exercise a few synthetic-module strategies instead of only one.
- [ ] Run the bench and capture the result.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one `unittest` synthetic-module experiment bench
- one concrete validation result

## Files / Paths Impacted
- tests/experimentation/
- tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py
- codex/context_compass/tickets/tasks/2026-05-02_experiment_pytest_against_synthetic_modules_task.md
- codex/context_compass/attention_board.md

## Validation
- Executed:
  - `python tests/experimentation/unittest_synthetic_module_testbench.py`
- Result:
  - `START_UNITTEST_SYNTHETIC_MODULE_EXPERIMENTS`
  - `OK_UNITTEST_SYNTH_DIRECT_MODULE`
  - `OK_UNITTEST_SYNTH_IMPORT_BY_NAME`
  - `OK_UNITTEST_SYNTH_PATCH_SIBLING`
  - `OK_UNITTEST_SYNTH_RELATIVE_IMPORTS`
  - `OK_UNITTEST_SYNTH_LIFECYCLE`
  - `OK_UNITTEST_SYNTH_LIFECYCLE_ORDER`
  - `OK_UNITTEST_SYNTH_SUITE_COMPOSITION`
  - `OK_UNITTEST_SYNTH_FAILURE_REPORTING`
  - `OK_UNITTEST_SYNTH_DEACTIVATION`
  - `OK_UNITTEST_SYNTH_ASYNC_THREAD`
  - `OK_UNITTEST_SYNTHETIC_MODULE_EXPERIMENTS`

## Risks / Rollback Notes
- Risk: even `unittest` may need stricter import identity than our synthetic
  runtime currently provides.
  Rollback: keep that result explicit instead of overclaiming in-process test
  support.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-02T10:52:26Z
  TYPE: FACT
  CLAIM: The user wants actual runtime test experiments against synthetic
    modules, not another abstract answer.
  EVIDENCE:
  - user_instruction: "can you build an experiment to see if this is true? do a robust inmemory and runtime based pytest on a few different ideas"
  IMPACT: The next move is to build and run a bounded experiment bench, not
    just theorize about projection versus in-memory collection.
  NEXT: add the experiment bench and run it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T10:52:26Z
  TYPE: FACT
  CLAIM: The first `pytest` same-process shape was the wrong experiment. It
    broadened into a whole-directory in-process pytest session with the
    synthetic import hook installed globally, which turned the question from
    "can an in-memory synthetic module be tested?" into "what happens if pytest
    owns a large mutated runtime?" The user explicitly called out that drift and
    redirected the lane to `unittest`.
  EVIDENCE:
  - user_instruction: "bro I never said use subprocess I said use inmemory operations"
  - user_instruction: "ok so try that instane try using unittest instead"
  IMPACT: The right next move is a lighter same-process `unittest` bench, not
    more `pytest` iteration.
  NEXT: build a same-process `unittest` synthetic-module bench with a few
    runtime-oriented ideas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T11:15:13Z
  TYPE: MEASURE
  CLAIM: The lighter same-process `unittest` path works against live synthetic
    modules. The bench passed three different ideas: direct test loading from a
    synthetic module object, import-by-name through the synthetic loader, and a
    `unittest.mock.patch.object` case against a sibling synthetic module.
  EVIDENCE:
  - tests/experimentation/unittest_synthetic_module_testbench.py:1-314
  - validation_result: `python tests/experimentation/unittest_synthetic_module_testbench.py`
  IMPACT: The in-process testing story is much healthier with `unittest` than
    with `pytest`. We now have a working runtime-native test baseline and can
    treat `pytest` as a later subprocess/external compatibility path.
  NEXT: review the `unittest` bench result and decide whether to generalize it
    into a world-native test surface or keep it as an experiment only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T11:20:11Z
  TYPE: PLAN
  CLAIM: The next slice is not a new bench file; it is to deepen the existing
    `unittest` synthetic-module bench with the weak-point cases we explicitly
    identified: relative imports, setup/teardown lifecycle, suite composition,
    failure reporting, activation/deactivation behavior, and any clean
    same-process async/concurrency case we can add without bloating the bench.
  EVIDENCE:
  - prior_discussion: specific weak-point list after the first green unittest bench
  - user_instruction: "test all those things stop fucken drifting bro"
  IMPACT: The lane stays in one unittest file and becomes a deeper stress test
    of the runtime-native test model instead of branching into more files or
    more framework pivots.
  NEXT: extend the existing unittest bench and rerun it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T11:30:15Z
  TYPE: MEASURE
  CLAIM: The deeper `unittest` synthetic-module bench stayed green after the
    weak-point expansion. The same file now proves relative imports,
    lifecycle/class hooks, suite composition, readable failure reporting,
    unload/deactivation behavior, and a small async/thread probe in addition to
    the original direct-module/import-by-name/patch cases.
  EVIDENCE:
  - tests/experimentation/unittest_synthetic_module_testbench.py:1-435
  - validation_result: `python tests/experimentation/unittest_synthetic_module_testbench.py`
  IMPACT: The in-process runtime-native test surface for synthetic modules is
    broader than the baseline case and survived the first real weak-point
    sweep.
  NEXT: if we keep going, the next edge cases are circular imports, larger
    package graphs, and tests against live Melder world objects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T11:23:06Z
  TYPE: MEASURE
  CLAIM: The deeper `unittest` synthetic-module bench is green. In addition to
    the original direct-module/import-by-name/patch cases, the bench now proves
    relative imports, `setUp`/`tearDown` plus class hooks, suite composition
    across multiple synthetic modules, readable failure reporting with synthetic
    module identity, post-unload import failure, and a small async/thread probe.
  EVIDENCE:
  - tests/experimentation/unittest_synthetic_module_testbench.py:1-435
  - validation_result: `python tests/experimentation/unittest_synthetic_module_testbench.py`
  IMPACT: The runtime-native testing story is now significantly stronger than
    the original baseline. We have direct evidence that several weak-point
    seams still work against live synthetic modules in one interpreter.
  NEXT: review the broader green result and decide which remaining seams are
    still worth probing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T12:00:46Z
  TYPE: PLAN
  CLAIM: The next tranche is a second unittest experiment file focused only on
    the uncovered synthetic-module mechanics. The scope is not Melder world
    integration. It is synthetic-module behavior under larger graphs, circular
    imports, reactivation, concurrency, richer unittest features, collision
    behavior, file-backed morph interaction, and larger unload/cleanup scale.
  EVIDENCE:
  - user_instruction: "go ahead and test all those things in a new test file"
  - user_instruction: "We also do not care about testing melder here explicitly these are syntheticmodule mechanics and how unittests interact with that stuff"
  IMPACT: The task moves out of review and back into an implementation plus
    validation pass focused on a second bench file for the remaining seams.
  NEXT: add the new unittest synthetic-module edge-case bench and run it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T12:15:19Z
  TYPE: FACT
  CLAIM: The second synthetic-module edge-case bench needs its own internal
    timeout discipline. The outer tool timeout was not enough to stop one of
    the later experiments cleanly, so the bench currently has a real hang-risk
    seam that must be fixed before more interpretation work.
  EVIDENCE:
  - validation_result: `python tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py` -> user-aborted after long-running hang
  - user_instruction: "bro make sure your fucken process can time out dude, it was running for 8 minutes"
  IMPACT: The next move is not more blind reruns. The bench needs internal
    watchdog behavior and visible per-experiment progress markers first.
  NEXT: add internal per-experiment timeout handling and unbuffered progress
    markers to the edge-case bench, then rerun with a bounded outer timeout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T12:15:19Z
  TYPE: MEASURE
  CLAIM: The watchdog rerun isolated the first real weak seam. Circular
    imports, larger graph load/unload, aggressive patching, richer unittest
    features, concurrent import/use, and reactivation all completed inside the
    timeout budget. The first uncovered edge case that did not complete cleanly
    was collision/authority behavior, which timed out inside the dedicated
    collision block before the file-backed morph case even began.
  EVIDENCE:
  - tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py:1-858
  - validation_result: `python -u tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py` -> timeout at `UNITTEST_SYNTH_EDGE_COLLISION_BLOCK`
  IMPACT: The next synthetic-module investigation should focus narrowly on the
    collision/authority path instead of rerunning the whole edge-case suite
    blindly.
  NEXT: add finer-grained progress markers inside the collision experiment and
    identify the exact import or unload step that stalls.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-02T12:21:14Z
  TYPE: MEASURE
  CLAIM: The second unittest synthetic-module edge-case bench is now green.
    It covers the previously untested seams we cared about in synthetic-module
    scope only: circular imports, larger graph load/unload, aggressive
    multi-module patching, richer unittest features, concurrent import/use,
    reactivation/reload, collision and authority behavior, and file-backed
    morph interaction. The watchdog also now enforces an internal hard timeout
    so one stuck step cannot burn the whole run.
  EVIDENCE:
  - tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py:1-867
  - validation_result: `python -u tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py` -> `OK_UNITTEST_SYNTHETIC_MODULE_EDGE_CASE_EXPERIMENTS`
  IMPACT: The synthetic-module and unittest interaction story is now much
    broader than the first bench alone. The remaining unknowns are no longer
    basic runtime viability; they are future choices about how much more stress
    or cleanup polish we want around these mechanics.
  NEXT: return the second bench result for review and decide whether to keep
    the current coverage or probe even more pathological synthetic-module
    cases later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the focused runtime test synthetic-module experiment lane under
`tests/experimentation/`.
