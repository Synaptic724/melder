# Task: Optimize Phase 12 and Creation Context Execution Paths

## Metadata
- Task ID: TASK-2026-02-18-phase12-creation-context-optimization
- Story: STORY-2026-02-18-phase12-creation-context-speedup
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-02-18T18:54:05Z
- Updated: 2026-02-18T18:54:05Z

## Objective
Implement approved Phase 12 and creation_context optimizations targeting fast
and override routes, while preserving behavior and enforcing weighted policy.

## Ticket Contract
- ENTRY_GATE: discovery notes provide ranked phase12/creation_context hotspots.
- EXECUTION_BOUNDARY: phase12 executors and creation_context execute helpers.
- DEPENDENCIES: TASK-2026-02-18-phase8-12-holistic-codegen-discovery.
- EXIT_GATE: weighted benchmark passes and route means/medians are reported.
- FAILURE_ESCALATION: raise DECISION_REQUEST for scope expansion or parity risk.

## Scope Boundaries
- In scope:
  - `phase12_no_overrides_executor.py`
  - `phase12_overrides_executor.py`
  - `creation_context.py` execution helpers
  - benchmark/report changes required for mean metrics (if missing)
- Out of scope:
  - unrelated phase refactors
  - external API changes

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: execution task prepared for primary target lane.

## Steps / Checklist
- [ ] Confirm ranked hotspots from discovery notes.
- [ ] Implement approved optimization tranche for phase12/creation_context.
- [ ] Add or update tests for behavioral parity.
- [ ] Ensure validation reports both means and medians for fast/override routes.
- [ ] Validate using weighted policy:
      `cprofile_weight=0.75`, `time_weight=0.25`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Phase12/creation_context optimization patch.
- Weighted benchmark report with fast/override route means and medians.
- Non-regression evidence for behavior and performance.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py` (if mean fields required)

## Validation
- Not run.
- Recommended commands:
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --profile-iteration-count 5 --output-path <baseline_json>`
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --profile-iteration-count 5 --baseline-path <baseline_json> --weighted-cprofile-weight 0.75 --weighted-time-weight 0.25 --output-path <phase12_after_json>`

## Risks / Rollback Notes
- Risk: improvement on fast route regresses override routes.
- Mitigation: gate acceptance on both fast and override weighted scores.
- Risk: missing mean metrics in report schema.
- Mitigation: add schema extension within benchmark runner if discovery confirms gap.

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
  TYPE: FACT
  CLAIM: Weighted scoring already combines profile and time ratios and defaults
    to 0.75/0.25, matching requested validation policy.
  EVIDENCE:
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:353-355
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1183-1187
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1222-1223
  IMPACT: Implementation can enforce policy without redefining benchmark math.
  NEXT: confirm mean metric availability and phase12 hotspot ranking in discovery.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T19:23:32Z
  TYPE: PLAN
  CLAIM: Ranked execution order sets this task as tranche #3 with concrete target symbols: `CreationContext._execute_with_overrides`, `_get_or_compile_override_executor`, and `_compile_override_executor_from_plan_rows`, plus route/weighted benchmark gates in `run_codegen_benchmark_deltas.py`.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md:129-163
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:565-706
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1064-1176
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:810-840
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:971-1229
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1280-1346
  IMPACT: Phase12/context work is now explicitly focused on override specialization cache-hit/miss cost and validated against existing route matrix + weighted score reports.
  NEXT: execute after tranche #1 and #2 complete, then confirm route medians/weighted ratios stay within gate thresholds.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Primary implementation task is prepared and blocked on discovery completion.
