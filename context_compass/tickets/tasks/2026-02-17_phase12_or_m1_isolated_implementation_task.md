# Task: Implement OR-M1 Overrides Shape-Source Candidate (Isolated Wave2)

## Metadata
- Task ID: TASK-2026-02-17-phase12-or-m1-isolated-implementation
- Story: STORY-2026-02-17-phase12-creation-context-discovery-and-benchmark
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-17T18:28:41Z
- Updated: 2026-02-17T18:28:41Z

## Objective
Implement medium-risk candidate `OR-M1` in isolation and validate its impact
with targeted tests and pinned-core benchmark comparison.

## Ticket Contract
- ENTRY_GATE: next-wave selection task selected `OR-M1` as the next execution
  lane.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
  - `tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
  - `benchmarks/testing_other_di/results/`
- DEPENDENCIES:
  - `tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md`
  - `benchmarks/testing_other_di/results/codegen_benchmark_baseline.json`
- EXIT_GATE: OR-M1 behavior is implemented, tested, benchmarked, and documented
  in story/epic notes with evidence.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if OR-M1 requires widening scope
  outside overrides executor or introduces correctness risk.

## Scope Boundaries
- In scope:
  - shape-specialized source preference in overrides executor compile path,
  - overrides executor unit tests for compile/source-selection contract,
  - benchmark delta capture after implementation.
- Out of scope:
  - no-overrides executor changes,
  - creation-context candidate implementation,
  - high-risk candidates.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: wave-1 rollback required a new isolated medium-risk lane.

## Steps / Checklist
- [ ] Implement OR-M1 source-selection preference in overrides compile flow.
- [ ] Update/extend overrides executor unit tests for OR-M1 contracts.
- [ ] Run targeted pytest validation for overrides lane.
- [ ] Run pinned-core benchmark comparison and capture weighted score.
- [ ] Update story/epic notes and board routing with results.

## Deliverables
- OR-M1 code updates in overrides executor.
- Updated/added unit tests for source-selection behavior.
- Benchmark output comparing OR-M1 branch against baseline.

## Validation
- Not run.
- Planned commands:
  - `$env:PYTHONPATH='.;src'; python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --profile-iteration-count 5 --baseline-path benchmarks/testing_other_di/results/codegen_benchmark_baseline.json --output-path benchmarks/testing_other_di/results/codegen_benchmark_after_or_m1_isolated.json --allow-baseline-regression`

## Risks / Rollback Notes
- Risk: shape-specialized path broadening changes semantics for non-eligible
  plans.
  Mitigation: keep explicit eligibility checks and generic fallback path.
- Risk: benchmark noise masks true OR-M1 effect.
  Mitigation: keep pinned-core and same profile iteration count as baseline.

## Applicable Anti-Patterns
- [ ] No optimization claim without benchmark delta output.
- [ ] No compile-path contract claim without source/test evidence.
- [ ] No scope expansion into non-overrides modules without escalation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Noting Behavior
- Note focus: overrides compile-path findings and immediate validation impact.
- Add a `## Notes` entry after each meaningful tranche.
- Keep entries append-only and evidence-backed.

## Notes
- DATETIME: 2026-02-17T18:28:41Z
  TYPE: PLAN
  CLAIM: OR-M1 is selected as the next isolated medium-risk implementation lane
    because override-route weighting remains the most sensitive benchmark area.
  EVIDENCE:
  - tickets/tasks/2026-02-17_phase12_overrides_executor_discovery_task.md:64-68
  - benchmarks/testing_other_di/results/codegen_benchmark_after_branch_compare_chat_ref.json:809-823
  - benchmarks/testing_other_di/results/codegen_benchmark_after_branch_compare_chat_ref.json:190-193
  IMPACT: Execution can proceed with a single-candidate implementation that is
    directly tied to current benchmark route behavior.
  NEXT: Implement OR-M1 compile-path preference in overrides executor and run
    targeted pytest/benchmark validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task is the active OR-M1 implementation lane for the next wave after
wave-1 rollback.
