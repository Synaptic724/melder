# Epic: Frame-Scoped Contract Registries And Rift Binding

## Metadata
- Epic ID: EPIC-2026-04-11-frame-scoped-contract-registries-and-rift-binding
- Status: draft
- Owner: codex
- Priority: p0
- Created: 2026-04-11T00:12:09Z
- Updated: 2026-04-11T00:12:09Z
- Target Window: 2026-Q2
- Related Program/Initiative: Rift access control and mode architecture

## Problem / Opportunity
The current ACL posture is still too close to a one-frame / one-current-ACL
model. That is too rigid for the next Rift shape.

The newly proposed direction is:
- one canonical descriptor per frame
- many ACL contracts per frame
- many codegen contracts per frame
- a Rift binds to one selected contract pair for the target frame

That gives us the flexibility to support:
- different agent skill levels
- different endpoint surfaces
- different static/capability/dynamic postures

without forcing one universal ACL answer for every consumer of a frame.

## MRP Alignment (Most Reasonable Product)
The MRP outcome is not "more ACL objects." It is a cleaner policy model:
- descriptor remains canonical frame truth
- ACL/codegen contracts become registrable policy lenses over that truth
- Rift consumes a selected lens instead of owning permission truth

If we keep the one-current-ACL-per-frame shape too long, later access-mode,
endpoint, and agent-tier work will keep fighting the wrong foundation.

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected the model toward many contracts
  per frame and a Rift-bound contract selection model.
- EXECUTION_BOUNDARY: discovery and design sequencing for frame-scoped ACL and
  codegen contract registries plus Rift binding only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
  - tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
  - src/melder/aether/nexus/acl/
  - src/melder/aether/nexus/rift/frame_link/
- EXIT_GATE: one explicit design lane exists for frame-scoped multi-contract
  registries, selected Rift binding, and the migration away from the current
  single-current-ACL assumption.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the discovery shows that
  contract registries and access-mode work cannot be separated cleanly.

## Goals (Outcomes)
- Investigate the current single-current-ACL model and its migration seams.
- Define the frame-scoped multi-contract registry model.
- Define how `FrameLinkContract` should bind selected ACL/codegen contracts.
- Produce a concrete implementation proposal before any runtime edits.

## Non-Goals (Explicit Exclusions)
- Immediate ACL subsystem implementation.
- Immediate static/capability/dynamic runtime implementation.
- CommandOps policy/agent-tier redesign.
- Broad descriptor redesign.

## Scope Boundaries
- In scope:
  - frame-scoped ACL contract registry concept
  - frame-scoped codegen contract registry concept
  - Rift-selected contract binding
  - discovery and implementation planning
- Out of scope:
  - full runtime edits
  - endpoint packaging
  - UI/HUD work

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created to isolate the new multi-contract frame policy
  direction before implementation begins.

## Success Metrics
- One dedicated epic owns the new contract-registry direction.
- The migration problem is explicit instead of living in chat only.
- A concrete implementation proposal exists before code work starts.

## Requirements (Functional + Non-Functional)
- Functional:
  - audit current ACL ownership model
  - define target contract registry shape
  - define Rift binding model
  - define migration sequencing
- Non-functional:
  - keep descriptor truth canonical
  - keep Rift as policy consumer, not policy authority
  - keep discovery evidence-backed

## Constraints / Assumptions
- Descriptor truth should remain one canonical frame aggregate.
- Many ACL/codegen contracts per frame are now the design target.
- Rift should bind to a selected contract pair rather than mutate a universal frame ACL.

## Dependencies / External References
- tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md

## Milestones (Track Progress)
- [ ] Milestone 1: Audit current ACL and Rift binding seams
- [ ] Milestone 2: Define target multi-contract model
- [ ] Milestone 3: Produce implementation proposal

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-11-investigate-multi-contract-frame-policy-model

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: audit the current Nexus ACL model and migration seams
- [ ] Task: define the target frame-scoped contract registry and Rift binding model
- [ ] Task: propose the implementation plan before runtime work
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The multi-contract frame policy model is documented, reviewed, and sequenced
  well enough that implementation can start from files instead of chat memory.

## Risks / Mitigations
- Risk: we accidentally blur base frame truth and selected policy lenses again.
  Mitigation: keep descriptor truth and contract selection explicitly separate.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Discovery and design validation first.
- No runtime validation claimed in this epic until implementation starts.

## Rollout / Adoption Plan
- Audit current model.
- Define target model.
- Propose implementation plan.
- Start runtime changes only after user review.

## Open Questions
- Where exactly should the per-frame contract registry live in Nexus ownership?
- Should ACL and codegen registries share one container or stay as sibling registries?
- How much compiled access state should be cached in `FrameLinkContract` versus recomputed?

## Decision Log
- Created after the user explicitly rejected the one-universal-ACL-per-frame
  direction in favor of many contracts per frame plus Rift-selected binding.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-11T00:12:09Z
  TYPE: PLAN
  CLAIM: The new design target is no longer "how do we vary one frame ACL per
    agent." It is "how do we support many contracts per frame and let Rift bind
    to one selected contract pair."
  EVIDENCE:
  - user_instruction: "I think we want a contract model where a rift is bound to a specific ACL contract"
  - user_instruction: "the ACLs are not universal for 1 frame, but they are registered to a frame"
  - user_instruction: "we could have multiple acls for the same frame"
  IMPACT: This needs its own discovery lane instead of being buried inside the
    older single-current-ACL design assumptions.
  NEXT: create the story and tasks, then audit the current ACL model first.
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
This epic isolates the multi-contract frame policy model so the next Rift
access-control work can be discovered and designed cleanly before implementation.
