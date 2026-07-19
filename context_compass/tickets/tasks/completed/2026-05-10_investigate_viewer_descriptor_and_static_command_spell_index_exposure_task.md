# Completed: 2026-05-10T12:04:09Z
# Summary: Superseded by the completed outward AR/viewer/static-command rename slice, which resolved this exposure surface directly.
# Task: Investigate Viewer, Descriptor, And Static Command SpellIndex Exposure

## Metadata
- Task ID: TASK-2026-05-10-investigate-viewer-descriptor-and-static-command-spell-index-exposure
- Story: STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-05-10T10:14:03Z
- Updated: 2026-05-10T10:14:03Z

## Objective
Investigate the AR/viewer/descriptor/static-command surfaces that expose
`spell_index_id` so we can see how much of the current external/runtime
language is already tied to SpellIndex wording.

## Ticket Contract
- ENTRY_GATE: the SpellIndex investigation story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/frame_descriptor/`
  - `src/melder/aether/nexus/rift/frame_viewer/`
  - `src/melder/aether/nexus/rift/command_system/static_command_system.py`
  - directly related tests only as evidence
- DEPENDENCIES:
  - focused SpellIndex search results
- EXIT_GATE: the task notes explain how visible `spell_index_id` already is in
  AR/viewer/descriptor surfaces and what that implies later.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if these external surfaces make
  any future terminology cleanup too breaking to discuss casually.

## Scope Boundaries
- In scope:
  - descriptor `spell_index_id`
  - viewer lineage/grouping helpers
  - static-command spell-index lookup
- Out of scope:
  - conduit lineage
  - broad Nexus redesign

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: viewer/descriptor/static-command exposure is the clearest
  outward-facing SpellIndex search space.

## Steps / Checklist
- [ ] Re-read the descriptor, viewer, and static-command SpellIndex surfaces.
- [ ] Record how SpellIndex wording is exposed outward.
- [ ] Record what later cleanup pressure that creates.

## Deliverables
- evidence-backed AR/viewer/descriptor SpellIndex exposure note

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-10_investigate_viewer_descriptor_and_static_command_spell_index_exposure_task.md

## Validation
- Not run.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No conduit-lineage drift.

## Notes
- DATETIME: 2026-05-10T10:14:03Z
  TYPE: PLAN
  CLAIM: This search space matters because `spell_index_id` is already part of
    descriptor and viewer vocabulary. If that language is wrong, it is no
    longer an internal-only issue.
  EVIDENCE:
  - focused_search_result: dense `spell_index_id` hit cluster under descriptor,
    viewer, static-command, and AR-facing tests
  IMPACT: Later terminology cleanup needs to know exactly how external these
    spell-index labels already are.
  NEXT: inspect the AR/viewer/descriptor surfaces directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Investigate outward-facing SpellIndex exposure in AR/viewer/descriptor surfaces.
