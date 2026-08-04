# Completed: 2026-05-10T12:04:09Z
# Summary: Superseded by the completed Spellbook/interface rename slice, which resolved the ownership-wording surface directly.
# Task: Investigate Spellbook SpellIndex Ownership

## Metadata
- Task ID: TASK-2026-05-10-investigate-spellbook-spell-index-ownership
- Story: STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T10:14:03Z
- Updated: 2026-05-10T10:14:03Z

## Objective
Investigate how `Spellbook` currently treats `SpellIndex` so we can determine
where spellbook is acting like a registration owner versus where it is acting
like lineage authority.

## Ticket Contract
- ENTRY_GATE: the SpellIndex investigation story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spellbook.py`
  - local and contracted SpellIndex map semantics only
- DEPENDENCIES:
  - focused SpellIndex search results
- EXIT_GATE: the task notes make the spellbook ownership bias explicit.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if spellbook semantics are too
  intertwined to investigate without immediately widening into runtime changes.

## Scope Boundaries
- In scope:
  - `_spells`
  - `_lookup_spells`
  - contracted spell maps
  - spell_id cache relationships
- Out of scope:
  - conduit lineage
  - mutation redesign

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: spellbook is one of the strongest places where SpellIndex
  appears to imply ownership.

## Steps / Checklist
- [ ] Re-read spellbook SpellIndex maps and helper paths.
- [ ] Record where Spellbook treats SpellIndex as identity, container, or
      authority.
- [ ] Record where later rename/ownership cleanup pressure is coming from.

## Deliverables
- evidence-backed spellbook/SpellIndex ownership note

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-10_investigate_spellbook_spell_index_ownership_task.md

## Validation
- Not run.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No conduit-lineage drift.

## Notes
- DATETIME: 2026-05-10T10:14:03Z
  TYPE: PLAN
  CLAIM: Spellbook is the strongest downstream ownership surface after the core
    object itself, because its maps and lookup helpers are where `SpellIndex`
    starts to feel spellbook-owned.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:198-209
  - src/melder/spellbook/spellbook.py:959-1147
  - src/melder/spellbook/spellbook.py:2478-2574
  IMPACT: This task should explain whether that ownership is real or just a
    container/registration bias.
  NEXT: inspect the map and helper surfaces carefully.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Investigate spellbook-side SpellIndex ownership and lookup semantics.
