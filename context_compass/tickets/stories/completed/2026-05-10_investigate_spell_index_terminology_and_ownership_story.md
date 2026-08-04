# Completed: 2026-05-10T12:04:09Z
# Summary: The SpellIndex terminology/ownership lane was carried through to completion across the controller/context, SpellSystemStates, Spellbook, outward viewer/static-command, and core SpellIndex surfaces while preserving real conduit lineage semantics.
# Story: Investigate SpellIndex Terminology And Ownership

## Metadata
- Story ID: STORY-2026-05-10-investigate-spell-index-terminology-and-ownership
- Epic: EPIC-2026-05-10-investigate-spell-index-terminology-and-ownership
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-10T10:14:03Z
- Updated: 2026-05-10T12:01:27Z

## User Narrative
As the project owner, I want the raw `lineage` search spaces investigated
separately where they are actually talking about SpellIndex semantics, so we
can clean up spell-index terminology and ownership without accidentally
touching real conduit-lineage semantics.

## Value / MRP Alignment
This story protects the runtime model from a sloppy broad “lineage cleanup.”
It creates one explicit lane where SpellIndex-specific meaning can be examined
without flattening unrelated lineage concepts that still make sense.

## Ticket Contract
- ENTRY_GATE: the user explicitly narrowed the problem to SpellIndex-related
  terminology and ownership drift.
- EXECUTION_BOUNDARY: investigation only, across the staged SpellIndex search
  spaces.
- DEPENDENCIES:
  - EPIC-2026-05-10-investigate-spell-index-terminology-and-ownership
  - the per-search-space investigation tasks created under this story
- EXIT_GATE: each SpellIndex search space has an evidence-backed investigation
  note stack that makes later rename/refactor decisions possible.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one search space proves to be
  primarily a conduit-lineage concern instead of a SpellIndex concern.

## Requirements (Functional)
- investigate the core SpellIndex object
- investigate spellbook ownership semantics around SpellIndex
- investigate SpellSystemStates coupling
- investigate Aether/AethericFrame registry wording tied to SpellIndex
- investigate MutationResearch wording tied to SpellIndex
- investigate interface-level SpellIndex contracts
- investigate spell-crafter and validation usage
- investigate AR/viewer/descriptor usage
- investigate tests/support surfaces that encode SpellIndex semantics

## Requirements (Non-Functional)
- keep conduit-lineage semantics out of scope
- keep evidence file-specific
- avoid premature rename decisions

## Scope Boundaries
- In scope:
  - the staged SpellIndex investigation tasks
- Out of scope:
  - actual rename/refactor implementation
  - conduit-lineage cleanup
  - broad mutation architecture changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user asked for an epic plus one task per SpellIndex
  search space and explicitly constrained the scope.

## Dependencies / Related Work
- EPIC-2026-05-10-investigate-spell-index-terminology-and-ownership

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-05-10-investigate-spell-index-core-object
- [x] Task: TASK-2026-05-10-investigate-spellbook-spell-index-ownership
- [x] Task: TASK-2026-05-10-investigate-spell-system-states-spell-index-coupling
- [x] Task: TASK-2026-05-10-investigate-aether-and-frame-spell-index-registry-language
- [x] Task: TASK-2026-05-10-investigate-mutation-research-spell-index-lineage-wording
- [x] Task: TASK-2026-05-10-investigate-spell-index-interface-contracts
- [x] Task: TASK-2026-05-10-investigate-spell-crafter-and-validation-spell-index-usage
- [x] Task: TASK-2026-05-10-investigate-viewer-descriptor-and-static-command-spell-index-exposure
- [x] Task: TASK-2026-05-10-investigate-spell-index-test-and-support-surfaces
- [x] Task: TASK-2026-05-10-rename-spell-index-gate-terminology-in-creation-context-and-controller
- [x] Task: TASK-2026-05-10-rename-spell-index-terminology-in-spell-system-states
- [x] Task: TASK-2026-05-10-rename-spell-index-terminology-in-spellbook
- [x] Task: TASK-2026-05-10-rename-spell-index-terminology-in-viewer-and-static-command
- [x] Task: TASK-2026-05-10-reframe-spell-index-core-semantics
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during investigation.

## Acceptance Criteria
- Every staged SpellIndex search space is investigated or explicitly
  reclassified out of scope.
- The story makes it possible to discuss later rename/refactor work without
  mixing in conduit-lineage semantics.

## Validation / Test Plan
- Investigation only.

## Risks / Mitigations
- Risk: the lane drifts back into a global lineage cleanup.
  Mitigation: keep each task tied to one search space and reject conduit
  lineage drift explicitly.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Which search spaces are truly using “lineage” semantically?
- Which search spaces are just inheriting SpellIndex naming bias?

## Decision Log
- 2026-05-10T10:14:03Z: Opened to hold the SpellIndex-only investigation lane
  after the user explicitly rejected a broader lineage cleanup scope.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-10T10:14:03Z
  TYPE: PLAN
  CLAIM: The right decomposition is not one task per raw grep hit. It is one
    task per high-signal raw `lineage` search space that still appears to be
    talking about SpellIndex semantics, so we can investigate each semantic
    cluster separately without turning the lane into grep spam.
  EVIDENCE:
  - focused_search_result: case-insensitive raw `lineage` hit map across `src/` and `tests/`
  - user_instruction: "make a task for each search space you found and we'll need to investigate each file"
  IMPACT: The task stack stays readable and investigation-driven instead of
    exploding into hundreds of tiny grep-hit tasks.
  NEXT: stage the search-space tasks under this story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition
  logic.
- Add notes when a search space splits further or is reclassified out of scope.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story groups the SpellIndex-only investigation tasks and keeps conduit
lineage explicitly out of scope.
