# Completed: 2026-05-10T12:04:09Z
# Summary: Superseded by the completed internal rename slices; no separate remaining SpellCrafter-specific SpellIndex wording work was needed in this tranche.
# Task: Investigate SpellCrafter And Validation SpellIndex Usage

## Metadata
- Task ID: TASK-2026-05-10-investigate-spell-crafter-and-validation-spell-index-usage
- Story: STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T10:14:03Z
- Updated: 2026-05-10T10:14:03Z

## Objective
Investigate how SpellIndex is used across spell-crafter and validation paths so
we can tell which uses are genuinely about version/current selection and which
are carrying lineage language by inertia.

## Ticket Contract
- ENTRY_GATE: the SpellIndex investigation story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/spell_crafter/**`
  - validation strategy files directly tied to SpellIndex usage
- DEPENDENCIES:
  - focused SpellIndex search results
- EXIT_GATE: the task notes separate structural/current-version uses from
  lineage-authority uses in spell-crafter/validation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if this search space is too
  broad and needs further subdivision before useful investigation can happen.

## Scope Boundaries
- In scope:
  - `spell.spell_index.current`
  - `spell.spell_index.id`
  - SpellIndex-keyed maps and notes inside spell-crafter/validation
- Out of scope:
  - full mutation research semantics
  - conduit lineage

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: spell-crafter and validation are one of the largest
  downstream semantic clusters for SpellIndex.

## Steps / Checklist
- [ ] Re-read the highest-signal spell-crafter and validation SpellIndex call sites.
- [ ] Record which uses are current-version mechanics versus lineage semantics.
- [ ] Record any terminology cleanup pressure.

## Deliverables
- evidence-backed spell-crafter/validation SpellIndex note

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-10_investigate_spell_crafter_and_validation_spell_index_usage_task.md

## Validation
- Not run.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No conduit-lineage drift.

## Notes
- DATETIME: 2026-05-10T10:14:03Z
  TYPE: PLAN
  CLAIM: Spell-crafter and validation are a major search space because they use
    both `spell.spell_index.current` and `spell.spell_index.id` repeatedly and
    may reveal where “current version” and “lineage” are already well split.
  EVIDENCE:
  - focused_search_result: dense SpellIndex hit cluster under `src/melder/spellbook/spell_crafter/**`
  IMPACT: This task should show whether the current code already contains the
    beginnings of a cleaner semantics split.
  NEXT: inspect the highest-signal spell-crafter and validation call sites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Investigate SpellIndex semantics inside spell-crafter and validation.
