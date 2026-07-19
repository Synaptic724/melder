# Task: Experiment Melder Spellspace Cycle Metrics

## Metadata
- Task ID: TASK-2026-04-29-experiment-melder-spellspace-cycle-metrics
- Story:
- Epic: EPIC-2026-04-29-spellspace-benchmark-measurement-and-optimization
- Status: in_progress
- Owner: codex
- Agent Name: codex_01
- Priority: p0
- Created: 2026-04-29T23:49:00Z
- Updated: 2026-04-30T00:07:03Z

## Objective
Build a focused Melder-only experimentation bench that measures spellspace
build, first meld, cached meld, and cleanup separately so we can see the raw
scope-cycle mechanics without the cross-library benchmark harness.

## Ticket Contract
- ENTRY_GATE: the spellspace benchmark epic is active and the benchmark lane
  already shows spellspace build/first/cached/exit splits for Melder.
- EXECUTION_BOUNDARY:
  - `tests/experimentation/`
  - this task ticket
  - related epic/board state only
- DEPENDENCIES:
  - Melder spellspace runtime path
  - current benchmark understanding from `test_shallow_all.py`
- EXIT_GATE: one focused experiment exists, runs, and prints separate Melder
  spellspace cycle metrics for at least one minimal and one non-trivial graph.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the bench needs production
  runtime edits rather than simple experimentation code.

## Scope Boundaries
- In scope:
  - focused experimentation bench
  - Melder-only measurements
  - build/first/cached/cleanup timing separation
- Out of scope:
  - cross-library benchmarking
  - production Melder optimization edits

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a Melder-only experiment to
  measure spellspace build, first meld, cached meld, and cleanup.

## Steps / Checklist
- [ ] Add a Melder-only spellspace experimentation bench under `tests/experimentation/`.
- [ ] Measure build, first meld, cached meld, and cleanup separately.
- [ ] Run the bench and capture the result.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Melder-only spellspace cycle experiment bench
- one concrete printed timing result

## Files / Paths Impacted
- tests/experimentation/
- codex/context_compass/tickets/tasks/2026-04-29_experiment_melder_spellspace_cycle_metrics_task.md
- codex/context_compass/tickets/epics/2026-04-29_spellspace_benchmark_measurement_and_optimization_epic.md

## Validation
- Executed:
  - `python tests/experimentation/melder_spellspace_cycle_testbench.py`
- Result:
  - `[melder-spellspace-experiment] solo iters(1000) | build=4.76us | first_meld=7.07us | cached_meld=0.96us | exit=2.11us | total=14.91us`
  - `[melder-spellspace-experiment] shallow iters(1000) | build=5.20us | first_meld=13.80us | cached_meld=1.07us | exit=2.71us | total=22.78us`
  - `[melder-spellspace-experiment] deep iters(1000) | build=5.36us | first_meld=30.19us | cached_meld=1.16us | exit=3.46us | total=40.17us`
  - `OK_MELDER_SPELLSPACE_CYCLE_EXPERIMENT`
- Executed:
  - `python tests/experimentation/melder_spellspace_cycle_testbench.py`
- Result:
  - `[melder-conduit-experiment] solo iters(500) | normal_build=3152.12us | normal_first_meld=99.64us | normal_cached_meld=1.79us | lesser_build=26.99us | lesser_first_meld=8.60us | lesser_cached_meld=0.86us | lesser_cleanup=8.04us | normal_cleanup=5006.41us`
  - `[melder-conduit-experiment] shallow iters(500) | normal_build=4018.33us | normal_first_meld=133.71us | normal_cached_meld=1.92us | lesser_build=30.83us | lesser_first_meld=14.23us | lesser_cached_meld=1.08us | lesser_cleanup=10.87us | normal_cleanup=5818.80us`
  - `[melder-conduit-experiment] deep iters(500) | normal_build=6703.39us | normal_first_meld=199.95us | normal_cached_meld=2.74us | lesser_build=33.59us | lesser_first_meld=30.33us | lesser_cached_meld=1.19us | lesser_cleanup=12.05us | normal_cleanup=6028.58us`
  - `OK_MELDER_SPELLSPACE_CYCLE_EXPERIMENT`
- Executed:
  - `python tests/experimentation/melder_spellspace_cycle_testbench.py`
- Result:
  - automatic and dynamic mode printed side-by-side for spellspace, normal conduit, and lesser conduit cycles
  - `OK_MELDER_SPELLSPACE_CYCLE_EXPERIMENT`

## Risks / Rollback Notes
- Risk: the experiment duplicates too much benchmark setup code.
  Rollback: keep it explicitly experimental and narrow rather than trying to
  over-generalize it.

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
- DATETIME: 2026-04-29T23:49:00Z
  TYPE: PLAN
  CLAIM: The user wants a focused Melder-only experiment that isolates raw
    spellspace lifecycle mechanics: create scope, first meld, cached meld, and
    cleanup. The goal is to see the raw shape directly in `tests/experimentation`
    rather than only through the cross-library benchmark harness.
  EVIDENCE:
  - user_instruction: "can you do an experiment in tests/experimentation and compare against a spellspace creation full creation to meld some object meld a cached and then cleanup"
  IMPACT: The next move is a narrow experiment bench, not more benchmark
    abstraction.
  NEXT: add the focused Melder-only experiment and run it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-29T23:50:40Z
  TYPE: MEASURE
  CLAIM: The focused experiment is green and confirms the split benchmark
    numbers. The major cost is not cached spellspace meld and not build alone;
    it is the first spellspace meld path after the scope is active.
  EVIDENCE:
  - tests/experimentation/melder_spellspace_cycle_testbench.py:1-201
  - validation_result: `python tests/experimentation/melder_spellspace_cycle_testbench.py` -> `OK_MELDER_SPELLSPACE_CYCLE_EXPERIMENT`
  IMPACT: The benchmark lane can now stop asking whether the harness is the
    main cause. The runtime path itself is the next real target.
  NEXT: use the runtime trace to attack first spellspace meld semantics
    directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-29T23:54:15Z
  TYPE: MEASURE
  CLAIM: The extended Melder-only experiment shows that spellspace is much
    cheaper than a full normal-conduit cycle and very close to a lesser-conduit
    cycle. The heavy costs in the broader system are the normal root-conduit
    build and normal cleanup, while spellspace first-meld sits roughly in the
    same range as lesser-conduit first-meld for the same shapes.
  EVIDENCE:
  - tests/experimentation/melder_spellspace_cycle_testbench.py:1-295
  - validation_result: `python tests/experimentation/melder_spellspace_cycle_testbench.py` -> printed spellspace and conduit metrics for solo/shallow/deep
  IMPACT: This narrows the likely diagnosis. Spellspace is not uniquely
    pathological relative to all Melder scoping options; the normal root-conduit
    lifecycle is far heavier, and the spellspace first-meld path looks more like
    a lightweight scoped-create path than like the full conduit bring-up.
  NEXT: compare spellspace first-meld and lesser-conduit first-meld paths more
    directly in code to see which extra mechanics account for the residual gap.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-30T00:07:03Z
  TYPE: MEASURE
  CLAIM: Dynamic mode adds visible overhead across the board. Spellspace cached
    meld rises from roughly `~1.08-1.44us` in automatic mode to
    `~1.60-2.08us` in dynamic mode on the sampled shapes; lesser cached meld
    rises from `~0.91-1.13us` to `~1.62-2.00us`; and normal cached meld rises
    from `~1.93-2.63us` to `~2.74-3.90us`. The same pattern shows up in first
    meld and cleanup. The dynamic-mode gate/ticket machinery is therefore a
    real contributor on these paths.
  EVIDENCE:
  - tests/experimentation/melder_spellspace_cycle_testbench.py:1-297
  - validation_result: `python tests/experimentation/melder_spellspace_cycle_testbench.py` -> automatic/dynamic side-by-side timings
  IMPACT: Automatic-vs-dynamic differences are now measured directly instead of
    guessed. Any future spellspace optimization story should separate automatic
    and dynamic expectations instead of treating them as one cost surface.
  NEXT: if desired, trace the dynamic gate/ticket path specifically to quantify
    how much of the delta is in gate admission versus the underlying create path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns a focused experimentation bench for Melder spellspace
build/first/cached/cleanup timing, separate from the broader cross-library
benchmark lane.
