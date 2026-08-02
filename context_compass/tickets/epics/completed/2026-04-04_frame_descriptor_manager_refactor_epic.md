# Epic: Extract Frame Descriptor Manager
- Completed: 2026-04-09T21:59:36Z
- Summary: Completed the FrameDescriptorManager refactor epic and archived the finished manager-extraction lane.


## Metadata
- Epic ID: EPIC-2026-04-04-frame-descriptor-manager-refactor
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-04T20:41:17Z
- Updated: 2026-04-09T21:59:36Z
- Target Window: 2026-Q2
- Related Program/Initiative: AR / Rift runtime maturation

## Problem / Opportunity
`Nexus` is currently carrying two different responsibilities in one large
class:
- process-wide Rift registry, configuration, enablement, and topology policy
- frame-scoped descriptor/store management for passive records and
  Nexus-managed frame records

The second cluster has grown into a distinct subsystem:
- `_frame_descriptors_by_name`
- posture refresh / publishability checks
- frame/conduit/spell record publication and removal
- Nexus-managed frame-record creation/lookup/list/count

Keeping that state and those workflows in `Nexus` makes the public root too
large, harder to reason about, and harder to evolve toward a multi-object
facade later.

## MRP Alignment (Most Reasonable Product)
The MRP outcome is not a cosmetic line-count change. It is one cleaner runtime
ownership split:
- `Nexus` remains the Rift-domain root and façade
- `FrameDescriptorManager` owns frame-scoped descriptor/store state

That gives us a durable foundation for later ACL systems and frame/view
consumers without keeping all frame-state mutation logic trapped inside
`Nexus`.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved the manager extraction direction and
  accepted direct migration without backward-compat scaffolding.
- EXECUTION_BOUNDARY: extract frame-scoped descriptor/store logic out of
  `Nexus`, migrate call sites, update focused tests/docs, and remove the old
  in-class state paths.
- DEPENDENCIES:
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
  - tickets/tasks/2026-03-28_refactor_rift_public_surface_into_nexus_singleton_task.md
  - system_docs/patches/active/nexus_frame_descriptor_refactor/architecture_patch.md
  - system_docs/patches/active/nexus_passive_ingest_canonical_store/architecture_patch.md
- EXIT_GATE: `Nexus` delegates frame-scoped descriptor/store work to a
  thread-safe manager, the old in-class descriptor-store paths are removed,
  and focused runtime/tests are aligned to the new ownership split.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the extraction would force a
  broader public API redesign beyond the frame-scoped state boundary.

## Goals (Outcomes)
- Make `Nexus` leaner by removing frame-scoped descriptor/store ownership.
- Introduce one thread-safe `FrameDescriptorManager`.
- Keep frame-scoped state mutation out of `Nexus`.
- Preserve current behavior while removing old internal storage paths.
- Set up a cleaner multi-object façade direction for future ACL/view work.

## Non-Goals (Explicit Exclusions)
- Final ACL system implementation.
- Final viewer/query contracts.
- Backward-compat shims for the old in-class descriptor-store paths.

## Scope Boundaries
- In scope:
- `src/melder/aether/nexus/nexus.py`
- new `FrameDescriptorManager` class and file
- focused runtime/test updates needed for the migration
- active patch docs and ticket state
- Out of scope:
- unrelated Nexus/Rift API redesign
- broad refactors outside the Nexus/frame-state boundary

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the story/task landed the manager extraction and focused
  Nexus validation passed, so the epic is now waiting on review of the new
  ownership split rather than further initial implementation.

## Success Metrics
- `Nexus` no longer owns `_frame_descriptors_by_name`.
- All frame-scoped publish/remove/lookup flows route through the manager.
- The manager is explicitly thread-safe for multi-step state mutation.
- Old duplicated frame-state paths inside `Nexus` are removed.

## Requirements (Functional + Non-Functional)
- Functional:
  - move descriptor dictionary ownership into the manager
  - move passive record publication/removal flows into the manager
  - move Nexus-managed frame-record lookup/create/list/count into the manager
  - keep `Nexus` façade methods semantically coherent
- Non-functional:
  - thread-safe
  - no compatibility shim
  - reviewable migration with explicit ownership

## Constraints / Assumptions
- `Nexus` should keep process-wide Rift registry/config/topology ownership.
- The manager should own frame-scoped state only.
- Multi-step mutations need explicit locking even if container primitives are
  internally synchronized by the runtime.
- `FrameDescriptor` remains the per-frame aggregate, not a runtime
  frame replacement.

## Dependencies / External References
- `src/melder/aether/nexus/nexus.py`
- `src/melder/aether/nexus/frame_descriptor.py`
- `src/melder/aether/nexus/nexus_frame_record.py`
- `src/melder/aether/nexus/canonical_store/`

## Milestones (Track Progress)
- [ ] Milestone 1: Investigation and method split are locked in ticket notes.
- [ ] Milestone 2: `FrameDescriptorManager` is introduced and `Nexus`
      delegates frame-scoped state flows to it.
- [ ] Milestone 3: Old in-class descriptor-store paths are removed and focused
      validation is recorded.

## Stories (Required to Complete)
- [x] Story: STORY-2026-04-04-extract-frame-descriptor-manager - migrate the
      frame-scoped Nexus state boundary into a dedicated manager

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-04-04-extract-frame-descriptor-manager
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- One dedicated manager owns frame-scoped descriptor/store state.
- `Nexus` keeps only façade/root responsibilities in this boundary.
- The user accepts the new ownership split and the old internal paths are gone.

## Risks / Mitigations
- Risk: manager extraction still leaves dual ownership between `Nexus` and the
  manager.
  Mitigation: remove old paths instead of aliasing them.
- Risk: lock ordering becomes ambiguous between `Nexus`, manager, and
  descriptor.
  Mitigation: keep `Nexus` work and manager work separated by clear delegation
  boundaries.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Focused runtime validation against current Nexus publish/frame-record flows.
- Focused tests for the migrated manager boundary.
- Truthful reporting when validation is not run.

## Rollout / Adoption Plan
- Lock the method split first.
- Introduce the manager.
- Migrate call sites.
- Remove old in-class state.
- Validate and return the lane for review.

## Open Questions
- Which small façade helpers should stay on `Nexus` vs move fully into the
  manager.
- Whether a dedicated target-frame onboarding façade should land in this slice
  or later.

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/nexus_frame_descriptor_manager/architecture_patch.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/component_patch_nexus.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/component_patch_frame_descriptor_manager.md
  - system_docs/patches/active/nexus_frame_descriptor_manager/code_description_patch_frame_descriptor_manager.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: retain while the manager extraction lane is active or until
  merged into canonical source docs

## Notes
- DATETIME: 2026-04-04T20:55:05Z
  TYPE: FACT
  CLAIM: The epic now has a real runtime result instead of only a migration
    plan. `FrameDescriptorManager` is landed, `Nexus` no longer owns the
    descriptor dictionary directly, frame-scoped publish/remove helpers now
    live behind the manager boundary, and the focused Nexus unit surface passed
    after the migration.
  EVIDENCE:
  - tickets/tasks/2026-04-04_migrate_nexus_frame_state_into_frame_descriptor_manager_task.md:1-182
  - src/melder/aether/nexus/frame_descriptor_manager.py:18-595
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py
  IMPACT: The program lane is now in review on the quality of the ownership
    split, not on whether the migration can be executed at all.
  NEXT: review the new boundary with the user and decide whether any follow-up
    façade cleanup belongs in this lane or later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T20:41:17Z
  TYPE: PLAN
  CLAIM: The new refactor lane exists because `Nexus` now owns both process-wide
    Rift-root behavior and a large frame-scoped descriptor/store subsystem. The
    extraction target is a dedicated thread-safe `FrameDescriptorManager` that
    owns descriptor lookup/create, posture refresh, passive record publication,
    and Nexus-managed frame-record mutation while `Nexus` remains the façade.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:147-149
  - src/melder/aether/nexus/nexus.py:668-969
  - src/melder/aether/nexus/nexus.py:1715-1921
  IMPACT: We now have one explicit program lane for making `Nexus` leaner and
    clarifying frame-scoped ownership before ACL/view layers keep building on
    the wrong internal shape.
  NEXT: create the story/task and active patch docs, then lock the exact method
    split before code edits.
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
This epic exists to extract the frame-scoped Nexus descriptor/store subsystem
into a dedicated manager so `Nexus` can stay a leaner façade/root for Rift
policy and topology work. The first migration slice is now landed and waiting
on review of the resulting boundary.

