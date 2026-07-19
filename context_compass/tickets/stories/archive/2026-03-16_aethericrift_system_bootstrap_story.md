# Story: AethericRift System Bootstrap

## Metadata
- Story ID: STORY-2026-03-16-aethericrift-system-bootstrap
- Epic: EPIC-2026-03-16-aethericrift-system-bootstrap-implementation
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-03-16T00:31:16Z
- Updated: 2026-03-28T22:47:05Z

## User Narrative
As the project owner, I want the AethericRift system bootstrap broken into
separate implementation slices, so that we can build the registry, model
objects, space hierarchy, facade wiring, and tests without one oversized change.

## Value / MRP Alignment
This story keeps the first AR code slice honest. It captures only the hosted
system boundary, model skeletons, class-based space hierarchy, Aether facade,
and supporting tests that are necessary to start implementation safely.

## Ticket Contract
- ENTRY_GATE: the implementation epic is active and the current `Aether`
  source/test seams are investigated.
- EXECUTION_BOUNDARY: story-level planning and task decomposition only; no code
  implementation in this story ticket itself.
- DEPENDENCIES:
  - EPIC-2026-03-16-aethericrift-system-bootstrap-implementation
  - src/melder/aether/aether.py
  - tests/unit/melder/aether/test_aether.py
  - src/melder/utilities/helpers/id_builder.py
  - current AR object-model/patch docs
- EXIT_GATE: the bootstrap planning task is reviewed and the child
  implementation tasks are ready as separate execution slices.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested bootstrap scope
  still hides multiple incompatible implementation strategies.

## Requirements (Functional)
- Investigate the current `Aether` source/test seams that the AR bootstrap must
  fit into.
- Create a planning task that records the relevant code findings.
- Create separate implementation tasks for registry, model skeletons,
  `RiftSpace` hierarchy, Aether facade wiring, and tests.
- Keep the first scaffold fast by default with direct dict-backed ownership and
  paired id/name indexes where name lookup matters.
- Encode the user’s requested folder layout and ownership boundary in those tasks.

## Requirements (Non-Functional)
- Keep tasks small and reviewable.
- Keep `Aether` as facade only.
- Keep future extension points visible in the class hierarchy.
- Prefer direct dict-backed indexing over heavier registry abstractions in the
  bootstrap slice.

## Scope Boundaries
- In scope:
  - ticket decomposition
  - implementation sequencing
  - investigation notes tied to actual code
- Out of scope:
  - writing bootstrap code in this story
  - validation/profile/dynamic execution behavior beyond planning notes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested ticketed investigation and staged
  implementation planning before coding the bootstrap.

## Dependencies / Related Work
- codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md
- codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md
- codex/context_compass/tickets/tasks/2026-03-15_aethericrift_runtime_core_task.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-03-16-plan-aethericrift-system-bootstrap - investigate code and lock the staged bootstrap plan
- [ ] Task: TASK-2026-03-22-implement-aethericrift-system-configuration-governance - add process-wide AR system configuration, enablement, and frame governance
- [ ] Task: TASK-2026-03-28-refactor-rift-public-surface-into-nexus-singleton - move the public root to `Nexus`, hide `Aether`, and remove the separate public Rift state model
- [ ] Task: TASK-2026-03-29-design-rift-frame-disposal-event-propagation - design the later Rift/workspace event model for disposed backing frames before workstation/workspace implementation resumes
- [x] Task: TASK-2026-03-28-investigate-conduit-same-frame-link-guard - verify whether cross-frame conduit linking is already forbidden and capture the runtime truth
- [x] Task: TASK-2026-03-28-implement-conduit-same-frame-link-guard - enforce same-frame-only peer conduit links in the runtime
- [ ] Task: TASK-2026-03-16-implement-aethericrift-system-registry - add the hosted system registry scaffold
- [ ] Task: TASK-2026-03-16-implement-aethericrift-and-state-skeletons - add `AethericRift` / `AethericRiftState` skeletons
- [ ] Task: TASK-2026-03-16-implement-rift-space-hierarchy - add class-based `RiftSpace`, `StaticRiftSpace`, and `DynamicRiftSpace`
- [ ] Task: TASK-2026-03-16-facade-aether-rift-system-access - add `Aether` facade methods that delegate to the system
- [ ] Task: TASK-2026-03-16-test-aether-rift-system-facade - add focused facade/registry tests
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The planning task records the relevant code seams with evidence.
- Separate ready tasks exist for each bootstrap slice.
- The task set explicitly preserves `AethericRiftSystem` ownership and `Aether`
  facade-only access.

## Validation / Test Plan
- Planning validation only:
  - verify source/test seams are cited
  - verify the task boundaries do not overlap excessively

## UX / API / Data Notes
- The first slice is infrastructure-facing, not user-facing.
- `RiftSpace` identity should be ULID-based, with explicit name -> ULID lookup
  planned as part of the hierarchy task.
- All AR assets should live under the `aetheric_rift_system/` subtree to match
  the ownership boundary in the docs.

## Risks / Mitigations
- Risk: the first implementation slice quietly absorbs future validation/profile
  concerns.
  Mitigation: keep those concerns explicitly out of the ready tasks.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether `RiftSpace` name uniqueness should be enforced per Rift or per system
  in the first slice.

## Decision Log
- 2026-03-16: bootstrap work will be planned and implemented in separate tasks,
  not as a single monolithic change.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-03-16T00:31:16Z
  TYPE: FACT
  CLAIM: The existing `Aether` unit tests already validate the exact facade
    style the bootstrap needs: Aether methods delegate into subordinate
    dictionaries/objects, and tests assert that behavior directly instead of
    treating `Aether` as the ultimate owner of everything.
  EVIDENCE:
  - tests/unit/melder/aether/test_aether.py:79-91
  - tests/unit/melder/aether/test_aether.py:248-280
  - src/melder/utilities/helpers/id_builder.py:1-16
  IMPACT: The bootstrap tasks can follow current code/test conventions instead
    of inventing a one-off AR testing style.
  NEXT: create the planning task and ready implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T21:38:03Z
  TYPE: FACT
  CLAIM: The March 28 conduit/runtime support slice is now closed under this
    story: the codebase now has an evidence-backed same-frame conduit link
    invariant plus the related narrow test-drift repairs, while the remaining
    active bootstrap work stays centered on ARS governance and the upcoming AR
    state-object / managed-frame-responsibility design.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/completed/2026-03-28_investigate_conduit_same_frame_link_guard_task.md:1-119
  - codex/context_compass/tickets/tasks/completed/2026-03-28_implement_conduit_same_frame_link_guard_task.md:1-176
  - codex/context_compass/tickets/tasks/completed/2026-03-28_repair_conduit_and_spellcrafter_test_drift_task.md:1-150
  - codex/context_compass/tickets/tasks/2026-03-22_implement_aethericrift_system_configuration_governance_task.md:110-185
  IMPACT: The story no longer needs to route attention through the completed
    conduit/test-support tasks; compaction can resume from the active ARS
    governance ticket.
  NEXT: keep the ARS governance task active and move the completed March 28
    tickets into the completed-task archive.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-28T22:47:05Z
  TYPE: DECISION
  CLAIM: The bootstrap story now needs one more focused runtime refactor slice:
    the current public ARS model should simplify into a public `Nexus`
    singleton root with hidden `Aether` substrate hosting and live `Rift`
    objects owning their own runtime state directly, instead of widening the
    older shell/state/facade split.
  EVIDENCE:
  - codex/context_compass/tickets/tasks/2026-03-22_implement_aethericrift_system_configuration_governance_task.md:158-185
  - src/melder/aether/aether.py:47-88
  - src/melder/aether/aetheric_rift_system/aetheric_rift_system.py:22-57
  - src/melder/aether/aetheric_rift_system/aetheric_rift_state/aetheric_rift_state.py:8-41
  IMPACT: The story should route into a dedicated Nexus refactor task before
    deeper workspace/state work continues, because the public root and live
    object model are changing.
  NEXT: route the new Nexus singleton task on the attention board and create
    the matching patch artifacts before implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story stages the first AR code bootstrap into separate tasks. The active
step is the planning task that encodes the code investigation and locks the
separate implementation slices.
