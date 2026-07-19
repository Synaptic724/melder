# Task: RiftSpace and Target Model

## Metadata
- Task ID: TASK-2026-03-15-rift-space-and-target-model
- Story: STORY-2026-03-15-aethericrift-v1-workspace-runtime
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-03-15T11:59:14Z
- Updated: 2026-03-15T11:59:14Z

## Objective
Implement `RiftSpace` as the base room contract, implement `StaticRiftSpace` as
the first concrete room surface, and establish the declared workspace target model:
- `RiftAttribute`
- `RiftMethod`

This task also establishes the `StaticRiftSpace` declared-target surface and basic room
cleanup semantics.

## Ticket Contract
- ENTRY_GATE: TASK-2026-03-15-aethericrift-runtime-core is complete enough that
  the room can attach to a real AR-local substrate.
- EXECUTION_BOUNDARY: workspace state, target registries, room facade behavior,
  and `StaticRiftSpace` declared-target semantics only.
- DEPENDENCIES:
  - TASK-2026-03-15-aethericrift-runtime-core
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_space.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_targets.md
- EXIT_GATE: `RiftSpace` / `StaticRiftSpace` expose declared target registries
  cleanly, target registration/clearing works, and the static room surface does
  not collapse into ambient Python state.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the room requires reviving
  `ObjectRef`, `RiftField`, `RiftRunner`, or other discarded target models.

## Scope Boundaries
- In scope:
  - `RiftSpace`
  - `StaticRiftSpace`
  - `RiftAttribute`
  - `RiftMethod`
  - target registration/inspection/clear semantics
  - room cleanup behavior
  - `StaticRiftSpace` declared-target surface
- Out of scope:
  - AST validation pipeline
  - profile merge behavior
  - `dynamic` conduit-backed construction

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the current AR patch contracts define the room and target
  boundary cleanly enough for an engineer task.

## Steps / Checklist
- [ ] Implement the `RiftSpace` base room contract.
- [ ] Implement `StaticRiftSpace` as the first concrete room surface.
- [ ] Implement `RiftAttribute` and `RiftMethod` target types/records.
- [ ] Implement explicit target registration, replacement, inspection, and clear operations.
- [ ] Implement room cleanup behavior for local transient targets.
- [ ] Implement `StaticRiftSpace` declared-target surface rules.
- [ ] Add tests for target registration, lookup, cleanup, and static-room behavior.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- `RiftSpace`
- `StaticRiftSpace`
- `RiftAttribute`
- `RiftMethod`
- room cleanup behavior
- static room-surface tests

## Files / Paths Impacted
- src/melder/aether/aetheric_rift/
- tests/

## Validation
- Not run.
- Recommended commands:
  - `pytest tests -k rift_space -v`
  - `pytest tests -k rift_target -v`

## Risks / Rollback Notes
- Risk: the room leaks ambient Python state and stops behaving like a declared
  target universe.
  Rollback: tighten registration/lookup semantics before widening capability.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-03-15T11:59:14Z
  TYPE: PLAN
  CLAIM: This task translates the room/target patches directly into an
    implementable slice: `RiftSpace` is the base room contract,
    `StaticRiftSpace` is the first concrete room surface, and `RiftAttribute` /
    `RiftMethod` define the normal declared target universe.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_space.md:1-33
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_targets.md:1-33
  IMPACT: Completing this task establishes the room the operator actually works
    inside before validation and `DynamicRiftSpace` are added.
  NEXT: begin implementation once the runtime core substrate exists.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Second implementation task for the patch-driven AR v1 stack. It establishes the
room and declared target model that validation and later dynamic behavior will
reason over.
