# Task: Optimize Phase 11 Execution Plan Assembly

## Metadata
- Task ID: TASK-2026-02-18-phase11-execution-plan-optimization
- Story: STORY-2026-02-18-phase11-execution-plan-speedup
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-18T18:54:05Z
- Updated: 2026-02-18T19:32:27Z

## Objective
Implement approved Phase 11 optimization tranche for execution-plan assembly and
signature-based reuse, without behavior drift.

## Ticket Contract
- ENTRY_GATE: discovery outputs include Phase 11 hotspot evidence.
- EXECUTION_BOUNDARY: Phase 11 assembly/reuse surfaces only.
- DEPENDENCIES: TASK-2026-02-18-phase8-12-holistic-codegen-discovery.
- EXIT_GATE: weighted benchmark validation passes for target routes.
- FAILURE_ESCALATION: raise BLOCKER on parity uncertainty.

## Scope Boundaries
- In scope:
  - Phase 11 plan assembly and cache signatures
  - Phase 11 to Phase 12 interface boundaries
- Out of scope:
  - independent creation_context rewrites

## State Transition Event
- from_state: blocked
- to_state: in_progress
- transition_reason: guarded fast-key path fix cleared weighted benchmark gate on rerun.

## Steps / Checklist
- [x] Confirm discovery-ranked hotspots and target signatures.
- [x] Implement scoped Phase 11 optimization.
- [x] Update tests/docs as needed.
- [x] Validate with weighted benchmark non-regression checks.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Phase 11 optimization patch.
- Weighted benchmark validation summary.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- phase-specific tests and benchmark artifacts as needed

## Validation
- Ran (pinned before/after):
  - before (clean `HEAD` snapshot): `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --profile-iteration-count 5 --output-path context_compass/artifacts/2026-02-18_phase11_before.json`
  - after (current tree): `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --profile-iteration-count 5 --baseline-path context_compass/artifacts/2026-02-18_phase11_before.json --weighted-cprofile-weight 0.75 --weighted-time-weight 0.25 --output-path context_compass/artifacts/2026-02-18_phase11_after.json`
- Result:
  - Initial run: weighted check failed (`warm_override_targeted_ns weighted ratio 1.0093 > 1.0000`).
  - Rerun after fast-key guard fix: gate, route baseline, and weighted checks all passed (`overall_weighted_ratio=0.9754`).
  - Targeted unit tests passed:
    - `python -m pytest tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py -k "run_phase_execution_plan_reuses_no_overrides_plan_when_input_signature_unchanged or run_phase_execution_plan_reuses_cached_variant_set_when_input_signature_unchanged or run_phase_execution_plan_rebuilds_no_overrides_plan_when_input_signature_changes" -q`

## Risks / Rollback Notes
- Risk: plan reuse bug introduces stale executors.
- Mitigation: preserve signature contracts and add targeted tests.

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
  CLAIM: Task is ready and scheduled after discovery hotspot ranking.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md:1-147
  IMPACT: Keeps implementation order consistent with measured bottlenecks.
  NEXT: wait for discovery completion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-02-18T19:23:32Z
  TYPE: PLAN
  CLAIM: Ranked execution order sets this task as tranche #1 with concrete target symbols: `run_phase_execution_plan`, `_build_execution_plan_variant`, `_try_build_execution_plan_variant_from_base`, and `_compile_phase12_no_overrides_executor_from_plan` in `spell_crafter.py`.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md:129-163
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4348-4463
  IMPACT: First implementation tranche is now scoped to phase11 assembly/reuse and no-overrides compile handoff without cross-phase drift.
  NEXT: when routed active, begin with signature-unchanged fast-path reuse checks and executor compile reuse boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T19:24:55Z
  TYPE: DECISION
  CLAIM: This task is now the active implementation lane for the epic and will execute tranche #1 before phase8/9/10 and phase12 tranches.
  EVIDENCE:
  - attention_board.md:24-34
  - tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md:168-177
  IMPACT: Phase11 implementation can begin immediately with stable boundaries and no additional discovery prerequisites.
  NEXT: capture first implementation finding in this task notes before any cross-file expansion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T19:28:41Z
  TYPE: MEASURE
  CLAIM: Pinned before/after benchmark for the phase11 tranche fails the weighted gate only on `warm_override_targeted_ns`; all non-weighted route/gate checks pass.
  EVIDENCE:
  - context_compass/artifacts/2026-02-18_phase11_before.json:128-155
  - context_compass/artifacts/2026-02-18_phase11_after.json:153-214
  - context_compass/artifacts/2026-02-18_phase11_after.json:808-832
  IMPACT: The tranche cannot be accepted yet; override-targeted route needs follow-up optimization or a user-approved threshold exception.
  NEXT: isolate `warm_override_targeted_ns` delta path, then decide whether to tune phase11 path further or route to tranche #3 (`creation_context` override specialization) for remediation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-18T19:32:27Z
  TYPE: MEASURE
  CLAIM: After adding a guard so the phase11 fast-key reuse path applies only when phase8/phase9 input signatures are available, weighted benchmark and targeted phase11 unit tests pass.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4400-4430
  - context_compass/artifacts/2026-02-18_phase11_after.json:153-214
  - context_compass/artifacts/2026-02-18_phase11_after.json:808-842
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:6387-6692
  IMPACT: Tranche #1 regression gate is cleared and the epic can proceed to the next implementation tranche.
  NEXT: route active work to tranche #2 task and continue optimization sequence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Phase11 tranche change is implemented with passing targeted unit tests and
pinned weighted benchmark rerun. Next step is routing to tranche #2
(phase8/phase9/phase10 dirty/export surfaces).
