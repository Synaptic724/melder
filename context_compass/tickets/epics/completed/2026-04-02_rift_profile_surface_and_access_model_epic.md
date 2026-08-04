# Epic: Rift Profile Surface And Access Model
- Completed: 2026-05-16T16:41:00Z
- Summary: Closed at user direction as a retained design baseline for later
  profile, ACL, descriptor, and Rift runtime implementation lanes.

## Metadata
- Epic ID: EPIC-2026-04-02-rift-profile-surface-and-access-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-02T22:25:55Z
- Updated: 2026-05-16T16:41:00Z
- Target Window: 2026-Q2
- Related Program/Initiative: AR / Rift runtime maturation

## Problem / Opportunity
The live runtime now has enough pieces to expose a serious AR-facing working
surface, but the data contracts that should feed that surface are still not
cleanly separated. We have:
- semantic/introspection data in `SpellAIProfile`
- structural/runtime-topology data in structure profiles
- policy/access decisions not yet defined cleanly
- Rift/Nexus session state with no finished aggregation model

If we do not separate these now, we will end up smearing meaning, topology,
ACLs, and session state together in a way that will be hard to reason about
later and expensive to relearn.

## MRP Alignment (Most Reasonable Product)
This is MRP-critical because these profile/access contracts will become the
intelligence-facing understanding surface of the system. They must be durable,
holistic, and extensible enough that we do not need to rebuild the conceptual
model later.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved focusing on the data model first and
  treating this as a holistic, MRP-level design problem rather than a minimal
  patch.
- EXECUTION_BOUNDARY: profile-data contracts, ACL contracts, and Rift-side
  aggregation design only.
- DEPENDENCIES:
  - tickets/tasks/2026-03-28_refactor_rift_public_surface_into_nexus_singleton_task.md
  - src/melder/spellbook/spell_crafter/spell_examiner/
  - src/melder/aether/structure_profiles/
  - src/melder/aether/nexus/
- EXIT_GATE: the repo has a coherent design plan for semantic profiles,
  structure profiles, ACL/access decisions, and the later Rift aggregation
  layer.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the design forces a major
  public-contract decision the user has not approved.

## Goals (Outcomes)
- Separate semantic, structural, access, and session concerns cleanly.
- Define what data belongs in `SpellAIProfile`.
- Define what data belongs in structure profiles.
- Define how ACL/access policy should sit on top without polluting profile
  layers.
- Define which object should aggregate and consume the data on the Rift side.
- Keep the profile model extensible through explicit strategy/contract seams.
- Define the layered ACL ownership model across Spell, Spellbook, Conduit, and
  Frame.
- Define the merge rule that compiles those raw ACL specs into one derived
  access contract for view/contract/codegen consumers.
- Define the frame-scoped ACL subsystem objects that live under one
  descriptor-backed manager and eventually feed Rift-facing contract
  propagation.

## Non-Goals (Explicit Exclusions)
- Full Rift event queue implementation in this epic's first slice.
- Full workspace execution/agent tooling implementation.
- MutationResearch runtime implementation.

## Scope Boundaries
- In scope:
  - `SpellAIProfile`
  - `SpellBindingProfile`
  - `SpellResolutionProfile`
  - structure profile models/builders
  - ACL / access-decision design
  - Rift aggregation responsibility design
- Out of scope:
  - final UI display semantics
  - CommandOps communication semantics
  - multi-agent comms model

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly wants this treated as an epic-level,
  holistic design problem and approved starting with profile data contracts.

## Success Metrics
- One clean separation exists between semantic, structural, access, and
  session layers.
- Future re-entry can explain where a field belongs without ambiguity.
- The design is extensible without rewriting the base model.

## Requirements (Functional + Non-Functional)
- Functional:
  - support agent-facing semantic understanding
  - support system-topology understanding
  - support access control decisions
  - support later Rift aggregation
- Non-functional:
  - explicit and typed
  - strategy-friendly/extensible
  - durable under repo growth
  - coherent with MRP and no-MVP posture

## Constraints / Assumptions
- `SpellAIProfile` should not become a dumping ground for session/access data.
- Structure profiles should remain runtime/system-shape oriented.
- ACL policy should remain separable from both semantic and structural profiles.
- Rift aggregation should come after the lower data contracts are solid.
- Raw ACL specs should live on real runtime ownership layers, not inside one
  vague middleware blob.
- Lower/more specific ACL layers should narrow/filter broader ones rather than
  silently widen access above a higher-level deny.

## Proposed Layered ACL Model
The current design direction is:

### Raw ACL ownership layers
- `Spell`
  - method visibility
  - attribute visibility
  - full-spell deny
- `Spellbook`
  - spell/spell-index allow/deny shaping
  - broader spellbook-scoped restrictions
- `Conduit`
  - conduit/root/link access restrictions
- `AethericFrame`
  - coarse conduit and spell shaping at frame scope

### Merge rule
- Higher layers define the broad candidate access picture.
- Lower/more specific layers filter that picture.
- Effective access is compiled as a narrowing/intersection pipeline, not
  last-writer-wins widening.

### Derived result
- Nexus should collect the raw ACL specs and compile them into a derived access
  contract/result.
- That derived contract is what future frame/view/contract/codegen layers
  consume.
- Raw substrate link contracts remain separate from the future top-side
  frame/view access contract.

## Current ACL Subsystem Direction
The next implementation slice should treat ACLs as a frame-scoped subsystem
owned under the descriptor boundary.

### Ownership chain
- `Nexus`
  - façade/root
  - owns one `FrameACLManager`
- `FrameACLManager`
  - owns `frame_name -> FrameACLContainer`
- `FrameDescriptor`
  - remains the canonical frame/runtime aggregate
- `FrameACLContainer`
  - holds the frame-scoped ACL objects for that frame only:
    - current `FrameACLConfiguration`
    - bounded configuration history
    - one frame-scoped `FrameACLBuilder`
    - one `FrameACLValidator`

### Builder semantics
- one builder object per frame container
- returned from the container each time rather than recreated ad hoc
- one writer flow per frame
- builder owns the ACL change process
- descriptor creation should also ensure the matching frame ACL container
  exists and is initialized with defaults

### Configuration semantics
- one current frame ACL configuration per frame
- history retained in bounded form for rollback
- JSON load/store is part of the subsystem story
- config changes should propagate into the Rift-facing consumer surfaces and
  codegen validation surfaces as the system settles

## Dependencies / External References
- `src/melder/spellbook/spell_crafter/spell_examiner/*`
- `src/melder/aether/structure_profiles/*`
- `src/melder/aether/nexus/*`

## Milestones (Track Progress)
- [ ] Milestone 1: Define semantic vs structural vs access boundaries.
- [ ] Milestone 2: Design field-level contract changes.
- [ ] Milestone 3: Design Rift-side aggregation responsibility.
- [ ] Milestone 4: Implement profile-layer improvements.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-02-profile-contracts-and-access-boundaries - define the profile/ACL responsibility split
- [ ] Story: STORY-2026-04-02-rift-aggregation-and-event-consumption-model - define how Rift consumes and surfaces the data
- [ ] Story: STORY-2026-04-04-frame-acl-subsystem-bootstrap - scaffold the
      first descriptor-backed ACL subsystem objects

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-04-02-profile-contracts-and-access-boundaries
- [x] Task: Complete TASK-2026-04-04-enforce-root-conduit-name-uniqueness-for-acl-selectors
- [ ] Task: Complete story STORY-2026-04-04-frame-acl-subsystem-bootstrap
- [ ] Task: Complete story STORY-2026-04-02-rift-aggregation-and-event-consumption-model
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- A field-by-field contract exists for semantic profiles, structure profiles,
  access decisions, and Rift aggregation.
- The user accepts the separation and sequencing.
- Follow-up implementation tickets are created and routed.

## Risks / Mitigations
- Risk: profile responsibilities bleed into each other.
  - Mitigation: enforce explicit layer ownership.
- Risk: ACLs get buried inside AI or structure profiles.
  - Mitigation: keep access decisions a separate contract.

## Validation / Test Approach
- Design validation through source-evidence review and explicit contract review.
- Runtime tests deferred to implementation tasks.

## Rollout / Adoption Plan
- Define contracts first.
- Then implement profile-layer improvements.
- Then build ACL layer.
- Then build Rift aggregation layer.

## Open Questions
- Whether access decisions should be one unified object or multiple narrower
  policy outputs.
- How much of `SpellResolutionProfile` should stay placeholder vs be expanded.

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/nexus_acl_builder_and_persistence_model.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-04T21:59:53Z
  TYPE: DECISION
  CLAIM: The ACL epic now has a corrected first implementation-facing subsystem
    shape. `Nexus` should stay the faÃ§ade/root, the `FrameDescriptor`
    `FrameACLManager`. That manager should own a dictionary of
    `frame_name -> FrameACLContainer`. The descriptor remains the canonical
    frame/runtime aggregate, but descriptor creation should also ensure the ACL
    manager creates a matching frame ACL container with default objects. The
    container should hold the frame-scoped ACL
    objects for one frame only: the current configuration, bounded history, one
    builder object, and one validator. The builder is object-singleton per
    frame container rather than a process singleton or an unlimited draft
    factory.
  EVIDENCE:
  - user_instruction: "FrameACLContainer can hold history of different configurations and the builder and anything else we might need to hold in there"
  - user_instruction: "there is only 1 builder and we make it a object based singleton"
  - user_instruction: "Nexus owns the FrameACLManager and then it owns inside it all those other objects"
  IMPACT: We now have enough structure to start a bounded placeholder
    implementation slice instead of staying in pure ACL theory, and the
    ownership split no longer overloads the descriptor with ACL manager duties.
  NEXT: create the frame ACL subsystem bootstrap story/task and scaffold the
    placeholder objects under `src/melder/aether/nexus/`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T19:42:03Z
  TYPE: FACT
  CLAIM: The ACL epic now has a single artifact that captures the current
    implementation-facing design direction in much greater detail than the epic
    notes alone: builder-first authoring, persisted selector-first ACL
    documents, descriptor-owned management/validation/compiled-access systems,
    stable selectors, and validated path-gating semantics.
  EVIDENCE:
  - codex/context_compass/tickets/artifacts/nexus_acl_builder_and_persistence_model.md:1-267
  IMPACT: The next thread can restart the ACL lane from a dedicated design
    artifact rather than from reconstructed note fragments.
  NEXT: use the artifact as the main ACL implementation/design reference.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T19:25:19Z
  TYPE: FACT
  CLAIM: The ACL epic now has one concrete runtime prerequisite completed. Root
    and normal conduit names are enforced unique per frame with `"default"`
    fallback and cleanup unregistration, so conduit names can now serve as
    stable persisted ACL selectors instead of remaining cloud-only optional
    metadata.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-04_enforce_root_conduit_name_uniqueness_for_acl_selectors_task.md:1-205
  IMPACT: The remaining ACL design work can focus on builder/document shape and
    compilation rather than reopening conduit selector identity.
  NEXT: continue the active ACL task on the builder/document/compile model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T12:05:48Z
  TYPE: DECISION
  CLAIM: The ACL side of this epic is now much sharper than before. The active
    direction is a layered ACL ownership model attached to real Melder objects
    (Spell, Spellbook, Conduit, Frame), not one flat policy blob. Raw ACL specs
    should be collected by Nexus and compiled into a derived access contract for
    future frame/view/contract/codegen consumers. Merge semantics should be
    narrowing/intersection by default so lower/more specific layers filter
    broader ones instead of widening access silently.
  EVIDENCE:
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:112-166
  - user_instruction: "ACLs were meant to be Spell Level"
  - user_instruction: "Spellbook level"
  - user_instruction: "Conduit Level"
  - user_instruction: "final Frame level"
  - user_instruction: "the bottom variant would outrank the higher varients"
  IMPACT: The epic now has a real access-model spine instead of only generic
    ACL language. The next task-level work should define the exact ACL spec
    schemas and the derived access contract shape.
  NEXT: route the missing story file and keep the active task focused on ACL
    schema plus merge-rule definition.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T23:00:19Z
  TYPE: FACT
  CLAIM: The ACL lane now has its first real reusable profile foundation
    landed. `FrameACLManager` owns a SpellExaminer-style
    `FrameACLProfileBuilder`, the reusable profile side is typed
    (`FrameACLRule`, `FrameACLRuleSet`, typed view/codegen profiles, composed
    `FrameACLProfile`), and focused ACL profile/manager/Nexus profile tests
    passed. The manager/container/chain shell remains intact, so the next ACL
    tranche can focus on typed `FrameACLConfiguration` and
    `FrameACLViewConfiguration` rather than rebuilding the whole subsystem.
  EVIDENCE:
  - tickets/tasks/2026-04-05_implement_frame_acl_profile_builder_foundation.md:1-190
  IMPACT: The ACL program now has a real reusable substrate instead of only
    design notes and placeholder JSON-holder objects.
  NEXT: decide the next bounded ACL tranche:
    typed `FrameACLConfiguration` / `FrameACLViewConfiguration`
    or another selector/contract refinement pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T23:51:00Z
  TYPE: FACT
  CLAIM: The ACL reusable profile foundation is now materially useful, not just
    typed. The manager-owned profile builder seeds a real named ladder:
    `safe`, `hybrid`, `permissive` for both view and codegen, with curated rule
    content and ACL profile version metadata. Focused ACL profile/manager/Nexus
    profile tests passed.
  EVIDENCE:
  - tickets/tasks/2026-04-05_implement_frame_acl_safe_default_profiles_task.md:1-180
  IMPACT: The next ACL tranche can move into typed configuration work on top of
    an actual reusable profile catalog instead of empty defaults.
  NEXT: decide whether the next bounded ACL tranche should be typed
    `FrameACLConfiguration` / `FrameACLViewConfiguration`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:00:41Z
  TYPE: FACT
  CLAIM: The ACL lane now has a typed applied configuration layer on top of the
    reusable named profile catalog. The system has moved from:
    - placeholder JSON-holder reusable profiles
    - placeholder JSON-holder applied configuration
    to:
    - typed reusable named profiles (`safe`, `hybrid`, `permissive`)
    - typed `FrameACLViewConfiguration`
    - typed `FrameACLCodegenConfiguration`
    - typed root `FrameACLConfiguration`
    - typed builder draft/apply/commit flow
    Focused ACL configuration/builder/container/validator tests passed.
  EVIDENCE:
  - tickets/tasks/2026-04-05_implement_frame_acl_typed_configuration_foundation.md:1-190
  IMPACT: The next ACL tranche can stop dealing with storage/model scaffolding
    and move into the actual descriptor-backed validator/compiler path.
  NEXT: decide whether the next bounded ACL tranche should target the
    validator/compiler path over payload-backed descriptor records.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-02T22:25:55Z
  TYPE: FACT
  CLAIM: The user explicitly wants this handled as an epic-level, holistic
    design problem. The guiding principle is not minimum viable data, but the
    strongest durable understanding surface we can build the first time. The
    current direction is to separate semantic profiles, structure profiles,
    ACLs/access decisions, and Rift-side aggregation rather than collapsing
    them together.
  EVIDENCE:
  - user_instruction: "lets make an epic"
  - user_instruction: "we need a holistic solution"
  - user_instruction: "we focus on the profiles to give the most potential then go to ACLs, and then build the next stuff for the rift right?"
  IMPACT: This should be routed as a real design program, not a one-off note
    in the old Nexus task.
  NEXT: create the first task for field-level profile and access-boundary
    design.
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
This epic exists to design the holistic profile/ACL/Rift-surface model before
implementation hardens the wrong contracts.
