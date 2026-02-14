# Task: Discovery Phase Group 8-11 Baseline

## Metadata
- Task ID: TASK-2026-02-14-discovery-phase-group-8-11-baseline
- Story: STORY-2026-02-14-phase-group-8-11-baseline
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Define the baseline direct-call profiling contract for conduit plan phases 8-11.

## Scope Boundaries
- In scope:
- Sequence and fixture requirements for phases 8-11.
- Baseline output requirements for per-phase and grouped totals.
- Out of scope:
- Local target 8-11 profiling.
- Implementation of optimization changes.

## Steps / Checklist
- [x] Map exact 8-11 direct-call ordering and state dependencies.
- [x] Define fixture and warm/cold baseline variants for this track.
- [x] Define output fields needed for hotspot ranking.
- [x] Record findings and open unknowns in story/task notes.

## Deliverables
- Discovery notes for 8-11 baseline design.
- Approved output and fixture baseline contract.

## Discovery Output (2026-02-14)
### Baseline Execution Contract
- Execute conduit 8-11 chain in this exact order:
  - `occurrence_plan`
  - `injection_plan`
  - `patch_maps`
  - `execution_plan`
- Direct-call harness chain (per selected spell in set):
  - `spell.run_phase_occurrence_plan(conduit_id, None)`
  - `spell.run_phase_injection_plan(conduit_id, None)`
  - `spell.run_phase_patch_maps(conduit_id, None)`
  - `spell.run_phase_execution_plan(conduit_id, None)`

### Preconditions
- Require non-empty `conduit_id`.
- Require phase-5 artifacts to exist before 8-11 execution.
- Default baseline scope is full local spell set (matching per-spell production
  plan-phase units).

### Warm/Cold Variants
- `cold_plan_reset`:
  - call `spell._ensure_crafter().clear_phase5_artifacts()` for selected spells
    before run to force phase-5/8-11 rebuild path.
- `warm_plan_reuse`:
  - rerun 8-11 without explicit artifact reset.

### Output Fields for Ranking
- Required summary fields:
  - `spell_count`
  - `group_8_11_total_ms`
  - `phase_occurrence_plan_ms`
  - `phase_injection_plan_ms`
  - `phase_patch_maps_ms`
  - `phase_execution_plan_ms`
  - `resolution_has_errors`
- Recommended execution-plan attribution fields:
  - `execution_plan_step_count`
  - `execution_plan_unique_spell_count`
  - `execution_plan_max_occurrence_depth`
  - `execution_plan_max_dependency_count`
  - `execution_plan_dispatch_route`
- Optional profiler section:
  - `[PROFILE] <label> (sort=<sort>, top=<top>)`
  - printed `pstats` top table.

## Measured Baseline Output (2026-02-14)
- Source artifact:
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt`
- `group_8_11_cold`:
  - `group_8_11_total_ms=51.877`
  - `phase_occurrence_plan_ms=1.992`
  - `phase_injection_plan_ms=1.532`
  - `phase_patch_maps_ms=6.724`
  - `phase_execution_plan_ms=41.63`
  - `execution_plan_dispatch_route=ENGINE`
  - `execution_plan_step_count=17`
  - `execution_plan_unique_spell_count=17`
  - `execution_plan_max_occurrence_depth=8`
  - `execution_plan_max_dependency_count=2`
- `group_8_11_warm`:
  - `group_8_11_total_ms=34.993`
  - `phase_occurrence_plan_ms=8.735`
  - `phase_injection_plan_ms=7.588`
  - `phase_patch_maps_ms=8.844`
  - `phase_execution_plan_ms=9.826`
  - `execution_plan_dispatch_route=ENGINE`
  - `execution_plan_step_count=17`
  - `execution_plan_unique_spell_count=17`
  - `execution_plan_max_occurrence_depth=8`
  - `execution_plan_max_dependency_count=2`
- Warm cProfile sample highlights:
  - `269176 function calls in 0.091 seconds`
  - top cumulative entries include
    `SpellCrafter._capture_phase8_11_codegen_ir`,
    `SpellCrafter._build_phase11_variant_ir_payload`,
    `Spell.run_phase_execution_plan`,
    `Spell.run_phase_patch_maps`,
    `Spell.run_phase_occurrence_plan`,
    `Spell.run_phase_injection_plan`

## Files / Paths Impacted
- `context_compass/stories/2026-02-14_phase_group_8_11_baseline_story.md`
- `context_compass/tasks/2026-02-14_discovery_phase_group_8_11_baseline_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/component -k \"phase and 8_11\"`

## Risks / Rollback Notes
- Risk: baseline misses plan-phase setup behavior used in production.
- Rollback: refine discovery scope and fixture assumptions.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: 8-11 baseline now has cold/warm timings and a warm cProfile sample showing IR capture and phase11 payload build as top cumulative hotspots.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:10-14, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:20-33
  IMPACT: 8-11 track is ranking-ready with both aggregate timings and function-level hotspot indicators.
  NEXT: Use these measured hotspots to draft prioritized optimization candidates in the backlog task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: 8-11 discovery contract is locked with per-spell grouped ordering, explicit cold/warm plan variants, and execution-plan-aware output fields for ranking.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1111, src/melder/spellbook/spellbook_creation_system.py:1701, src/melder/spellbook/spell_crafter/spell_crafter.py:3652, src/melder/spellbook/spell.py:1158, src/melder/spellbook/spell_crafter/spell_crafter.py:665
  IMPACT: Implementation can proceed with deterministic sequence and richer attribution metrics for optimization prioritization.
  NEXT: Propagate this discovery output to story notes and move task to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Phase-11 execution planning updates spell-level execution metrics and the spell facade invalidates creation context after phase-11, while `clear_phase5_artifacts()` resets phase 8-11 artifacts for a cold rerun.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:3652, src/melder/spellbook/spell_crafter/spell_crafter.py:3659, src/melder/spellbook/spell.py:1157, src/melder/spellbook/spell.py:1158, src/melder/spellbook/spell_crafter/spell_crafter.py:665, src/melder/spellbook/spell_crafter/spell_crafter.py:719
  IMPACT: 8-11 baseline variants can be defined as cold (force phase5/8-11 reset) vs warm (reuse current plan artifacts), and output can include execution-plan route metrics for hotspot attribution.
  NEXT: Lock 8-11 discovery output contract block (sequence, variants, output fields) in this task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit 8-11 phases are per-spell units over local spells (empty when no spells), executed in fixed order: occurrence -> injection -> patch_maps -> execution_plan.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1111, src/melder/spellbook/spellbook_creation_system.py:1132, src/melder/spellbook/spellbook_creation_system.py:1150, src/melder/spellbook/spellbook_creation_system.py:1701, src/melder/spellbook/spellbook_creation_system.py:1788, src/melder/spellbook/spellbook_creation_system.py:1512
  IMPACT: Baseline fixture policy should default to full local spell set and include spell-count in reports.
  NEXT: Define warm/cold variants around plan artifact reuse/reset and lock output schema.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit plan phases are registered and executed as one grouped 8-11 chain in creation-system orchestration.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1111, src/melder/spellbook/spellbook_creation_system.py:1121, src/melder/spellbook/spell.py:1067, src/melder/spellbook/spell.py:1140
  IMPACT: Baseline chain can mirror production order while bypassing scheduler overhead in component profiling.
  NEXT: Determine whether default baseline should run one root lineage or full spellbook roots.

## Context / Handoff Summary
Discovery output now defines 8-11 sequence, preconditions, warm/cold variants,
ranking output fields, and measured baseline outputs with cProfile hotspot
signal. Next step is optimization-backlog ranking.
