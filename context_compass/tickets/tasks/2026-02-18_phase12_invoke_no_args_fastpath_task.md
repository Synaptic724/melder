# Task: Optimize Phase12 Invoke No-Args Fast Path

## Metadata
- Task ID: TASK-2026-02-18-phase12-invoke-no-args-fastpath
- Story: STORY-2026-02-18-codegen-baseline-and-hotspot-map
- Status: blocked
- Owner: codex
- Priority: p0
- Created: 2026-02-18T10:41:20Z
- Updated: 2026-02-18T10:42:12Z

## Objective
Reduce invocation overhead for phase12 executor calls without `__args__` by
using direct `spell.spell(**kwargs)` paths instead of allocating/splatting an
empty args list.

## Ticket Contract
- ENTRY_GATE: baseline is restored and active board routes to this story.
- EXECUTION_BOUNDARY: phase12 helper invoke paths only (`phase12_no_overrides_executor.py` and `phase12_overrides_executor.py`).
- DEPENDENCIES: pinned baseline artifact and previous tranche rollback decisions.
- EXIT_GATE: helper patch + pinned rerun evidence for non-spellspace means.
- FAILURE_ESCALATION: raise `CONFLICT` if helper edits require generator template redesign.

## Scope Boundaries
- In scope:
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
  - pinned rerun artifacts
- Out of scope:
  - patch-map algorithms
  - creation-context dispatch logic
  - benchmark harness changes

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: no-args invocation path is a fresh hotspot slice after reverted tranches.

## Steps / Checklist
- [x] Add no-args invoke fast path in no-overrides helper.
- [x] Add no-args invoke fast path in overrides helper.
- [x] Verify compile correctness.
- [x] Run pinned reruns and compute non-spellspace mean deltas.
- [x] Document results in notes and update story/epic routing notes.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Helper-level invocation fast-path patch.
- Pinned rerun artifacts and delta summary.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_invoke_fastpath_tranche4.json`

## Validation
- Not run.
- Recommended commands:
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 3 --warmup-count 1 --pin-p-cores --output-path benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_invoke_fastpath_tranche4.json`

## Risks / Rollback Notes
- Risk: invoke-path branching could alter error wrapping semantics.
  - Mitigation: keep existing exception wrapping and positional-args validation unchanged.

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
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_invoke_fastpath_tranche4.json
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: story closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-18T10:41:20Z
  TYPE: PLAN
  CLAIM: Introduce direct no-args invocation path in phase12 helpers when `__args__` is absent, preserving current behavior for positional override payloads.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1088-1114
  - src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2926-2952
  IMPACT: Targets a high-frequency call path common to mixed and targeted routes.
  NEXT: Apply helper patches and run pinned reruns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:42:12Z
  TYPE: MEASURE
  CLAIM: Tranche 4 no-args invoke fast path regressed non-spellspace means in both override routes and mixed route versus pinned baseline.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_invoke_fastpath_tranche4.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_invoke_fastpath_tranche4_r2.json:652-671
  IMPACT: This tranche fails acceptance and cannot be retained.
  NEXT: Revert tranche 4 patch and reassess hotspot strategy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:42:12Z
  TYPE: DECISION
  CLAIM: Tranche 4 no-args invoke patch has been reverted.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1088-1114
  - src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2926-2952
  IMPACT: Code is back on baseline for this path; new optimization direction is required.
  NEXT: Pivot to a measurement strategy with larger samples before next code change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Tranche 4 patch was measured and reverted due regression. Next step is
selecting a new hotspot strategy from baseline.
