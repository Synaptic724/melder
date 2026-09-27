

# Story: ConduitCloud returns all of its conduits

## Metadata
- Story ID: STORY-2026-09-27-conduit-cloud-list-all-conduits
- Epic: EPIC-2026-09-27-aether-conduit-lookup-api
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-27T10:07:08Z
- Updated: 2026-09-27T10:41:49Z

## User Narrative
As a Melder user, I want ConduitCloud to hand me every conduit it knows, not only their names or ids, so that
discovery code can iterate live scopes directly.

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
- Returns a snapshot of borrowed conduit references taken under the Cloud lock.
- Membership matches `list_conduit_names()` / `list_conduit_ids()` at the time of the snapshot.

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
- Approved: `ConduitCloud.list_conduits() -> Tuple[Conduit, ...]`, a snapshot of NAMED scopes (borrowed refs,
  taken under the Cloud lock), matching list_conduit_ids/list_conduit_names membership (owner, 2026-09-27).

## Risks / Mitigations
- A rename breaks every caller at once: survey all usages first; the migration form (hard rename or deprecated alias)
  is an epic-level owner decision.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Named scopes only (the Cloud directory), or every live conduit in the frame including anonymous lessers?
- Does Aether also get a frame-level `list ... conduits` companion?

## Decision Log
- 2026-09-27T10:31:58Z: owner approved NAMED coverage for ConduitCloud.list_conduits(); no Aether companion requested.
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
- DATETIME: 2026-09-27T10:26:47Z
  TYPE: FACT
  CLAIM: ConduitCloud's read surface is get_conduit, get_conduit_by_name, get_conduit_by_id, list_conduit_ids,
    list_conduit_names, list_cloud_names, count_conduits, has_conduit_id, has_conduit_name and
    find_conduit_id_by_name; every one answers over NAMED scopes (named roots and active named lessers), and
    none returns the conduit objects. The Cloud also holds the frame's borrowed root map, so a walk over every
    live conduit (anonymous lessers included) is reachable from it.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/conduit_cloud.py:457-686
  - src/melder/aether/aetheric_frame/conduit_cloud.py:709-738
  - src/melder/aether/aetheric_frame/conduit_cloud.py:146-153
  IMPACT: 'All conduits' is a new method; its coverage (named scopes vs every live conduit) is the owner's call.
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
