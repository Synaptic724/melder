# Task: Investigate single-meld lock and check_cleaned paths

## Metadata
- Task ID: TASK-2026-05-23-investigate-single-meld-lock-and-check-cleaned-paths
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-24T01:16:49Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Build one focused single-meld benchmark that resolves one representative object
once and reports:
- which runtime-owned locks participate in that one meld path
- how many times each instrumented lock is entered/acquired/released
- how many `check_cleaned()` calls happen in one meld

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for a one-meld investigation bench
  rather than more gauntlet-level aggregate profiling.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/conduit/meld/meld.py`
  - `src/melder/aether/conduit/creations/creations.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - `src/melder/utilities/general_base/cleanable.py`
  - one new focused benchmark/experimentation file
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-23_fix_melder_only_gauntlet_benchmark_task.md`
  - `tickets/tasks/2026-05-23_add_real_world_gauntlet_gil_mode_switch_task.md`
- EXIT_GATE: one focused single-meld bench runs under `.venv_new`, produces a
  concrete per-meld lock/check-cleaned report, and the static lock path is
  summarized with evidence.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if truthful lock counting
  requires widening beyond a bounded bench into broader runtime instrumentation.

## Scope Boundaries
- In scope:
  - one representative single-meld runtime setup
  - static read of lock/check-cleaned call paths
  - dynamic instrumentation of owned `_lock` surfaces and `check_cleaned()`
  - one focused run and report
- Out of scope:
  - broad gauntlet profiling
  - runtime optimization changes
  - multi-thread contention analysis

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly redirected the lane to one-meld
  lock-path and `check_cleaned()` investigation.

## Steps / Checklist
- [ ] Re-read the one-meld path in conduit, meld, creations, creation context,
      and cleanable sources.
- [ ] Build one focused bench that resolves one representative object once.
- [ ] Instrument `check_cleaned()` calls and owned `_lock` surfaces.
- [ ] Run the bench under `.venv_new`.
- [ ] Summarize per-meld lock traffic and `check_cleaned()` counts with source
      evidence.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- one focused single-meld bench
- one per-meld lock/check-cleaned count report
- one static lock-path summary tied to source lines

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-23_investigate_single_meld_lock_and_check_cleaned_paths_task.md`
- `codex/context_compass/attention_board.md`
- one new benchmark or experimentation file under `benchmarks/testing_other_di/`
  or `tests/experimentation/`

## Validation
- Not run.
- Planned commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -q -s <focused bench path>`

## Risks / Rollback Notes
- Risk: lock traffic at the Python level may be undercounted if some important
  paths use built-in lock behavior we cannot attribute without a broader hook.
- Rollback: keep the bench honest about what it instruments and pair it with a
  static call-path summary instead of inventing precision.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No gauntlet-level conclusions from one-meld data.

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
- Note focus: static lock path, instrumented counts, and one-step continuation.
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
- DATETIME: 2026-05-24T01:16:49Z
  TYPE: PLAN
  CLAIM: The user does not want another aggregate gauntlet answer. The narrow
    question is: for one representative meld, which owned locks participate and
    how many `check_cleaned()` calls happen. The right cut is therefore one
    focused bench plus a static one-meld call-path read, not another whole-run
    profile interpretation.
  EVIDENCE:
  - user_instruction
  IMPACT: The next step is to read the exact one-meld runtime path and then
    build a single-meld bench with explicit instrumentation.
  NEXT: read `conduit.py`, `meld.py`, `creations.py`, `creation_context.py`,
    and `cleanable.py` at the one-meld entrypoints and guard paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T01:31:12Z
  TYPE: FACT
  CLAIM: The one-meld hot path is already narrower than the gauntlet totals
    imply. `Conduit.meld(...)` does a front-door `check_cleaned()` and, in
    dynamic mode only, creation-gate ticketing before delegating. `Meld.meld(...)`
    itself is not wrapped in a blanket `with self._lock`; the meld-owned
    `RLock` is used for cleanup and lazy `SpellCompilerSystem` initialization.
    `CreationContext` is spell-owned and reused through
    `Spell._get_or_build_creation_context()` plus
    `CreationContextFactory.get_or_build_for_spell(...)`, not rebuilt per
    lesser conduit or per spellspace entry.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2612-2710
  - src/melder/aether/conduit/meld/meld.py:264-448
  - src/melder/aether/conduit/meld/meld.py:1384-1400
  - src/melder/aether/spellbook/spell.py:665-694
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:101-359
  IMPACT: The focused bench should instrument the actual participating lock
    owners instead of assuming every meld descends through a global meld lock
    or rebuilds creation context on each scope.
  NEXT: read `CreationContextFactory` and then build a single-meld bench around
    one representative gauntlet request object with lock proxies and a global
    `check_cleaned()` counter.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T01:36:40Z
  TYPE: DECISION
  CLAIM: The focused bench should not include scope creation/teardown in the
    measured window. The representative target will be one gauntlet
    request-scope root object resolved inside an already-open lesser conduit
    plus spellspace, with two measured calls:
    - first resolve in that scope
    - second resolve in the same scope
    That isolates per-meld lock and `check_cleaned()` traffic from the much
    larger scope-churn cost.
  EVIDENCE:
  - user_instruction
  - benchmarks/testing_other_di/test_melder_gauntlet.py:126-178
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:968-1047
  IMPACT: The bench can answer the one-meld question directly and also show the
    warm-path delta without contaminating the counts with lesser-conduit or
    spellspace setup/cleanup noise.
  NEXT: add the focused bench file with lock proxies, a `check_cleaned()`
    counter, and first-vs-second in-scope meld reporting for one request root.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T01:43:55Z
  TYPE: MEASURE
  CLAIM: The first focused bench result sharply narrows the actual one-meld
    lock story. For one representative request-root object inside an already
    open lesser conduit + spellspace:
    - first in-scope meld hit `check_cleaned()` `455` times
    - second same-scope meld hit `check_cleaned()` `15` times
    - neither call touched a blanket front-door `Conduit._lock` or
      `Meld._lock`
    - the dominant participating lock on both calls was the lesser conduit's
      `Creations._lock` (`63` enters on the first call, `61` on the second)
    - the first call also touched the root conduit's `Creations._lock`
      (`10` enters) and five singleton `Spell._lock` entries once each
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_single_meld_lock_and_check_cleaned.py:1-401
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q -s benchmarks\\testing_other_di\\test_melder_single_meld_lock_and_check_cleaned.py`
  IMPACT: The warm-path question is now more specific than "lots of locks".
    The obvious hot lock in this representative path is `Creations._lock`,
    while the blanket "meld is lock-wrapped" hypothesis is false for this
    route.
  NEXT: summarize the measured owners plus the `check_cleaned()` caller
    breakdown to the user, and flag the remaining open question: whether to
    add a second micro-bench for a simpler root/singleton meld to isolate
    pure warm-hit behavior from request-root graph traversal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T01:50:31Z
  TYPE: FACT
  CLAIM: The `SpellIndex.current` hotspot is not spread across dozens of
    runtime layers in this representative first meld. All `408` reads came
    from one Phase 11 IR-building path in
    `shared_compiler_executions.py`:
    - `204` reads from `build_phase11_step_ir_row(...)`
    - `204` reads from the `step_spell_ids` tuple-comprehension inside
      `build_phase11_variant_ir_payload(...)`
    The second same-scope meld hit `SpellIndex.current` `0` times, which means
    this is a first-build artifact-generation cost, not a warm cached-meld
    cost.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1108-1108
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1351-1351
  - src/melder/aether/spellbook/bind/spell_index.py:113-124
  - validation_result: focused caller-count pass on the same representative
    request-root meld
  IMPACT: The 408-read spike is telling us that the first request-root meld is
    still paying Phase 11 IR/signature construction work for that spell graph.
    It is not evidence that the steady-state warm meld path itself keeps
    hammering `SpellIndex.current`.
  NEXT: answer the user with the exact caller breakdown and distinguish first
    build cost from steady-state warm-hit cost.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T10:54:24Z
  TYPE: FACT
  CLAIM: The repo state changed after the first caller-count run: `SpellIndex.current`
    no longer calls `check_cleaned()`. In the current code it only acquires
    its local `RLock` and returns `_current_id`. Re-running the focused
    representative first-meld `check_cleaned()` counter confirms the current
    hot set no longer includes `SpellIndex.current`; the remaining dynamic
    callers are small `Creations`, `SpellSpace`, and plan-artifact accessors.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:113-125
  - validation_result: focused representative first-meld caller-count rerun
  IMPACT: My earlier statement that the current benchmark-path
    `check_cleaned()` spike was dominated by `SpellIndex.current` is stale for
    the current repo state. The live question is now lock traffic and the
    smaller remaining `check_cleaned()` set, not `SpellIndex.current`
    guard overhead.
  NEXT: answer the user with the current benchmark-path callsites only and
    explicitly mark the prior SpellIndex guard attribution as obsolete.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the focused one-meld lock and `check_cleaned()` investigation.
The target is a representative single resolve, not another gauntlet aggregate.

