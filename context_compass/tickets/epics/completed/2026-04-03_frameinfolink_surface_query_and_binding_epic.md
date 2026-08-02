# Epic: Frame Surface Query And Binding
- Completed: 2026-04-09T21:59:36Z
- Summary: Retired the frameinfolink query-and-binding epic at user direction and archived the lane as historical context.


## Metadata
- Epic ID: EPIC-2026-04-03-frame-surface-query-and-binding
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-03T09:17:21Z
- Updated: 2026-04-09T21:59:36Z
- Target Window: 2026-Q2
- Related Program/Initiative: AR / Rift runtime maturation

## Problem / Opportunity
We now understand the agent interaction model more clearly:
- `Rift` is an execution/API surface into Melder
- `CommandOps` owns threads, actor execution, and parallel work
- static and dynamic AR both need discovery/query/resolve/bind
- only dynamic AR should expose open conduit-backed local construction
- once a real object is bound into workspace, codegen should operate on it
  first-class instead of routing every operation through the query surface

What is still missing is the concrete surface system that lets an agent:
- inspect what exists under one or more connected frames
- understand it through multiple profiles/views
- discover commands and affordances
- keep query/view concerns separate from direct object access
- consume a surface that can stay current as lower spell/conduit/frame truth changes

## MRP Alignment (Most Reasonable Product)
This is MRP-critical because it defines the intelligence-facing object
interface for the system. If the query/display/bind surface is weak, the whole
agent environment will feel confused and expensive to relearn later.

The correct MRP standard here is not a thin stopgap. It is a durable, typed,
extensible surface model we can build on without having to replace the core
mental model later.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for a new epic focused on the frame
  query/display/bind surface and then corrected the ownership model so Nexus
  owns and updates canonical links while views/viewers sit above that layer.
- EXECUTION_BOUNDARY: high-level design for frame query/display/bind surfaces,
  not runtime implementation yet.
- DEPENDENCIES:
  - tickets/tasks/2026-03-28_refactor_rift_public_surface_into_nexus_singleton_task.md
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
  - tickets/artifacts/aethericrift_riftspace_interaction_architecture.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_space.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_targets.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_profiles.md
- EXIT_GATE: one clear HLD exists for the canonical frame link layer,
  `FrameView`, `FrameViewer`, and the Nexus-owned update boundary, plus the
  object-acquisition boundary through conduit/Rift.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the HLD forces a naming or
  ownership choice the user has not approved.

## Goals (Outcomes)
- Define the frame-scoped query/display surface clearly.
- Separate display/query from object acquisition and direct execution.
- Define the stable objects that host the data and the strategies that project
  it.
- Define how multiple profile families feed the surface.
- Define generic commands the agent can discover without exposing raw objects.
- Define the ownership split where Nexus owns and updates canonical links,
  FrameView owns references to those links, and FrameViewer provides query
  methods over the resulting view.
- Define how one viewer can consume multiple frame views and build multiple
  interactive areas from them.

## Non-Goals (Explicit Exclusions)
- Final runtime implementation.
- Full eventstream implementation.
- CommandOps thread scheduling design.
- Final UI/HUD design.

## Scope Boundaries
- In scope:
  - canonical frame link layer
  - `FrameView`
  - `FrameViewer`
  - Nexus-owned link update boundary
  - query/display contracts
  - bind boundary
  - command discovery surface
- Out of scope:
  - full ACL implementation details
  - conduit construction semantics beyond the static/dynamic distinction
  - direct multi-agent comms design

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked for a new epic centered on the
  frame query/display/bind surface instead of leaving the idea inside the
  broader profile/access discussion.

## Success Metrics
- One clear frame-scoped surface model exists.
- Future re-entry can explain where query, bind, and direct execution live.
- The design stays extensible through strategies rather than hardcoding one
  view forever.

## Requirements (Functional + Non-Functional)
- Functional:
  - discover frame-scoped nodes and affordances
  - project multiple profile families into one query surface
  - expose generic commands
  - keep direct object access out of the viewer surface
  - support later binding into workspace
- Non-functional:
  - typed
  - extensible
  - strategy-driven
  - durable under repo growth
  - coherent with static/dynamic AR split

## Constraints / Assumptions
- `FrameViewer` should not hand out raw object references.
- Real object acquisition should still go through conduit/Rift resolution paths.
- The same underlying frame/object truth may need multiple projected views.
- Nexus should own and update canonical frame links when lower runtime truth
  changes.
- `FrameView` should own references to links for one perspective.
- ACL/contract logic should be represented in links after policy application,
  not executed by the viewer.
- Core model should stay deterministic first; weakref-driven auto-updates are a
  later optimization path, not the initial source-of-truth model.

## Dependencies / External References
- `src/melder/spellbook/spell_crafter/spell_examiner/*`
- `src/melder/aether/structure_profiles/*`
- `src/melder/aether/nexus/*`
- `codex/context_compass/tickets/artifacts/aethericrift_riftspace_interaction_architecture.md`

## Milestones (Track Progress)
- [ ] Milestone 1: Lock object responsibilities and boundaries.
- [ ] Milestone 2: Lock view/projection strategy model.
- [ ] Milestone 3: Lock query/bind/direct-execution boundary.
- [ ] Milestone 4: Create implementation-ready stories/tasks.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-03-frameinfolink-hld - define the HLD for frame query/display/bind surfaces

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Review/close TASK-2026-04-03-scaffold-frame-surface-runtime-objects
- [x] Task: Review/close TASK-2026-04-03-implement-aethericframe-configuration-posture
- [ ] Task: Complete story STORY-2026-04-03-frameinfolink-hld
- [x] Task: Complete TASK-2026-04-04-implement-nexus-passive-ingest-and-canonical-store
- [ ] Task: Hold TASK-2026-04-04-extend-nexus-spell-mutation-publication until
      the real mutation object-promotion contract is defined
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- `FrameInfoLink`, `FrameView`, `FrameViewer`, and `FrameInfoLinkSystem` have
  a documented HLD.
- The boundary between query/display and real object acquisition is explicit.
- The user accepts the design enough to move into implementation planning.

## Risks / Mitigations
- Risk: the viewer layer becomes a disguised object-access backdoor.
  - Mitigation: keep raw acquisition behind conduit/Rift bind APIs.
- Risk: too many overlapping objects make the surface harder, not easier.
  - Mitigation: keep each object responsibility narrow and explicit.

## Validation / Test Approach
- Design validation through ticket notes, artifact alignment, and user review.
- Runtime validation deferred to implementation tasks.

## Rollout / Adoption Plan
- Lock the HLD first.
- Then design the profile-to-surface mapping.
- Then design the bind boundary.
- Then implement the surface system.

## Open Questions
- Whether `FrameLink` remains the right final name or whether a less overloaded
  term should replace it later.
- Whether the canonical link-update machinery should live directly on `Nexus`
  or behind a dedicated Nexus-owned manager object.
- How to represent rapid spell-version churn when spells do not currently live
  inside a shell that models multiple simultaneous versions.
- Whether weakref-backed subscriptions are worth the complexity later for
  high-churn update paths.

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-03T09:17:21Z
  TYPE: FACT
  CLAIM: The user wants the next HLD focused specifically on a frame-scoped
    query/display/bind system. The proposed working object names are
    `FrameInfoLink`, `FrameView`, `FrameViewer`, and `FrameInfoLinkSystem`.
    The hard design rule is that the viewer surface should help the agent find
    and understand things, but should not itself grant raw object access; real
    object acquisition should still happen through the conduit/Rift resolution
    path.
  EVIDENCE:
  - user_instruction: "we need FrameLink to host all the different objects that can be viewed"
  - user_instruction: "FrameLinkSystem will host the strategies we use to view them"
  - user_instruction: "maybe we have the FrameViewer"
  - user_instruction: "we don't want the frame viewer to give you actual access to the objects you'd call the conduit and grab things instead right?"
  IMPACT: This deserves its own design epic instead of being diluted inside the
    broader profile/access lane.
  NEXT: create the first HLD task for the frame surface objects and strategy model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T09:35:02Z
  TYPE: DECISION
  CLAIM: The HLD ownership model is now corrected. Nexus should own and update
    the canonical frame link representations. `FrameView` should own
    references to those links for one applied perspective. `FrameViewer`
    should provide the methods that query/interact with a view. ACLs do not
    live in the viewer; they are represented in the links after Nexus applies
    the relevant frame/rift/spell/conduit policy.
  EVIDENCE:
  - user_instruction: "the FrameView should own the objects and the Viewer should have the methods to interact with them right?"
  - user_instruction: "the Nexus updates links if something changes"
  - user_instruction: "ACLs don't live in the FrameLink they are just represented there"
  IMPACT: The epic should now be read as a Nexus-owned canonical-surface design
    problem rather than a Rift-owned viewer-store design problem.
  NEXT: update the first HLD task to reflect the corrected ownership split and
    then define exact responsibilities under that model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T11:26:49Z
  TYPE: FACT
  CLAIM: The frame-surface design now has two more first-class pressures
    captured explicitly. First, one `FrameViewer` may need to consume multiple
    `FrameView` objects so it can build multiple interactive areas across
    contracts that span more than one frame. Second, lower truth may churn
    quickly, including repeated spell mutation, so the update model must
    acknowledge version/churn cost honestly. Weak references may help later,
    but they are not the first deterministic ownership model. The fact that
    spells do not currently live in a shell that models multiple simultaneous
    versions is now an explicit open pressure on the design.
  EVIDENCE:
  - user_instruction: "we might have multiple frames in the contracts, right?"
  - user_instruction: "the Viewer can build multiple interactive areas because its the final output consumer"
  - user_instruction: "things will change quickly and sometimes a spell might mutate a few times in a few minutes"
  - user_instruction: "spells don't live in a shell that can represent multiple versions"
  IMPACT: The epic now more accurately reflects the real complexity of the
    frame-surface model instead of stopping at a simpler single-frame snapshot
    story.
  NEXT: keep these pressures front and center while defining the exact object
    responsibilities in the HLD task and story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T20:49:16Z
  TYPE: FACT
  CLAIM: The frame-surface lane is now at the point where the next real design
    target is not more viewer polish but the Nexus-side holding zone for the
    canonical representations the viewer layer will consume. The current
    `FrameLink`, `FrameLinkContract`, `FrameView`, and `FrameViewer` files are
    only placeholder shells; that is intentional. The missing substance is the
    Nexus-owned canonical representation store and update API that can keep
    frame/conduit/spell information current as lower runtime truth changes.
  EVIDENCE:
  - user_instruction: "we haven't built the nexus holding zone for all the objects we want to actually consume here"
  - user_instruction: "I think we go there first"
  - src/melder/aether/nexus/rift/frame_link/frame_link.py:1-170
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-149
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-141
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-172
  IMPACT: The epic should now be read as sequencing into a Nexus-owned
    canonical representation store before substantial viewer/view integration
    work. Until that store exists, the frame-surface objects remain scaffolding
    only.
  NEXT: update the story and active task so the next concrete slice is the
    Nexus-side holding zone / canonical representation format.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T07:46:28Z
  TYPE: FACT
  CLAIM: The epic now has its first concrete runtime child for the holding-zone
    problem. The new passive-ingest task activates the implementation path for
    canonical Nexus records without trying to solve the whole viewer model at
    once. Its explicit stance is that record hosting should begin before
    interactive Rift enablement and should be gated by frame posture rather
    than by `Nexus.enable(...)`.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-04_implement_nexus_passive_ingest_and_canonical_store_task.md:1-115
  IMPACT: The epic now has a clearer sequence: frame posture prerequisite,
    passive canonical store, then deeper viewer/query integration on top of
    that store.
  NEXT: keep the implementation task narrow and use it to validate the store
    model before expanding further into view/viewer work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T10:35:07Z
  TYPE: FACT
  CLAIM: The active epic is now better synchronized to the actual implementation
    stack beneath it. The viewer-side scaffold and frame-posture prerequisite
    are both landed and in review, the passive Nexus canonical-store slice is
    landed and now includes the missing Conduit-side publication refinements,
    and the mutation-continuity follow-up is no longer being treated as settled
    architecture. It is now explicitly a blocked/provisional child because the
    real mutation contract likely requires promoting a new Spell object under a
    stable lineage instead of mutating one Spell object's identity in place.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-03_scaffold_frame_surface_runtime_objects_task.md:1-149
  - tickets/tasks/completed/2026-04-03_implement_aetheric_frame_configuration_task.md:1-287
  - tickets/tasks/completed/2026-04-04_implement_nexus_passive_ingest_and_canonical_store_task.md:1-289
  - tickets/tasks/2026-04-04_extend_nexus_spell_mutation_publication_task.md:1-203
  IMPACT: Epic sequencing is cleaner: frame/view/store work can keep advancing
    on stable assumptions, while mutation-specific continuity is deferred until
    its real contract is designed instead of being normalized prematurely.
  NEXT: keep the HLD and passive-store lane as the main active path and treat
    mutation continuity as a later contract-design problem.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic exists to define the frame-scoped query/display/bind surface model
with Nexus owning and updating canonical links before implementation hardens a
weak or leaky API.

