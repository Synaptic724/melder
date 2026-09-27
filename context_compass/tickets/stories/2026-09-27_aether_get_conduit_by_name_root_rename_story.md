

# Story: Aether.get_conduit_by_name gets a root-explicit name, with every usage migrated

## Metadata
- Story ID: STORY-2026-09-27-aether-get-conduit-by-name-root-rename
- Epic: EPIC-2026-09-27-aether-conduit-lookup-api
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-27T10:07:08Z
- Updated: 2026-09-27T10:41:49Z

## User Narrative
As a Melder user, I want `Aether.get_conduit_by_name` to say in its name that it covers ROOT conduits only, so
that I never read a missing named lesser as a missing conduit.

## Value / MRP Alignment
Names state coverage; the root lookup keeps its exact behaviour; callers move deliberately, never silently.

## Ticket Contract
- ENTRY_GATE: Epic row routes the investigation; this story's usage inventory is recorded in Notes; the owner
  has approved the name, the migration form and the version step.
- EXECUTION_BOUNDARY: `Aether.get_conduit_by_name` (and its private helper, if any) and every usage recorded
  in Notes; no behaviour change.
- DEPENDENCIES: Epic API decision; patch docs for the public API change.
- EXIT_GATE: Renamed with a rich docstring; every recorded usage migrated or deliberately kept; old name
  handled per the migration decision; tests green on 3.14t and GIL.
- FAILURE_ESCALATION: DECISION_REQUEST when a usage cannot move to the approved name as-is (generated assets, external
  docs, compatibility); CONFLICT when documents and source disagree.

## Requirements (Functional)
- The root-only behaviour of `Aether.get_conduit_by_name` is preserved exactly under the approved root-explicit name.
- The old name follows the approved migration form (removed, or a deprecated alias that warns once per call site).

## Requirements (Non-Functional)
- No new lock, allocation or indirection on the lookup path.
- Docstring states root-only coverage.

## Scope Boundaries
- In scope: `Aether.get_conduit_by_name` and its usages in src, tests, docs, examples, system docs and
  generated bundles.
- Out of scope: The new any-conduit lookups (their own stories); ConduitCloud and Nexus command methods of the
  same name.

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
- [ ] Usage survey (epic investigation; results in Notes)
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
- Current: `Aether.get_conduit_by_name(name, aetheric_frame_name="default") -> Conduit`
  (src/melder/aether/aether.py:1842-1863, 1914-1948) returns a ROOT conduit by name via
  `_get_conduit_by_name`; raises ValueError when missing.
- Approved name: `get_root_conduit_by_name` (owner, 2026-09-27); hard rename, no alias.

## Risks / Mitigations
- A rename breaks every caller at once: survey all usages first; the migration form (hard rename or deprecated alias)
  is an epic-level owner decision.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Final root-explicit name?
- Hard rename or deprecated alias, and for how long?

## Decision Log
- 2026-09-27T10:31:58Z: owner approved option A: `get_conduit_by_name` -> `get_root_conduit_by_name`, hard
  rename, no alias; the generic name is reused for the new any-conduit lookup (its own story); one 0.01
  version notch when the epic lands; frame parameter stays `aetheric_frame_name: str = "default"`.
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
  CLAIM: Usage inventory for Aether.get_conduit_by_name (AST survey, receivers resolved; 0.2.78). src: none
    outside Aether (private `_get_conduit_by_name`, aether.py:1914-1948). tests: test_aether.py:794 plus
    private-helper tests :703-718; Aether() calls in test_spellbook_component_structural_snapshot_parity.py:385,
    test_aether_integration_frames.py:123, test_non_resolvable_graph_replay.py:155,
    test_ordered_disposal_replay.py:127, 239, 310 (all root lookups after restore). benchmarks:
    test_gauntlet_melder_lane_parity.py:248. Docs: none.
  EVIDENCE:
  - src/melder/aether/aether.py:1842-1863
  - tests/unit/melder/aether/test_aether.py:692-718
  - tests/unit/melder/aether/test_aether.py:766-795
  - context_compass/artifacts/aether_lookup_api_survey_20260927/usage_survey_20260927.txt:46-71
  - context_compass/artifacts/aether_lookup_api_survey_20260927/usage_survey_20260927.txt:2-45
  IMPACT: Every listed site moves to the approved root-explicit name; nothing else in the hand-written tree
    calls this Aether method. Generated bundles are rebuilt, not edited.
  NEXT: Owner API decision (epic), then an implementation task under this story.
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
