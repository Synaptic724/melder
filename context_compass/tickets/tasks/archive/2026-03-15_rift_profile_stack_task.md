# Task: Rift Profile Stack

## Metadata
- Task ID: TASK-2026-03-15-rift-profile-stack
- Story: STORY-2026-03-15-aethericrift-v1-workspace-runtime
- Status: ready
- Owner: codex
- Priority: p1
- Created: 2026-03-15T11:59:14Z
- Updated: 2026-03-15T11:59:14Z

## Objective
Implement the active AR profile stack:
- `RiftProfile`
- `AethericFrameProfile`
- `SpellbookRiftProfile`
- `SpellRiftProfile`

and keep it distinct from `RiftConfiguration`, while using `FrameExaminer` to
gather configured-frame profile truth for room exposure.

## Ticket Contract
- ENTRY_GATE: the runtime core and validation boundaries are in place far
  enough that profile-layer behavior can feed exposure and validation semantics.
- EXECUTION_BOUNDARY: profile objects, merge behavior, and config/profile
  separation only.
- DEPENDENCIES:
  - TASK-2026-03-15-aethericrift-runtime-core
  - TASK-2026-03-15-rift-validation-system
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_profiles.md
- EXIT_GATE: the active AR profile stack exists, contradictory profile state
  fails explicitly, and `RiftConfiguration` is not treated as an ACL profile.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if implementation requires
  reviving dead concepts like `ConduitProfile` or collapsing config/profile into
  one object.

## Scope Boundaries
- In scope:
  - profile objects
  - merge/aggregation behavior
  - `FrameExaminer`
  - profile-driven room population inputs
  - config/profile separation
  - wiring profile state into room exposure and validation behavior
- Out of scope:
  - transport/auth middleware
  - MutationResearch policy model

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the current patch set defines the AR profile stack clearly
  enough to break it into a focused implementation task.

## Steps / Checklist
- [ ] Implement the active AR profile objects.
- [ ] Implement merge/aggregation behavior with explicit contradiction handling.
- [ ] Implement `FrameExaminer` as the configured-frame inspection/gathering tool.
- [ ] Keep `RiftConfiguration` separate from capability/profile semantics.
- [ ] Wire profile state into room exposure and validation behavior.
- [ ] Add tests for merge behavior and config/profile separation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- AR profile-layer objects
- `FrameExaminer`
- merge behavior
- tests for profile aggregation and config/profile separation

## Files / Paths Impacted
- src/melder/aether/aetheric_rift/
- tests/

## Validation
- Not run.
- Recommended commands:
  - `pytest tests -k rift_profile -v`

## Risks / Rollback Notes
- Risk: config and profile concerns get fused again and reintroduce design drift.
  Rollback: keep merge semantics narrow and fail loudly on contradictory state.

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
  CLAIM: This task isolates the AR profile-layer work so capability/exposure
    behavior can be implemented without polluting `RiftConfiguration` or
    reviving discarded profile concepts, and so configured-frame truth can be
    gathered through `FrameExaminer` instead of being smeared across the public
    Rift object.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_profiles.md:1-31
  - codex/context_compass/tickets/artifacts/aethericrift_v1_object_model_and_build_direction.md:68-104
  IMPACT: Completing this task keeps the room's capability picture explicit and
    keeps runtime configuration distinct from ACL/exposure behavior.
  NEXT: implement once the core runtime and validation path exist.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Fourth implementation task for the patch-driven AR v1 stack. It implements the
profile layer that shapes room exposure while staying separate from runtime
configuration.
