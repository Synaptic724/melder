# Task: Survey the Crystallizer transactional surface

## Metadata
- Task ID: TASK-2026-07-31-survey-crystallizer-transactional-surface
- Story ID: STORY-2026-07-31-subsystem-transactional-survey
- Epic ID: EPIC-2026-07-31-aetheric-mediator-subsystem
- Status: ready
- Owner: cowork
- Agent Name: UNASSIGNED
- Priority: p1
- Created: 2026-07-31T23:00:41Z
- Updated: 2026-07-31T23:00:41Z

## SELF-CONTAINED BY DESIGN
You do NOT need the history of the investigation that produced this task. Read
the epic's Problem section for the why, then work only from the reads below.
This task is READ-ONLY. Do not change code.

## Purpose
Establish what in Crystallizer actually needs transactionalizing, so the
AethericMediator plane can be wired to it later without guessing.

## Starting Facts (verified 2026-07-31; re-verify, do not trust)
Crystallizer currently protects concurrent structural mutation with:
Aether-hosted LoadGate (globally exclusive, one load at a time; cohort enrolled via _enroll_restore_cohort so the load's own 4 default workers pass free), engine-local _build_lock for check-then-posture, and posture idempotence. Failure handling is _teardown_built() (newest-first, best-effort, swallows per-unit cleanup errors) plus an 80-site shortfall ledger.

## Required Reads
- `context_compass/tickets/epics/2026-07-31_aetheric_mediator_subsystem_epic.md`
  (Problem, Component Split, Key Design Decisions)
- src/melder/crystallizer/ -> crystal_loader_system/crystal_loader_system.py, crystal_loader_system/restore_engine.py, crystal_loader_system/load_plan.py

## Questions To Answer (each with file:line evidence)
1. What STRUCTURAL MUTATION verbs does Crystallizer expose or perform? Name them.
2. What protects each today, and what does that protection NOT cover?
3. What SCOPE KEYS would express those mutations? Propose concrete strings using
   the namespaced flat form (e.g. `crystallizer:<unit>:<id>`).
4. What MODE does each need - `x` exclusive, `s` shared, or `ix` intent?
   Justify any `ix`; do not use it by default.
5. What are Crystallizer's "BASIC CONDITIONS" - the state it would emit to the plane
   when it becomes enabled and active? (Owner constraint 6.)
6. Is there any protection here that CANNOT be expressed as scope claims? That is
   a first-class finding, not a failure - record it loudly.

## Acceptance Criteria
- All six questions answered with `path:start-end` evidence.
- Proposed scope keys and modes are concrete, not descriptive.
- Any inexpressible protection is recorded as a CONFLICT note.
- No code changed.

## Applicable Anti-Patterns
- [ ] No proposing a design; this is a survey.
- [ ] No promoting a doc claim to FACT without opening the source.
- [ ] No code changes under a read-only task.

## Validation / Test Approach
Not run - read-only survey.

## Notes
- (append findings here as they land, per the Ticket Microcycle)

## Context / Handoff Summary
Read-only survey of Crystallizer feeding the AethericMediator wiring story. Answer the
six questions with evidence; propose scope keys and modes; flag anything that
cannot be expressed as a claim.
