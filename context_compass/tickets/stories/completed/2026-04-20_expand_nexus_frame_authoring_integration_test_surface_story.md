# Story: Expand Nexus Frame Authoring Integration Test Surface
- Completed: 2026-04-25T21:59:28Z
- Summary: Closed after the Nexus frame authoring integration story landed a
  green 42-case real runtime matrix over topology, lifecycle, root-conduit, and
  cleanup behavior.

## Metadata
- Story ID: STORY-2026-04-20-expand-nexus-frame-authoring-integration-test-surface
- Epic: EPIC-2026-04-20-expand-nexus-frame-authoring-test-surface
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-20T16:45:16Z
- Updated: 2026-04-25T21:59:28Z

## User Narrative
As a maintainer, I want real integration coverage for Nexus frame authoring, so
that runtime authoring behavior is proven through real Nexus/Rift/Aether flows
instead of only isolated or component-level slices.

## Value / MRP Alignment
This story proves the full runtime contract where it matters: real frame
creation, retrieval, topology access, descriptor publication, and cleanup
through the public and semi-public Nexus/Rift entrypoints.

## Ticket Contract
- ENTRY_GATE: the epic is created and the integration story is explicitly
  staged.
- EXECUTION_BOUNDARY:
  - integration tests for real Nexus frame authoring runtime behavior
- DEPENDENCIES:
  - `EPIC-2026-04-20-expand-nexus-frame-authoring-test-surface`
  - `tests/integration/melder/aether/`
- EXIT_GATE: at least 40 meaningful integration cases exist and the focused
  integration ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if reaching the count target
  requires broad slow suites unrelated to Nexus frame authoring.

## Requirements (Functional)
- Cover shared/indexed/one-per-workspace topology authoring behavior.
- Cover real Rift-created Nexus frames.
- Cover real dynamic-only posture on created frames.
- Cover real root-conduit bootstrap and descriptor publication.
- Cover real cleanup/removal behavior through Aether/Nexus.

## Requirements (Non-Functional)
- Keep integration cases deterministic.
- Keep the suite bounded to frame authoring behavior.

## Scope Boundaries
- In scope:
  - real Nexus/Rift/Aether frame authoring flows
- Out of scope:
  - broad AR feature matrices unrelated to frame authoring

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: the linked task delivered 42 green integration cases,
  which is above the story’s 40-case acceptance threshold.

## Dependencies / Related Work
- `EPIC-2026-04-20-expand-nexus-frame-authoring-test-surface`

## Tasks (Implementation Checklist)
- [ ] Task: audit current integration coverage for Nexus frame authoring
- [ ] Task: expand topology and lifecycle integration tests
- [ ] Task: expand root-conduit and cleanup integration tests
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The integration story reaches at least 40 meaningful integration cases.
- The focused integration ring is green.
- The cases prove real runtime authoring behavior, not just duplicated unit
  logic.

## Validation / Test Plan
- `python -m pytest -q tests/integration/melder/aether/`

## UX / API / Data Notes
- Integration coverage should prioritize public or stable semipublic entry
  surfaces like `Rift.create_nexus_frame()` and `Nexus` frame accessors.

## Risks / Mitigations
- Risk: integration count target becomes slow or noisy.
  Mitigation: keep every case tied to a topology, lifecycle, or runtime
  contract that unit/component tests cannot fully prove.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether existing Nexus integration tests are better extended or whether a
  dedicated integration file is cleaner.

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
  CLAIM: The integration story should target real Nexus/Rift/Aether frame
    authoring flows and topology behavior, because that is where the dynamic-
    only contract and manager cleanup actually prove themselves end to end.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1983-2049
  - src/melder/aether/nexus/nexus_frame_manager.py:221-733
  IMPACT: The integration lane should be behavior-first and topology-first,
    not just a slower copy of the unit story.
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
This story owns the integration-level Nexus frame authoring test expansion lane.
