# Story: Implement the human-first meld identity API

## Metadata
- Story ID: STORY-2026-08-30-human-meld-identity-api
- Epic: EPIC-2026-08-30-human-meld-identity-api
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p0
- Created: 2026-08-30T19:42:00Z
- Updated: 2026-08-30T21:31:49Z

## User Narrative
As a Python application author, I want to meld by a human SpellName and reserve
`spell_id=` for machines, so I do not retain implementation classes or opaque SHAs.

## Value / MRP Alignment
Restores the canonical human API while preserving Melder's optimized internal spine.

## Ticket Contract
- ENTRY_GATE: Epic active, task routed, and patch artifacts linked.
- EXECUTION_BOUNDARY: Meld facade dispatch, owned callers, docs/examples, tests/assets.
- DEPENDENCIES: TASK-2026-08-30-meld-spell-reference-ergonomics.
- EXIT_GATE: Task in review with all acceptance checks passing.
- FAILURE_ESCALATION: Stop on behavior outside the canonical identity split.

## Requirements (Functional)
- Positional strings are SpellNames.
- `spell_id=` is the explicit machine path.
- Both inputs together are rejected.
- Conduit and SpellSpace behavior remains aligned.
- Public per-call construction payloads use `override=`; internal Meld keeps
  `spell_override=`.

## Requirements (Non-Functional)
- No extra lookup on explicit ID calls.
- Existing internal Meld fast doors remain unchanged.

## Scope Boundaries
- In scope: facade/API migration and dependent repository surfaces.
- Out of scope: internal execution-plan redesign.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Public override signatures, callers, documentation,
  assets, and complete supported tests are green.

## Dependencies / Related Work
- `context_compass/tickets/epics/2026-08-30_human_meld_identity_api_epic.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-08-30-meld-spell-reference-ergonomics - implement and validate.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Human and ID syntax execute as designed on Conduit and SpellSpace.
- `override=` executes through Conduit, SpellSpace, and CapabilityCommandSystem.
- Owned callers/docs/examples are migrated and supported suites pass.

## Validation / Test Plan
- Focused, supported tiers, examples, assets, and diff hygiene.

## UX / API / Data Notes
- Human strings are names; machine IDs are explicit keywords.

## Risks / Mitigations
- Call-site breadth controlled by inventory and deterministic migration.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- None.

## Decision Log
- 2026-08-30: Clean breaking public split selected by owner.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/human_meld_identity_api_2026_08_30/architecture_patch.md`
  - `system_docs/patches/active/human_meld_identity_api_2026_08_30/component_patch_meld_resolution.md`
  - `system_docs/patches/active/human_meld_identity_api_2026_08_30/code_description_patch_meld_identity_dispatch.md`
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: story acceptance

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - human meld identity
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-08-30T21:31:49Z
  TYPE: MEASURE
  CLAIM: The story extension is complete: public `override=` is validated on
    all three public surfaces, 83 callers are migrated, five lessons execute,
    and the complete supported suite passes 10,962 tests.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md`
  IMPACT: The story has met its expanded technical acceptance criteria and is
    ready for owner review.
  NEXT: Close only after explicit owner acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:14:24Z
  TYPE: DECISION
  CLAIM: Extend the story with the public `spell_override=` to `override=`
    rename while retaining internal runtime terminology and behavior.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md`
  IMPACT: Story acceptance now includes the shorter public override call shape.
  NEXT: Complete the linked task's patch update, implementation, migration, and validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T20:44:24Z
  TYPE: MEASURE
  CLAIM: The linked task delivers the complete human-first identity split and
    passes the complete supported suite with 10,962 passes plus every final
    migration, asset, focused-test, and diff-hygiene gate.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md`
  IMPACT: The story has met its technical acceptance criteria and is ready for
    owner review; closure still requires explicit acceptance.
  NEXT: Walk through the delivered syntax and validation with the owner, then
    close only after acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:42:00Z
  TYPE: PLAN
  CLAIM: Implement facade dispatch first, migrate callers/docs second, regenerate
    derived assets third, then validate from focused to full scope.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md`
  IMPACT: The story has one ordered, reviewable migration path.
  NEXT: Link and author the patch artifacts before source edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: task evidence, dependency flow, and acceptance state.

## Context / Handoff Summary
Runtime, callers, examples, README, component documentation, generated assets,
and tests now agree on human SpellNames, explicit machine IDs, and concise
public `override=` forwarding into the unchanged internal override engine. The
story is in review pending owner acceptance; no ticket or patch artifact is closed.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
