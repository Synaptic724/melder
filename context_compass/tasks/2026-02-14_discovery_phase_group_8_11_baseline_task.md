# Task: Discovery Phase Group 8-11 Baseline

## Metadata
- Task ID: TASK-2026-02-14-discovery-phase-group-8-11-baseline
- Story: STORY-2026-02-14-phase-group-8-11-baseline
- Status: ready
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
- [ ] Map exact 8-11 direct-call ordering and state dependencies.
- [ ] Define fixture and warm/cold baseline variants for this track.
- [ ] Define output fields needed for hotspot ranking.
- [ ] Record findings and open unknowns in story/task notes.

## Deliverables
- Discovery notes for 8-11 baseline design.
- Approved output and fixture baseline contract.

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
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Conduit plan phases are registered and executed as one grouped 8-11 chain in creation-system orchestration.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:1111, src/melder/spellbook/spellbook_creation_system.py:1121, src/melder/spellbook/spell.py:1067, src/melder/spellbook/spell.py:1140
  IMPACT: Baseline chain can mirror production order while bypassing scheduler overhead in component profiling.
  NEXT: Determine whether default baseline should run one root lineage or full spellbook roots.

## Context / Handoff Summary
Task is ready for discovery on phase 8-11 baseline path and reporting format.
