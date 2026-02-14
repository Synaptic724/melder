Completed: 2026-02-14
Summary: Accepted in the phase-testing closure pass; implementation and validation artifacts are captured in this task.

# Task: Discovery Phase Component CProfile Harness

## Metadata
- Task ID: TASK-2026-02-14-discovery-phase-component-cprofile-harness
- Story: STORY-2026-02-14-phase-component-cprofile-harness
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Define the direct-call component profiling harness contract for phase testing,
including toggle schema, fixture rules, and output format.

## Scope Boundaries
- In scope:
- Direct-call phase invocation contract (no scheduler path).
- Toggle matrix for grouped chain execution.
- Output schema for cprofile/timing reporting.
- Out of scope:
- Harness implementation and performance claims.

## Steps / Checklist
- [x] Map direct phase callable entrypoints and required setup state.
- [x] Define toggle matrix for grouped chain execution.
- [x] Define output contract for printed timing/profile sections.
- [x] Link discovery output into story notes and handoff summary.

## Deliverables
- Documented harness contract with explicit no-scheduler requirements.
- Approved toggle matrix and output schema.

## Discovery Output (2026-02-14)
### No-Scheduler Contract
- Harness execution must call spell phase facades directly and must not invoke
  scheduler orchestration paths.
- For phase groups 5+, the harness must provide a non-empty `conduit_id`.

### Toggle Matrix
- `enable_group_1_4_structural` (default: `true`)
- `enable_group_5_7_conduit` (default: `true`)
- `enable_group_5_7_local` (default: `true`)
- `enable_group_8_11_conduit` (default: `true`)
- `enable_profile_stats` (default: `true`)
- `profile_sort` (default: `"cumtime"`)
- `profile_top` (default: `30`)
- `enable_phase_timing_lines` (default: `true`)

### Direct-Call Chains
- Group `1_4_structural`:
  - `spell.run_structural_phases(cancel_event=None)`
- Group `5_7_conduit` (lead-spell frame scope):
  - `lead_spell.run_phase_root_blueprints(conduit_id, None)`
  - `lead_spell.run_phase_system_validation(conduit_id, None)`
  - `lead_spell.run_phase_change_control(conduit_id, None)`
- Group `5_7_local` (target spell scope):
  - `target_spell.run_phase_root_blueprints_local(conduit_id, None)`
  - `target_spell.run_phase_system_validation_local(conduit_id, None)`
  - `target_spell.run_phase_change_control_local(conduit_id, None)`
- Group `8_11_conduit` (per selected spell):
  - `spell.run_phase_occurrence_plan(conduit_id, None)`
  - `spell.run_phase_injection_plan(conduit_id, None)`
  - `spell.run_phase_patch_maps(conduit_id, None)`
  - `spell.run_phase_execution_plan(conduit_id, None)`

### Fixture and Ordering Rules
- Build one deterministic spellbook fixture and select:
  - one lead spell (for conduit 5-7),
  - one target spell (for local 5-7),
  - one selected spell set (for conduit 8-11).
- Preserve prerequisite ordering:
  - run 1-4 before any 5+ chain,
  - run 5 before 6/7,
  - run 5-7 before 8-11.
- Mirror production gating by skipping 8-11 when conduit resolution errors are
  present after 5-7.

### Output Schema
- Summary lines:
  - `Group <group_name> total (ms): <float>`
  - optional per-phase lines:
    - `Phase <phase_name> (ms): <float>`
- Optional cProfile stats block:
  - header:
    - `[PROFILE] <label> (sort=<sort>, top=<top>)`
  - body:
    - `pstats.Stats(...).print_stats(top)` text.

## Files / Paths Impacted
- `context_compass/stories/completed/2026-02-14_phase_component_cprofile_harness_story.md`
- `context_compass/tasks/completed/2026-02-14_discovery_phase_component_cprofile_harness_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/component -k phase`

## Risks / Rollback Notes
- Risk: contract misses hidden setup requirements.
- Rollback: revise discovery output before implementation.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed
## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Harness contract has now been executed successfully via the implementation task, and baseline output artifact confirms all four groups emit standardized profile lines.
  EVIDENCE: context_compass/tasks/completed/2026-02-14_implement_phase_component_cprofile_harness_task.md:3-3, context_compass/artifacts/2026-02-14_phase_component_cprofile_harness_baseline_output.txt:5-13
  IMPACT: Discovery contract is validated against real run output, not only source inspection.
  NEXT: Use the artifact as canonical evidence in baseline and backlog tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Harness contract is locked to four toggled groups (`1-4`, `5-7 conduit`, `5-7 local`, `8-11 conduit`) with direct spell facade invocation and production-order gating.
  EVIDENCE: src/melder/spellbook/spell.py:1270, src/melder/spellbook/spell.py:1011, src/melder/spellbook/spell.py:1160, src/melder/spellbook/spellbook_creation_system.py:748, src/melder/spellbook/spellbook_creation_system.py:753, src/melder/spellbook/spellbook_creation_system.py:1666, src/melder/spellbook/spellbook_creation_system.py:1701, src/melder/spellbook/spellbook_creation_system.py:1788
  IMPACT: Implementation can proceed without ambiguity on ordering, scope shape, and gating semantics.
  NEXT: Propagate this discovery output into the parent story note and move task status to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Existing hotpath profiling utilities already standardize printable output with a `[PROFILE]` header (`label/sort/top`) plus optional per-phase timing lines in milliseconds.
  EVIDENCE: benchmarks/testing_other_di/test_melder_hotpath_profiles.py:149, benchmarks/testing_other_di/test_melder_hotpath_profiles.py:153, benchmarks/testing_other_di/test_melder_hotpath_profiles.py:219, benchmarks/testing_other_di/test_melder_hotpath_profiles.py:221
  IMPACT: The phase component harness can reuse this reporting style instead of inventing a new format.
  NEXT: Define harness output sections as `summary(ms)` + optional `[PROFILE]` pstats block with configurable `sort/top`.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit-wide foundational phases (5-7) are lead-spell frame-scoped units, while conduit plan phases (8-11) are per-spell units.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1666, src/melder/spellbook/spellbook_creation_system.py:1821, src/melder/spellbook/spellbook_creation_system.py:1860, src/melder/spellbook/spellbook_creation_system.py:1701, src/melder/spellbook/spellbook_creation_system.py:1788
  IMPACT: The component harness must preserve this shape split to avoid profiling a non-production execution geometry.
  NEXT: Encode chain definitions so 5-7 conduit runs one lead spell and 8-11 conduit iterates the selected spell set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: `Spell` exposes direct per-phase facades for phases 5-11, but grouped 5-7 and 8-11 sequencing is currently encoded in `SpellbookCreationSystem` scheduler registration helpers.
  EVIDENCE: src/melder/spellbook/spell.py:1011, src/melder/spellbook/spell.py:1067, src/melder/spellbook/spell.py:1160, src/melder/spellbook/spellbook_creation_system.py:1063, src/melder/spellbook/spellbook_creation_system.py:1111
  IMPACT: Component harness design should group calls in harness code (not rely on a missing grouped spell facade) while preserving production order.
  NEXT: Define the explicit harness toggle matrix and ordered direct-call chains for 1-4, 5-7 conduit-wide, 5-7 local, and 8-11.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Direct phase facades are available on `Spell` and can be sequenced without scheduler APIs.
  EVIDENCE: src/melder/spellbook/spell.py:1270, src/melder/spellbook/spell.py:1011, src/melder/spellbook/spell.py:1160
  IMPACT: Harness can isolate phase logic from scheduling overhead.
  NEXT: Define fixture state prerequisites for each phase group.

## Context / Handoff Summary
Discovery output now defines the no-scheduler contract, toggle matrix, direct
call chains, fixture/ordering rules, and profile output schema. Next step is to
confirm acceptance, then begin harness implementation under the parent story.
