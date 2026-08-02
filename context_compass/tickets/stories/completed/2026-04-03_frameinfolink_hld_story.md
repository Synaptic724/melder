# Story: Frame Surface High-Level Design
- Completed: 2026-04-09T21:59:36Z
- Summary: Retired the frame surface HLD story at user direction and archived the lane as historical design context.


## Metadata
- Story ID: STORY-2026-04-03-frameinfolink-hld
- Epic: EPIC-2026-04-03-frame-surface-query-and-binding
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-03T11:26:49Z
- Updated: 2026-04-09T21:59:36Z

## User Narrative
As the project owner, I want a clear high-level design for the frame-scoped
surface model so the agent can understand what exists under one or more
connected frames, query it safely, and bind real objects only through the
proper Rift/conduit path.

## Value / MRP Alignment
This story protects one of the hardest parts of Rift from being built by drift.
If the frame surface is wrong, the system becomes hard to reason about,
expensive to relearn, and easy to bypass in the wrong ways.

## Ticket Contract
- ENTRY_GATE: the frame-surface epic is active and the user has corrected the
  ownership model enough to begin HLD work.
- EXECUTION_BOUNDARY: HLD and sequencing only; no runtime implementation in
  this story itself.
- DEPENDENCIES:
  - EPIC-2026-04-03-frame-surface-query-and-binding
  - TASK-2026-04-03-design-frame-surface-hld
  - TASK-2026-04-02-design-profile-contracts-and-access-boundaries
  - tickets/artifacts/aethericrift_riftspace_interaction_architecture.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_space.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_targets.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_profiles.md
- EXIT_GATE: the story clearly describes the frame-surface HLD, the ownership
  split, the query/display/bind boundary, and the next implementation slices.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the HLD still has unresolved
  object-boundary contradictions after design review.

## Requirements (Functional)
- Define the canonical link layer and its ownership.
- Define what `FrameView` is and what it owns.
- Define what `FrameViewer` is and what it owns.
- Define how ACL application is represented in links.
- Define the boundary between viewer/query and real object acquisition.
- Define how multiple frame views can be consumed together.

## Requirements (Non-Functional)
- Typed enough to implement without ambiguity.
- Explicit about ownership and update flow.
- Honest about churn/versioning limitations.
- Extensible without replacing the core model later.

## Scope Boundaries
- In scope:
  - frame-surface HLD
  - ownership boundaries
  - multi-frame viewer consumption
  - churn/weakref tradeoff framing
- Out of scope:
  - runtime coding
  - final ACL matrix
  - eventstream implementation

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the frame-surface epic now has enough corrected context to
  support a dedicated HLD story instead of only task-level notes.

## Dependencies / Related Work
- tickets/epics/2026-04-03_frameinfolink_surface_query_and_binding_epic.md
- tickets/tasks/2026-04-03_design_frameinfolink_hld_task.md
- tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-03-scaffold-frame-surface-runtime-objects - placeholder
      viewer-side object layout is landed and archived
- [x] Task: TASK-2026-04-03-implement-aethericframe-configuration-posture - frame
      posture prerequisite is landed and archived
- [ ] Task: TASK-2026-04-03-design-frame-surface-hld - define the exact HLD
- [x] Task: TASK-2026-04-04-implement-nexus-passive-ingest-and-canonical-store - implement the first passive Nexus canonical store slice
- [ ] Task: TASK-2026-04-04-extend-nexus-spell-mutation-publication - mutation
      continuity follow-up is currently blocked pending the real mutation
      object-promotion contract
- [ ] Enforce Ticket Microcycle across the active HLD task.

## Acceptance Criteria
- The HLD clearly states:
  - Nexus owns and updates canonical links
  - `FrameView` owns references to links for one frame/perspective
  - `FrameViewer` owns the methods/strategies over one or more views
  - viewer/query is separate from bind/direct object execution
- The story captures the multi-frame and churn pressures explicitly.

## Validation / Test Plan
- Design review only.
- Runtime validation deferred to follow-up implementation tasks.

## Risks / Mitigations
- Risk: the HLD still carries stale names like `FrameInfoLinkSystem` after the
  ownership model changed.
  Mitigation: keep the story and task aligned to the corrected semantics and
  treat names as provisional when needed.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether `FrameLink` remains the right final name.
- Whether Nexus needs a dedicated internal manager object for canonical links.

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-03T11:26:49Z
  TYPE: FACT
  CLAIM: This story exists because the frame-surface model is now clearly a
    story-sized problem rather than just a task note. It has an ownership
    model, a query/display/bind split, and real cross-cutting pressures like
    multi-frame viewing and rapid lower-truth churn.
  EVIDENCE:
  - tickets/tasks/2026-04-03_design_frameinfolink_hld_task.md:109-149
  - tickets/epics/2026-04-03_frameinfolink_surface_query_and_binding_epic.md:13-123
  IMPACT: The design lane is now easier to resume and reason about because the
    HLD has a proper story anchor between the epic and task.
  NEXT: continue pushing exact responsibilities down into the active task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T20:49:16Z
  TYPE: FACT
  CLAIM: The story now has a clearer next dependency. We have placeholder
    viewer-side objects, but they are not the next substance-carrying slice.
    The next substance-carrying slice is the Nexus-owned canonical
    representation store that will host the frame/conduit/spell information
    those viewer-side objects eventually consume. Until that holding zone
    exists, the HLD for views/viewers remains intentionally incomplete.
  EVIDENCE:
  - user_instruction: "we haven't built the nexus holding zone for all the objects we want to actually consume here"
  - user_instruction: "I think we go there first"
  - src/melder/aether/nexus/rift/frame_link/frame_link.py:1-170
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-172
  IMPACT: The story should now sequence into the Nexus-side canonical
    representation format before trying to overdesign viewer behavior in a
    vacuum.
  NEXT: keep the active task focused on the Nexus-side holding zone and record
    the viewer layer as dependent on it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T07:46:28Z
  TYPE: FACT
  CLAIM: The first implementation slice under the holding-zone design is now
    active. The passive-ingest task is not trying to finish the whole viewer
    model; it is focusing on the first real runtime store: private direct
    publication into `Nexus`, canonical living records, and separation between
    passive ingest and interactive `Nexus.enable(...)`.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-04_implement_nexus_passive_ingest_and_canonical_store_task.md:1-115
  IMPACT: The story now has a concrete implementation child instead of only HLD
    discussion, which should make sequencing into runtime work much easier.
  NEXT: keep the HLD and implementation task aligned while the first canonical
    store shape is defined and built.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T10:35:07Z
  TYPE: FACT
  CLAIM: The frame-surface story now has a cleaner runtime sitrep than it did
    yesterday. The viewer-side scaffold, the frame-posture prerequisite, and
    the first passive Nexus canonical-store slice are all landed and sitting in
    review, and the passive-ingest task now includes the missing Conduit-side
    publication refinements for policy changes, lesser-to-normal promotion, and
    cleanup nulling of the owned Nexus reference. The mutation-continuity child
    task still exists, but it is now explicitly provisional and blocked because
    the real mutation contract likely promotes a new Spell object under the
    lineage instead of mutating one existing Spell object's identity in place.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-03_scaffold_frame_surface_runtime_objects_task.md:1-149
  - tickets/tasks/completed/2026-04-03_implement_aetheric_frame_configuration_task.md:1-287
  - tickets/tasks/completed/2026-04-04_implement_nexus_passive_ingest_and_canonical_store_task.md:1-289
  - tickets/tasks/2026-04-04_extend_nexus_spell_mutation_publication_task.md:1-203
  IMPACT: Story sequencing is clearer now: the next real design/implementation
    push should stay on the stable frame/store/view lane and avoid pretending
    the mutation path is settled.
  NEXT: keep the HLD task active, keep the passive-ingest slice in review, and
    defer deeper mutation continuity work until the mutation object-promotion
    contract is explicitly designed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story anchors the frame-surface HLD between the epic and the active task
so the ownership and query/display/bind model can be resumed cleanly later.

