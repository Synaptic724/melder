# Task: Optimize Overrides Executor Kwargs Fast Path

## Metadata
- Task ID: TASK-2026-02-18-overrides-executor-kwargs-fastpath
- Story: STORY-2026-02-18-codegen-baseline-and-hotspot-map
- Status: blocked
- Owner: codex
- Priority: p0
- Created: 2026-02-18T10:37:40Z
- Updated: 2026-02-18T10:39:48Z

## Objective
Reduce overhead in phase12 overrides executor kwargs materialization for steps
with empty override values by adding a no-membership-check fast path.

## Ticket Contract
- ENTRY_GATE: post-revert baseline is restored and story remains active.
- EXECUTION_BOUNDARY: `phase12_overrides_executor.py` helper optimization only.
- DEPENDENCIES: pinned deep profile hotspot map and prior tranche rollback decision.
- EXIT_GATE: helper patch + pinned rerun evidence for non-spellspace means.
- FAILURE_ESCALATION: raise `CONFLICT` if helper change requires expanding into generator architecture edits.

## Scope Boundaries
- In scope:
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
  - benchmark rerun artifacts for before/after comparison
- Out of scope:
  - patch-map internals
  - creation-context dispatch changes
  - benchmark harness behavior changes

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: reverted baseline requires a fresh hotspot tranche.

## Steps / Checklist
- [x] Add fast-path boolean guard in `_build_kwargs_with_overrides` to skip
      override-membership checks when `override_values` is empty.
- [x] Verify compile correctness.
- [x] Run pinned reruns and compute non-spellspace mean deltas.
- [x] Record results in notes and update story/epic routing notes.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Helper-level optimization patch.
- Pinned rerun artifacts and delta summary.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_overrides_executor_tranche3.json`

## Validation
- Not run.
- Recommended commands:
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 3 --warmup-count 1 --pin-p-cores --output-path benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_overrides_executor_tranche3.json`

## Risks / Rollback Notes
- Risk: altered kwargs precedence when overrides are present.
  - Mitigation: only gate membership checks behind `has_override_values` while preserving existing precedence logic.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_overrides_executor_tranche3.json
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: story closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-18T10:37:40Z
  TYPE: PLAN
  CLAIM: `_build_kwargs_with_overrides` will skip per-parameter `param_name in override_values` checks when `override_values` is empty, preserving existing precedence for non-empty cases.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2759-2888
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:602-616
  IMPACT: This targets helper overhead inside generated overrides executor without reopening reverted tranche code.
  NEXT: Apply helper patch and run pinned reruns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:39:48Z
  TYPE: MEASURE
  CLAIM: Two pinned reruns for tranche 3 show slight targeted improvement (`warm_override_targeted_ns` -0.98%) but mixed-route regression (`warm_mixed_ns` +3.25%) versus pinned baseline.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_overrides_executor_tranche3.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_overrides_executor_tranche3_r2.json:652-671
  IMPACT: Tranche does not meet mixed-route acceptance expectation and is not kept.
  NEXT: Revert tranche 3 patch and move to a different hotspot.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:39:48Z
  TYPE: DECISION
  CLAIM: Tranche 3 overrides-executor kwargs fast-path patch has been reverted.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2759-2888
  IMPACT: Codebase is restored to baseline for this hotspot; follow-on work must target another optimization surface.
  NEXT: Start a new hotspot tranche focused on no-args invocation fast path in phase12 executors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Tranche 3 was measured and reverted due mixed-route regression. Next step is a
new hotspot tranche on phase12 no-args invocation path.
