# Task: Discovery Phase Component CProfile Harness

## Metadata
- Task ID: TASK-2026-02-14-discovery-phase-component-cprofile-harness
- Story: STORY-2026-02-14-phase-component-cprofile-harness
- Status: ready
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
- [ ] Map direct phase callable entrypoints and required setup state.
- [ ] Define toggle matrix for grouped chain execution.
- [ ] Define output contract for printed timing/profile sections.
- [ ] Link discovery output into story notes and handoff summary.

## Deliverables
- Documented harness contract with explicit no-scheduler requirements.
- Approved toggle matrix and output schema.

## Files / Paths Impacted
- `context_compass/stories/2026-02-14_phase_component_cprofile_harness_story.md`
- `context_compass/tasks/2026-02-14_discovery_phase_component_cprofile_harness_task.md`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/component -k phase`

## Risks / Rollback Notes
- Risk: contract misses hidden setup requirements.
- Rollback: revise discovery output before implementation.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Direct phase facades are available on `Spell` and can be sequenced without scheduler APIs.
  EVIDENCE: src/melder/spellbook/spell.py:1270, src/melder/spellbook/spell.py:1011, src/melder/spellbook/spell.py:1160
  IMPACT: Harness can isolate phase logic from scheduling overhead.
  NEXT: Define fixture state prerequisites for each phase group.

## Context / Handoff Summary
Task is ready to begin discovery for the component cprofile harness contract.
