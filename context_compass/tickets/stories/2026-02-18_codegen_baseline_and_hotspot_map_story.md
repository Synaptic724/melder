# Story: Baseline and Hotspot Map for Phase12 Codegen

## Metadata
- Story ID: STORY-2026-02-18-codegen-baseline-and-hotspot-map
- Epic: EPIC-2026-02-18-phase12-creation-context-codegen-optimization
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-18T10:22:40Z
- Updated: 2026-02-18T10:24:30Z

## User Narrative
As a performance engineer, I want a reproducible mean-based hotspot map for
Phase 12 and CreationContext codegen, so that we implement the highest-yield
ops first with measurable impact.

## Value / MRP Alignment
This story establishes the minimum trustworthy measurement baseline and hotspot
ordering required before code changes. It keeps optimization work focused on
the core runtime path with reproducible evidence.

## Ticket Contract
- ENTRY_GATE: `attention_board.md` routes active work to this story and epic scope is active.
- EXECUTION_BOUNDARY: Phase 12 executor codegen and CreationContext override dispatch only.
- DEPENDENCIES: pinned discovery artifacts, epic metric policy, and benchmark runner controls.
- EXIT_GATE: mean baseline + ranked hotspot ops documented with evidence and linked tasks.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` for metric-policy conflicts or scope expansion.

## Requirements (Functional)
- Produce route means from pinned samples excluding `warm_spellspace_ns`.
- Rank Phase12/CreationContext ops by route weight and profiler cumulative cost.
- Map top profiler functions to concrete source symbols/line anchors.

## Requirements (Non-Functional)
- Use pinned affinity benchmark artifacts only for comparisons in this story.
- Use mean metrics (not medians) for optimization ordering.
- Keep outputs concise, reproducible, and evidence-linked.

## Scope Boundaries
- In scope:
  - `benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - `src/melder/spellbook/spell_crafter/blueprints/phase12_*`
  - `src/melder/spellbook/spell_crafter/blueprints/patch_maps.py`
- Out of scope:
  - branch strategy experiments
  - spellspace-driven optimization decisions
  - unrelated runtime refactors

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: user-directed continuation moved execution from epic routing into story-level hotspot mapping.

## Dependencies / Related Work
- `tickets/epics/2026-02-18_phase12_creation_context_codegen_optimization_epic.md`
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json`
- `benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned.json`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-18-codegen-phase12-baseline-mean-profile - publish pinned means excluding spellspace.
- [ ] Task: TASK-2026-02-18-codegen-phase12-hotspot-op-priority-map - rank concrete phase12/codegen ops.
- [ ] Task: TASK-2026-02-18-creation-context-override-dispatch-micro-optimization - optimize first override-dispatch target and remeasure.
- [ ] Task: TASK-2026-02-18-targeted-override-patchmap-micro-optimization - optimize targeted override patch-map path and remeasure.
- [ ] Task: TASK-2026-02-18-overrides-executor-kwargs-fastpath - optimize overrides executor kwargs materialization path and remeasure.
- [ ] Task: TASK-2026-02-18-phase12-invoke-no-args-fastpath - optimize no-args invocation helpers in phase12 executors and remeasure.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Mean baseline table exists for `warm_mixed_ns`, `warm_override_targeted_ns`,
  `warm_override_root_args_ns`, and `warm_root_ns` (excluding spellspace).
- Ranked hotspot list exists with at least four concrete ops and file anchors.
- Branch-structure exploration is explicitly excluded in story notes.
- Next implementation target is selected and linked to a follow-on task.

## Validation / Test Plan
- Recompute means from raw route samples in pinned artifact.
- Verify profiler hotspots from pinned deep route profile sections.
- Validation command reference:
  - `$env:PYTHONPATH='.;src'; python benchmarks/testing_other_di/run_codegen_benchmark_deltas.py --sample-count 3 --warmup-count 1 --profile-iteration-count 20 --profile-top-functions 30 --pin-p-cores --output-path benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json`

## UX / API / Data Notes
- No public API changes in this story.
- Data output is benchmark interpretation only.

## Risks / Mitigations
- Risk: noisy samples can mis-rank ops.
  - Mitigation: use pinned affinity artifacts and mean aggregation from raw samples.
- Risk: profiler includes non-codegen overhead.
  - Mitigation: rank only phase12/creation_context/patch-map symbols for execution targets.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should first implementation tranche target override dispatch or no-overrides executor reuse path?

## Decision Log
- 2026-02-18: Story-level hotspot ranking uses means and excludes spellspace for priority decisions.
- 2026-02-18: Branch exploration is excluded from this story scope.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-02-18T10:22:40Z
  TYPE: PLAN
  CLAIM: This story is now the active unit for baseline/hotspot mapping with strict phase12/codegen scope.
  EVIDENCE:
  - tickets/epics/2026-02-18_phase12_creation_context_codegen_optimization_epic.md:259-287
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:166-671
  IMPACT: Discovery and prioritization now execute at story granularity before implementation tranches.
  NEXT: Create and route baseline + hotspot tasks, then publish op ordering evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:22:40Z
  TYPE: MEASURE
  CLAIM: Non-spellspace means from pinned deep samples rank routes as warm_mixed (23100) > warm_override_targeted (6700) > warm_override_root_args (6133.33) > warm_root (600).
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:1066-1084
  IMPACT: Warm mixed and override routes carry the highest optimization yield under current policy.
  NEXT: Rank concrete codegen ops inside those routes by profiler cumulative time.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:24:30Z
  TYPE: DECISION
  CLAIM: Ranked phase12/codegen ops are (1) `_execute_with_overrides`, (2) generated overrides executor `_phase12_executor`, (3) patch-map apply/target-resolution, then (4) no-overrides executor creation/reuse helpers; first implementation target is override dispatch in `creation_context.py`.
  EVIDENCE:
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:427-434
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:595-616
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:665-665
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_pinned_deep.json:217-336
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:565-739
  - src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:268-416
  IMPACT: Next tranche can begin with a focused, low-blast-radius change in the hottest override-dispatch path.
  NEXT: Start implementation task for `creation_context` override dispatch micro-optimizations and remeasure pinned means.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:28:20Z
  TYPE: MEASURE
  CLAIM: First implementation tranche improved `warm_override_root_args_ns` while leaving targeted/mixed outcomes near-flat-to-slightly-regressed across two pinned reruns, so additional override-path optimization is required.
  EVIDENCE:
  - tickets/tasks/2026-02-18_creation_context_override_dispatch_micro_optimization_task.md:107-126
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_cc_override_dispatch.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_cc_override_dispatch_r2.json:652-671
  IMPACT: Story remains in progress; tranche 2 should target patch-map/apply and generated overrides executor costs.
  NEXT: Start second implementation tranche focused on override targeted path costs and rerun pinned benchmarks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:36:22Z
  TYPE: DECISION
  CLAIM: User directed reverting both tranche 1 and tranche 2 code changes due mixed-route outcome concerns.
  EVIDENCE:
  - tickets/tasks/2026-02-18_creation_context_override_dispatch_micro_optimization_task.md:122-141
  - tickets/tasks/2026-02-18_targeted_override_patchmap_micro_optimization_task.md:115-134
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:611-614
  - src/melder/spellbook/spell_crafter/blueprints/patch_maps.py:302-323
  IMPACT: Story continues with reverted baseline code and must pursue a different hotspot for phase12/codegen gains.
  NEXT: Open overrides-executor micro-optimization task and remeasure with pinned means.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:39:48Z
  TYPE: MEASURE
  CLAIM: Tranche 3 overrides-executor kwargs fast-path was also reverted after pinned reruns showed mixed-route regression despite slight targeted-route gain.
  EVIDENCE:
  - tickets/tasks/2026-02-18_overrides_executor_kwargs_fastpath_task.md:99-128
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_overrides_executor_tranche3.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_overrides_executor_tranche3_r2.json:652-671
  IMPACT: Three attempted tranches are now reverted; next attempt should target a different high-frequency path.
  NEXT: Start no-args invocation fast-path tranche in phase12 executor helpers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-02-18T10:42:12Z
  TYPE: MEASURE
  CLAIM: Tranche 4 no-args invocation helper fast path regressed non-spellspace means and was reverted.
  EVIDENCE:
  - tickets/tasks/2026-02-18_phase12_invoke_no_args_fastpath_task.md:106-125
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_invoke_fastpath_tranche4.json:652-671
  - benchmarks/testing_other_di/results/codegen_discovery_2026-02-18_after_invoke_fastpath_tranche4_r2.json:652-671
  IMPACT: Four implementation tranches are now reverted; further code edits should be preceded by stronger measurement confidence.
  NEXT: Run higher-sample pinned baseline/after comparisons before next optimization edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Story is active and scoped to pinned mean-baseline and phase12/codegen hotspot
ranking. Tranche 1/2/3/4 patches are reverted; next step is higher-sample
measurement before further code edits.
