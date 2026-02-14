# Task: Discovery Phase Group 5-7 Local Baseline

## Metadata
- Task ID: TASK-2026-02-14-discovery-phase-group-5-7-local-baseline
- Story: STORY-2026-02-14-phase-group-5-7-local-baseline
- Status: ready
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
- [ ] Map target-local 5-7 flow and required target fixture state.
- [ ] Define direct-call sequence and target selection policy.
- [ ] Define profile-output fields for local 5-7 track.
- [ ] Record unknowns and evidence in task/story notes.

## Deliverables
- Discovery contract for local 5-7 baseline profile track.
- Approved fixture/target policy for this track.

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
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Local foundational phases are explicit spell facades: root_blueprints_local, system_validation_local, and change_control_local.
  EVIDENCE: src/melder/spellbook/spell.py:1040, src/melder/spellbook/spell.py:1189, src/melder/spellbook/spell.py:1244
  IMPACT: Direct component profiling can target local 5-7 without scheduler wiring.
  NEXT: Define the minimal reproducible target-spell fixture for this track.

## Context / Handoff Summary
Task is ready to define local 5-7 direct-call profile baseline behavior.
