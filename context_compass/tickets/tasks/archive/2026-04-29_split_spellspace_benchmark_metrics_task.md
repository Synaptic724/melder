# Task: Split Spellspace Benchmark Metrics

## Metadata
- Task ID: TASK-2026-04-29-split-spellspace-benchmark-metrics
- Story:
- Epic: EPIC-2026-04-29-spellspace-benchmark-measurement-and-optimization
- Status: review
- Owner: codex
- Agent Name: codex_01
- Priority: p0
- Created: 2026-04-29T22:54:23Z
- Updated: 2026-04-29T23:32:05Z

## Objective
Redesign the spellspace benchmark output so it excludes scope-build time from
the primary spellspace meld metric and reports build and total cycle cost
separately for every compared library.

## Ticket Contract
- ENTRY_GATE: the spellspace benchmark discovery epic is active and has
  evidence that the current helper times the whole scope cycle for every
  library.
- EXECUTION_BOUNDARY:
  - `benchmarks/testing_other_di/test_shallow_all.py`
  - this task ticket
  - related attention-board routing/state
- DEPENDENCIES:
  - benchmark discovery epic
  - current runtime builder semantics for dependency-injector, dishka,
    injector, lagom, and melder
- EXIT_GATE: the benchmark prints spellspace meld/build/total metrics from the
  split timing path and focused validation confirms the new output shape.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one library cannot support a
  fair split enter/resolve/exit benchmark path without materially changing the
  benchmark model.

## Scope Boundaries
- In scope:
  - benchmark refactor for split spellspace metrics
  - focused validation of output shape
- Out of scope:
  - Melder runtime optimization
  - broad benchmark-suite redesign outside the spellspace path

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested that spellspace build time
  be excluded from the primary spellspace metric and that build + total be
  shown alongside the meld metric.

## Steps / Checklist
- [ ] Add spellspace enter/resolve/exit hooks to the per-lib runtime ops shape.
- [ ] Add a split timing helper for spellspace build / meld / total metrics.
- [ ] Update the single-resolve benchmark print line to show the new metrics.
- [ ] Run focused validation and capture the output/result.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- updated spellspace benchmark metrics in `test_shallow_all.py`
- focused validation result proving the new output shape

## Files / Paths Impacted
- benchmarks/testing_other_di/test_shallow_all.py
- codex/context_compass/tickets/tasks/2026-04-29_split_spellspace_benchmark_metrics_task.md
- codex/context_compass/tickets/epics/2026-04-29_spellspace_benchmark_measurement_and_optimization_epic.md
- codex/context_compass/attention_board.md

## Validation
- Executed:
  - `$env:PYTHONPATH='src;.'; python -m pytest benchmarks/testing_other_di/test_shallow_all.py::test_single_resolve_timings -q -s`
- Result:
  - Melder printed split spellspace build / first meld / cached meld / exit / total metrics for all selected graphs
  - `5 passed, 10 skipped`
- Notes:
  - the comparison libraries were skipped in this local environment because the
    relevant packages were not installed here

## Risks / Rollback Notes
- Risk: a split metric path drifts semantics across libraries.
  Rollback: keep the old whole-cycle helper as a secondary metric and preserve
  the split path only for the primary spellspace meld comparison.

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
- DATETIME: 2026-04-29T22:58:25Z
  TYPE: PLAN
  CLAIM: The current benchmark shape times the whole spellspace/request scope
    cycle for every library. The requested fix is to keep that total visible if
    useful, but make the primary spellspace metric a split metric where build
    time is excluded and reported separately.
  EVIDENCE:
  - benchmarks/testing_other_di/test_shallow_all.py:824-835
  - benchmarks/testing_other_di/test_shallow_all.py:996-1004
  - benchmarks/testing_other_di/test_shallow_all.py:1054-1061
  - benchmarks/testing_other_di/test_shallow_all.py:1138-1145
  - benchmarks/testing_other_di/test_shallow_all.py:1623-1628
  - user_instruction: "ensure that build time is excluded"
  IMPACT: The implementation work is benchmark-structure work, not Melder
    runtime tuning.
  NEXT: patch the runtime ops shape and single-run timing path to emit split
    spellspace metrics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-29T23:07:12Z
  TYPE: FACT
  CLAIM: The benchmark now exposes split spellspace timing semantics instead of
    only the old whole-cycle helper. `_RuntimeOps` now carries spellspace
    enter/resolve/exit hooks, `_average_spellspace_metrics_ns(...)` computes
    split build/meld/cached/total timings, and the single-run print line now
    shows those metrics next to the A/B root timings.
  EVIDENCE:
  - benchmarks/testing_other_di/test_shallow_all.py:80-121
  - benchmarks/testing_other_di/test_shallow_all.py:787-789
  - benchmarks/testing_other_di/test_shallow_all.py:889-915
  - benchmarks/testing_other_di/test_shallow_all.py:1167-1194
  - benchmarks/testing_other_di/test_shallow_all.py:1270-1303
  - benchmarks/testing_other_di/test_shallow_all.py:1767-1781
  IMPACT: The benchmark can now report the metric the user actually wants:
    spellspace meld speed without folding build time into the primary spellspace
    number, while still leaving build and total visible.
  NEXT: review the split metric shape and rerun in the full comparison
    environment to capture split numbers for dependency-injector and dishka too.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-29T23:07:12Z
  TYPE: MEASURE
  CLAIM: Local validation of the Melder path is green. The split benchmark now
    prints build, meld, cached, and total spellspace timings for each selected
    graph, and the Melder outputs show that build time is a meaningful part of
    the previous whole-cycle metric.
  EVIDENCE:
  - validation_result: `$env:PYTHONPATH='src;.'; python -m pytest benchmarks/testing_other_di/test_shallow_all.py::test_single_resolve_timings -q -s`
  IMPACT: We now have concrete Melder-only evidence for the split metric shape,
    even though the side-by-side comparison libraries still need a rerun in the
    fuller benchmark environment.
  NEXT: run the same benchmark in the environment where dependency-injector and
    dishka are installed so the comparison numbers can be updated cleanly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-29T23:26:36Z
  TYPE: FACT
  CLAIM: The benchmark builder is already using automatic mode for Melder, not
    dynamic mode. `Spellbook.conjure(...)` defaults `automatic=True`, the
    benchmark calls `spellbook.conjure(name=...)` with no override, and
    `SpellbookCreationSystem` passes that automatic flag straight into the
    `Conduit` constructor.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:870-930
  - src/melder/spellbook/spellbook_creation_system.py:95-159
  - src/melder/spellbook/spellbook_creation_system.py:286-315
  - benchmarks/testing_other_di/test_shallow_all.py:1224-1251
  IMPACT: The spellspace benchmark is not accidentally paying dynamic-mode gate
    behavior. The remaining spellspace cost is inside the automatic-mode
    spellspace lifecycle and resolve path itself.
  NEXT: focus tracing on `SpellSpace` enter/cleanup bookkeeping and the
    `unique_per_spell_space` route in Meld/CreationContext.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-29T23:26:36Z
  TYPE: FACT
  CLAIM: The remaining spellspace cost is coming from real spellspace-specific
    mechanics. One spellspace cycle in Melder creates and registers a
    `SpellSpace`, pushes/pops the context-local spellspace stack, checks active
    scope through `SpellSpace.meld(...)`, routes through the
    `unique_per_spell_space` branch in Meld/CreationContext, and on exit resets
    and clears the spellspace bucket from `Creations`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:601-634
  - src/melder/aether/conduit/spell_space/spell_space.py:14-188
  - src/melder/aether/conduit/creations/creations.py:519-624
  - src/melder/aether/conduit/meld/meld.py:503-515
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:66-79
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:547-575
  IMPACT: The gap is not explained by accidental dynamic mode. The next useful
    decomposition is to separate spellspace first-create cost from cached
    in-scope cost and then inspect whether stack, lookup, or cleanup semantics
    are still too heavy.
  NEXT: add or inspect first-create vs cached-in-scope metrics if the current
    split still hides too much inside the averaged spellspace meld field.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-29T23:32:05Z
  TYPE: MEASURE
  CLAIM: The corrected benchmark semantics now show the actual spellspace seam.
    The cached meld inside an already-active spellspace is cheap for Melder
    (roughly ~1us across the sampled graphs), while the first spellspace meld is
    the heavy path (roughly ~7us solo, ~13-14us shallow/wide/diamond, and
    ~31us deep). Build and exit are non-trivial but clearly smaller than the
    first spellspace meld on the non-solo graphs.
  EVIDENCE:
  - validation_result: `$env:PYTHONPATH='src;.'; python -m pytest benchmarks/testing_other_di/test_shallow_all.py::test_single_resolve_timings -q -s`
  IMPACT: The benchmark is no longer hiding the real hot path. The next useful
    optimization/discovery work should focus on first-create / first-meld
    behavior in the `unique_per_spell_space` route rather than on cached lookup
    or on generic root meld speed.
  NEXT: compare the same split metrics in the full comparison environment and
    then trace what the first spellspace meld does that ordinary many-route meld
    does not.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the benchmark-level refactor that separates spellspace build
time from spellspace meld time and reports total cycle cost separately.
