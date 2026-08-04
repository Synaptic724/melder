# Story: Profile Contracts And Access Boundaries

## Metadata
- Story ID: STORY-2026-04-02-profile-contracts-and-access-boundaries
- Epic: EPIC-2026-04-02-rift-profile-surface-and-access-model
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-04-04T12:05:48Z
- Updated: 2026-04-04T19:42:03Z

## User Narrative
As the project owner, I want the profile/ACL contract model written down as a
real story so the access layer can be designed as a durable system contract
instead of drifting between runtime permissions, conduit policies, and viewer
assumptions.

## Value / MRP Alignment
This story protects a core MRP boundary. If ACLs are vague or attached to the
wrong layer, then view generation, contract behavior, and codegen validation
will all learn the wrong semantics and have to be rebuilt later.

## Ticket Contract
- ENTRY_GATE: the profile/access epic is already active and the user has now
  defined a concrete layered ACL direction.
- EXECUTION_BOUNDARY: design and sequencing only; no runtime ACL implementation
  in this story.
- DEPENDENCIES:
  - EPIC-2026-04-02-rift-profile-surface-and-access-model
  - TASK-2026-04-02-design-profile-contracts-and-access-boundaries
  - codex/context_compass/tickets/artifacts/nexus_acl_builder_and_persistence_model.md
  - codex/context_compass/tickets/artifacts/ai_profile_and_policy_middleware_design.md
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md
  - codex/context_compass/tickets/artifacts/codegen_validation_pipeline_design.md
- EXIT_GATE: the story defines the layered ACL ownership model, the merge rule,
  and the next implementation/design tasks needed to realize it.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the ACL merge semantics or
  ownership surfaces remain contradictory after design review.

## Requirements (Functional)
- Define the four ACL ownership layers:
  - spell
  - spellbook
  - conduit
  - frame
- Define what each layer is allowed to express.
- Define the merge rule between those layers.
- Define the derived access object that downstream view/contract/codegen layers
  will consume.
- Keep substrate link contracts separate from top-side frame/view contracts.

## Requirements (Non-Functional)
- Deterministic.
- Set-friendly and fast to evaluate.
- Narrowing by default instead of silently widening access.
- Compatible with later Nexus-side compilation and caching.

## Scope Boundaries
- In scope:
  - layered ACL ownership model
  - merge/precedence rule
  - derived access contract direction
  - operation buckets for future access filtering
- Out of scope:
  - runtime code implementation
  - final viewer integration
  - transport/auth wrappers

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the ACL direction now has enough concrete user-defined
  structure to justify a story-level design anchor under the existing epic.

## Dependencies / Related Work
- tickets/epics/2026-04-02_rift_profile_surface_and_access_model_epic.md
- tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-02-design-profile-contracts-and-access-boundaries -
      define the layered ACL spec and merge rules
- [x] Task: TASK-2026-04-04-enforce-root-conduit-name-uniqueness-for-acl-selectors -
      land the root/normal conduit naming prerequisite for persisted ACL selectors
- [ ] Task: define the derived access contract shape used by frame/view/contract/codegen
- [ ] Enforce Ticket Microcycle across the active ACL/profile task.

## Acceptance Criteria
- The story defines:
  - per-layer ACL ownership
  - narrowing/intersection merge semantics
  - the distinction between raw ACL specs and derived access results
  - the next design/implementation targets for Nexus and the viewer layer

## Validation / Test Plan
- Design review only.
- Runtime validation deferred to later ACL implementation tasks.

## Risks / Mitigations
- Risk: ACLs get flattened into one vague middleware blob again.
  Mitigation: keep raw layer-owned ACL specs and derived access results as
  separate concepts.
- Risk: lower layers widen access over broader denies.
  Mitigation: define merge as narrowing/intersection by default.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Exact operation buckets for the derived access contract.
- Whether deny sets are sufficient or whether mode/reason metadata is also
  needed on the compiled access result.
- Which layer should compile the derived access contract: Nexus directly or a
  dedicated Nexus-owned manager.

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/nexus_acl_builder_and_persistence_model.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-04T19:42:03Z
  TYPE: FACT
  CLAIM: The ACL story now has one dedicated implementation-facing artifact
    that consolidates the current builder/persistence/validation/compile model.
    This reduces the risk that the next thread will restart from the older
    notes-only state and miss the refined selector story or subsystem split.
  EVIDENCE:
  - codex/context_compass/tickets/artifacts/nexus_acl_builder_and_persistence_model.md:1-267
  IMPACT: The story now has a durable ACL design source beyond task notes.
  NEXT: keep the next ACL design or implementation work aligned to that
    artifact unless the user explicitly changes the model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T19:25:19Z
  TYPE: FACT
  CLAIM: The ACL story now has its first runtime prerequisite completed. Root
    and normal conduit names are now stable per-frame selectors with
    deterministic `"default"` fallback and cleanup unregistration. That means
    the ACL builder/document design can treat `conduit_name` as a real
    persisted selector instead of a best-effort cloud-only property.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-04_enforce_root_conduit_name_uniqueness_for_acl_selectors_task.md:1-205
  IMPACT: One major identity question is now settled for the ACL lane: frame
    names and conduit names are stable selectors, while spell selectors can use
    the existing meld-key/signature path.
  NEXT: keep the active task focused on the ACL builder/document/compile model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T12:05:48Z
  TYPE: FACT
  CLAIM: This story formalizes the ACL model that is emerging from the
    profile/access lane. The user-defined direction is a four-layer ownership
    stack: spell ACL, spellbook ACL, conduit ACL, and frame ACL. Those raw ACL
    specs should be collected through Nexus and compiled into a derived access
    contract that the future frame/view/contract/codegen layers consume. Merge
    semantics should be narrowing/intersection by default so lower/more
    specific layers filter broader ones instead of widening access silently.
  EVIDENCE:
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:112-166
  IMPACT: The ACL conversation now has a durable story anchor instead of living
    only in task notes and chat.
  NEXT: tighten the epic and active task to carry this layered ACL model
    explicitly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when ACL ownership, merge, or downstream consumer boundaries change.
- Reference child-task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story anchors the layered ACL design inside the active profile/access epic
so the future Nexus/view/codegen contract work can build on one stable access
model instead of several overlapping policy ideas.
