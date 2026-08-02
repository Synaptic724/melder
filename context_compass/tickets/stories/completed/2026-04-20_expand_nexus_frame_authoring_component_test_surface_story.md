# Story: Expand Nexus Frame Authoring Component Test Surface
- Completed: 2026-04-25T21:59:28Z
- Summary: Closed after the Nexus frame authoring component story landed a
  green 42-case real-wiring slice over publication, ACL-container, topology,
  and cleanup behavior.

## Metadata
- Story ID: STORY-2026-04-20-expand-nexus-frame-authoring-component-test-surface
- Epic: EPIC-2026-04-20-expand-nexus-frame-authoring-test-surface
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-20T16:45:16Z
- Updated: 2026-04-25T21:59:28Z

## User Narrative
As a maintainer, I want component-level test coverage for Nexus frame
authoring, so that the small real wiring slices around Nexus/Aether/descriptor
publication are proven without needing full end-to-end integration every time.

## Value / MRP Alignment
This story proves the subsystem in small real slices: manager + descriptor,
manager + ACL container, root-conduit bootstrap, and disposal synchronization.

## Ticket Contract
- ENTRY_GATE: the epic is created and the component story is explicitly staged.
- EXECUTION_BOUNDARY:
  - component tests touching only the minimal real Nexus/Aether wiring needed
    for frame authoring truth
- DEPENDENCIES:
  - `EPIC-2026-04-20-expand-nexus-frame-authoring-test-surface`
  - `tests/component/melder/aether/`
- EXIT_GATE: at least 40 meaningful component cases exist and the focused
  component ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if component cases start
  drifting into broad integration sweeps.

## Requirements (Functional)
- Cover descriptor publication after frame creation.
- Cover ACL-container provisioning around authored frames.
- Cover root-conduit bootstrap and overview refresh.
- Cover external Aether disposal synchronization for managed frames.
- Cover topology-specific create/recover flows with minimal real wiring.

## Requirements (Non-Functional)
- Keep each case bounded to a small real slice.
- Avoid external I/O and broad environment dependency.

## Scope Boundaries
- In scope:
  - small real Nexus/Aether/descriptor/ACL slices
- Out of scope:
  - full cross-subsystem integration runs

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: the linked task delivered 42 green component cases, which
  is above the story’s 40-case acceptance threshold.

## Dependencies / Related Work
- `EPIC-2026-04-20-expand-nexus-frame-authoring-test-surface`

## Tasks (Implementation Checklist)
- [ ] Task: audit current component coverage for Nexus frame authoring
- [ ] Task: expand authored frame creation/publication component tests
- [ ] Task: expand disposal and topology component tests
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The component story reaches at least 40 meaningful component cases.
- The focused component ring is green.
- The cases stay bounded to small real wiring slices.

## Validation / Test Plan
- `python -m pytest -q tests/component/melder/aether/`

## UX / API / Data Notes
- Component cases should prove that the authoring subsystem wires cleanly into
  descriptors and ACL containers.

## Risks / Mitigations
- Risk: component tests bloat into pseudo-integration.
  Mitigation: keep the real set minimal and explicit.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Which existing component tests can be extended versus which need a new file.

## Decision Log
- None yet.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-20T16:45:16Z
  TYPE: PLAN
  CLAIM: The component story should focus on the small real slices that matter
    for frame authoring truth: publication, descriptor/ACL alignment, root
    conduit bootstrap, and disposal.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:221-733
  IMPACT: We can get real value here without turning the component lane into
    full integration.
  NEXT: stop after story creation and wait for user direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

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
This story owns the component-level Nexus frame authoring test expansion lane.
