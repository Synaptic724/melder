# Task: Discovery Phase Group 5-7 Conduit Baseline

## Metadata
- Task ID: TASK-2026-02-14-discovery-phase-group-5-7-conduit-baseline
- Story: STORY-2026-02-14-phase-group-5-7-conduit-baseline
- Status: ready
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
- [ ] Map conduit-wide 5-7 sequence from source and identify required preconditions.
- [ ] Define direct-call baseline fixture setup and conduit_id handling.
- [ ] Define per-phase and grouped output fields.
- [ ] Record evidence/unknowns in task/story notes.

## Deliverables
- Discovery contract for conduit-wide 5-7 baseline.
- Approved baseline output schema.

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
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit-wide foundational phases register root_blueprints, system_validation, and change_control in that order.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1084, src/melder/spellbook/spellbook_creation_system.py:1090, src/melder/spellbook/spellbook_creation_system.py:1096
  IMPACT: Baseline chain should preserve this order when executed directly.
  NEXT: Specify direct-call equivalent using spell facades and conduit_id setup.

## Context / Handoff Summary
Task is ready to define conduit-wide phase 5-7 baseline profiling contract.
