# Task: Discovery Phase12 Codegen



Completed: 2026-02-15
Summary: Closed after user acceptance; implementation and validation artifacts are recorded in this ticket.


## Metadata
- Task ID: TASK-2026-02-13-discovery-phase12-codegen
- Story: STORY-2026-02-13-optimize-phase12-codegen
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-13
- Updated: 2026-02-15

## Objective
Build a discovery baseline and hotspot map for Phase 12 executor generation
paths so optimization tasks can be prioritized by measured impact.

## Scope Boundaries
- In scope:
- No-overrides and overrides Phase 12 executor emission paths.
- Emission-shape hotspots that influence runtime branch/call depth.
- Ranked optimization candidate extraction with contract constraints.
- Out of scope:
- Runtime behavior changes in this task.
- Broader SpellCrafter phase optimization outside Phase 12.

## Steps / Checklist
- [x] Map no-overrides and overrides compiler/emitter entrypaths.
- [x] Identify highest-cost emission steps and duplicated shaping logic.
- [x] Record invariants that must remain stable for generated executor contracts.
- [x] Produce ranked optimization candidates and append follow-up tasks.

## Deliverables
- Phase 12 codegen discovery baseline with evidence-backed hotspot ranking.
- Prioritized follow-up optimization candidates for Phase 12 emitter work.

## Files / Paths Impacted
- `context_compass/stories/completed/2026-02-13_optimize_phase12_codegen_story.md`
- `context_compass/tasks/2026-02-13_discovery_phase12_codegen_task.md`
- `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md`
- `context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md`
- `context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md`
- `context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output.txt`
- `context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output_py_path.txt`
- `context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output_env_root_src.txt`

## Validation
- Not run.
- Attempted benchmark validation is currently blocked by stale benchmark imports on head (`run_codegen_benchmark_deltas.py` still imports removed `meld_runtime` path).
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/spellbook/spell_crafter -k \"phase12 or codegen\"`

## Risks / Rollback Notes
- Risk: optimization candidates ignore generated-executor contract boundaries.
- Rollback: mark candidates UNKNOWN until contract constraints are evidenced.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Post-archive pointer hygiene is complete for this phase12 lane: all lingering references now target `stories/completed` and `tasks/completed`, and user-reported benchmark evidence ranges were normalized to exact begin/end lines.
  EVIDENCE: context_compass/tasks/2026-02-13_discovery_phase12_codegen_task.md:35-40, context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:102-104, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:112-114, context_compass/attention_board.md:27-30
  IMPACT: Compaction re-entry now resolves directly to archived phase12 tickets without dead-path scans.
  NEXT: Keep routing on remaining active phase-discovery tickets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: This story requires exactly one discovery task and already references this task ID.
  EVIDENCE: context_compass/epics/completed/2026-02-13_optimize_melder_epic.md:51-51, context_compass/stories/completed/2026-02-13_optimize_phase12_codegen_story.md:48-52
  IMPACT: Creating this task closes the missing ticket link and unblocks discovery execution.
  NEXT: Start emitter-path mapping in `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py` and `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`.

- DATE: 2026-02-14
  TYPE: UNKNOWN
  CLAIM: Policy docs point to `config/context_compass_config.yaml` for microcycle strict/relaxed mode, but this checkout did not resolve that path yet.
  EVIDENCE: context_compass/AGENTS.MD:437-437, context_compass/WORKFLOW.md:83-83, context_compass/agent_onboarding/agent/general/skills/context_window_budget.md:12-12
  IMPACT: Discovery execution should treat strict microcycle as default until the canonical config location is verified.
  NEXT: Locate the actual config file path (or confirm missing/stale reference) before using any non-default microcycle behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Microcycle config exists at `context_compass/config/context_compass_config.yaml` with strict mode enabled (`enabled: true`, `mode: strict`); policy docs using root `config/...` path are stale pointers.
  EVIDENCE: context_compass/config/context_compass_config.yaml:8-13, context_compass/AGENTS.MD:437-437, context_compass/WORKFLOW.md:83-83
  IMPACT: We will enforce strict microcycle rules from the discovered canonical config path during this task.
  NEXT: Start Phase 12 discovery mapping by tracing no-overrides and overrides compiler entrypaths in blueprint modules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Phase12 no-overrides compilation always compiles emitted source inline (`compile(...)+exec(...)`) and currently exposes no reusable code-object compile path, while overrides already has explicit code-object compile/reuse APIs that CreationContext caches by step count.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:55-148, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:347-375, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:117-170, src/melder/aether/conduit/meld/creation_context/creation_context.py:1008-1065
  IMPACT: A top discovery candidate is adding no-overrides code-object/source reuse parity for repeated step-count compiles.
  NEXT: Trace no-overrides call sites in CreationContext to confirm where compile churn can occur and rank this candidate against other Phase12 hotspots.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: No-overrides Phase12 compilation is SpellCrafter lifecycle-scoped (dirty-cycle triggered with signature reuse) and then injected into CreationContext as a prebound executor, so it is not a per-meld runtime compile-miss path.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:1969-2037, src/melder/spellbook/spell_crafter/spell_crafter.py:3756-3758, src/melder/aether/conduit/meld/creation_context/creation_context.py:199-221, src/melder/aether/conduit/meld/creation_context/creation_context.py:277-320
  IMPACT: No-overrides code-object reuse parity is likely a lower-priority optimization than override specialization miss-path costs.
  NEXT: Focus remaining discovery on override executor emission/runtime shape (step branch lattice, per-step helper call depth, targeted override checks).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Override executor emission currently generates a full per-step branch lattice (target-kind selection + existence-mode reuse/register paths) and duplicates override-reuse guard/lookup/construct calls across branches for every emitted step.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:393-459, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:474-657, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:890-920
  IMPACT: Emitted source size and branch/call depth scale directly with step count, making per-step branch-shape reductions a high-value optimization candidate.
  NEXT: Check existing profile artifacts for runtime concentration in emitted override helper calls (`_get_existing_creation`, `_construct_spell_instance_with_overrides`, `_build_kwargs_with_overrides`) to rank this candidate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Current phase-component cProfile artifacts are generation-heavy top-30 snapshots and do not surface Phase12 override runtime helper symbols, so they are insufficient to rank emitted-step runtime helper hotspots.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_creation_context_override_prefilter_caching_output.txt:8-40, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_creation_context_override_miss_compile_reuse_output.txt:8-40
  IMPACT: We need a runtime-targeted measurement hook (or deeper profile window) before assigning measured priority to helper-level Phase12 runtime refactors.
  NEXT: Locate existing benchmark/test hooks that execute override meld runtime directly (not phase generation) and evaluate whether they can produce helper-level profiling evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Existing `run_codegen_benchmark_deltas.py` route-matrix data already captures override-runtime routes and shows `warm_override_targeted_ns` as the slowest warm route (0.1033 cold ratio), above `warm_override_root_args_ns` (0.0663), spellspace (0.0135), and warm root (0.00045).
  EVIDENCE: benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:280-293, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:486-525, benchmarks/testing_other_di/results/codegen_benchmark_report_smoke_v2_pass12.json:19-31
  IMPACT: Override-targeted runtime remains the strongest measured Phase12-adjacent lane for optimization ranking in this story.
  NEXT: Run a fresh benchmark delta sample on current HEAD and store an artifact so ranking is based on current code rather than prior smoke snapshots.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Fresh benchmark attempt failed in this shell because `melder` is not importable by default (`ModuleNotFoundError`), so runtime measurement requires explicit `PYTHONPATH=src`.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output.txt:8-11, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:7-7
  IMPACT: Discovery measurement commands need repo-local module path wiring to produce usable artifacts.
  NEXT: Re-run the route-matrix benchmark with `PYTHONPATH=src` and capture new output/json artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: `PYTHONPATH=src` alone is still invalid for this benchmark entrypoint because `src/melder/__init__.py` imports `src.melder...`, so the repo root must also be on `PYTHONPATH`.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output_py_path.txt:11-13, src/melder/__init__.py:11-11
  IMPACT: Benchmark invocation must use `PYTHONPATH=.;src` (or equivalent) for this repo's import contract.
  NEXT: Re-run benchmark with `PYTHONPATH=.;src` and collect the fresh route-matrix artifact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Fresh route-matrix benchmark execution is blocked on stale imports in `run_codegen_benchmark_deltas.py` (`melder.aether.conduit.meld.meld_runtime.meld_runtime` no longer exists on current HEAD).
  EVIDENCE: context_compass/artifacts/2026-02-14_phase12_codegen_route_matrix_current_head_output_env_root_src.txt:17-21, benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:9-9
  IMPACT: Current measured ranking must rely on existing benchmark artifacts until this benchmark entrypoint is migrated to current CreationContext-era module paths.
  NEXT: Continue discovery using existing route-matrix artifacts and source-evidence ranking; optionally raise a follow-up ticket to repair benchmark imports.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Phase12 override contracts that optimization must preserve are explicit in tests: emitted executors must keep inlined target routing/prebound step metadata, preserve root-positional+targeted override precedence, reject override reuse on existing shared instances, and keep non-shared path filtering compile-time only.
  EVIDENCE: tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py:258-290, tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py:440-490, tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py:492-616, tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py:773-827
  IMPACT: Follow-up optimization tasks must be source-shape and helper-path focused without weakening these guardrails.
  NEXT: Produce ranked Phase12 optimization candidates and create scoped follow-up tasks constrained by these invariants.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Override source/code-object reuse is currently keyed only by `step_count`, while emitted source is generic and runtime-branches on per-step `target_kind`/`existence`; this keeps cache reuse high but preserves per-call branch lattice overhead for all shapes.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:1008-1044, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:214-227, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:393-445, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:474-657
  IMPACT: Highest-impact candidate is likely shape-aware source specialization that trades some cache cardinality for lower runtime branch/call depth in targeted override lanes.
  NEXT: Convert discovered candidates into ranked follow-up tasks (shape-specialized source, helper-path tightening, benchmark harness repair).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Discovery ranking is finalized and translated into three follow-up tasks: (1) override shape-specialized source (rank-1), (2) override helper callpath tightening (rank-2), and (3) route-matrix benchmark entrypoint repair (measurement enabler).
  EVIDENCE: context_compass/tasks/completed/2026-02-14_optimize_phase12_override_shape_specialized_source_task.md:1-70, context_compass/tasks/completed/2026-02-14_optimize_phase12_override_helper_callpath_tightening_task.md:1-68, context_compass/tasks/completed/2026-02-14_repair_phase12_route_matrix_benchmark_entrypoint_task.md:1-66
  IMPACT: Story is now execution-ready with ranked scope and explicit measurement unblock path.
  NEXT: Update story/attention board routing and request user acceptance for discovery closure before starting rank-1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Discovery is complete and in review. Ranked follow-up tasks are created for
Phase12 execution, and benchmark refresh on current head is currently blocked by
stale `run_codegen_benchmark_deltas.py` imports (`meld_runtime` path). Next step
is user acceptance for discovery closure and rank-1 task start.


