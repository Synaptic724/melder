# Task: Discovery Phase Group 5-7 Conduit Baseline

## Metadata
- Task ID: TASK-2026-02-14-discovery-phase-group-5-7-conduit-baseline
- Story: STORY-2026-02-14-phase-group-5-7-conduit-baseline
- Status: review
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Define the conduit-wide foundational 5-7 direct-call profiling baseline.

## Scope Boundaries
- In scope:
- Conduit-wide 5/6/7 call sequence and fixture setup requirements.
- Baseline output requirements for 5-7 grouped profiling.
- Out of scope:
- Local 5-7 profiling and phase implementation changes.

## Steps / Checklist
- [x] Map conduit-wide 5-7 sequence from source and identify required preconditions.
- [x] Define direct-call baseline fixture setup and conduit_id handling.
- [x] Define per-phase and grouped output fields.
- [x] Record evidence/unknowns in task/story notes.

## Deliverables
- Discovery contract for conduit-wide 5-7 baseline.
- Approved baseline output schema.

## Discovery Output (2026-02-14)
### Baseline Execution Contract
- Run conduit-wide foundational chain in this exact order:
  - `root_blueprints`
  - `system_validation`
  - `change_control`
- Direct-call harness chain (no scheduler):
  - `lead_spell.run_phase_root_blueprints(conduit_id, None)`
  - `lead_spell.run_phase_system_validation(conduit_id, None)`
  - `lead_spell.run_phase_change_control(conduit_id, None)`

### Preconditions
- Fixture must contain at least one local spell (otherwise production factories
  return empty work for conduit-wide 5-7).
- `conduit_id` must be non-empty to align with conduit resolution entry
  contracts and change-control scoping.
- Keep deterministic lead-spell selection by preserving fixture registration
  order.

### Fixture Policy
- Default fixture scope: full spellbook populated, but 5-7 execution uses the
  lead spell as the frame-scoped phase host.
- Optional diagnostic variant:
  - clear phase-5 artifacts on selected spells before run when forcing full
    phase-5 rebuild (`spell._ensure_crafter().clear_phase5_artifacts()`).

### Output Fields for Ranking
- Required summary fields:
  - `spell_count`
  - `lead_spell_id`
  - `group_5_7_total_ms`
  - `phase_root_blueprints_ms`
  - `phase_system_validation_ms`
  - `phase_change_control_ms`
  - `resolution_has_errors`
- Optional profiler section:
  - `[PROFILE] <label> (sort=<sort>, top=<top>)`
  - printed `pstats` top table.

## Measured Baseline Output (2026-02-14)
- Source artifact:
  - `context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt`
- `group_5_7_conduit_cold`:
  - `group_5_7_total_ms=4.971`
  - `phase_root_blueprints_ms=4.429`
  - `phase_system_validation_ms=0.533`
  - `phase_change_control_ms=0.01`
  - `resolution_has_errors=False`
  - `spell_count=17`
- `group_5_7_conduit_warm`:
  - `group_5_7_total_ms=5.577`
  - `phase_root_blueprints_ms=5.095`
  - `phase_system_validation_ms=0.474`
  - `phase_change_control_ms=0.007`
  - `resolution_has_errors=False`
  - `spell_count=17`

## Files / Paths Impacted
- `context_compass/stories/2026-02-14_phase_group_5_7_conduit_baseline_story.md`
- `context_compass/tasks/2026-02-14_discovery_phase_group_5_7_conduit_baseline_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/component -k \"phase and 5_7 and conduit\"`

## Risks / Rollback Notes
- Risk: missing frame-scoped lead-spell assumptions.
- Rollback: expand discovery to capture lead-spell coupling explicitly.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Conduit-wide 5-7 measurements are now captured for cold and warm phase-5 variants, with phase-level timing and resolution error state.
  EVIDENCE: context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:7-8
  IMPACT: Conduit 5-7 track is ready for optimization backlog ranking inputs.
  NEXT: Correlate warm-vs-cold deltas in backlog ranking notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Conduit-wide 5-7 discovery contract is locked to a lead-spell direct-call chain with deterministic fixture ordering, non-empty conduit scope, and ranking-ready output fields including `resolution_has_errors`.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1063, src/melder/spellbook/spellbook_creation_system.py:1666, src/melder/spellbook/spellbook_creation_system.py:1821, src/melder/spellbook/spellbook_creation_system.py:748, src/melder/spellbook/spell_crafter/spell_crafter.py:665
  IMPACT: Implementation can proceed without ambiguity on sequencing, fixture shape, or reporting contract.
  NEXT: Propagate this discovery output to story notes and move task to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Production conduit flow executes 5-7 first and conditionally skips 8-11 when conduit resolution errors are present.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:742, src/melder/spellbook/spellbook_creation_system.py:748, src/melder/spellbook/spellbook_creation_system.py:752, src/melder/spellbook/spellbook_creation_system.py:756
  IMPACT: 5-7 baseline output should include a `resolution_has_errors` flag to preserve gating semantics used by full conduit orchestration.
  NEXT: Finalize discovery output contract (fixture policy, conduit_id rule, output fields) in this task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit-wide phases 5-7 use one lead spell (`next(iter(spellbook._spells.values()))`) and return no units when there are no local spells.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1663, src/melder/spellbook/spellbook_creation_system.py:1666, src/melder/spellbook/spellbook_creation_system.py:1821, src/melder/spellbook/spellbook_creation_system.py:1860
  IMPACT: Baseline fixture must include at least one local spell and preserve deterministic lead-spell selection for repeatability.
  NEXT: Lock fixture policy and conduit_id preconditions in discovery output.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit-wide foundational phases register root_blueprints, system_validation, and change_control in that order.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1084, src/melder/spellbook/spellbook_creation_system.py:1090, src/melder/spellbook/spellbook_creation_system.py:1096
  IMPACT: Baseline chain should preserve this order when executed directly.
  NEXT: Specify direct-call equivalent using spell facades and conduit_id setup.

## Context / Handoff Summary
Discovery output now defines conduit-wide 5-7 sequence, preconditions, fixture
policy, hotspot-ranking output fields, and measured baseline outputs for cold
and warm variants. Next step is optimization-backlog ranking.
