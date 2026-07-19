# Completed: 2026-05-10T12:04:09Z
# Summary: Superseded by the completed SpellSystemStates rename slice, which resolved the coupling vocabulary directly.
# Task: Investigate SpellSystemStates SpellIndex Coupling

## Metadata
- Task ID: TASK-2026-05-10-investigate-spell-system-states-spell-index-coupling
- Story: STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T10:14:03Z
- Updated: 2026-05-10T10:14:03Z

## Objective
Investigate how tightly `SpellSystemStates` is coupled to `SpellIndex`
terminology and semantics, especially around registration, dirtiness, and
dependency tracking.

## Ticket Contract
- ENTRY_GATE: the SpellIndex investigation story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
  - directly related interface references if needed
- DEPENDENCIES:
  - focused SpellIndex search results
- EXIT_GATE: the task notes state whether SpellSystemStates really needs
  lineage wording here or is inheriting it from SpellIndex by convention.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if this surface proves too
  mutation-critical to classify safely without a wider design decision.

## Scope Boundaries
- In scope:
  - `register_lineage`
  - `unregister_lineage`
  - `update_dependencies`
  - dirty-lineage semantics
- Out of scope:
  - conduit lineage
  - creation-gate controller

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: SpellSystemStates is one of the core non-spellbook places
  where SpellIndex language becomes system truth.

## Steps / Checklist
- [ ] Re-read SpellSystemStates SpellIndex-related methods.
- [ ] Record whether the state model depends on lineage semantics or only on a
      stable spell-index key.
- [ ] Record any naming/ownership pressure clearly.

## Deliverables
- evidence-backed SpellSystemStates coupling note

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-10_investigate_spell_system_states_spell_index_coupling_task.md

## Validation
- Not run.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No conduit-lineage drift.

## Notes
- DATETIME: 2026-05-10T10:14:03Z
  TYPE: PLAN
  CLAIM: SpellSystemStates is the strongest non-spellbook authority surface for
    SpellIndex, so it needs its own investigation instead of being folded into
    the spellbook task.
  EVIDENCE:
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:206-287
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:418-576
  - src/melder/aether/dev_ops/spell_system_states/spell_system_states.py:682-706
  IMPACT: This task will tell us whether “lineage” here is conceptually real
    or just SpellIndex vocabulary leaking upward.
  NEXT: inspect the registration/dependency/dirty-state paths directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Investigate how SpellSystemStates depends on SpellIndex semantics.
