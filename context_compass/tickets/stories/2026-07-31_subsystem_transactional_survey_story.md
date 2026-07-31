# Story: Survey what MR / Nexus / Crystallizer actually need transactionalized

## Metadata
- Story ID: STORY-2026-07-31-subsystem-transactional-survey
- Epic ID: EPIC-2026-07-31-aetheric-mediator-subsystem
- Status: ready
- Owner: cowork
- Agent Name: UNASSIGNED (deliberately - see note)
- Priority: p1
- Created: 2026-07-31T23:00:41Z
- Updated: 2026-07-31T23:00:41Z

## Problem / Opportunity
We do not yet know WHAT to transactionalize in each subsystem, only that each
invented its own concurrency control. Before wiring, each subsystem needs a
survey answering: what structural mutations does it perform, what does it
currently protect them with, what scope keys would express that, and what are its
"basic conditions" emitted on enable.

## Ticket Contract
- ENTRY_GATE: core plane vocabulary exists (claim modes + scope key shape).
- EXECUTION_BOUNDARY: READ-ONLY survey. No code changes under this story.
- EXIT_GATE: three task surveys complete with source evidence.
- FAILURE_ESCALATION: RAISE if a subsystem's protection cannot be expressed as
  scope claims - that is a finding, not a failure.

## Tasks
- [ ] TASK-2026-07-31-survey-mr-transactional-surface
- [ ] TASK-2026-07-31-survey-nexus-transactional-surface
- [ ] TASK-2026-07-31-survey-crystallizer-transactional-surface

## Acceptance Criteria
- Each survey names the subsystem's structural mutation verbs with file:line.
- Each names its CURRENT protection mechanism and what that mechanism misses.
- Each proposes scope keys and modes.
- Each answers "what basic conditions does this subsystem emit when enabled".

## Notes
- DATETIME: 2026-07-31T23:00:41Z
  TYPE: DECISION
  CLAIM: Left UNASSIGNED on purpose. These surveys should be run by agents with
    FRESH context, not inherited from the long investigation session that
    produced the epic. Each task is written to be self-contained.
  EVIDENCE:
  - context_compass/tickets/epics/2026-07-31_aetheric_mediator_subsystem_epic.md
  IMPACT: Keeps survey quality independent of one contaminated session.
  NEXT: Any agent may claim one survey task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Three read-only surveys. Self-contained by design so a fresh agent can take one
without reading the whole investigation history.
