# Epic: Publish Lesser Conduits Into Nexus Descriptor
- Completed: 2026-04-13T11:34:18Z
- Summary: Completed the lesser-conduit descriptor publication epic after the narrow publication/upgrade/remove slice landed and became settled topology substrate.

## Metadata
- Epic ID: EPIC-2026-04-11-publish-lesser-conduits-into-nexus-descriptor
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T12:20:21Z
- Updated: 2026-04-13T11:34:18Z
- Target Window: 2026-Q2
- Related Program/Initiative: Rift topology and conduit targeting surface

## Problem / Opportunity
The current descriptor/publication model only tracks normal/root conduits.
Lesser conduits are real execution scopes, but they are invisible to the
descriptor and therefore invisible to Rift-facing topology and targeting
surfaces.

## MRP Alignment (Most Reasonable Product)
The MRP outcome is narrow:
- publish lesser conduits through the existing `ConduitRecord` family
- preserve the same `conduit_id` through lesser -> normal upgrade
- remove lesser records on lesser cleanup
- do not turn frame-level summary publication into a high-frequency lesser
  topology tracker

## Ticket Contract
- ENTRY_GATE: the user explicitly approved implementing lesser-conduit
  descriptor publication after walking through the publication and upgrade
  model.
- EXECUTION_BOUNDARY: lesser conduit publish/remove/upgrade behavior only, plus
  focused tests and doc routing.
- DEPENDENCIES:
  - src/melder/aether/conduit/conduit.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/aether/nexus/frame_descriptor/conduit_record.py
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py
- EXIT_GATE: lesser conduits publish into the descriptor using the existing
  conduit record model, upgrades overwrite the same record, and cleanup removes
  the published record cleanly.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the first cut requires a new
  record family or frame-summary redesign instead of a narrow conduit-record
  expansion.

## Goals (Outcomes)
- Make lesser conduits descriptor-visible.
- Keep frame publication coarse.
- Keep conduit record identity stable through lesser -> normal upgrade.

## Non-Goals (Explicit Exclusions)
- Spellspace publication.
- Frame summary redesign for lesser counts.
- New conduit record family.
- Full static/capability command tooling.

## Scope Boundaries
- In scope:
  - lesser conduit publish gating
  - lesser conduit record removal
  - upgrade overwrite behavior
  - focused tests
- Out of scope:
  - parent_conduit_id expansion
  - frame record topology expansion
  - spell record changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved the lesser-conduit
  descriptor publication slice.

## Milestones (Track Progress)
- [x] Milestone 1: Inspect publish/remove/upgrade seams
- [x] Milestone 2: Implement lesser conduit descriptor publication
- [x] Milestone 3: Validate upgrade/remove behavior with focused tests

## Stories (Required to Complete)
- [x] Story: STORY-2026-04-11-enable-lesser-conduit-descriptor-publication

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/lesser_conduit_descriptor_publication/architecture_patch.md
  - system_docs/patches/active/lesser_conduit_descriptor_publication/component_patch_conduit.md
  - system_docs/patches/active/lesser_conduit_descriptor_publication/component_patch_frame_descriptor_manager.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the conduit publication model is merged into
  canonical docs or intentionally retired.

## Notes
- DATETIME: 2026-04-11T12:20:21Z
  TYPE: PLAN
  CLAIM: The first lesser-conduit publication cut should reuse the existing
    `ConduitRecord` family and keep frame publication coarse. That means:
    publish lesser conduits, remove them on lesser cleanup, let lesser->normal
    upgrade overwrite the same `conduit_id` record, and leave frame summary
    updates alone except where the runtime already does them.
  EVIDENCE:
  - user_instruction: "go ahead and implement this make an epic, investigate, then propose and then implement"
  - user_instruction: "the frame doesn't seem to publish often like I don't think it needs to know how many conduits are active at all times"
  IMPACT: The slice can stay narrow and avoid a frame-record redesign.
  NEXT: create the story/task lane and inspect the current lesser create,
    cleanup, and upgrade publish paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:34:18Z
  TYPE: DECISION
  CLAIM: This epic is complete. The lesser-conduit publication lane stayed
    narrow, landed through the existing `ConduitRecord` family, and later room
    and command work now treat lesser publication as settled topology
    substrate rather than as an open design lane.
  EVIDENCE:
  - tickets/stories/completed/2026-04-11_enable_lesser_conduit_descriptor_publication_story.md:1-39
  - tickets/tasks/completed/2026-04-11_implement_lesser_conduit_descriptor_publication.md:1-155
  IMPACT: The epic can move to the completed lane and stop occupying active
    planning state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This epic isolated the lesser-conduit descriptor publication slice so it could
land without smearing into broader frame-topology redesign. That slice is now
complete and archived.
