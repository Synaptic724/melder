

# Story: Aether finds any live named conduit in a frame, root or lesser, by name

## Metadata
- Story ID: STORY-2026-09-27-aether-find-any-conduit-by-name
- Epic: EPIC-2026-09-27-aether-conduit-lookup-api
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-27T10:07:08Z
- Updated: 2026-09-27T10:41:49Z

## User Narrative
As a Melder user, I want Aether to return any live named conduit - a root or a named lesser at any depth - by
name, so that I can reach a named scope from the runtime root without holding its parent.

## Value / MRP Alignment
Frame-wide discovery at the runtime root, stated precisely: what is covered, what is borrowed, what raises.

## Ticket Contract
- ENTRY_GATE: Epic row routes the investigation; the design facts this story needs are recorded in Notes; the
  owner has approved the name, signature and coverage.
- EXECUTION_BOUNDARY: The new method, its docstring and tests, and the docs that teach discovery; no change to
  existing semantics.
- DEPENDENCIES: Epic API decision; patch docs; the registries named in Notes.
- EXIT_GATE: Method in place with a rich docstring; unit and integration tests; docs and system docs updated.
- FAILURE_ESCALATION: DECISION_REQUEST when a usage cannot move to the approved name as-is (generated assets, external
  docs, compatibility); CONFLICT when documents and source disagree.

## Requirements (Functional)
- Resolves exact names of named roots and active named lessers, in automatic and dynamic frames.
- Returns a borrowed reference with no lease; retired, pooled and anonymous scopes never resolve.
- Missing names raise a clear ValueError; a missing frame raises as the root lookups do today.

## Requirements (Non-Functional)
- Lookups take only leaf locks and invoke no callbacks.
- No hot-path cost for ordinary meld paths.

## Scope Boundaries
- In scope: The new method and its documentation.
- Out of scope: Renaming the existing root-only methods (their own stories).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Created from EPIC-2026-09-27-aether-conduit-lookup-api on owner instruction (2026-09-27):
  one story per method; investigate
  usages before any migration.

## Dependencies / Related Work
- tickets/epics/2026-09-27_aether_conduit_lookup_api_epic.md
- tickets/tasks/2026-09-27_trace_get_conduit_by_name_named_lesser_lookup_task.md (cause and repro of the
  root-only lookup)

## Tasks (Implementation Checklist)
- [ ] Design facts (epic investigation; results in Notes)
- [ ] Task: TASK-2026-09-27-implement-aether-conduit-lookup-api - one change set for the epic
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The approved API change is in place with a rich docstring stating coverage, lease and error contract.
- Every usage found by the survey is migrated or deliberately kept, each one recorded in Notes.
- Tests cover the contract and pass on 3.14t and GIL (owner-run or agent-run, reported truthfully).

## Validation / Test Plan
- Not run.
- `python -m pytest tests/unit/melder/aether/test_aether.py -q` and `python -m pytest
  tests/integration/melder/aether -q`
  on the 3.14.7t venv, then the GIL build; symptom-named regression tests where behaviour changes.

## UX / API / Data Notes
- Current: not available on this surface.
- Approved: `Aether.get_conduit_by_name(name: str, aetheric_frame_name: str = "default") -> Conduit` over NAMED
  scopes via the frame's ConduitCloud; frame-scoped only, frame optional, string-typed (owner, 2026-09-27).

## Risks / Mitigations
- A rename breaks every caller at once: survey all usages first; the migration form (hard rename or deprecated alias)
  is an epic-level owner decision.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Name and signature (reuse `get_conduit_by_name` for the frame-wide meaning, or a new name)?
- Frame-scoped (explicit frame name, as today) or searched across every frame (names are unique per frame only)?

## Decision Log
- 2026-09-27T10:31:58Z: owner decisions: reuse `get_conduit_by_name`; frame-scoped only (no cross-frame search, no
  None sentinel); `aetheric_frame_name: str = "default"` like the rest of Aether; hard rename; 0.01 notch.
- 2026-09-27T10:07:08Z: story created; name, migration form and version are pending the epic's API decision.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: story closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T10:24:22Z
  TYPE: FACT
  CLAIM: The frame's ConduitCloud directory already holds every named root and every active named lesser at any
    depth, retires names on return, and is reachable today through Aether.get_conduit_cloud(frame); one Cloud
    belongs to one frame, so names are unique per frame only and a cross-frame search can match more than one
    scope.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/conduit_cloud.py:23-45
  - src/melder/aether/aetheric_frame/conduit_cloud.py:242-310
  - src/melder/aether/aetheric_frame/conduit_cloud.py:481-501
  - tickets/tasks/2026-09-27_trace_get_conduit_by_name_named_lesser_lookup_task.md
  IMPACT: A frame-scoped any-by-name lookup is a direct delegation to the Cloud; a cross-frame variant needs an
    ambiguity rule (owner decision).
  NEXT: Carry into the design proposal.
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
Draft story under EPIC-2026-09-27-aether-conduit-lookup-api. The epic's investigation records this story's
usage inventory and design facts in Notes;
implementation waits for the owner's API decision.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
