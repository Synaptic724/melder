# Task: Optimize Phase 9 Injection Plan Compilation

## Metadata
- Task ID: TASK-2026-02-18-phase9-injection-plan-optimization
- Story: STORY-2026-02-18-phase9-injection-plan-speedup
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-02-18T18:54:05Z
- Updated: 2026-02-18T18:54:05Z

## Objective
Implement approved Phase 9 optimizations after discovery identifies hotspots.

## Ticket Contract
- ENTRY_GATE: discovery task publishes Phase 9 hotspot evidence.
- EXECUTION_BOUNDARY: Phase 9 compile/signature surfaces only.
- DEPENDENCIES: TASK-2026-02-18-phase8-12-holistic-codegen-discovery.
- EXIT_GATE: non-regression under weighted benchmark gates.
- FAILURE_ESCALATION: raise CONFLICT on cross-phase scope creep.

## Scope Boundaries
- In scope:
  - Phase 9 injection plan compilation
  - phase9 signature/cache handling
- Out of scope:
  - unrelated phase implementations

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: execution task prepared pending discovery results.

## Steps / Checklist
- [ ] Confirm Phase 9 hotspot targets from discovery.
- [ ] Implement approved optimization tranche.
- [ ] Update tests/docs as needed.
- [ ] Run weighted benchmark validation against baseline.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Phase 9 optimization patch.
- Weighted benchmark validation summary.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- phase-related tests and benchmark artifacts as needed

## Validation
- Not run.
- Recommended commands:
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --pin-p-cores --profile-iteration-count 5 --baseline-path <baseline_json> --weighted-cprofile-weight 0.75 --weighted-time-weight 0.25 --output-path <phase9_after_json>`

## Risks / Rollback Notes
- Risk: shifted plan generation semantics.
- Mitigation: phase-local tests and strict behavior checks.

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
  CLAIM: Task remains gated on discovery outputs for scoped hotspot targeting.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md:1-147
  IMPACT: Phase 9 execution stays aligned to measured bottlenecks.
  NEXT: wait for discovery completion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-02-18T19:23:32Z
  TYPE: PLAN
  CLAIM: Ranked execution order places this task in tranche #2 with concrete target symbols: `run_phase_injection_plan`, `_build_phase9_injection_plan_input_signature`, and `_mark_phase8_11_codegen_ir_dirty` in `spell_crafter.py`.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase8_12_holistic_codegen_discovery_task.md:129-163
  - src/melder/spellbook/spell_crafter/spell_crafter.py:4120-4190
  IMPACT: Phase9 optimization remains phase-local while directly targeting signature/reuse churn that fans into phase11 compile cost.
  NEXT: execute in tranche #2 after tranche #1, validating that injection-plan cache hits increase without altering dependency wiring semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Task is ready and blocked on discovery findings.
