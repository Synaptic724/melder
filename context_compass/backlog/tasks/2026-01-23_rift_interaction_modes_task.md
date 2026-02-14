# Task: Discuss AethericRift interaction modes (workstation vs static exposure)

## Metadata
- Task ID: TASK-2026-01-23-rift-interaction-modes
- Story: STORY-2026-01-23-aethericrift-design-discussions
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-23
- Updated: 2026-01-23

## Objective
Agree on the philosophical split between workstation/REPL mode and static exposure mode, including shared CallSpec semantics, session rules, ObjectRefs, and surface/ACL implications.

## Scope Boundaries
- In scope:
  - Definition of workstation vs static exposure modes.
  - Session and ObjectRef semantics shared across modes.
  - How modes map to surfaces, scopes, and ACL enforcement.
- Out of scope:
  - Transport protocols (HTTP/MCP/etc.).
  - Endpoint design and serialization.

## Steps / Checklist
- [ ] Review the interaction modes ticket content.
- [ ] Discuss the required shared engine (CallSpec) and differences in UX/bench semantics.
- [ ] Record decisions and open questions in this ticket.

## Deliverables
- Decision summary for interaction mode definitions and shared execution semantics.

## Files / Paths Impacted
- context_compass/tasks/2026-01-23_rift_interaction_modes_task.md

## Validation
- Not run.
- Recommended commands:
  - None (discussion-only).

## Risks / Rollback Notes
- Risk: unclear mode boundaries cause accidental overexposure or an overly narrow interface.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Discussion task created; no decisions recorded yet.
