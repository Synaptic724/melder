# Task: Survey the Nexus / Rift transactional surface

## Metadata
- Task ID: TASK-2026-07-31-survey-nexus-transactional-surface
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
Establish what in Nexus / Rift actually needs transactionalizing, so the
AethericMediator plane can be wired to it later without guessing.

## Starting Facts (verified 2026-07-31; re-verify, do not trust)
Nexus / Rift currently protects concurrent structural mutation with:
RiftGate + RiftGateController (per-Rift admission, drain, entry-mode), instance RLocks, config-backed drain via projection_refresh_gate_enabled / _timeout_seconds / _poll_interval_seconds, and FrameACLConfigurationChain.rollback_to_configuration(id) which is savepoint-shaped.

## Required Reads
- `context_compass/tickets/epics/2026-07-31_aetheric_mediator_subsystem_epic.md`
  (Problem, Component Split, Key Design Decisions)
- src/melder/nexus/ -> nexus.py, rift/rift_gate/rift_gate.py, rift/rift_gate_controller/, acl/frame_acl_configuration_chain.py

## Questions To Answer (each with file:line evidence)
1. What STRUCTURAL MUTATION verbs does Nexus / Rift expose or perform? Name them.
2. What protects each today, and what does that protection NOT cover?
3. What SCOPE KEYS would express those mutations? Propose concrete strings using
   the namespaced flat form (e.g. `nexus:<unit>:<id>`).
4. What MODE does each need - `x` exclusive, `s` shared, or `ix` intent?
   Justify any `ix`; do not use it by default.
5. What are Nexus / Rift's "BASIC CONDITIONS" - the state it would emit to the plane
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
Read-only survey of Nexus / Rift feeding the AethericMediator wiring story. Answer the
six questions with evidence; propose scope keys and modes; flag anything that
cannot be expressed as a claim.
