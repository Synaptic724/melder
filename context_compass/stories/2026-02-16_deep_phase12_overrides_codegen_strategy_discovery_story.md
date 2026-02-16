# Story: Deep Phase12 Overrides Codegen Strategy Discovery

## Metadata
- Story ID: STORY-2026-02-16-deep-phase12-overrides-codegen-strategy-discovery
- Epic: EPIC-2026-02-15-creationcontext-phase12-codegen-optimization
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## User Narrative
As a runtime/codegen maintainer, I want deep structural analysis of
`phase12_overrides_executor.py`, so we improve override codegen strategy beyond
the hotspots already optimized in wave-1.

## Value / MRP Alignment
This discovery lane targets deeper generator decisions:
- compile pipeline shape (source/code-object/exec),
- shape-metadata inference complexity,
- inline kwargs/invoke emission scale and duplication.

## Requirements (Functional)
- Map core override compile pipeline and source-path alternatives.
- Identify generator complexity centers not addressed by prior slices.
- Propose deep strategy options with risk/benefit tradeoffs.

## Requirements (Non-Functional)
- Discovery-only in this story.
- Maintain UNKNOWN labeling for unevidenced cache-usage/frequency claims.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- Core compile flow, shape-source emission, and prefilter cache hooks.
- Out of scope:
- No-overrides emitter internals.
- Public runtime contract changes.

## Dependencies / Related Work
- `context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md`
- `context_compass/tasks/completed/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md`

## Tasks (Implementation Checklist)
- [x] Analyze core compile flow and source/code-object reuse boundaries.
- [x] Quantify complexity of shape-metadata and inline kwargs/invoke emitters.
- [x] Define strategy candidates (shape-family partitioning, generated-function size control, metadata precomputation lanes).
- [x] Define benchmark/validation plan for follow-on implementation.
- [x] Enforce benchmark gate for every follow-on optimization slice (pre-test, post-test, and mandatory `DECISION_REQUEST` escalation on failure/non-winning delta).
- [x] Open first implementation task from rank-1 strategy with benchmark gate copied verbatim.
- [x] Open and maintain low/medium/high risk-lane discovery tasks for this story.
- [ ] Execute `TASK-2026-02-16-phase12-overrides-low-risk-discovery`.
- [x] Execute `TASK-2026-02-16-phase12-overrides-medium-risk-discovery`.
- [ ] Execute `TASK-2026-02-16-phase12-overrides-high-risk-discovery`.

## Acceptance Criteria
- At least three deep findings documented with evidence.
- At least two strategy candidates documented with tradeoffs.
- Clear follow-on experiment plan recorded.

## Validation / Test Plan
- Discovery-only for this story.
- Follow-on validation commands (for implementation):
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`

## Benchmark Gate (Mandatory)
- Pre-test baseline (before any code edit):
  - Run unit suite:
    - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py -q`
  - Run benchmark cadence using the same suites used throughout wave-1:
    - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s` (run twice sequentially)
    - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s` (run twice sequentially)
  - Capture medians and write baseline artifact/delta context against:
    - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_retained_baseline_checkpoint_2026-02-16.txt`
- Post-test (after each candidate edit):
  - Re-run the same unit + benchmark cadence.
  - Emit a candidate delta artifact under:
    - `benchmarks/testing_other_di/profiles/overrides_graphs_melder/`
- Decision gate (non-negotiable):
  - If unit or benchmark command fails, raise `DECISION_REQUEST` and wait for user keep/revert direction.
  - If measured delta is non-winning versus retained checkpoint, raise `DECISION_REQUEST` and wait for user keep/revert direction.
  - Emit `RESULT: DECISION_REQUEST` with failure/non-winning evidence and explicit keep/revert options before any state change.
  - If user selects revert, run one full post-revert validation pass:
    - unit suite once, fast cprofile once, overrides cprofile once.
  - Emit post-revert validation artifact and explicit result-announce note (`RESULT: REVERTED` + reason + artifact path).
- Retain gate:
  - Retain only candidates that pass validation, satisfy checkpoint comparison criteria, and have explicit user keep direction.
  - Emit explicit result-announce note (`RESULT: RETAINED` + median deltas + artifact path).

## Risk-Lane Discovery Queue (Required Reference)
Process rule:
- Before each new investigation or implementation iteration, select one task from this queue and reference its task ID in `## Notes`.
- Do not run ad-hoc candidate exploration outside this queue unless a `DECISION` note expands scope first.

| Risk lane | Status | Task | Focus |
|---|---|---|---|
| low | ready | `context_compass/tasks/2026-02-16_phase12_overrides_low_risk_discovery_task.md` | compact, contract-safe override efficiency candidates |
| medium | done | `context_compass/tasks/2026-02-16_phase12_overrides_medium_risk_discovery_task.md` | medium-reward compile/source strategy candidates |
| high | ready | `context_compass/tasks/2026-02-16_phase12_overrides_high_risk_discovery_task.md` | high-risk override generator redesign discovery |

## Strategy Candidates (Ranked)
1. Rank-1 (selected for first implementation task): compact generated step bodies by extracting cold/error-heavy invoke/kwargs branches to shared helpers while preserving inline fast paths for common override shapes.
- Why now:
- Current shape emitter inlines large kwargs/invoke/error blocks into every step body, inflating generated function size and compile/exec payload.
- Expected effect:
- Reduce emitted source size and compile pressure on shape misses while keeping hot success paths specialized.
- Risks:
- Helper fallback can add runtime call overhead if over-applied; scope first slice to cold/error branches only.
2. Rank-2: cache shape-step metadata snapshots keyed by `(plan_signature, socket_shape, root_positional_arity)` to avoid repeated metadata walks on cache misses for adjacent override calls.
- Why now:
- `_build_shape_source_step_metadata` performs required-field validation, existence enum conversion, dependency tuple rebuilding, and optional spell lookup per row.
- Expected effect:
- Lower compile-miss setup cost before source emission.
- Risks:
- Cache invalidation semantics must stay tied to plan signature and spell lookup freshness.
3. Rank-3: trim namespace/prebind payload churn by reducing per-compile tuple materialization where static values are already represented in row metadata.
- Why now:
- Namespace assembly currently builds multiple per-step tuple projections before `exec`.
- Expected effect:
- Moderate compile-miss reduction; likely smaller gain than rank-1 and rank-2.
- Risks:
- Aggressive trimming can break generated-source contract defaults if bindings diverge.

## Risks / Mitigations
- Risk: reducing generated complexity could regress override correctness.
  Mitigation: keep root/override precedence contracts as non-negotiable gates.
- Risk: large emitter refactors lose reviewability.
  Mitigation: structure follow-on work into small strategy-specific slices.

## Open Questions
- Which parts of override generation dominate compile time vs runtime?
- What are observed hit rates for prefilter and specialization caches under benchmark workloads?

## Decision Log
- 2026-02-16: Story opened per user direction for deep overrides codegen strategy discovery.

## Notes
- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Core override compile flow supports source and code-object paths, builds per-step override targets, and executes compiled code with generated namespace binding.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:337-433
  IMPACT: Strategy work can target compile pipeline decisions (source reuse, code-object reuse, prefilter reuse) in addition to emitted runtime code shape.
  NEXT: map where compile callers can safely pass reusable caches/code objects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Shape-source path performs heavy per-row metadata inference (existence resolution, callable/existing/disposal flags, target-count heuristics) before emitting specialized source.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:751-848
  IMPACT: Metadata inference complexity is a deep pre-emit optimization surface distinct from runtime helper micro-tuning.
  NEXT: evaluate metadata precomputation and reuse strategy candidates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Override emitter inlines large kwargs/invoke logic blocks, including dependency-missing error construction and positional-args decode paths, across generated step bodies.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:983-1490, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1540-1689
  IMPACT: Generated-function size and duplication are likely major strategic levers for further performance/maintainability gains.
  NEXT: define code-size control options (split emitters, helper extraction for cold/error paths, shape-family partitioning).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Step-target prefilter logic supports external caches for per-step target tuples and path metadata.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2516-2587
  IMPACT: Compile-time reuse strategy can extend this cache model if call sites consistently pass stable cache keys/objects.
  NEXT: trace call sites to determine real cache utilization patterns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: UNKNOWN
  CLAIM: Effective cache-hit rates for `prefilter_step_targets_cache` and `prefilter_path_metadata_cache` in production-like compile flows are not yet measured.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2516-2587
  IMPACT: Cache-expansion strategy cannot be prioritized confidently without usage measurements.
  NEXT: instrument compile call sites to capture cache usage and hit rate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Follow-on implementation from this story is gated by mandatory benchmark discipline: pre-test baseline, post-test comparison, and `DECISION_REQUEST` escalation on failing tests or non-winning deltas.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:48-80, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave1_retained_baseline_checkpoint_2026-02-16.txt:1-20
  IMPACT: Enforces consistent keep/revert behavior with the same benchmark suites used in wave-1.
  NEXT: Apply this gate to every generated-code optimization slice from this story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Benchmark gate wording is now standardized across all deep codegen stories and epic-level rules, including explicit `RESULT: RETAINED` and `RESULT: REVERTED` announcement requirements.
  EVIDENCE: context_compass/stories/2026-02-16_deep_creation_context_codegen_strategy_discovery_story.md:63-84, context_compass/stories/2026-02-16_deep_phase12_no_overrides_codegen_strategy_discovery_story.md:63-84, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:63-84, context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md:137-140
  IMPACT: Follow-on optimization tasks for non-overrides and overrides now share one enforceable pre/post/revert benchmark contract with mandatory outcome reporting.
  NEXT: Copy this gate verbatim into each new implementation task opened from these deep stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Override specialization compile plumbing already uses shape-key executor caching plus source/code-object/prefilter caches in `CreationContext` compile-miss flow.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context.py:657-688, src/melder/aether/conduit/meld/creation_context/creation_context.py:1141-1177, src/melder/aether/conduit/meld/creation_context/creation_context.py:1194-1235, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2521-2587
  IMPACT: Priority shifts from adding new cache plumbing to reducing per-miss source generation and compile payload size.
  NEXT: Rank strategy candidates by expected compile-miss impact and open first implementation task for rank-1 lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Ranked options are (1) cold/error-path helper extraction with inline fast paths retained, (2) shape-step metadata snapshot caching, (3) namespace/prebind payload trimming; rank-1 offers the best reviewable first slice with lower contract risk.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:869-980, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:983-1310, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1540-1689, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1827-1935, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:436-534
  IMPACT: We can move from discovery to one compact implementation slice while preserving existing benchmark/revert gates.
  NEXT: Open a new task for rank-1 lane and copy benchmark gate verbatim.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Opened `TASK-2026-02-16-phase12-overrides-cold-path-helper-extraction` as the first compact implementation slice for the rank-1 strategy.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_cold_path_helper_extraction_task.md:1-104, context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:87-108
  IMPACT: Discovery is now connected to a single actionable implementation lane with benchmark/revert/announce requirements pre-encoded.
  NEXT: Route active attention to the new task and run pre-test baseline cadence before code edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: First compact rank-1 implementation slice completed full pre-test and post-test cadence; checkpoint comparison was non-winning due fast-lane regression.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_cold_path_helper_extraction_task.md:101-117, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_posttest_summary_2026-02-16.txt:1-25
  IMPACT: Candidate cannot be retained under mandatory keep/revert policy.
  NEXT: Record explicit revert announcement and complete post-revert validation evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: RESULT: REVERTED - `TASK-2026-02-16-phase12-overrides-cold-path-helper-extraction` candidate was reverted after non-winning checkpoint deltas; post-revert validation completed.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_cold_path_helper_extraction_task.md:119-135, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave2_phase12_overrides_coldpath_slice1_postrevert_summary_2026-02-16.txt:1-25
  IMPACT: Overrides executor runtime is restored to pre-candidate behavior with compliance artifacts captured.
  NEXT: Choose next compact slice (narrower rank-1 variant or rank-2 metadata snapshot caching) under the same benchmark gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Created a mandatory low/medium/high risk-lane queue for overrides discovery and required future iterations to start from queued task IDs.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:85-96, context_compass/tasks/2026-02-16_phase12_overrides_low_risk_discovery_task.md:1-77, context_compass/tasks/2026-02-16_phase12_overrides_medium_risk_discovery_task.md:1-77, context_compass/tasks/2026-02-16_phase12_overrides_high_risk_discovery_task.md:1-77
  IMPACT: Next override iterations now run from a fixed risk-lane backlog instead of rediscovery-based path selection.
  NEXT: Start the next iteration from `TASK-2026-02-16-phase12-overrides-medium-risk-discovery` unless user reprioritizes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: PLAN
  CLAIM: Overrides low/medium/high tasks are now loaded with multi-candidate backlogs and reusable ops-reference steps so we can iterate directly from task ops.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_low_risk_discovery_task.md:34-84, context_compass/tasks/2026-02-16_phase12_overrides_medium_risk_discovery_task.md:35-85, context_compass/tasks/2026-02-16_phase12_overrides_high_risk_discovery_task.md:34-83
  IMPACT: Overrides lane can execute repeated attempts without redoing candidate discovery setup.
  NEXT: Begin with `OV-M1` for medium-risk pass; keep strict result/revert gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Discovery iteration 2 expanded the overrides medium-risk queue to eight candidates, adding deeper compile-miss preprocessing reuse options while keeping `OV-M1` as first execution pick.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_medium_risk_discovery_task.md:38-55, src/melder/aether/conduit/meld/creation_context/creation_context.py:653-675, src/melder/aether/conduit/meld/creation_context/creation_context.py:875-924, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:269-334, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2397-2486
  IMPACT: Medium-risk lane now supports several additional iterations without fresh backlog work.
  NEXT: Execute `OV-M1`; if reverted, continue with `OV-M6` then `OV-M2` under the same benchmark gate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Execution order was switched to high-risk-first; opened OV-H1 implementation task slice 1 for benchmark-gated execution.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_high_risk_discovery_task.md:34-54, context_compass/tasks/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice1_task.md:1-112
  IMPACT: Overrides lane now begins implementation from high-risk queue while preserving mandatory keep/revert controls.
  NEXT: Run pre-test baseline cadence in the OV-H1 slice task, then implement one compact high-risk change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: OV-H1 slice 1 failed the post-test unit gate before benchmark comparison; the shape-source emission no longer matched existing direct-callable-invoke test expectations.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice1_task.md:121-128, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_phase12_overrides_highrisk_ovh1_slice1_posttest_2026-02-16.txt:4-68
  IMPACT: Candidate cannot be retained and must be reverted per standardized gate.
  NEXT: Complete mandatory revert + post-revert validation and record explicit RESULT note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: RESULT: REVERTED - OV-H1 slice 1 was reverted after unit failure; post-revert validation passed and runtime code returned to pre-slice behavior.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice1_task.md:130-137, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_phase12_overrides_highrisk_ovh1_slice1_postrevert_2026-02-16.txt:1-986
  IMPACT: High-risk lane remains open, but next attempt should narrow helper segmentation to preserve shape-source text contracts.
  NEXT: Open OV-H1 slice 2 task and continue high-risk-first iteration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: MEASURE
  CLAIM: OV-H1 slice 2 is opened and prebaseline cadence is complete, enabling immediate post-edit keep/revert evaluation on the next patch.
  EVIDENCE: context_compass/tasks/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice2_task.md:1-115, benchmarks/testing_other_di/profiles/overrides_graphs_melder/wave3_phase12_overrides_highrisk_ovh1_slice2_prebaseline_2026-02-16.txt:1-1954
  IMPACT: High-risk-first iteration resumes without additional discovery/setup delay.
  NEXT: Implement slice-2 owner-target helper segmentation and run post-test cadence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: DECISION
  CLAIM: Active overrides execution now requires `RESULT: DECISION_REQUEST` and explicit user keep/revert direction for failing/non-winning benchmark outcomes.
  EVIDENCE: context_compass/stories/2026-02-16_deep_phase12_overrides_codegen_strategy_discovery_story.md:80-91, context_compass/tasks/2026-02-16_phase12_overrides_high_risk_segmented_shape_helpers_slice2_task.md:61-72
  IMPACT: The agent no longer performs autonomous keep/revert decisions in this story lane.
  NEXT: If OV-H1 slice 2 fails/non-wins post-test, publish `RESULT: DECISION_REQUEST` and pause for user choice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Deep overrides discovery opened with evidence on compile pipeline, shape
metadata complexity, inline emitter size, and prefilter cache hooks. Next step
is selecting the next compact candidate after the first rank-1 slice was
executed and reverted as non-winning (with full post-revert validation
artifacts captured). Benchmark gate wording is standardized across all deep
codegen stories, including explicit `RESULT` announcement requirements for
user-directed keep/revert decisions. Low/medium/high risk-lane discovery tasks are now
opened and required as the iteration entry queue. Medium-risk ticket is turned
in and marked done.
