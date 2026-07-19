# Story: Command Surface Cleanup And Rift Gate Entry
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-18-command-surface-cleanup-and-rift-gate-entry
- Epic: EPIC-2026-04-18-command-surface-cleanup-and-rift-gate-entry
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T19:42:55Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a runtime maintainer, I want the command surface to use explicit top-level
RiftGate entry and real policy checks, so that gate behavior and command
semantics are understandable and correct.

## Value / MRP Alignment
This removes magic from a core agent-facing surface and makes the runtime more
trustworthy at the MRP layer.

## Ticket Contract
- ENTRY_GATE: the audit identified real structural issues and the user approved
  implementation.
- EXECUTION_BOUNDARY: `CommandSystem`, `StaticCommandSystem`, and directly
  affected tests only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_refactor_command_system_public_surface_and_rift_gate_integration_task.md
- EXIT_GATE: the command wrapper magic is gone, public-to-public chaining is
  removed where required, and focused tests are green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if fixing command properly
  requires widening into workstation/viewer work in the same slice.

## Requirements (Functional)
- Remove `__getattribute__`-based command wrapping.
- Remove `_command_memory_call_depth`.
- Replace fake no-op policy seams with real checks/predicates.
- Keep top-level command memory emission behavior.
- Keep top-level command RiftGate admission/ticketing behavior.

## Requirements (Non-Functional)
- No compatibility shim for the old magic wrapper.
- Keep the cleanup bounded to command for this slice.

## Scope Boundaries
- In scope:
  - base and static command cleanup
  - focused tests
- Out of scope:
  - workstation gate integration
  - viewer gate integration beyond current behavior

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested command cleanup implementation after the
  audit surfaced real structural issues.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-18-refactor-command-system-public-surface-and-rift-gate-integration - clean the command surface and explicit gate entry
- [ ] Enforce Ticket Microcycle across linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Command no longer relies on magic wrapper/call-depth suppression.
- Command gate entry is explicit and top-level only.
- Static command policy seams are represented honestly.

## Validation / Test Plan
- `python -m py_compile ...`
- `python -m pytest -q tests/unit/melder/aether/test_command_system_direct.py tests/unit/melder/aether/test_static_command_system_direct.py tests/unit/melder/aether/test_nexus.py`

## Risks / Mitigations
- Risk: command cleanup may expose more public-to-public chaining than expected.
  Mitigation: refactor only the shared hotspots required for top-level gating.

## Notes
- DATETIME: 2026-04-18T20:02:43Z
  TYPE: FACT
  CLAIM: The child task landed the bounded command-only cleanup and the focused
    command ring is green.
  EVIDENCE:
  - tickets/tasks/2026-04-18_refactor_command_system_public_surface_and_rift_gate_integration_task.md:1-180
  IMPACT: The story is ready for review instead of more implementation.
  NEXT: wait for acceptance or a bounded follow-on request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T19:42:55Z
  TYPE: PLAN
  CLAIM: The bounded implementation slice is command-only: remove the magic
    wrapper, move public-to-public chaining into private helpers, and make gate
    entry explicit on top-level command methods.
  EVIDENCE:
  - tickets/tasks/2026-04-18_audit_command_system_surface_and_plan_cleanup_task.md:1-120
  IMPACT: This keeps the cleanup honest without widening into workstation and
    viewer in the same pass.
  NEXT: implement the command task and validate the focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This story tracks the bounded command-only cleanup before any wider gate
integration work.