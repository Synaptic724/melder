# Story: Consumer-specialized transients - plans specialized to their door and to what they were made for

## Metadata
- Story ID: STORY-2026-09-27-consumer-specialized-transients
- Epic: EPIC-2026-09-27-adaptive-creation-contexts
- Status: draft
- Owner: cowork
- Agent Name: fable_0
- Priority: p2
- Created: 2026-09-27T23:42:45Z
- Updated: 2026-09-28T00:57:27Z

## User Narrative
As the Melder owner, I want a `many` root's plan regenerated for the door it is always melded through and the
consumers it is always built for, so that the branches, prologues and reads that exist for cases the profile
never saw are dropped from that spell's version.

## Value / MRP Alignment
The 'what it was made for' half of the owner's direction turned into concrete cuts: the `many_store` prologue
branch (spellspace store, then conduit store) for a root always melded through one door; child transients only
ever built inside one parent kept inline with no separate entry; providers proven stable across the window
pinned as guarded constants. Each cut is small (15-25 ns) and adds up on deep trees; the profile decides
where.

## Ticket Contract
- ENTRY_GATE: owner's pick; capture and versioning stories shipped; patch docs before src.
- EXECUTION_BOUNDARY: `site_plan_lowering.py` (door-specialized emission), the hydrators (a version per
  door), the guard (door identity), tests.
- DEPENDENCIES: STORY-2026-09-27-creator-thread-context-capture; STORY-2026-09-27-creation-context-
  versioning.
- EXIT_GATE: a door-specialized version measured faster than the general body on a deep transient shape; a
  meld through the other door deopts; differential matrix green.
- FAILURE_ESCALATION: DECISION_REQUEST if the measured cut on the owner's shapes is under 3%.

## Requirements (Functional)
- Door-specialized version: the store bound at emission for the observed door; the other door deopts to the
  general version.
- Consumer-only transients: no separate context entry for a transient never melded directly (kept inline in
  its parent's plan).
- Stable providers: shared sites with a 100% hit rate over the window pinned as guarded constants (shared
  with the styles story).

## Requirements (Non-Functional)
- Every cut guarded by door identity or epoch; the general body always available.

## Scope Boundaries
- In scope: the door-specialized emission, the consumer-only rule, tests, measurement.
- Out of scope: singleton capture itself (the styles story owns the guard); registration (the trim story).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: Drafted from the owner's idea list (2026-09-27T23:42:45Z); opens when the owner picks it.

## Dependencies / Related Work
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:131
  3-1329
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:140
  1-1409
- STORY-2026-09-27-probe-selected-codegen-styles

## Tasks (Implementation Checklist)
- [ ] Task: INVESTIGATE how this idea lands in the `CreationContext` object (slot, executor variant, guard,
      cleanup ordering) before anything else; its finding is the story's first note (owner, 2026-09-27T23:54Z).
- [ ] Task: TASK measure the prologue branch and the per-frame cost on a deep transient shape in the harness.
- [ ] Task: TASK design the door-specialized emission and its guard; patch docs.
- [ ] Task: TASK implement as a regenerated version; differential tests through both doors.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- A chain8-style transient tree melded only through the conduit door runs a version without the store
  branch, measured faster; a SpellSpace meld of the same root deopts correctly.

## Validation / Test Plan
- Harness measurement first; component tests through both doors; the differential matrix.

## UX / API / Data Notes
- No public API change.

## Risks / Mitigations
- The cut is too small to pay for its guard -> measure first, park if under 3%.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.
- [ ] No perf claim from agent-side runs; ranking numbers are owner-run.

## Open Questions
- Does the door-specialized version live per (spell, door) or replace the general one while the profile
  holds?

## Decision Log
- 2026-09-27T23:42:45Z (owner): idea collected into the epic; one story per idea. Collected from the owner's
  'what it was made for' idea.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pgo_strategies_20260927/ (proof and runs shared by the epic; new runs land here)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: promoted into the canonical maps when the story ships.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - door specialization; consumer-only transients; stable providers
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-27T23:42:45Z
  TYPE: HYPOTHESIS
  CLAIM: The many_store prologue is two attribute reads and a None test per disposal-bearing plan run (~15
    ns); the transient tree is already inlined into one flat function, so the remaining cuts are the
    prologue and the stable-provider reads.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1313-1329
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1401-1409
  IMPACT: Small per cut; worth a story only on deep or wide shapes the report identifies.
  NEXT: owner picks; measure the cuts in the harness first.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

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
STATE 2026-09-27T23:42:45Z: DRAFT. Collected from the owner's direction; not routed. Opens when the owner
picks it; its first
task is the measurement plan and the patch docs.

STATE 2026-09-28T00:57:27Z: PARKED (backlog_by_owner) with the epic; reopen on the owner's word.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
