# Epic: Refactor Nexus Frame State Around FrameDescriptor
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the Nexus frame-state aggregate refactor epic and archived the finished FrameDescriptor-centered migration lane.


## Metadata
- Epic ID: EPIC-2026-04-04-refactor-nexus-frame-state-around-aethericframe-descriptor
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-04T13:10:15Z
- Updated: 2026-04-09T21:59:36Z
- Target Window: 2026-Q2
- Related Program/Initiative: Frame surface / Nexus maturation

## Problem / Opportunity
The first passive-ingest slice proved the need for Nexus-owned frame-scoped
state, but the current shape is too fragmented:
- flat `NexusCanonicalStore` fields
- `FrameRecord`
- `AethericFrameConfiguration`
- `NexusFrameRecord`
- future ACLs
- future compiled access/view state

That fragmentation will get worse if we keep layering viewer and ACL work on
top of it. The next coherent step is to make the frame itself the aggregate
unit inside Nexus.

## MRP Alignment (Most Reasonable Product)
This is MRP-critical because the frame is the real consumer boundary for:
- records
- posture
- ACLs
- frame-owned summaries
- future compiled access contracts

If we keep the current flat store shape too long, we will harden the wrong
internal model and pay for it in every later frame/view/ACL change.

## Ticket Contract
- ENTRY_GATE: the first passive-ingest slice is done enough to archive and the
  user explicitly wants the frame-scoped Nexus state reconfigured around one
  aggregate object.
- EXECUTION_BOUNDARY: staged Nexus-internal refactor only; move frame-scoped
  state under one aggregate object and update publication paths in multiple
  slices.
- DEPENDENCIES:
  - tickets/tasks/completed/2026-04-04_implement_nexus_passive_ingest_and_canonical_store_task.md
  - tickets/tasks/2026-04-03_design_frameinfolink_hld_task.md
  - src/melder/aether/nexus/
  - src/melder/aether/aetheric_frame.py
- EXIT_GATE: Nexus frame-scoped state is reorganized around
  `FrameDescriptor`, the migration is staged in multiple small slices,
  and the next viewer/ACL work can target one coherent frame aggregate instead
  of flat split state.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the refactor forces a public
  API change or a viewer/ACL decision the user has not approved.

## Goals (Outcomes)
- Introduce `FrameDescriptor` as the frame-scoped Nexus aggregate.
- Move frame posture, frame overview, Nexus-managed frame metadata, frame-local
  records, and future ACL/container state under it.
- Remove the need for flat frame-scoped fields directly on `Nexus`.
- Stage the migration across multiple implementation slices instead of one
  giant patch.

## Non-Goals (Explicit Exclusions)
- Final viewer implementation.
- Final ACL implementation.
- MutationResearch runtime design.
- Transport/auth work.

## Scope Boundaries
- In scope:
  - Nexus-internal frame aggregate design
  - migration plan from flat store to descriptor
  - staged runtime implementation slices
- Out of scope:
  - public `Nexus` API redesign
  - final frame/view/contract/codegen surfaces

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly redirected the lane to a frame-scoped
  Nexus aggregate refactor before deeper ACL/view work continues.

## Success Metrics
- One clear frame aggregate exists in Nexus.
- Frame-scoped state no longer lives in scattered flat fields.
- Later viewer/ACL work can target the descriptor directly.

## Requirements (Functional + Non-Functional)
- Functional:
  - own one descriptor per frame
  - host frame posture/config/overview inside the descriptor
  - host frame-local conduit/spell entries and indexes inside the descriptor
  - host `NexusFrameRecord` inside the descriptor when applicable
- Non-functional:
  - staged migration
  - no giant single-step refactor
  - low regression risk
  - deterministic internal ownership

## Constraints / Assumptions
- `FrameDescriptor` is a Nexus-side aggregate, not a replacement for
  the real runtime `AethericFrame`.
- `AethericFrameConfiguration` should live inside the descriptor, not beside it.
- `NexusFrameRecord` should remain distinct metadata, but should live inside
  the descriptor instead of as another top-level parallel structure.

## Milestones (Track Progress)
- [ ] Milestone 1: Create epic/story/task + patch lane for descriptor refactor.
- [ ] Milestone 2: Investigate the exact migration surface and staged slices.
- [ ] Milestone 3: Implement first descriptor slice.
- [ ] Milestone 4: Complete migration away from flat frame-scoped store state.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-04-aethericframe-descriptor-refactor - design and stage the descriptor migration

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-04-04-aethericframe-descriptor-refactor
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- `FrameDescriptor` exists and becomes the frame-scoped Nexus aggregate.
- Flat frame-scoped Nexus state is migrated under the descriptor.
- The migration happened in multiple staged slices with passing focused validation.

## Risks / Mitigations
- Risk: the refactor turns into a giant unsafe rename/move patch.
  Mitigation: stage it across investigation + multiple implementation tasks.
- Risk: `NexusFrameRecord` and `FrameRecord` semantics get blurred.
  Mitigation: keep them distinct nested parts inside the descriptor.

## Validation / Test Approach
- Focused unit validation after each migration slice.
- No claim of broad completion until the flat frame-scoped fields are actually gone.

## Rollout / Adoption Plan
- Add the planning lane first.
- Investigate current runtime and patch the descriptor lane.
- Introduce `FrameDescriptor`.
- Migrate the first safe frame-scoped fields into it.
- Retarget publication paths in later slices.

## Open Questions
- Exact internal names for the moved frame overview and entry containers.
- Whether the first descriptor slice should wrap the current store or replace it.

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-04T19:25:19Z
  TYPE: FACT
  CLAIM: The descriptor refactor tranche is now functionally complete at the
    task level. The frame-scoped Nexus aggregate exists, the flat runtime store
    residue is gone, and the remaining active work has shifted up-stack into
    ACL and frame/view design. This epic remains useful as historical context,
    but it is no longer the live implementation lane.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-04_investigate_aethericframe_descriptor_refactor_task.md:1-322
  IMPACT: The active board no longer needs a descriptor-task row, and future
    work should only reopen this epic if another internal frame-aggregate
    refactor is explicitly requested.
  NEXT: leave the epic as reference and keep the active routing focused on ACL
    and frame-surface work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T13:10:15Z
  TYPE: FACT
  CLAIM: The user explicitly wants the scattered Nexus frame-scoped state
    reorganized around one aggregate object named `FrameDescriptor`.
    The intended role is: one Nexus-side frame descriptor per frame that can
    host frame posture/configuration, frame overview data, `NexusFrameRecord`,
    frame-local records, and later ACL/container state, instead of keeping
    those concerns split across multiple top-level fields on `Nexus`.
  EVIDENCE:
  - user_instruction: "We need a single object that can host all this shit"
  - user_instruction: "lets call it str -> FrameDescriptor"
  - user_instruction: "The NexusFrameRecord can go inside it too"
  IMPACT: The next work should stop extending the flat Nexus frame-state shape
    and instead stage a real aggregate migration.
  NEXT: create the story/task and patch-doc lane, then investigate the exact
    migration surface before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when migration scope, ownership boundaries, or staging order change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic anchors the Nexus frame-state refactor around
`FrameDescriptor` so later viewer and ACL work can target a coherent
frame-scoped aggregate instead of a fragmented flat store.

