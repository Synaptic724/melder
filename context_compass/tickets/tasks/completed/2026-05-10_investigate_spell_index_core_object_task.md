# Completed: 2026-05-10T12:04:09Z
# Summary: Superseded by the completed SpellIndex rename slices, which finished the core object wording cleanup directly.
# Task: Investigate SpellIndex Core Object

## Metadata
- Task ID: TASK-2026-05-10-investigate-spell-index-core-object
- Story: STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T10:14:03Z
- Updated: 2026-05-10T10:14:03Z

## Objective
Investigate the core `SpellIndex` object itself to determine what it currently
means:
- lineage authority
- version container
- runtime selection slot
- ownership record

## Ticket Contract
- ENTRY_GATE: the SpellIndex investigation story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/bind/spell_index.py`
  - directly related tests for `SpellIndex`
- DEPENDENCIES:
  - focused SpellIndex search results
- EXIT_GATE: the task notes state what `SpellIndex` actually owns and what
  naming/semantic pressure it creates.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if this file alone already
  forces a broader ownership refactor outside the story boundary.

## Scope Boundaries
- In scope:
  - `SpellIndex` meaning and fields
  - `id` vs `current`
  - ownership fields
- Out of scope:
  - spellbook maps
  - conduit lineage

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: this is the highest-signal starting point in the
  SpellIndex lane.

## Steps / Checklist
- [ ] Re-read `spell_index.py` in detail.
- [ ] Record what `id`, `current`, `_versions`, and owner fields mean.
- [ ] Record where the file itself implies lineage authority versus runtime
      selection behavior.

## Deliverables
- evidence-backed SpellIndex core semantics note

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-10_investigate_spell_index_core_object_task.md

## Validation
- Not run.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No conduit-lineage drift.

## Notes
- DATETIME: 2026-05-10T10:14:03Z
  TYPE: PLAN
  CLAIM: The core object has to be investigated first because every other
    search space inherits its bias from here.
  EVIDENCE:
  - src/melder/spellbook/bind/spell_index.py:9-372
  IMPACT: This task should establish the baseline meaning before downstream
    ownership or terminology tasks try to reinterpret it.
  NEXT: inspect the file and write the first semantics note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Start with the core `SpellIndex` object before investigating downstream use.
