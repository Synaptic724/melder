# Story: Add Configurable RiftGate Projection Refresh
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Story ID: STORY-2026-04-18-add-configurable-rift-gate-projection-refresh
- Epic: EPIC-2026-04-18-rehome-frame-viewer-ownership-to-rift-space
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T23:45:00Z
- Updated: 2026-04-19T16:37:39Z

## User Narrative
As a runtime maintainer, I want `NexusConfiguration` to control whether
projection refresh uses the RiftGate drain barrier, so that the refresh
semantics are explicit, default-on, and testable.

## Value / MRP Alignment
The refresh barrier is already part of correctness for live ACL-driven
projection swaps. Making that behavior explicit in config documents the
contract, preserves the safe default, and gives one bounded opt-out for cases
where a caller knowingly wants ungated refresh.

## Ticket Contract
- ENTRY_GATE: user explicitly requested a Nexus configuration feature for the
  RiftGate-controlled projection refresh path.
- EXECUTION_BOUNDARY: `NexusConfiguration`, `INexusConfiguration`, the live
  Nexus projection-refresh path, focused tests, and matching docs only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_implement_configurable_rift_gate_projection_refresh_task.md
  - system_docs/patches/active/configurable_rift_gate_projection_refresh/architecture_patch.md
  - system_docs/patches/active/configurable_rift_gate_projection_refresh/component_patch_nexus_configuration.md
  - system_docs/patches/active/configurable_rift_gate_projection_refresh/component_patch_nexus.md
- EXIT_GATE: the config flag/timing fields exist, default-on behavior is green,
  opt-out behavior is green, and docs/tests are updated.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the user wants the refresh
  barrier to be a hard invariant with no config flag at all.

## Requirements (Functional)
- Add one configuration flag controlling whether ACL-driven projection refresh
  uses RiftGate drain semantics.
- Keep the flag enabled by default.
- Add config-backed timeout and poll interval for the barrier wait.
- Make `_refresh_rift_projection_sets_for_frame(...)` read those config values
  instead of hardcoded literals.

## Requirements (Non-Functional)
- No backward-compat shim or second config surface.
- Keep the safe default on.
- Keep test coverage focused on behavior, not implementation trivia.

## Scope Boundaries
- In scope:
  - `NexusConfiguration`
  - `INexusConfiguration`
  - `Nexus` ACL-refresh path
  - focused config and refresh tests
  - matching docs/ticket state
- Out of scope:
  - command/viewer/workstation gating redesign
  - `RiftGate` primitive redesign
  - broader ACL model work

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the config-driven refresh barrier feature is implemented
  and the focused validation ring is green.

## Dependencies / Related Work
- viewer ownership migration epic
- existing RiftGate controller/runtime slice

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-18-implement-configurable-rift-gate-projection-refresh
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- `NexusConfiguration` exposes the refresh-gating flag and timing fields.
- Default config keeps gated refresh on.
- Opt-out config skips the disable/wait/enable barrier and still refreshes
  impacted Rifts.
- Focused tests pass.

## Validation / Test Plan
- Focused config unit tests.
- Focused Nexus refresh orchestration unit tests.

## Risks / Mitigations
- Risk: adding the flag may imply the barrier is optional in cases where it
  should not be.
  Mitigation: keep the default on and document the opt-out as deliberate.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether this flag should remain a config option long-term or later collapse
  into a hard invariant once the runtime fully stabilizes.

## Decision Log
- Pending implementation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-18T23:58:36Z
  TYPE: FACT
  CLAIM: The child task landed the config-driven RiftGate projection refresh
    feature with default-on barrier behavior, timing fields, focused tests, and
    small AR doc updates.
  EVIDENCE:
  - tickets/tasks/2026-04-18_implement_configurable_rift_gate_projection_refresh_task.md:1-168
  IMPACT: The story is ready for review instead of more implementation.
  NEXT: hold for acceptance or a bounded follow-on request.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-18T23:45:00Z
  TYPE: PLAN
  CLAIM: The bounded follow-on is to move the current hardcoded refresh-gate
    behavior into `NexusConfiguration` as one default-on flag plus timeout and
    poll-interval settings, then wire `_refresh_rift_projection_sets_for_frame(...)`
    to respect them.
  EVIDENCE:
  - src/melder/aether/nexus/configuration/nexus_configuration.py:63-85
  - src/melder/aether/nexus/nexus.py:1881-1978
  IMPACT: This keeps the refresh barrier explicit and configurable without
    reopening the ownership work we just landed.
  NEXT: implement the linked task and validate the focused config/refresh ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story tracks the bounded config follow-on for the RiftGate-controlled
projection refresh path. It is now implemented and waiting on review.