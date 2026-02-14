# Task: Discovery Phase Group 5-7 Local Baseline

## Metadata
- Task ID: TASK-2026-02-14-discovery-phase-group-5-7-local-baseline
- Story: STORY-2026-02-14-phase-group-5-7-local-baseline
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Define a direct-call baseline for target-local foundational phases 5-7.

## Scope Boundaries
- In scope:
- Local 5/6/7 sequence, target spell prerequisites, and profile-output contract.
- Out of scope:
- Conduit-wide 5-7 and local 8-11.

## Steps / Checklist
- [x] Map target-local 5-7 flow and required target fixture state.
- [x] Define direct-call sequence and target selection policy.
- [x] Define profile-output fields for local 5-7 track.
- [x] Record unknowns and evidence in task/story notes.

## Deliverables
- Discovery contract for local 5-7 baseline profile track.
- Approved fixture/target policy for this track.

## Discovery Output (2026-02-14)
### Baseline Execution Contract
- Local foundational chain order:
  - `root_blueprints_local`
  - `system_validation_local`
  - `change_control_local`
- Direct-call harness chain:
  - `target_spell.run_phase_root_blueprints_local(conduit_id, None)`
  - `target_spell.run_phase_system_validation_local(conduit_id, None)`
  - `target_spell.run_phase_change_control_local(conduit_id, None)`

### Preconditions and Target Policy
- Require non-empty `conduit_id`.
- Require explicit non-null `target_spell`.
- Default target policy:
  - choose one deterministic target spell from fixture (stable id/name).
- Keep target id and fixture registration order stable across samples.

### Scoped-Work Semantics
- Although invocation is target-local, phase-5 local work spans the target’s
  dependency closure and updates scoped spell crafters.
- Local baseline reports must include scoped size indicators so measured cost is
  attributable to closure size, not only target identity.

### Output Fields for Ranking
- Required summary fields:
  - `target_spell_id`
  - `scoped_spell_count`
  - `scoped_root_count`
  - `group_5_7_local_total_ms`
  - `phase_root_blueprints_local_ms`
  - `phase_system_validation_local_ms`
  - `phase_change_control_local_ms`
  - `resolution_has_errors`
- Optional profiler section:
  - `[PROFILE] <label> (sort=<sort>, top=<top>)`
  - printed `pstats` top table.

## Measured Baseline Output (2026-02-14)
- Source artifact:
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt`
- `group_5_7_local`:
  - `group_5_7_local_total_ms=5.531`
  - `phase_root_blueprints_local_ms=5.049`
  - `phase_system_validation_local_ms=0.468`
  - `phase_change_control_local_ms=0.014`
  - `scoped_spell_count=17`
  - `scoped_root_count=1`
  - `resolution_has_errors=False`

## Files / Paths Impacted
- `context_compass/stories/2026-02-14_phase_group_5_7_local_baseline_story.md`
- `context_compass/tasks/2026-02-14_discovery_phase_group_5_7_local_baseline_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/component -k \"phase and 5_7 and local\"`

## Risks / Rollback Notes
- Risk: local scope requirements are under-specified.
- Rollback: expand discovery to include setup/state prerequisites before implementation.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Target-local 5-7 baseline measurement is now captured with scoped-size fields and per-phase timings.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:9-9
  IMPACT: Local 5-7 track is now directly comparable to conduit-wide 5-7 for ranking decisions.
  NEXT: Use scoped-size metrics when evaluating local-phase optimization candidates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Local 5-7 discovery contract is locked to explicit target-scoped direct calls with deterministic target policy and scoped-size reporting fields.
  EVIDENCE: src/melder/spellbook/spell.py:1040, src/melder/spellbook/spell.py:1189, src/melder/spellbook/spell.py:1244, src/melder/spellbook/spellbook_creation_system.py:792, src/melder/spellbook/spell_crafter/spell_crafter.py:3284
  IMPACT: Implementation can proceed with clear local-scope semantics and ranking-ready outputs separated from conduit-wide 5-7.
  NEXT: Propagate discovery output to story notes and move this task to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Local phase-5 execution is target-rooted but scopes to the target’s dependency closure and attaches phase-5 artifacts across all scoped spells.
  EVIDENCE: src/melder/spellbook/spell_crafter/spell_crafter.py:3254, src/melder/spellbook/spell_crafter/spell_crafter.py:3284, src/melder/spellbook/spell_crafter/spell_crafter.py:3299, src/melder/spellbook/spell_crafter/spell_crafter.py:3232
  IMPACT: Local 5-7 baseline output should capture scoped spell/root counts, not only target spell id, to explain cost variation.
  NEXT: Finalize discovery output with target-selection policy plus scoped-size reporting fields.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Local 5-7 conduit flow requires both non-empty `conduit_id` and non-null `target_spell`, then executes local foundational phases as one target-scoped chain.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:792, src/melder/spellbook/spellbook_creation_system.py:795, src/melder/spellbook/spellbook_creation_system.py:800, src/melder/spellbook/spellbook_creation_system.py:1206
  IMPACT: Baseline fixture policy must always specify explicit target spell selection and conduit scope.
  NEXT: Lock target selection policy and output schema for local 5-7 discovery contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Local foundational phases are explicit spell facades: root_blueprints_local, system_validation_local, and change_control_local.
  EVIDENCE: src/melder/spellbook/spell.py:1040, src/melder/spellbook/spell.py:1189, src/melder/spellbook/spell.py:1244
  IMPACT: Direct component profiling can target local 5-7 without scheduler wiring.
  NEXT: Define the minimal reproducible target-spell fixture for this track.

## Context / Handoff Summary
Discovery output now defines local 5-7 sequence, target policy, scoped-work
semantics, ranking output fields, and measured baseline output. Next step is
optimization-backlog ranking.
