# Task: Optimize Phase 10 Patch Map Compilation

## Metadata
- Task ID: TASK-2026-02-18-phase10-patch-map-optimization
- Story: STORY-2026-02-18-phase10-patch-map-speedup
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-18T18:54:05Z
- Updated: 2026-02-18T18:54:05Z

## Objective
Implement approved Phase 10 patch-map optimizations once discovery confirms
hotspots and dependency boundaries.

## Ticket Contract
- ENTRY_GATE: discovery findings include Phase 10 hotspot evidence.
- EXECUTION_BOUNDARY: Phase 10 patch-map surfaces only.
- DEPENDENCIES: TASK-2026-02-18-phase8-12-holistic-codegen-discovery.
- EXIT_GATE: weighted benchmark validation passes for override lanes.
- FAILURE_ESCALATION: raise DECISION_REQUEST on behavior risk.

## Scope Boundaries
- In scope:
  - patch-map build/normalization flow
  - related signature and invalidation logic
- Out of scope:
  - non-phase10 code paths

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: execution task prepared pending discovery results.

## Steps / Checklist
- [ ] Confirm discovery hotspot targets.
- [ ] Implement scoped patch-map optimization.
- [ ] Update tests/docs as needed.
- [ ] Validate with weighted benchmark report (fast and override routes).
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Phase 10 optimization patch.
- Weighted benchmark non-regression evidence.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py` (if required)
- benchmark/test paths as needed

## Validation
- Not run.
- Recommended commands:
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --profile-iteration-count 5 --baseline-path <baseline_json> --weighted-cprofile-weight 0.75 --weighted-time-weight 0.25 --output-path <phase10_after_json>`

## Risks / Rollback Notes
- Risk: override route regressions.
- Mitigation: route-specific weighted checks before acceptance.

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
  CLAIM: Task will start after discovery confirms Phase 10 ranking in the full
    phase8-12 pipeline.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md:1-147
  IMPACT: Avoids phase-local optimization without system-level context.
  NEXT: wait for discovery completion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-02-18T19:23:32Z
  TYPE: PLAN
  CLAIM: Ranked execution order places this task in tranche #2 with concrete target symbols: `run_phase_patch_maps`, `_build_phase10_patch_maps_input_signature`, and `_mark_phase8_11_codegen_ir_dirty` in `spell_crafter.py`.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md:129-163
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4197-4270
  IMPACT: Phase10 work is now scoped to patch-map compile/reuse and dirty-flag fanout that drives override specialization inputs.
  NEXT: execute in tranche #2 after tranche #1, then verify route-level override regressions remain within weighted thresholds.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Task is ready and blocked on discovery findings.
