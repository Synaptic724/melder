# Task: Discovery Phase Group 1-4 Baseline

## Metadata
- Task ID: TASK-2026-02-14-discovery-phase-group-1-4-baseline
- Story: STORY-2026-02-14-phase-group-1-4-baseline
- Status: ready
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
- [ ] Map exact 1-4 direct call ordering and state dependencies.
- [ ] Define fixture and warm/cold baseline variants for this track.
- [ ] Define output fields needed for hotspot ranking.
- [ ] Record findings and open unknowns in story/task notes.

## Deliverables
- Discovery notes for 1-4 baseline design.
- Approved output and fixture baseline contract.

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
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Canonical direct structural chain is requirements -> symbolic_graph -> local_frame -> validation.
  EVIDENCE: src/melder/spellbook/spell.py:1294, src/melder/spellbook/spell.py:1297
  IMPACT: Baseline chain can follow existing spell-level structural order.
  NEXT: Determine whether baseline iterates one spell or all spellbook spells.

## Context / Handoff Summary
Task is ready for discovery on phase 1-4 baseline path and reporting format.
