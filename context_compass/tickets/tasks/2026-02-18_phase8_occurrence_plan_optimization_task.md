# Task: Optimize Phase 8 Occurrence Plan Compilation

## Metadata
- Task ID: TASK-2026-02-18-phase8-occurrence-plan-optimization
- Story: STORY-2026-02-18-phase8-occurrence-plan-speedup
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-18T18:54:05Z
- Updated: 2026-02-18T20:31:23Z

## Objective
Implement approved Phase 8 optimizations after discovery confirms hotspots.

## Ticket Contract
- ENTRY_GATE: discovery task provides evidence-backed Phase 8 hotspot ranking.
- EXECUTION_BOUNDARY: Phase 8 compile/invalidation surfaces only.
- DEPENDENCIES: TASK-2026-02-18-phase8-12-holistic-codegen-discovery.
- EXIT_GATE: changes merged with weighted benchmark non-regression.
- FAILURE_ESCALATION: raise CONFLICT if changes require cross-phase rewrites.

## Scope Boundaries
- In scope:
  - Phase 8 compile flow
  - phase8 signature/caching interactions
- Out of scope:
  - Phase 9-12 implementations

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: tranche #1 cleared; attention routing moved to tranche #2 phase8 implementation.

## Steps / Checklist
- [ ] Confirm discovery findings and exact target functions.
- [ ] Implement Phase 8 optimization tranche.
- [ ] Update docs/comments/tests where needed.
- [ ] Benchmark fast/override routes with weighted score policy.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Phase 8 code optimization patch.
- Validation report including weighted and route metrics.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/` paths as required by behavior changes
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py` (only if needed)

## Validation
- Not run.
- Recommended commands:
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --profile-iteration-count 5 --baseline-path <baseline_json> --weighted-cprofile-weight 0.75 --weighted-time-weight 0.25 --output-path <phase8_after_json>`

## Risks / Rollback Notes
- Risk: cache invalidation regressions.
- Mitigation: preserve signature behavior and add targeted tests.

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
- DATETIME: 2026-02-18T18:54:05Z
  TYPE: PLAN
  CLAIM: Task is staged and will start only after holistic discovery finalizes
    Phase 8 hotspot ranking.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md:1-147
  IMPACT: Keeps optimization plan evidence-driven.
  NEXT: wait for discovery completion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-02-18T19:23:32Z
  TYPE: PLAN
  CLAIM: Ranked execution order sets this task in tranche #2 with concrete target symbols: `run_phase_occurrence_plan`, `_build_phase8_occurrence_plan_input_signature`, and `_mark_phase8_11_codegen_ir_dirty` in `spell_crafter.py`.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md:129-163
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4058-4113
  IMPACT: Phase8 work is now explicitly constrained to occurrence-plan compile/reuse + dirty-flag transitions that feed downstream IR export.
  NEXT: execute after tranche #1, preserving phase11 parity while reducing avoidable phase8 recompute churn.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T19:32:27Z
  TYPE: DECISION
  CLAIM: Task is now active as tranche #2 after phase11 benchmark gate clearance.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase11_execution_plan_optimization_task.md:30-33
  - tickets/tasks/2026-02-18_phase11_execution_plan_optimization_task.md:146-154
  IMPACT: Implementation focus shifts to phase8 occurrence-plan compile/reuse and dirty-flag boundaries.
  NEXT: capture first phase8 implementation finding before touching phase9/phase10 tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T19:58:37Z
  TYPE: FACT
  CLAIM: Phase8 cache-hit checks still pay full deep input-signature recomputation on each run, while phase11 already uses a fast-key guard to skip equivalent deep signature rebuild when inputs are unchanged.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:786-911
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4094-4103
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4386-4419
  IMPACT: Warm phase8 runs can incur avoidable signature cost before the existing plan-reuse return path.
  NEXT: implement a scoped phase8 fast-key reuse guard that preserves current dirty-flag semantics and only reuses cached signatures when phase8 inputs are available.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T20:04:50Z
  TYPE: MEASURE
  CLAIM: Weighted benchmark run against the tranche baseline currently fails route-baseline and weighted gates (`warm_root_ns`, `warm_override_root_args_ns`, `warm_override_targeted_ns`), with `overall_weighted_ratio=1.0283`.
  EVIDENCE:
  - context_compass/artifacts/2026-02-18_phase8_after.json:181-197
  - context_compass/artifacts/2026-02-18_phase8_after.json:810-817
  IMPACT: The current phase8 patch state is not acceptance-ready and requires either further optimization or benchmark-stability follow-up before closure.
  NEXT: run targeted unit tests, then inspect the phase8 fast-key path for extra warm-route overhead before rerunning weighted validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T20:17:26Z
  TYPE: MEASURE
  CLAIM: Means-only before/after graph snapshots (solo/shallow/wide/diamond) for both fast and override lanes are now captured in artifacts, showing lower after means across all requested graphs/lane pairs.
  EVIDENCE:
  - context_compass/artifacts/2026-02-18_fast_graphs_benchmark.jsonl:1-4
  - context_compass/artifacts/2026-02-18_override_graphs_benchmark.jsonl:1-4
  - context_compass/artifacts/phase8_after_snapshot_2026-02-18_20-16-20.json:144-322
  - context_compass/artifacts/2026-02-18_phase8_fast_override_means_before_after.json:7-48
  IMPACT: Requested mean-only lane reporting is satisfied with artifact-backed before/after values for all four graphs in fast and override routes.
  NEXT: run targeted phase8 unit tests and then rerun weighted codegen benchmark gate to confirm acceptance criteria.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T20:31:23Z
  TYPE: MEASURE
  CLAIM: Matched before/after cprofile graph datasets show phase8 change is effectively flat-to-worse on requested mean lanes (fast: 3/4 worse, override: 2/4 worse) and weighted cprofile-time gate still fails only on `warm_override_targeted_ns` with unchanged cprofile ratio.
  EVIDENCE:
  - context_compass/artifacts/2026-02-18_phase8_cprofile_graph_means_before_after.json:3-58
  - context_compass/artifacts/2026-02-18_phase8_after_weighted.json:807-843
  - context_compass/artifacts/2026-02-18_phase8_weighted_cprofile_route_comparison.json:5-40
  IMPACT: Prior large deltas were invalid cross-harness comparisons; matched datasets do not show a real phase8 speedup and do not improve cprofile call density.
  NEXT: either drop/reshape phase8 fast-key optimization or retarget the hotspot to `warm_override_targeted_ns` where weighted regression remains.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Task is active and ready for tranche #2 implementation after phase11 gate
clearance.
