# Task: Optimize Targeted Override PatchMap Micro-Path

## Metadata
- Task ID: TASK-2026-02-18-targeted-override-patchmap-micro-optimization
- Story: STORY-2026-02-18-codegen-baseline-and-hotspot-map
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-18T10:29:40Z
- Updated: 2026-02-18T10:31:20Z

## Objective
Reduce targeted override overhead in Phase 10 patch-map application path by
improving single-key raw override cache behavior.

## Ticket Contract
- ENTRY_GATE: story is active in implementation mode and tranche 2 is routed on board.
- EXECUTION_BOUNDARY: `patch_maps.py` targeted-override apply path only plus benchmark measurement.
- DEPENDENCIES: hotspot evidence in pinned deep profile and tranche-1 outputs.
- EXIT_GATE: patch + pinned rerun evidence for targeted/mixed route means.
- FAILURE_ESCALATION: raise `CONFLICT` if optimization requires executor codegen scope expansion.

## Scope Boundaries
- In scope:
  - `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
  - pinned benchmark rerun outputs for mean comparisons
- Out of scope:
  - creation-context front-door changes
  - phase12 generated executor rewrites

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: tranche 2 requires targeted override path optimization after tranche 1 results.

## Steps / Checklist
- [x] Implement single-key raw-key cache fast path in patch-map apply path.
- [x] Run pinned benchmark rerun(s) and compute non-spellspace deltas.
- [x] Record results in task notes and update story routing notes.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Patch-map targeted override optimization patch.
- Pinned rerun artifacts and delta summary.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- `benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_patchmap_tranche2.json`

## Validation
- Not run.
- Recommended commands:
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 3 --warmup-count 1 --pin-p-cores --output-path benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_patchmap_tranche2.json`

## Risks / Rollback Notes
- Risk: cache semantics could alter override conflict behavior.
  - Mitigation: preserve same target resolution path and only change cache hit reconstruction.

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
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_patchmap_tranche2.json
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: story closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-02-18T10:29:40Z
  TYPE: FACT
  CLAIM: Patch-map single-key apply path now reuses raw-key cache regardless of value identity and reconstructs value-specific override maps from cached socket keys.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:287-327
  IMPACT: Targeted override calls with fresh objects per call can avoid repeated raw-key target resolution in hot path.
  NEXT: Run pinned reruns and compare targeted/mixed mean deltas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:31:20Z
  TYPE: MEASURE
  CLAIM: Tranche 2 improved targeted override mean vs baseline (`warm_override_targeted_ns` 6833.33 -> 6733.33, -1.46%) and vs tranche 1 average (-2.18%), but mixed worsened (`warm_mixed_ns` 22033.33 -> 22700, +3.03%).
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_patchmap_tranche2.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_patchmap_tranche2_r2.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_cc_override_dispatch.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_cc_override_dispatch_r2.json:652-671
  IMPACT: Patch-map change helps targeted override path, but program-level acceptance is blocked by mixed-route regression.
  NEXT: Continue with phase12 overrides executor optimization tranche and remeasure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:31:20Z
  TYPE: DECISION
  CLAIM: Keep tranche 2 patch-map change for now and proceed to next hotspot tranche rather than reverting immediately.
  EVIDENCE:
  - src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:287-327
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_patchmap_tranche2.json:362-390
  IMPACT: Execution continues forward with cumulative optimization tranches while preserving measured targeted-route gains.
  NEXT: Create task for generated overrides executor micro-optimizations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Task is active with patch-map targeted override micro-optimization applied.
Pinned reruns are complete with mixed results. Next step is the overrides
executor tranche to recover mixed-route performance.
