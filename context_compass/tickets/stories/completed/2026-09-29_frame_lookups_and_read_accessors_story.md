

# Story: Noncreating frame lookups and read-only accessors for host integrations

## Metadata
- Story ID: STORY-2026-09-29-frame-lookups-and-read-accessors
- Epic: EPIC-2026-09-29-host-integration-read-surface
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-29T21:20:43Z
- Updated: 2026-09-29T22:28:56Z

- Completed: 2026-09-29T22:28:56Z
- Summary: The lookups and read accessors landed with 27 tests, notch 0.2.8208 and the release-note section;
  turned in by owner directive with the system-document promotion parked in a backlog task.

## User Narrative
As a host that creates Melder frames (MelderOps), I want to look frames up without creating them and read the
configuration facts I compare against, so that I can manage what I created without reading Melder's private state.

## Value / MRP Alignment
Replaces six private reads in MelderOps with documented contracts; no runtime path changes.

## Ticket Contract
- ENTRY_GATE: board row routed to TASK-2026-09-29-implement-frame-lookups-and-read-accessors; patch docs linked
  before any source edit.
- EXECUTION_BOUNDARY: aether.py, aetheric_frame.py, aetheric_frame_configuration.py, spellbook_configuration.py,
  conduit.py (additions only), new tests, system docs, graph, release note, `__version__`, assets and bundles.
- DEPENDENCIES: EPIC-2026-09-29-host-integration-read-surface.
- EXIT_GATE: the task's exit gate met and the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST when an accessor cannot mirror MelderOps' current read exactly.

## Requirements (Functional)
- `Aether.find_frame`, `Aether.get_frame`, `Aether.list_frame_names`: noncreating, "default" included.
- Read-only accessors for the frame-wide shared book configuration, configuration freeze state, a book
  configuration's frame and a conduit's Spellbook.

## Requirements (Non-Functional)
- No meld-path cost; no new lock order; rich docstrings; tests at the density the role asks for.

## Scope Boundaries
- In scope: the requirements above.
- Out of scope: changing existing lookups, frame creation or cleanup; priv_commandops edits.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner directive in chat (2026-09-29) to turn in after the release note.

## Dependencies / Related Work
- tickets/stories/backlog/2026-09-29_atomic_frame_retirement_and_creation_attribution_story.md (parked).

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-09-29-implement-frame-lookups-and-read-accessors - lookups, accessors, notch, release note
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Each new call is documented, tested and listed in the system documents and release note.
- None of the lookups creates a frame or freezes the Aether configuration (tested).

## Validation / Test Plan
- New unit tests; meld/conduit and package suites on 3.14t; asset and bundle checks.

## UX / API / Data Notes
- Names follow Aether's verb grammar: `get_*` raises, `find_*` returns None, `list_*` returns a tuple.

## Risks / Mitigations
- A borrowed frame can be cleaned right after a lookup: documented; lookups grant no lease.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- none

## Decision Log
- 2026-09-29: one change set, one notch (owner: "notch the version").

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/host_read_surface_20260929/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: story closure

## Notes
- DATETIME: 2026-09-29T22:28:56Z
  TYPE: DECISION
  CLAIM: Closed by owner directive. Acceptance: each new call is documented in its docstring and the release
    note and tested, and no lookup creates a frame or freezes the Aether configuration (tested). Not met
    before closure: the system-document listing, parked with the 13 shifted citations in the backlog task.
    Rollout: the 0.2.8208 wheel is installed in MelderOps' env and MelderOps requires melder>=0.2.8208.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-09-29_implement_frame_lookups_and_read_accessors_task.md
  - context_compass/tickets/tasks/completed/2026-09-29_build_0_2_8208_wheel_into_melderops_env_task.md
  - context_compass/tickets/tasks/backlog/2026-09-29_promote_host_read_surface_into_system_docs_task.md
  IMPACT: The story's API is delivered; its documentation half is tracked, not lost.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Turned in 2026-09-29T22:28:56Z. The implementation task and the wheel task are in tasks/completed/; the doc promotion is
parked in 2026-09-29_promote_host_read_surface_into_system_docs_task.md.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
