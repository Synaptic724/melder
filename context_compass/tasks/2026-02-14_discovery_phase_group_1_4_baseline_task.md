# Task: Discovery Phase Group 1-4 Baseline

## Metadata
- Task ID: TASK-2026-02-14-discovery-phase-group-1-4-baseline
- Story: STORY-2026-02-14-phase-group-1-4-baseline
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Define the baseline direct-call profiling contract for structural phases 1-4.

## Scope Boundaries
- In scope:
- Sequence and fixture requirements for phases 1-4.
- Baseline output requirements for per-phase and grouped totals.
- Out of scope:
- Implementation of optimization changes.

## Steps / Checklist
- [x] Map exact 1-4 direct call ordering and state dependencies.
- [x] Define fixture and warm/cold baseline variants for this track.
- [x] Define output fields needed for hotspot ranking.
- [x] Record findings and open unknowns in story/task notes.

## Deliverables
- Discovery notes for 1-4 baseline design.
- Approved output and fixture baseline contract.

## Discovery Output (2026-02-14)
### Baseline Execution Contract
- 1-4 baseline must execute the canonical structural order:
  - `requirements -> symbolic_graph -> local_frame -> validation`.
- Default baseline scope is full local spell set (per-spell structural runs),
  matching production structural scheduler shape.
- Optional diagnostic slice may profile a single selected spell, but it is not
  the primary baseline.

### Fixture Policy
- Build one deterministic spellbook fixture and keep spell registration order
  stable for repeatability.
- Select two fixture scopes:
  - `full_spellbook` (default)
  - `single_spell` (diagnostic)
- Reuse a stable spell-id list for repeated samples.

### Warm/Cold Variants
- `cold_reset`:
  - call `spell._ensure_crafter().cleanup_phase_artifacts()` on selected spells
    before each measured run.
  - this clears phase 1-4 artifacts and validation cache fields.
- `warm_reuse`:
  - rerun without phase-artifact cleanup between samples to capture retained
    structural state behavior.

### Output Fields for Ranking
- Required summary fields:
  - `scope` (`full_spellbook` | `single_spell`)
  - `variant` (`cold_reset` | `warm_reuse`)
  - `spell_count`
  - `group_total_ms`
  - `phase_requirements_ms`
  - `phase_symbolic_graph_ms`
  - `phase_local_frame_ms`
  - `phase_validation_ms`
- Optional profiler block:
  - `[PROFILE] <label> (sort=<sort>, top=<top>)`
  - printed `pstats` top table.
- Error discipline:
  - record and fail run on broken spells (same structural contract as
    production structural pipeline).

## Measured Baseline Output (2026-02-14)
- Source artifact:
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt`
- `group_1_4_cold`:
  - `group_1_4_total_ms=2.716`
  - `phase_requirements_ms=0.444`
  - `phase_symbolic_graph_ms=0.139`
  - `phase_local_frame_ms=1.063`
  - `phase_validation_ms=1.07`
  - `spell_count=17`
  - `broken_spell_count=0`
- `group_1_4_warm`:
  - `group_1_4_total_ms=2.21`
  - `phase_requirements_ms=0.534`
  - `phase_symbolic_graph_ms=0.144`
  - `phase_local_frame_ms=0.763`
  - `phase_validation_ms=0.77`
  - `spell_count=17`
  - `broken_spell_count=0`

## Files / Paths Impacted
- `context_compass/stories/2026-02-14_phase_group_1_4_baseline_story.md`
- `context_compass/tasks/2026-02-14_discovery_phase_group_1_4_baseline_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/component -k \"phase and 1_4\"`

## Risks / Rollback Notes
- Risk: baseline misses setup behavior used in production.
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
  CLAIM: 1-4 baseline measurements are now captured for both cold and warm variants with full per-phase timing breakdown and zero broken spells.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:5-6
  IMPACT: Structural baseline track is now evidence-complete for ranking inputs.
  NEXT: Feed these measurements into the optimization-backlog ranking task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: 1-4 discovery contract is locked: default full-spellbook baseline, optional single-spell diagnostic slice, and explicit `cold_reset`/`warm_reuse` variants with per-phase timing output fields.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:617, src/melder/spellbook/spellbook_creation_system.py:1542, src/melder/spellbook/spellbook_creation_system.py:1525, src/melder/spellbook/spell_crafter/spell_crafter.py:595, src/melder/spellbook/spell_crafter/spell_crafter.py:2910, src/melder/spellbook/spell.py:1294
  IMPACT: Implementation can proceed with deterministic scope, variant semantics, and ranking-ready output schema.
  NEXT: Propagate this discovery output into the parent story notes and move the task to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: `cleanup_phase_artifacts()` clears Phase 1-4 artifacts and validation cache fields, while `run_phase_validation()` can fast-return when prior phase-4 result is still valid.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:595, src/melder/spellbook/spell_crafter/spell_crafter.py:638, src/melder/spellbook/spell_crafter/spell_crafter.py:642, src/melder/spellbook/spell_crafter/spell_crafter.py:2910, src/melder/spellbook/spell_crafter/spell_crafter.py:2914
  IMPACT: Warm/cold baseline variants can be defined deterministically: cold = force artifact reset before run; warm = rerun without reset to capture cache-retention behavior.
  NEXT: Lock the 1-4 discovery output block (sequence, fixture variants, output fields) in this task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Production structural orchestration executes phases 1-4 as per-spell units across `spellbook._spells`, so the default 1-4 baseline should profile full local spell set rather than a single spell.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:617, src/melder/spellbook/spellbook_creation_system.py:640, src/melder/spellbook/spellbook_creation_system.py:1542, src/melder/spellbook/spellbook_creation_system.py:1617, src/melder/spellbook/spellbook_creation_system.py:1525
  IMPACT: Baseline fixture policy should define full-spellbook run as canonical and single-spell run as optional diagnostic slice.
  NEXT: Define warm/cold variants based on Phase 1-4 artifact retention vs cleanup semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Canonical direct structural chain is requirements -> symbolic_graph -> local_frame -> validation.
  EVIDENCE: src/melder/spellbook/spell.py:1294, src/melder/spellbook/spell.py:1297
  IMPACT: Baseline chain can follow existing spell-level structural order.
  NEXT: Determine whether baseline iterates one spell or all spellbook spells.

## Context / Handoff Summary
Discovery output now defines sequence, fixture scope policy, warm/cold variants,
ranking output fields, and measured baseline outputs for the 1-4 track. Next
step is to apply these measurements in optimization-backlog ranking.
