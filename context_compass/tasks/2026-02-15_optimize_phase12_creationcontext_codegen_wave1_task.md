# Task: Optimize Phase12 and CreationContext Codegen Wave 1

## Metadata
- Task ID: TASK-2026-02-15-optimize-phase12-creationcontext-codegen-wave1
- Story: STORY-2026-02-15-phase12-codegen-runtime-tightening
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-16

## Objective
Implement the first hotspot-led codegen runtime optimization patch for
Phase12/CreationContext and validate with targeted profiler suites.

## Scope Boundaries
- In scope:
- Hotpath edits in `phase12_no_overrides_executor.py`,
  `phase12_overrides_executor.py`, and `creation_context.py` only if required.
- Targeted reruns of fast-graph and override cprofile suites.
- Out of scope:
- Public API changes.
- Broad refactors outside measured hotspot callpaths.

## Steps / Checklist
- [x] Confirm top hotspot helper targets from `.summary.txt` + call-chain artifacts.
- [x] Apply minimal optimization patch on selected helper path(s).
- [x] Re-run targeted cprofile pytest suites and compare key lanes.
- [x] Record measured deltas and behavior observations.
- [x] Run Ticket Microcycle during execution (`Investigate -> Document -> Strategy/Plan -> Document -> Implement -> Document -> Validate -> Document`).
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Wave-1 runtime optimization code patch.
- Updated profiler artifacts for fast and overrides lanes.
- Notes entry documenting before/after observations.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py` (only if needed)
- `context_compass/tasks/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md`

## Validation
- Ran:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s`
- Result:
  - `8 passed, 1 warning in 0.78s` (fast graphs)
  - `8 passed, 1 warning in 0.38s` (override graphs)

## Risks / Rollback Notes
- Risk: speed change in one lane regresses another lane.
  Rollback: keep patch isolated, then compare both suites before finalizing.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 8 for required re-entry notes)
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Retain the `CreationContext` prebound Phase10 apply-callable slice as the current wave-1 baseline.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_prebound_phase10_apply_delta_vs_prebaseline.txt:3-6, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_prebound_phase10_apply_delta_vs_prebaseline.txt:9-12, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_prebound_phase10_apply_postbaseline.txt:3-13
  IMPACT: Active optimization baseline remains override-focused and measurable.
  NEXT: Continue from this baseline for the next structural hotspot.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: `CreationContext` now binds `_override_apply_with_socket_shape_prechecked_phase10` at initialization and reuses it in `_execute_with_overrides(...)`.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:152-152, src/melder/aether/conduit/meld/creation_context/creation_context.py:228-234, src/melder/aether/conduit/meld/creation_context/creation_context.py:619-629, tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py:99-130
  IMPACT: Removes repeated patch-map method lookup on each override-bearing call.
  NEXT: Keep this path in retained state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Reject and revert the prebound active route-field slice in `CreationContext`.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_prebound_route_fields_delta_vs_prebaseline.txt:3-6, src/melder/aether/conduit/meld/creation_context/creation_context.py:253-253
  IMPACT: Prevents retaining a regression on priority override lanes.
  NEXT: Avoid route-field aliasing experiments for this tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Reject and revert the positional executor-invocation slice (`CreationContext` positional tail args + non-keyword-only `_phase12_executor` signatures).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_positional_executor_invocation_delta_vs_prebaseline.txt:3-12, src/melder/aether/conduit/meld/creation_context/creation_context.py:585-590, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:558-558
  IMPACT: Keeps executor call contracts stable and avoids non-winning complexity.
  NEXT: Target a different structural hotspot.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Do not retain the no-overrides registration-inline emitter slice in this tranche.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:587-591, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:625-629, benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_register_inline_slice_reverted.txt:2-20
  IMPACT: No no-overrides codegen contract change is carried forward.
  NEXT: Keep effort on override-path structural wins.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Post-revert validation is green for targeted runtime paths (`83 passed` creation-context focused checks, `27 passed` no-overrides executor checks, `16 passed` fast/override cprofile suites).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_creation_context_positional_executor_invocation_slice_reverted.txt:1-9, benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_register_inline_slice_reverted.txt:2-20
  IMPACT: Confirms retained baseline correctness after cleanup of non-winning slices.
  NEXT: Re-rank hotspots and implement next structural override optimization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Keep this ticket in compact active-memory mode: recent retained/rejected decisions only in `## Notes`; detailed historical benchmark chronology is preserved in profile artifacts and git history.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/:1-1, context_compass/CONTEXT_COMPACTION.md:1-68
  IMPACT: Reduces note bloat while preserving re-entry signal.
  NEXT: Append only net-new meaningful findings from future slices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Next slice will add a `CreationContext` one-key override fast path that caches Phase10-resolved socket targets per raw key and builds the override map directly for single-key payloads, bypassing generic multi-key patch-map branching on the hot lane.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:6-8, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.hotspots.json:43-48, src/melder/aether/conduit/meld/creation_context/creation_context.py:565-706, src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:268-354
  IMPACT: Targets remaining per-call override preprocessing cost while preserving existing conflict/validation behavior through Phase10 target resolution.
  NEXT: Implement cache fields + helper in `CreationContext`, run focused unit/component validation, then rerun the cprofile benchmark cadence for keep/revert.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Refresh profiling baselines before selecting the next structural slice because the latest shallow hotspot artifact is not aligned with the current source helper path.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:8-10, src/melder/aether/conduit/meld/creation_context/creation_context.py:152-234, src/melder/aether/conduit/meld/creation_context/creation_context.py:565-741
  IMPACT: Prevents choosing optimization targets from stale hotspot data.
  NEXT: Run fresh fast/override cprofile suites, then re-rank current hotspots and pick one structural change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Fresh baselines show override hotpath concentration at `_execute_with_overrides` plus Phase10 override preprocessing (`patch_maps._apply_with_socket_shape_prechecked`) while fast graphs remain dominated by no-overrides Phase12 registration/executor paths.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:7-10, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_wide.summary.txt:7-10, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:8-10, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_wide.summary.txt:8-10
  IMPACT: Next override slice should target Phase10 override preprocessing with minimal fast-lane spillover risk.
  NEXT: Inspect `OverridePatchMap._apply_with_socket_shape_prechecked` and implement one structural optimization, then rerun override+fast suites for before/after deltas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: ALIGNMENT_CHECK
  CLAIM: Re-onboarding was completed again before continuing optimization work, and execution is resuming from the existing "Phase10 override preprocessing" next-slice plan.
  EVIDENCE: context_compass/AGENTS.MD:3-3, context_compass/AGENTS.MD:64-80, context_compass/AGENTS.MD:456-456, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:7-14, context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md:26-39, context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt:8-9, context_compass/agent_onboarding/agent/general/skills/onboarding_read_paths.txt:82-82, context_compass/tasks/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md:149-154
  IMPACT: Ticket routing and policy gates stay explicit while work resumes on the intended hotspot.
  NEXT: Inspect current `CreationContext`/Phase10 override preprocessing path, implement one structural slice, and run pre/post benchmark cadence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: The one-key override fast-path slice (`_try_apply_single_override_payload_fast`) regressed the primary override lanes versus baseline, despite passing unit/cprofile suites.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_single_key_override_fast_path_delta_vs_prebaseline.txt:1-36, src/melder/aether/conduit/meld/creation_context/creation_context.py:632-632, src/melder/aether/conduit/meld/creation_context/creation_context.py:724-771
  IMPACT: This slice does not satisfy the unanimous-win requirement for retained codegen/runtime changes.
  NEXT: Revert this slice and retarget the next structural hotspot.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Reject and revert the CreationContext one-key override fast-path cache slice.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_single_key_override_fast_path_delta_vs_prebaseline.txt:6-31, src/melder/aether/conduit/meld/creation_context/creation_context.py:163-163, src/melder/aether/conduit/meld/creation_context/creation_context.py:724-771
  IMPACT: Prevents carrying a clear override-path regression into active baseline.
  NEXT: Continue optimization from the retained prebound-Phase10 baseline with a different structural change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: After reverting the one-key fast-path slice, the override hotspot profile returned to the prior shape (`_execute_with_overrides` + `_phase12_executor` + Phase10 prechecked apply), with timings back near retained baseline.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:1-10, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_wide.summary.txt:1-10, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_creation_context_single_key_override_fast_path_delta_vs_prebaseline.txt:6-31
  IMPACT: Confirms the regression was tied to the rejected slice and that baseline is restored.
  NEXT: Target a different structural hotspot with override-lane priority.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Next optimization slice should target generated override executor structure (`phase12_overrides_executor.py`) instead of adding more preprocessing in `CreationContext`, because `_phase12_executor` remains the largest stable override hotspot after baseline restoration.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:7-10, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_wide.summary.txt:7-10, src/melder/aether/conduit/meld/creation_context/creation_context.py:565-706, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:232-742
  IMPACT: Moves wave-1 effort from preprocessing micro-structure to executor-structure changes with higher upside.
  NEXT: Inspect override executor emission for repeated runtime branching/lookup that can be hoisted or shape-specialized.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: The Phase12 override-emitter many-registration slice (inline `add_many_creations` + skip unused registration metadata locals) produced consistent override-lane wins across repeated runs with mixed/mostly-neutral fast-lane movement.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_overrides_many_register_inline_delta_vs_postrevert_baseline.txt:1-37, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1684-1699, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1802-1805, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2073-2095, tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py:484-506
  IMPACT: Adds a measured structural win on the override hot lane without correctness regressions in targeted tests.
  NEXT: Keep this slice in working state and continue iterative tuning for remaining `_phase12_executor` hotspot cost.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Retain the Phase12 overrides many-registration inline slice for now and continue optimization from this baseline.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_overrides_many_register_inline_delta_vs_postrevert_baseline.txt:10-31, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:1-10, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_wide.summary.txt:1-10
  IMPACT: Preserves override-path gains while we keep monitoring fast-lane variance in subsequent slices.
  NEXT: Target another structural reduction inside generated `_phase12_executor` (override-value assembly/invoke branch structure) and re-run cadence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Lock-gating the many-registration inline emitter (`if has_disposal_methods: with lock -> add_many_creations`) tightened this slice and produced a favorable latest run versus baseline on fast shallow/wide/diamond and override shallow/wide/diamond.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_overrides_many_register_inline_delta_vs_postrevert_baseline.txt:45-63, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1799-1802, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2070-2095
  IMPACT: Current retained slice now avoids unnecessary lock acquisition on many-steps without disposal tracking.
  NEXT: Continue from this baseline and target remaining `_phase12_executor` branch/assembly overhead.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Next `_phase12_executor` slice will specialize Existence.many registration on static disposal metadata so steps with statically-false disposal methods emit no registration branch/metadata loads at runtime.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1684-1696, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1798-1802, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2070-2095, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:7-10
  IMPACT: Targets per-step branch/load overhead in the remaining override executor hotspot without changing public APIs.
  NEXT: Implement static-disposal metadata in shape emission, validate phase12 unit tests, then run fast/override cprofile cadence for keep/revert.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Static disposal specialization for Existence.many registration delivered a net-positive override profile (median wins on solo/wide/diamond, near-flat shallow) across three cadences while keeping all targeted tests green.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_overrides_many_static_disposal_registration_delta_vs_lock_gate_baseline.txt:1-37, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1696-1709, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1827-1839, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2122-2144, tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py:499-536
  IMPACT: Removes runtime many-registration work for static no-disposal steps and removes the runtime disposal-branch for static yes-disposal steps.
  NEXT: Keep this slice and move to the next `_phase12_executor` structure reduction target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Retain the static-disposal many-registration specialization slice in active baseline.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1696-1709, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1827-1839, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2122-2144, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_overrides_many_static_disposal_registration_delta_vs_lock_gate_baseline.txt:22-37
  IMPACT: Preserves measured override-lane gains and lowers many-step runtime branching/metadata loads for static shapes.
  NEXT: Re-rank remaining `_phase12_executor` costs (kwargs assembly/invoke path) and implement one structural follow-up slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Next slice will specialize no-override invoke emission so steps with statically-empty kwargs call callable spells directly (`spell()`) instead of allocating `{}` and invoking `spell(**kwargs)`.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1310-1360, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1530-1604, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:7-10
  IMPACT: Targets hot-lane invoke overhead on override executors for steps that carry no dependency/contract/override payload.
  NEXT: Implement emitter specialization + tests, then rerun fast/override cprofile cadence for keep/revert.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Direct-call specialization for static empty-kwargs lanes produced strong median override wins on shallow/wide (and slight diamond win) across two cadences, with a modest solo tradeoff.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_overrides_direct_callable_empty_kwargs_delta_vs_static_disposal_baseline.txt:1-29, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1512-1536, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1611-1634, tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py:550-564
  IMPACT: Reduces no-override callable invoke overhead inside override executors by removing unnecessary `{}` allocation and `**kwargs` unpack on static-empty lanes.
  NEXT: Retain this slice and continue ranking remaining `_phase12_executor` cost centers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Retain the direct-call static empty-kwargs invoke specialization in active baseline.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1320-1336, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1512-1536, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1611-1634, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_overrides_direct_callable_empty_kwargs_delta_vs_static_disposal_baseline.txt:22-29
  IMPACT: Keeps the latest structural reduction in override executor invoke paths while preserving green targeted validations.
  NEXT: Continue wave-1 on the next structural hotspot with override-lane priority.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Next `_phase12_executor` slice will skip emitting `spell_{i} = step_spells[i]` for shape-specialized rows where creations target is statically caller/spellspace and spell locals are not consumed.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1742-1744, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1800-1807, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:7-10
  IMPACT: Removes one repeated tuple-index load/local assignment from hot override step blocks without changing runtime semantics.
  NEXT: Implement emitter guard + source-shape tests, then rerun unit and cprofile cadence for keep/revert.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: The many caller/spellspace spell-local elision slice is correct but regresses retained-baseline medians in shallow/wide/diamond override lanes across three runs.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_overrides_many_caller_spell_local_elision_delta_vs_direct_callable_baseline.txt:1-42
  IMPACT: This slice does not satisfy the retained-wave criterion (stable override-lane gains versus current baseline).
  NEXT: Reject and revert this slice, then move to a different `_phase12_executor` structural target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Reject and revert the many caller/spellspace spell-local elision slice in `phase12_overrides_executor`.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_overrides_many_caller_spell_local_elision_delta_vs_direct_callable_baseline.txt:24-42
  IMPACT: Keeps the retained direct-call/static-disposal baseline unchanged and avoids carrying measured regressions.
  NEXT: Re-rank remaining `_phase12_executor` hotspots and implement a different structural slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Next `_phase12_executor` slice will prebind per-step `plan_step_{i}` defaults in the generated signature and remove per-call `plan_step_{i} = steps[i]` assignments.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:766-775, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1742-1744, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:7-10
  IMPACT: Targets repeated tuple-index lookups on the hottest override executor path while preserving step semantics.
  NEXT: Implement emitter changes + source-shape tests, then run unit and cprofile cadence for keep/revert.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: The prebound `plan_step_{i}` defaults slice shows mixed override movement and regresses wide override timing on both runs versus the retained baseline.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_overrides_prebound_plan_steps_delta_vs_direct_callable_baseline.txt:1-35
  IMPACT: Candidate fails the stable-win retention bar for the active wave.
  NEXT: Reject and revert this slice; keep retained baseline unchanged.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Reject and revert the prebound `plan_step_{i}` defaults slice.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_overrides_prebound_plan_steps_delta_vs_direct_callable_baseline.txt:19-35
  IMPACT: Avoids carrying non-winning runtime changes into the override baseline.
  NEXT: Re-rank remaining `_phase12_executor` structure costs and continue with a different slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Fast-graph hotspot summaries still concentrate on no-overrides `_phase12_executor` work, with repeated helper time in `_get_existing_creation` and `_construct_spell_instance`; next slice will target no-overrides emitted step structure (creations-target routing) instead of override executors.
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:7-10, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_wide.summary.txt:7-10, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:483-607
  IMPACT: Aligns this tranche to the requested non-override target while keeping the same benchmark cadence and evidence style.
  NEXT: Specialize no-overrides emitted creations-target routing by static target kind, run unit + cprofile suites, and keep/revert based on measured deltas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: The no-overrides static target-kind routing slice (emit-time specialization for CALLER/SPELLSPACE/OWNER) regressed both fast and override medians versus retained baseline, despite passing targeted unit and cprofile suites.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:550-576, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_static_target_routing_delta_vs_direct_callable_baseline.txt:15-41
  IMPACT: Candidate does not meet the wave retention bar.
  NEXT: Reject and revert this no-overrides slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Reject and revert the no-overrides static target-kind routing specialization.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_static_target_routing_delta_vs_direct_callable_baseline.txt:23-31, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_static_target_routing_delta_vs_direct_callable_baseline.txt:38-41
  IMPACT: Preserves retained baseline behavior and avoids carrying measured regressions.
  NEXT: Revert code changes and continue from retained baseline with a different non-override structural target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Post-revert validation is green and timing profiles return to retained-baseline shape (no-overrides hotspot remains `_phase12_executor` with `_construct_spell_instance`/`_build_kwargs_no_overrides` in call-chain highlights; override lanes back near retained baseline magnitudes).
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:493-572, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:1-29, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_wide.summary.txt:1-29, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_shallow.summary.txt:1-10, benchmarks/testing_other_di/profiles/overrides_graphs_melder/melder_overrides_timings_wide.summary.txt:1-10
  IMPACT: Confirms baseline restoration after rejecting the candidate.
  NEXT: Target a different no-overrides structural cost center.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Next no-overrides slice will optimize `_construct_spell_instance` invocation when kwargs are statically/operationally empty (direct `spell.spell()` path) to reduce helper overhead without changing executor shape routing.
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:24-29, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_wide.summary.txt:24-29, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:919-981
  IMPACT: Keeps focus on no-overrides hotspot internals while minimizing semantic risk.
  NEXT: Implement direct empty-kwargs invoke path, run unit + cprofile cadence, and keep/revert by measured deltas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: ALIGNMENT_CHECK
  CLAIM: Results will be explicitly announced in-ticket and in user-facing updates for each optimization slice.
  EVIDENCE: context_compass/AGENTS.MD:54-54, context_compass/AGENTS.MD:450-450
  IMPACT: Keeps execution status and keep/revert outcomes visible without requiring artifact deep-dives.
  NEXT: Announce current no-overrides slice results immediately after validation completes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: The no-overrides empty-kwargs direct-call candidate remains rejected (strong fast-lane regressions versus retained baseline), and post-revert validation is green with hotspot shape restored to `_construct_spell_instance` -> `_build_kwargs_no_overrides`.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_empty_kwargs_direct_call_delta_vs_direct_callable_baseline.txt:3-3, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_empty_kwargs_direct_call_delta_vs_direct_callable_baseline.txt:23-31, benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_empty_kwargs_direct_call_slice_reverted.txt:10-13, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:24-28, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_wide.summary.txt:24-28
  IMPACT: Confirms baseline restoration after unwind and preserves the keep/revert gate for no-overrides work.
  NEXT: Continue with a different no-overrides structural target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: ALIGNMENT_CHECK
  CLAIM: Results are now explicitly announced in-ticket for this no-overrides slice (reject + revert + validated baseline).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_empty_kwargs_direct_call_slice_reverted.txt:19-20, context_compass/AGENTS.MD:54-54
  IMPACT: Satisfies explicit visibility requirement without requiring users to inspect raw benchmark outputs first.
  NEXT: Keep announcing each slice outcome immediately after validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Next no-overrides slice will remove eager `spell.spell_index.current` fetch in `_build_kwargs_no_overrides` and only resolve spell id on error paths (missing dependency), reducing hot-path attribute access with no runtime-contract change.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1021-1023, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:24-28, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_wide.summary.txt:24-28
  IMPACT: Targets a repeated no-overrides helper cost center while keeping semantics and error surface intact.
  NEXT: Implement the lazy spell-id retrieval change, run no-overrides unit tests, then rerun fast+override cprofile cadence for keep/revert.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: The no-overrides lazy error-path spell-id slice is semantically correct but non-winning versus retained baseline (mixed overrides and consistent fast-lane regressions).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_lazy_error_spell_id_delta_vs_direct_callable_baseline.txt:3-3, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_lazy_error_spell_id_delta_vs_direct_callable_baseline.txt:23-31, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_lazy_error_spell_id_delta_vs_direct_callable_baseline.txt:39-41
  IMPACT: Candidate does not satisfy retained-wave criteria for no-overrides optimization.
  NEXT: Reject and revert this slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Reject and revert the no-overrides lazy error-path spell-id slice.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_lazy_error_spell_id_delta_vs_direct_callable_baseline.txt:28-31, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_lazy_error_spell_id_delta_vs_direct_callable_baseline.txt:40-41
  IMPACT: Keeps retained baseline unchanged and prevents carrying measured regressions.
  NEXT: Run post-revert validation and continue with a different non-override structural target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Post-revert validation is green and hotspot shape remains baseline (`_construct_spell_instance` -> `_build_kwargs_no_overrides` on fast lanes; `_execute_with_overrides` -> override executor on override lanes).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_lazy_error_spell_id_slice_reverted.txt:10-17, benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_lazy_error_spell_id_slice_reverted.txt:19-20
  IMPACT: Confirms no-overrides baseline restoration after candidate rejection.
  NEXT: Continue no-overrides optimization from restored baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: ALIGNMENT_CHECK
  CLAIM: Results for the lazy spell-id no-overrides slice were explicitly announced in-ticket at rejection/revert time.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_lazy_error_spell_id_slice_reverted.txt:19-20, context_compass/AGENTS.MD:54-54
  IMPACT: Keeps execution outcomes visible per request and policy.
  NEXT: Continue the same announce-on-each-slice pattern.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Next no-overrides slice will bypass trivial `ExecutionPlanStep` property wrappers in `_build_kwargs_no_overrides` by reading precomputed step fields directly (dependency order + contract flags/payload), removing repeated property-call overhead on the hot path.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/execution_plan.py:255-259, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:995-996, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1000-1103, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:24-28
  IMPACT: Targets the remaining no-overrides helper hotspot with minimal semantic risk because fields are precomputed at phase-build time.
  NEXT: Implement direct-field reads in `_build_kwargs_no_overrides`, run no-overrides unit tests, then rerun fast+override benchmark cadence for keep/revert.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Next no-overrides slice will replace hot-path `spell.spell_index.current` reads in `_build_kwargs_no_overrides` with direct `spell.spell_id` reads to remove per-call SpellIndex property overhead without changing dependency resolution behavior.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:982-1103, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.call_chain.json:938-947, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:24-29
  IMPACT: Targets a measured helper hotspot where `spell_index.current` currently appears as a repeated callee.
  NEXT: Implement the substitution, run no-overrides unit tests, then rerun fast/override cprofile cadence for keep/revert.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: The no-overrides spell-id attribute slice (`spell.spell_id` in `_build_kwargs_no_overrides`) removes the `spell_index.current` call-chain edge but regresses retained-baseline medians across all fast lanes and most override lanes.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_spell_id_attr_lookup_delta_vs_direct_callable_baseline.txt:1-34, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:24-29
  IMPACT: Candidate fails the retained-wave performance bar.
  NEXT: Reject and revert this slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Reject and revert the no-overrides spell-id attribute slice.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_spell_id_attr_lookup_delta_vs_direct_callable_baseline.txt:23-31, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_spell_id_attr_lookup_delta_vs_direct_callable_baseline.txt:33-34
  IMPACT: Keeps retained baseline intact and prevents carrying a measured regression.
  NEXT: Revert code change, run post-revert validation, and announce the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Post-revert validation is green and no-overrides hotspot call-chain is restored with `_build_kwargs_no_overrides` again calling `spell_index.current`.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_spell_id_attr_lookup_slice_reverted.txt:1-10, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:24-29
  IMPACT: Confirms baseline restoration after rejecting the candidate.
  NEXT: Continue from retained baseline with a different no-overrides structural target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: ALIGNMENT_CHECK
  CLAIM: Slice outcome was explicitly announced in artifacts (rejected + reverted + baseline restored).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_spell_id_attr_lookup_slice_reverted.txt:8-10, context_compass/AGENTS.MD:54-54
  IMPACT: Maintains explicit result visibility as requested.
  NEXT: Keep announce-on-slice behavior for subsequent non-override targets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Next no-overrides slice will reorder `_get_existing_creation` existence branching to fast-path `Existence.unique_per_spell_space` first (current benchmark hotspot) before shared-scope tuple checks.
  EVIDENCE: benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.hotspots.json:150-157, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.call_chain.json:1033-1040, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1114-1164
  IMPACT: Targets the largest remaining no-overrides helper hotspot with a minimal structural change.
  NEXT: Implement branch reordering, run unit + fast/override cprofile cadence, and keep/revert by measured deltas.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: The `_get_existing_creation` spellspace-branch-first candidate is functionally correct but regresses retained-baseline medians, with severe fast-lane regressions (especially shallow/wide/diamond).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_spellspace_branch_order_delta_vs_direct_callable_baseline.txt:1-34
  IMPACT: Candidate fails the non-override retention criteria.
  NEXT: Reject and revert this slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Reject and revert the `_get_existing_creation` spellspace-branch-first slice.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_spellspace_branch_order_delta_vs_direct_callable_baseline.txt:23-31, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_phase12_no_overrides_spellspace_branch_order_delta_vs_direct_callable_baseline.txt:33-34
  IMPACT: Prevents carrying a large fast-lane regression into the retained baseline.
  NEXT: Revert code change, run post-revert validation, and announce result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: Post-revert validation is green and no-overrides hotspot call-chain is back on retained baseline behavior.
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_spellspace_branch_order_slice_reverted.txt:1-10, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:24-29
  IMPACT: Confirms branch-order candidate rollback and baseline restoration.
  NEXT: Continue no-overrides optimization from retained baseline with a different structural target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: ALIGNMENT_CHECK
  CLAIM: Branch-order slice outcome was explicitly announced (reject + revert + baseline restored).
  EVIDENCE: benchmarks/testing_other_di/profiles/overrides_graphs_melder/validation_unit_wave1_phase12_no_overrides_spellspace_branch_order_slice_reverted.txt:8-10, context_compass/AGENTS.MD:54-54
  IMPACT: Keeps per-slice result visibility explicit as requested.
  NEXT: Preserve this announcement pattern for subsequent non-override slices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Next no-overrides slice will remove unreachable list-shape branches from `_build_kwargs_no_overrides` when `dependency_count > 2` (values list always length >= 3 if no KeyError), reducing per-step branch overhead without changing emitted semantics.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1068-1103, benchmarks/testing_other_di/profiles/fast_graphs_melder/melder_fast_timings_shallow.summary.txt:24-29
  IMPACT: Applies a minimal structural cleanup in a measured helper hotspot.
  NEXT: Implement branch cleanup, run no-overrides unit tests, then rerun fast/override benchmark cadence for keep/revert.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Wave-1 task is active with the latest retained baseline set to the
CreationContext prebound Phase10 apply-callable slice
(`wave1_creation_context_prebound_phase10_apply_postbaseline.txt`).
The retained Phase12 follow-up slice inlines Existence.many registration
inside the overrides shape emitter and skips unused registration metadata
locals for non-registering many steps
(`wave1_phase12_overrides_many_register_inline_delta_vs_postrevert_baseline.txt`).
The retained follow-up specialization now also emits static disposal-aware
many-registration lanes (skip entirely for static no-disposal rows; emit direct
registration for static yes-disposal rows)
(`wave1_phase12_overrides_many_static_disposal_registration_delta_vs_lock_gate_baseline.txt`).
The retained invoke-path follow-up emits direct callable invocation for static
empty-kwargs no-override lanes inside override executors
(`wave1_phase12_overrides_direct_callable_empty_kwargs_delta_vs_static_disposal_baseline.txt`).
The follow-up many caller/spellspace spell-local elision candidate was measured
as non-winning and reverted
(`wave1_phase12_overrides_many_caller_spell_local_elision_delta_vs_direct_callable_baseline.txt`).
The follow-up prebound `plan_step_{i}` defaults candidate was also measured as
non-winning and reverted
(`wave1_phase12_overrides_prebound_plan_steps_delta_vs_direct_callable_baseline.txt`).
The follow-up route-field prebind slice was rejected and reverted
(`wave1_creation_context_prebound_route_fields_delta_vs_prebaseline.txt`).
Next action is to target the next structural override runtime hotspot inside
generated `_phase12_executor` and rerun normal cadence.


