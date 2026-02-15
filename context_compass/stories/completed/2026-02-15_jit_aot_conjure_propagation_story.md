# Story: JIT/AOT Conjure Propagation

Completed: 2026-02-15
Summary: Closed after user acceptance; linked discovery/implementation tasks are complete and validated for this story scope.


## Metadata
- Story ID: STORY-2026-02-15-jit-aot-conjure-propagation
- Epic: EPIC-2026-02-14-jit-aot-phase-split-configuration
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-15
- Updated: 2026-02-15

## User Narrative
As a runtime maintainer, I want spells stamped with mode defaults during conjure
so runtime gates can trust spell state from first activation.

## Value / MRP Alignment
Conjure-time propagation ensures consistent initial state for all owned spells
without changing contracted ownership behavior.

## Requirements (Functional)
- During conduit wiring into local spells, stamp mode semantics derived from config.
- Set `resolution_required` consistently for JIT opt-in mode.
- Preserve current owner wiring behavior and existing-object registration semantics.

## Requirements (Non-Functional)
- No regressions for full AOT default path.
- Keep scope limited to conjure-time stamping path.

## Scope Boundaries
- In scope:
- `SpellbookCreationSystem.define_conduit_into_spells` propagation logic.
- Out of scope:
- Late-bind path and transfer path (separate stories).

## Dependencies / Related Work
- `TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces`
- `STORY-2026-02-15-jit-aot-config-flag-and-fluent-api`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-02-15-implement-jit-aot-conjure-propagation - add conjure-time stamping behavior.
- [ ] Task: TASK-2026-02-15-discovery-jit-aot-propagation-contract-surfaces - confirm exact ownership/stamping insertion points.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Conjure stamps owned spells with mode-derived `resolution_required` state.
- Full AOT default path remains behaviorally unchanged.
- Contracted-spell ownership semantics remain unaffected.

## Validation / Test Plan
- Unit tests focused on conjure-time spell state after conduit wiring.

## UX / API / Data Notes
- Internal runtime behavior only; no public API shape change.

## Risks / Mitigations
- Risk: stamping logic accidentally touching contracted spell maps.
  Mitigation: keep implementation scoped to local spell iteration path only.

## Open Questions
- Should `resolution_required` be stamped before or after existing-object registration into Creations?

## Decision Log
- 2026-02-15: Story created to isolate conjure-time propagation from late-bind and transfer paths.

## Notes
- DATE: 2026-02-15
  TYPE: PLAN
  CLAIM: Conjure propagation should attach to existing ownership-stamping loop that already wires owner conduit and creation metadata into local spells.
  EVIDENCE: src/melder/spellbook/spellbook_creation_system.py:457-485
  IMPACT: We can add mode propagation without introducing a new traversal path.
  NEXT: Confirm exact field-write contract in propagation discovery task and then implement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Ready story with clear touchpoint. Waiting on discovery gate completion.


