# Epic: Implement AethericRift System Bootstrap

## Metadata
- Epic ID: EPIC-2026-03-16-aethericrift-system-bootstrap-implementation
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-03-16T00:31:16Z
- Updated: 2026-03-16T00:31:16Z
- Target Window: 2026-Q1
- Related Program/Initiative: AethericRift v1 runtime bootstrap

## Problem / Opportunity
The AR docs now define the ownership boundary, but the codebase still has no
concrete `AethericRiftSystem`, `AethericRift`, `AethericRiftState`, or
class-based `RiftSpace` hierarchy under `src/melder/aether/`. `Aether`
already exposes the right singleton/facade seams for frames and conduits, but
those seams need to be extended to host and delegate into a system-owned Rift
registry rather than making `Aether` the direct owner of those dictionaries.

## MRP Alignment (Most Reasonable Product)
The smallest coherent bootstrap is:
- a hosted `AethericRiftSystem` with system-owned Rift dictionaries
- skeleton `AethericRift` and `AethericRiftState` classes
- a class-based `RiftSpace` hierarchy (`RiftSpace`, `StaticRiftSpace`,
  `DynamicRiftSpace`) that is intentionally extendable
- `Aether` facade methods that delegate into the system
- focused tests that prove `Aether` is a facade and the system is the owner

## Ticket Contract
- ENTRY_GATE: ownership-boundary docs are aligned and the relevant `Aether`
  source/test seams have been investigated.
- EXECUTION_BOUNDARY: bootstrap scaffolding only for the AR system registry,
  public Rift object/state, class-based space hierarchy, Aether facade methods,
  and focused tests.
- DEPENDENCIES:
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_aetheric_rift_core.md
  - codex/context_compass/tickets/tasks/2026-03-15_aethericrift_runtime_core_task.md
  - src/melder/aether/aether.py
  - tests/unit/melder/aether/test_aether.py
- EXIT_GATE: the implementation story is accepted and the bootstrap tasks exist
  in a separate, staged sequence that can be executed independently.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the bootstrap requires
  collapsing future validation/profile/dynamic behavior into the same tranche.

## Goals (Outcomes)
- Encode the requested folder layout under `src/melder/aether/`.
- Keep Rift ownership in `AethericRiftSystem`, not in `Aether`.
- Make `Aether` the host/facade entrypoint for add/remove/list/get Rift access.
- Use ULID identity for `RiftSpace` and a secondary name -> ULID lookup path.
- Break implementation into separate steps instead of a single monolithic task.

## Non-Goals (Explicit Exclusions)
- Full `RiftValidationSystem` implementation.
- Full profile-stack implementation.
- MutationResearch integration.
- Production-ready token field schemas and security semantics.

## Scope Boundaries
- In scope:
  - AR system bootstrap planning
  - ownership/facade registry model
  - class skeleton layout
  - minimal tests around Aether facade access
- Out of scope:
  - end-to-end AR runtime behavior
  - transport/auth surfaces
  - dynamic room execution semantics beyond skeleton boundaries

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested a staged implementation plan under a
  dedicated implementation epic instead of a single all-at-once task.

## Success Metrics
- One implementation story exists under this epic.
- Separate tasks exist for registry, model skeletons, `RiftSpace` hierarchy,
  Aether facade wiring, and tests.
- Investigation notes cite the actual `Aether` source/test seams that justify
  the decomposition.

## Requirements (Functional + Non-Functional)
- Preserve `Aether` as a facade host, not the Rift registry owner.
- Keep the first code slice small enough to land as separate tasks.
- Use existing codebase patterns for ULID generation and Aether facade tests.
- Keep future extension points visible in the class/folder layout.

## Constraints / Assumptions
- `Aether` is already a singleton with internal frame dictionaries.
- Existing `Aether` tests assert facade-style delegation into subordinate
  dictionaries.
- ULID generation already exists in helper code and current Aether objects.

## Dependencies / External References
- src/melder/aether/aether.py
- src/melder/utilities/helpers/id_builder.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_aether.py

## Milestones (Track Progress)
- [ ] Milestone 1: Bootstrap plan accepted - epic/story/tasks are reviewed and sequenced.
- [ ] Milestone 2: Registry and model skeletons implemented behind Aether facade.
- [ ] Milestone 3: RiftSpace hierarchy and facade tests land in separate follow-up tasks.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-03-16-aethericrift-system-bootstrap - stage the AR system bootstrap into separate implementation tasks

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: Complete story STORY-2026-03-16-aethericrift-system-bootstrap
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The implementation story is accepted.
- Separate ready tasks exist for each bootstrap slice.
- The active plan explicitly keeps `AethericRiftSystem` as the owner and
  `Aether` as the facade host.

## Risks / Mitigations
- Risk: bootstrap tickets grow into the full AR runtime design.
  Mitigation: keep validation/profiles/dynamic semantics out of the first slice.
- Risk: ownership drifts back toward `Aether` direct dictionaries.
  Mitigation: make registry/facade separation explicit in every child task.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Planning validation only:
  - verify ticket decomposition matches investigated code seams
  - verify each implementation slice has explicit scope boundaries

## Rollout / Adoption Plan
- Finish the planning task first.
- Implement registry/model/task slices one by one.
- Keep tests close to each implementation slice instead of deferring all tests.

## Open Questions
- Whether the first facade API should expose only ID-based lookup or both
  ID/name lookup for Rifts in the first slice.
- Whether `RiftSpace` name -> ULID lookup lives on the Rift, the system, or a
  dedicated registry helper.

## Decision Log
- 2026-03-16: Bootstrap work will be decomposed into separate implementation
  tasks instead of a single all-in-one change.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-03-16T00:31:16Z
  TYPE: FACT
  CLAIM: `Aether` already has the right host/facade seams for a system-owned
    Rift registry: it is a singleton, owns frame dictionaries directly, and
    exposes internal helper methods that delegate into subordinate frame/conduit
    state rather than making callers reach into storage directly.
  EVIDENCE:
  - src/melder/aether/aether.py:42-57
  - src/melder/aether/aether.py:249-300
  - src/melder/aether/aether.py:495-522
  IMPACT: The AR bootstrap should extend the same pattern instead of inventing
    a second ownership style for hosted subsystems.
  NEXT: encode the bootstrap as separate implementation tasks under one story.
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
This epic exists to stage the AethericRiftSystem bootstrap as separate
implementation slices. The next step is the bootstrap story plus the planning
task that turns the investigated code seams into ready implementation tasks.
