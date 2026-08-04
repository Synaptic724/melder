# Completed: 2026-05-10T12:04:09Z
# Summary: Superseded by the completed interface wording cleanup across `ispellbook.py`, `ispellsystemstates.py`, and `ispellindex.py`.
# Task: Investigate SpellIndex Interface Contracts

## Metadata
- Task ID: TASK-2026-05-10-investigate-spell-index-interface-contracts
- Story: STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T10:14:03Z
- Updated: 2026-05-10T10:14:03Z

## Objective
Investigate the interface layer that codifies SpellIndex semantics so we can
see where the public/runtime contracts themselves are teaching the system to
think in lineage-first terms.

## Ticket Contract
- ENTRY_GATE: the SpellIndex investigation story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/utilities/interfaces/ispellindex.py`
  - `src/melder/utilities/interfaces/ispellbook.py`
  - `src/melder/utilities/interfaces/ispellsystemstates.py`
  - related small interface files only if directly needed
- DEPENDENCIES:
  - focused SpellIndex search results
- EXIT_GATE: the task notes show where interface language itself may need to
  shift later.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if interface changes would
  imply a wider public contract break than expected.

## Scope Boundaries
- In scope:
  - interface wording
  - interface method naming
  - contract-level SpellIndex semantics
- Out of scope:
  - implementation code changes
  - conduit lineage interfaces

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the interface layer is one of the clearest places where
  wording bias can be frozen into the system.

## Steps / Checklist
- [ ] Re-read the SpellIndex-related interfaces.
- [ ] Record the lineage/index assumptions baked into the interface wording.
- [ ] Record where later contract cleanup would likely be needed.

## Deliverables
- evidence-backed interface-layer SpellIndex note

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-10_investigate_spell_index_interface_contracts_task.md

## Validation
- Not run.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No conduit-lineage drift.

## Notes
- DATETIME: 2026-05-10T10:14:03Z
  TYPE: PLAN
  CLAIM: Even if the core implementation is salvageable, the interface layer
    may still be hard-coding the wrong story. That needs its own pass.
  EVIDENCE:
  - src/melder/utilities/interfaces/ispellindex.py:5-138
  - src/melder/utilities/interfaces/ispellbook.py:14-18
  - src/melder/utilities/interfaces/ispellsystemstates.py:15-18
  IMPACT: Later rename or ownership cleanup will fail if the interface layer
    still teaches the old semantics.
  NEXT: inspect the SpellIndex interface family directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Investigate the interface layer that codifies SpellIndex semantics.
