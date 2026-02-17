# Task: Establish P-Core Baseline And Weighted Benchmark Scoring

## Metadata
- Task ID: TASK-2026-02-17-codegen-benchmark-pcore-baseline-and-scoring
- Story: STORY-2026-02-17-phase12-creation-context-discovery-and-benchmark
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-17T15:53:33Z
- Updated: 2026-02-17T15:53:33Z

## Objective
Define and run the benchmark protocol required before any optimization success
claim: pinned P-core before/after runs with weighted scoring (75% cProfile,
25% time diff).

## Ticket Contract
- ENTRY_GATE: story is active and benchmark harness path is in scope.
- EXECUTION_BOUNDARY:
  `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py` and
  `benchmarks/p_core_affinity/p_core_affinity.py`.
- DEPENDENCIES: location discovery tasks for interpretation context.
- EXIT_GATE: baseline command set, output schema, and scoring rubric are
  documented and ready for implementation waves.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if cProfile integration requires
  benchmark schema changes.

## Scope Boundaries
- In scope:
  - pinned-core run commands and output capture
  - structured before/after report requirements
  - weighted scoring definition
- Out of scope:
  - optimization implementation

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: task created for user-requested benchmark discipline and
  weighted success scoring.

## Steps / Checklist
- [ ] Confirm pinned-core command contract (`--pin-p-cores`).
- [ ] Define baseline run command for fast and override routes.
- [ ] Define after-change run command and comparison workflow.
- [ ] Define cProfile capture format and weighted score formula.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Benchmark protocol section with exact commands.
- Weighted scoring rubric and pass criteria.
- Structured data schema proposal for cProfile + time outputs.

## Files / Paths Impacted
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `benchmarks/p_core_affinity/p_core_affinity.py`
- `context_compass/tickets/tasks/2026-02-17_codegen_benchmark_pcore_baseline_and_scoring_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --output-path benchmarks/testing_other_di/results/codegen_benchmark_baseline.json`
  - `python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --baseline-path benchmarks/testing_other_di/results/codegen_benchmark_baseline.json --output-path benchmarks/testing_other_di/results/codegen_benchmark_after.json`

## Risks / Rollback Notes
- Risk: noisy measurements if affinity is not applied consistently.
- Mitigation: require affinity status capture in benchmark report output.

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
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-17T15:53:33Z
  TYPE: FACT
  CLAIM: Benchmark CLI already supports pinned-core execution and route-level
    medians, but cProfile capture is not currently part of the report schema.
  EVIDENCE:
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:358-362
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:760-845
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:945-1018
  IMPACT: We need explicit discovery/planning for cProfile integration before
    applying the 75% profiler-weighted success policy.
  NEXT: Define structured cProfile data model and weighted score computation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Task created to enforce pinned-core before/after benchmarking and weighted
success scoring policy for optimization waves.
