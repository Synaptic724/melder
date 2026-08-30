# Epic: Restore the human-first meld identity contract

## Metadata
- Epic ID: EPIC-2026-08-30-human-meld-identity-api
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p0
- Created: 2026-08-30T19:42:00Z
- Updated: 2026-08-30T21:31:49Z
- Target Window: 2026-Q3
- Related Program/Initiative: Melder public API and UX/AIX curriculum

## Problem / Opportunity
The canonical DI resolution contract assigns positional strings to human
SpellName resolution, while current public facades interpret them as machine
SHA ids. README and runnable examples compensate by retaining implementation
classes, producing an implementation-coupled human API.

## MRP Alignment (Most Reasonable Product)
Separate human and machine identity explicitly at the public boundary while
preserving the optimized internal ID spine. The smallest durable product is a
coherent API, migrated examples, synchronized system documentation, and full
supported-suite proof.

## Ticket Contract
- ENTRY_GATE: Active story/task routing and required patch artifacts exist before source edits.
- EXECUTION_BOUNDARY: Public meld identity, affected call sites, README/UX examples,
  resolution documentation, generated assets, and focused validation.
- DEPENDENCIES: Canonical 19-item resolution contract and current Meld implementation.
- EXIT_GATE: Story accepted, all migrated examples execute, supported suites and assets pass.
- FAILURE_ESCALATION: Stop on unresolved identity ambiguity, public behavior drift,
  or migration scope outside meld identity.

## Goals (Outcomes)
- Positional human strings resolve SpellNames.
- `spell_id=` reaches the existing machine fast lane directly.
- Human examples no longer retain implementations solely for root resolution.
- Runtime, tests, docs, and generated assets agree.
- Public construction overrides use concise `override=`.

## Non-Goals (Explicit Exclusions)
- Redesign constructor DI, SpellMap, existence, or internal compiled execution.
- Change spell-id generation or SpellIndex lineage semantics.

## Scope Boundaries
- In scope: Conduit/SpellSpace public facades, callers, docs, examples, tests, assets.
- Out of scope: unrelated resolution behavior and performance work.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: The added public override-keyword milestone is implemented
  and fully validated.

## Success Metrics
- Human and machine identity regressions pass across both public facades.
- Zero stale public `spell_name=` call sites after the selected breaking migration.
- Zero public Meld `spell_override=` call sites after the selected rename.
- README/UX examples use human SpellName strings where implementation classes were lookup-only.
- Build assets and supported test tiers pass.

## Requirements (Functional + Non-Functional)
- Preserve internal ID fast-door behavior and scope/gate/hook semantics.
- Reject simultaneous human target and `spell_id` inputs.
- Keep changes typed, documented, deterministic, and reviewable.

## Constraints / Assumptions
- Melder is pre-1.0 and the owner selected the clean public identity split.
- Machine callers can migrate explicitly to `spell_id=`.

## Dependencies / External References
- Owner-supplied `Melder DI Resolution Contract (19 Items)`.
- `context_compass/system_docs/src_components.md` Meld sections.

## Milestones (Track Progress)
- [x] Milestone 1: Public facade contract and focused regressions pass.
- [x] Milestone 2: Call sites, README, and UX examples are migrated.
- [x] Milestone 3: Documentation/assets and supported suites pass.
- [x] Milestone 4: Public `override=` migration and full regression pass.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-08-30-human-meld-identity-api - implement and migrate the contract.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete TASK-2026-08-30-meld-spell-reference-ergonomics.
- [x] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- Exact human syntax `conduit.meld("MyService")` executes.
- Exact machine syntax `conduit.meld(spell_id=<sha>)` executes without name lookup.
- Human docs and examples match executable behavior.
- Exact override syntax `conduit.meld("MyService", override={...})` executes.
- Owner confirms the delivered contract.

## Risks / Mitigations
- Broad caller migration: inventory first, make mechanical edits, then run all supported tiers.
- Generated docs drift: edit authored inputs and regenerate through the canonical runner.

## Applicable Anti-Patterns
- [x] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [x] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Focused experiment and integration regressions, then unit/component/integration
  suites, runnable-example harness, build-asset check, and diff hygiene.

## Rollout / Adoption Plan
- Breaking pre-1.0 migration completed atomically across repository-owned callers.

## Open Questions
- None; owner selected positional SpellName plus explicit `spell_id=`.

## Decision Log
- 2026-08-30: Public human and machine string identities receive separate call shapes.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/human_meld_identity_api_2026_08_30/architecture_patch.md`
  - `system_docs/patches/active/human_meld_identity_api_2026_08_30/component_patch_meld_resolution.md`
  - `system_docs/patches/active/human_meld_identity_api_2026_08_30/code_description_patch_meld_identity_dispatch.md`
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: epic acceptance

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - public meld identity
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-08-30T21:31:49Z
  TYPE: MEASURE
  CLAIM: Milestone 4 is complete. Public `override=` is atomic across runtime,
    repository callers, curriculum, canonical docs, packaged assets, and the
    10,962-test supported suite.
  EVIDENCE:
  - `context_compass/tickets/stories/2026-08-30_human_meld_identity_api_story.md`
  - `context_compass/tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md`
  IMPACT: The expanded epic is ready for owner acceptance with no technical blocker.
  NEXT: Present the final contract and wait for acceptance before closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:14:24Z
  TYPE: DECISION
  CLAIM: The epic remains atomic and now includes the short public
    `override=` keyword as part of the human-first Meld facade contract.
  EVIDENCE:
  - `context_compass/tickets/stories/2026-08-30_human_meld_identity_api_story.md`
  IMPACT: Epic review resumes only after runtime, repository callers,
    documentation, assets, and supported tests agree on the shorter keyword.
  NEXT: Execute the existing story/task extension without changing internal
    Meld execution semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T20:44:24Z
  TYPE: MEASURE
  CLAIM: The atomic public migration is implemented across facades, repository
    callers, human documentation, canonical component context, generated assets,
    and supported tests. All three epic milestones are validated.
  EVIDENCE:
  - `context_compass/tickets/stories/2026-08-30_human_meld_identity_api_story.md`
  - `context_compass/tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md`
  IMPACT: The epic is ready for owner review with no unresolved implementation
    blocker; explicit acceptance remains required before closure and artifact disposition.
  NEXT: Present the delivered public contract and validation proof to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T19:42:00Z
  TYPE: DECISION
  CLAIM: One epic owns the public facade split, repository call-site migration,
    human curriculum correction, documentation/assets, and full validation.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-08-30_meld_spell_reference_ergonomics_task.md`
  IMPACT: The breaking migration is atomic and cannot leave docs or tests on mixed semantics.
  NEXT: Create the implementation story and required patch artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program direction, migration ordering, and cross-surface acceptance.
- Reference child notes for tactical evidence.

## Context / Handoff Summary
All implementation milestones are complete and validated. The public contract is:
`meld("MyService")` or `meld(spell="MyService")` for human SpellNames,
`meld(spell=MyService)` for implementation objects, and
`meld(spell_id=<sha>)` for machine identity. Per-call construction uses
`override={...}` publicly and `spell_override` only inside the runtime.
Review and owner acceptance are the only remaining gates; tickets and active
patch artifacts remain open.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
