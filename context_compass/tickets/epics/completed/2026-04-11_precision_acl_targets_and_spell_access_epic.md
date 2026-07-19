# Epic: Precision ACL Targets And Spell Access
- Completed: 2026-04-13T21:43:06Z
- Summary: Completed the precision ACL targets-and-access epic after the retained model and the first shared viewer/command precision tranches landed.

## Metadata
- Epic ID: EPIC-2026-04-11-precision-acl-targets-and-spell-access
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T19:37:03Z
- Updated: 2026-04-13T21:43:06Z
- Target Window: 2026-Q2
- Related Program/Initiative: Rift ACL precision model for viewer and command

## Problem / Opportunity
The current ACL substrate is real, but too coarse for the next Rift lane.

What exists now:
- named frame ACL bundles
- separate child validation
- set compatibility validation
- a live viewer surface
- a live room-local command system
- published stable spell identity via `spell_index_id`

What is missing:
- a precise way to publish or deny exact frames, conduits, spells, and members
- one shared spell-access truth for both viewer and command
- a typed selector model that mirrors Meld/Spellbook lookup semantics
- a clean compiled target identity for spells (`spell_index_id`)

Without that, we keep getting stuck between:
- coarse view rules
- coarse command rules
- chat-only design decisions about which spells/methods are actually “on”

## MRP Alignment (Most Reasonable Product)
The MRP here is not “more ACL knobs.”

It is one coherent precision layer that lets the user:
- turn on a spell
- choose exactly which methods or attributes are visible
- choose exactly which methods are executable
- have viewer and command consume the same compiled truth

That is the minimum trustworthy foundation for:
- static mode
- capability mode
- later dynamic narrowing

If we do not isolate this lane, the ACL model stays smeared across view and
command concerns without one precise source of truth.

## Ticket Contract
- ENTRY_GATE: the command system, workstation, queue, and lock-hardening slices
  are landed, and the descriptor/viewer surface now publishes stable spell
  identity as `spell_index_id`.
- EXECUTION_BOUNDARY: precision ACL target model, authored selector model,
  validation, compiled spell target identity, and viewer/command consumption.
- DEPENDENCIES:
  - tickets/artifacts/nexus_acl_builder_and_persistence_model.md
  - tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md
  - tickets/tasks/2026-04-11_design_command_acl_enforcement_plan.md
  - src/melder/aether/nexus/acl/
  - src/melder/aether/nexus/frame_descriptor/
  - src/melder/aether/nexus/rift/frame_viewer/
  - src/melder/aether/nexus/rift/rift_space/command_system.py
- EXIT_GATE: one precision ACL model exists that is explicit enough to drive
  both viewer and command over frame/conduit/spell/member targets.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the precision model requires
  a broader publication or spellbook-selector redesign than this lane should own.

## Goals (Outcomes)
- Define one precision ACL layer shared by viewer and command.
- Support authored spell targeting by:
  - exact `spell_id`
  - Meld-style logical selector path
- Validate selectors through Spellbook/Meld-style lookup semantics.
- Compile spells to `spell_index_id` as the stable internal target identity.
- Keep the authored surface easier than raw generic rulesets.

## Non-Goals (Explicit Exclusions)
- Dynamic codegen validation policy redesign.
- Global endpoint/public API redesign outside Rift/Nexus.
- Replacing the current ACL shell objects wholesale.
- Renaming unrelated internal lineage/runtime identifiers beyond the already
  landed `spell_index_id` published contract.

## Scope Boundaries
- In scope:
  - precision frame/conduit/spell/member publication rules
  - selector identity and validation semantics
  - compiled target identity for spells
  - viewer + command consumption of the compiled precision layer
- Out of scope:
  - unrelated runtime hardening
  - unrelated descriptor publication work
  - UI/HUD concerns

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created to give the agreed precision ACL direction its
  own durable implementation lane before more enforcement work starts.

## Success Metrics
- One epic owns the precision ACL model directly.
- One retained artifact captures the model clearly enough for later
  implementation.
- Future work can target this lane without replaying the design discussion.

## Requirements (Functional + Non-Functional)
- Functional:
  - define typed precision rules for frame, conduit, spell, and member
  - define authored selector forms
  - define compile target identity
  - define viewer/command consumption order
- Non-functional:
  - default deny
  - no split-brain between viewer truth and command truth
  - no dependence on chat memory

## Constraints / Assumptions
- `spell_index_id` is now the published stable spell identity.
- Spell selectors must mirror existing Meld/Spellbook lookup semantics.
- Current generic rulesets are useful substrate, but not the final authoring
  surface for precise spell access.

## Dependencies / External References
- tickets/artifacts/nexus_acl_builder_and_persistence_model.md
- tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md

## Milestones (Track Progress)
- [x] Milestone 1: Lock the precision ACL model and selector identity rules
- [x] Milestone 2: Implement typed precision configuration and validation
- [x] Milestone 3: Project viewer and command from the compiled precision layer

## Stories (Required to Complete)
- [x] Story: define precision ACL target model and selector semantics
- [x] Story: implement compiled precision ACL layer for viewer and command

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: maintain the retained precision ACL artifact
- [ ] Task: verify Ticket Microcycle enforcement across active tickets/stories/tasks

## Acceptance Criteria (Epic Done)
- Precision ACLs are governed by one explicit epic.
- The retained artifact captures the model clearly enough for implementation.
- Viewer and command can be driven from one shared precision target layer.

## Risks / Mitigations
- Risk: precision logic gets split between view and command again.
  Mitigation: keep one shared precision layer and one compiled spell target identity.
- Risk: selector authoring becomes too low-level.
  Mitigation: keep the user-facing model selector-first and builder-oriented.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Start with retained design validation through artifact review.
- Later target focused ACL, viewer, and command-system slices.

## Rollout / Adoption Plan
- Stage the precision lane.
- Lock the model in the retained artifact.
- Implement typed precision configuration.
- Enforce it in viewer and command.

## Open Questions
- Should spellbook-level precision ACLs remain deferred until a stable
  spellbook selector exists?
- How much “all public” affordance should be available in the first cut?

## Decision Log
- Created after the stable published `spell_index_id` contract landed and the
  user asked to stage the precision ACL direction as durable repo memory.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-11_precision_acl_targets_and_spell_access_model.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the precision ACL runtime model is implemented
  and merged into canonical docs or intentionally retired.

## Notes
- DATETIME: 2026-04-11T19:37:03Z
  TYPE: PLAN
  CLAIM: The next ACL lane is no longer just “enforce command config.” The
    real missing piece is one precision layer that can turn on exact
    frame/conduit/spell/member targets and feed both viewer and command from
    the same compiled truth.
  EVIDENCE:
  - user_instruction: "we need a way to provide a precision set to conduit, frame, and spells"
  - user_instruction: "these can also apply to the viewer not just the command system"
  - user_instruction: "there should be a mode for this in ACLs so that we can have the viewer only show what spell is turned on"
  IMPACT: The next implementation work should not start until this precision
    model is captured cleanly as durable context.
  NEXT: create the retained artifact that defines the precision ACL model and
    tie it to this epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T21:43:06Z
  TYPE: DECISION
  CLAIM: This epic is complete. The retained precision ACL artifact exists,
    the model drove real runtime implementation, and viewer/command now share
    a materially real precision target layer through the landed selector,
    stable-lineage, and command-access slices.
  EVIDENCE:
  - tickets/artifacts/2026-04-11_precision_acl_targets_and_spell_access_model.md:1-284
  - tickets/stories/completed/2026-04-11_precision_acl_target_model_and_descriptor_validation_story.md:1-44
  - tickets/tasks/completed/2026-04-11_implement_acl_family_precision_profiles_and_validator_strategies_task.md:1-165
  - tickets/tasks/completed/2026-04-12_implement_spell_selector_resolution_and_spell_index_acl_compilation_task.md:1-145
  - tickets/tasks/completed/2026-04-12_implement_command_acl_access_enforcement_in_command_system_task.md:1-146
  IMPACT: The precision ACL epic no longer needs to remain in the active epic
    lane.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic isolates the precision ACL direction so the next thread can resume
from files instead of rebuilding the model from chat.
