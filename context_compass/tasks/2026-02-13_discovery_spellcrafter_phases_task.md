# Task: Discovery SpellCrafter Phases

## Metadata
- Task ID: TASK-2026-02-13-discovery-spellcrafter-phases
- Story: STORY-2026-02-13-optimize-spellcrafter-phases
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-14

## Objective
Build a source-anchored hotspot map for SpellCrafter phase execution and
phase-artifact lifecycle so follow-up optimization tasks are evidence-backed.

## Scope Boundaries
- In scope:
- SpellCrafter phase path analysis for structural, foundational, and plan phases.
- Artifact creation/cleanup and invalidation boundaries that affect phase cost.
- Hotspot ranking and candidate-task extraction.
- Out of scope:
- Runtime semantic changes in this task.
- Meld front-door optimization and mutation runtime wiring.

## Steps / Checklist
- [x] Map phase entrypoints and call ordering contracts in SpellCrafter paths.
- [x] Identify highest-cost operations and repeated allocations per phase group.
- [x] Capture phase-artifact lifecycle/invalidation boundaries that impact cost.
- [x] Produce ranked optimization candidates and append follow-up tasks.

## Deliverables
- Discovery baseline with per-phase hotspot map and evidence anchors.
- Prioritized follow-up optimization candidates for SpellCrafter phases.
- Ranked follow-up tasks:
  - `context_compass/tasks/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md`
  - `context_compass/tasks/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md`
  - `context_compass/tasks/completed/2026-02-14_optimize_phase8_10_codegen_row_builder_contract_fastpath_task.md`

## Files / Paths Impacted
- `context_compass/stories/2026-02-13_optimize_spellcrafter_phases_story.md`
- `context_compass/tasks/2026-02-13_discovery_spellcrafter_phases_task.md`
- `context_compass/tasks/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md`
- `context_compass/tasks/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md`
- `context_compass/tasks/completed/2026-02-14_optimize_phase8_10_codegen_row_builder_contract_fastpath_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter -k phase`

## Risks / Rollback Notes
- Risk: phase-level claims drift from real call order.
- Rollback: keep findings as UNKNOWN until source ordering is verified.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [ ] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Discovery ranking is complete; follow-up implementation should execute in priority order: (1) phase8-11 capture-frequency reduction, (2) phase11 signature hash pipeline, (3) phase8-10 row-builder contract fastpath.
  EVIDENCE: context_compass/tasks/2026-02-13_discovery_spellcrafter_phases_task.md:63-104, context_compass/tasks/2026-02-14_optimize_phase8_11_codegen_ir_capture_frequency_task.md:1-76, context_compass/tasks/2026-02-14_optimize_phase11_signature_hash_pipeline_task.md:1-76, context_compass/tasks/completed/2026-02-14_optimize_phase8_10_codegen_row_builder_contract_fastpath_task.md:1-77
  IMPACT: Story execution is unblocked with clear ranked implementation scope.
  NEXT: Update story task checklist and attention-board routing to start rank-1 implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Phase8-11 IR row builders retain heavy defensive attribute probing (`try/except AttributeError`) in hot paths even though upstream phase builders provide typed `InjectionPlan`/`InjectionSpec` and `OverridePatchMap` artifacts when phases run in order.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:23-23, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:43-43, src/melder/spellbook/spell_crafter/spell_crafter.py:1419-1478, src/melder/spellbook/spell_crafter/spell_crafter.py:1523-1562, src/melder/spellbook/spell_crafter/spell_crafter.py:1870-1890, src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:321-427, src/melder/spellbook/spell_crafter/blueprints/injection_plan.py:516-655, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:75-151, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:660-696
  IMPACT: A contract-strict refactor (direct attribute access + fail-fast on invalid state) is a viable optimization and correctness-hardening candidate for spell-scoped phase8-11 export.
  NEXT: Convert findings into ranked follow-up implementation tasks under the story (phase8-11 capture strategy, signature pipeline, and contract-strict row builders).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: `_capture_phase8_11_codegen_ir` is called on every phase8/9/10/11 run, resulting in repeated full IR/signature rebuild work across the same spell pass (`68` capture calls in warm 8-11 sample for `17` spells x `4` phase completions).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:17-22, src/melder/spellbook/spell_crafter/spell_crafter.py:3473-3477, src/melder/spellbook/spell_crafter/spell_crafter.py:3539-3542, src/melder/spellbook/spell_crafter/spell_crafter.py:3607-3611, src/melder/spellbook/spell_crafter/spell_crafter.py:3740-3746, src/melder/spellbook/spell_crafter/spell_crafter.py:1809-1959
  IMPACT: A staged/dirty-slice IR export strategy is a high-value follow-up candidate because current design recomputes phase8-11 export multiple times within one phase chain.
  NEXT: Verify contract expectations for per-phase IR freshness and enumerate safe refactor options (slice-level capture, deferred signature, or incremental signatures).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Phase8-11 warm cost remains dominated by IR capture payload/signature construction, with cProfile showing concentrated time in `_build_phase11_variant_ir_payload`, `_build_phase11_step_ir_row`, `_hash_codegen_signature`, and `_serialize_codegen_signature_part` (pickle path).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_phase5_opt_rerun_clean_output_run2.txt:18-33, src/melder/spellbook/spell_crafter/spell_crafter.py:747-792, src/melder/spellbook/spell_crafter/spell_crafter.py:1676-1807, src/melder/spellbook/spell_crafter/spell_crafter.py:1809-1923
  IMPACT: Highest remaining SpellCrafter optimization ROI is in phase8-11 IR/signature work rather than phase entrypoint orchestration.
  NEXT: Identify concrete repeated transforms/sorts/exception-guard paths inside phase8-11 row builders and propose ranked follow-up tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Existing component baselines show SpellCrafter warm-path cost concentration in phase groups 8-11 and conduit-wide 5-7; phase entrypoints are explicitly mapped in `spell_crafter.py` and align with measured group timings.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:6-6, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:8-8, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:11-11, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:13-13, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:22-33, src/melder/spellbook/spell_crafter/spell_crafter.py:2444-2444, src/melder/spellbook/spell_crafter/spell_crafter.py:2481-2481, src/melder/spellbook/spell_crafter/spell_crafter.py:2815-2815, src/melder/spellbook/spell_crafter/spell_crafter.py:2904-2904, src/melder/spellbook/spell_crafter/spell_crafter.py:3008-3008, src/melder/spellbook/spell_crafter/spell_crafter.py:3433-3433, src/melder/spellbook/spell_crafter/spell_crafter.py:3483-3483, src/melder/spellbook/spell_crafter/spell_crafter.py:3549-3549, src/melder/spellbook/spell_crafter/spell_crafter.py:3689-3689, src/melder/spellbook/spell_crafter/spell_crafter.py:3793-3793, src/melder/spellbook/spell_crafter/spell_crafter.py:4123-4123
  IMPACT: Discovery should prioritize phase8-11 IR and phase5 root-blueprint internals over phase1-4 for immediate optimization ROI.
  NEXT: Trace the internal hot functions surfaced by cProfile (`_capture_phase8_11_codegen_ir`, `_build_phase11_variant_ir_payload`) and map repeated allocation/sorting work with source anchors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: This story requires exactly one discovery task and already references this task ID.
  EVIDENCE: context_compass/epics/2026-02-13_optimize_melder_epic.md:51, context_compass/stories/2026-02-13_optimize_spellcrafter_phases_story.md:44
  IMPACT: Creating this task closes the missing ticket link and unblocks discovery execution.
  NEXT: Start call-path mapping in `src/melder/spellbook/spell_crafter/spell_crafter.py`.

## Context / Handoff Summary
Discovery is complete and review-ready with evidence-backed hotspot mapping for
SpellCrafter phases. Ranked follow-up tasks were created for capture-frequency
reduction, signature-hash pipeline optimization, and contract-fastpath row
builder cleanup. Next step is user acceptance for discovery and execution start
on the rank-1 follow-up task.

