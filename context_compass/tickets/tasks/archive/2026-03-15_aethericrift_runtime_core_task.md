# Task: AethericRift Runtime Core

## Metadata
- Task ID: TASK-2026-03-15-aethericrift-runtime-core
- Story: STORY-2026-03-15-aethericrift-v1-workspace-runtime
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-03-15T11:59:14Z
- Updated: 2026-03-15T11:59:14Z

## Objective
Implement the top-level AR runtime core so:
- `AethericRiftSystem` owns canonical Rift registration/state
- `Aether` hosts and facades access into `AethericRiftSystem` rather than
  owning the Rift registry directly
- public `AethericRift` objects begin as shells and bind lazily against that state
- live Rifts own the AR-local Spellbook, root conduit, `RiftConfiguration`,
  and workspace lifecycle

## Ticket Contract
- ENTRY_GATE: the AR v1 architecture patch and `aetheric_rift_core` component
  patch are re-read and the story routes this task as the first implementation
  slice.
- EXECUTION_BOUNDARY: `AethericRift` core ownership, AR-local substrate setup,
  and minimal creation-through-`Aether` wiring only.
- DEPENDENCIES:
  - STORY-2026-03-15-aethericrift-v1-workspace-runtime
  - TASK-2026-03-15-define-aethericrift-v1-patch-handoff
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_aetheric_rift_core.md
- EXIT_GATE: `AethericRift` can be created through `Aether`, owns its local
  Spellbook/root conduit/configuration, and has basic lifecycle tests.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if local Spellbook/root-conduit
  ownership cannot be implemented without changing the AR boundary model.

## Scope Boundaries
- In scope:
  - `AethericRiftSystem`
  - `AethericRiftState`
  - `AethericRift` core runtime object
  - AR-local Spellbook ownership
  - root conduit creation/ownership
  - `RiftConfiguration` bootstrap and lifecycle wiring
- Out of scope:
  - `RiftSpace`
  - target registries
  - validation logic
  - `dynamic` local construction behavior

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the AR patch contracts now define the core ownership model
  clearly enough to make this the first engineer implementation task.

## Steps / Checklist
- [ ] Create `AethericRiftSystem` as the canonical owner of Rift registration/state.
- [ ] Create `AethericRiftState` as the canonical per-Rift state record.
- [ ] Create the public `AethericRift` shell object in the active AR code surface.
- [ ] Use the existing `Aether` accessors (`_ensure_frame`, `_get_configuration`,
      `_bind_configuration`, `_add_conduit`) as the management surface.
- [ ] Add and use `_get_conduits_by_frame(...)` rather than depending on frame
      internals for configured-frame conduit exposure.
- [ ] Add the `Aether` facade helpers for add/find/remove/cleanup Rift
      operations through `AethericRiftSystem`.
- [ ] Keep any direct live-Rift retrieval behind `AethericRiftSystem`
      token/policy checks; do not add an ungated `Aether` bypass getter.
- [ ] Use explicit token objects:
      `AethericRiftCreationToken` and `AethericRiftToken`.
- [ ] Implement lazy registration/bind/hydration from shell Rift to live Rift state.
- [ ] Implement AR-local Spellbook ownership.
- [ ] Implement root conduit creation and lifecycle ownership.
- [ ] Implement `RiftConfiguration` attachment/bootstrap at Rift creation.
- [ ] Wire creation-through-`Aether`.
- [ ] Add unit tests for Rift creation and cleanup boundaries.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- `AethericRiftSystem`
- `AethericRiftState`
- `AethericRift` shell-to-live runtime object
- AR-local Spellbook ownership
- root conduit ownership
- baseline tests for creation/cleanup
- `Aether`-facaded creation/retrieval path that does not depend on direct
  frame-internals or bypass the system-owned Rift registry

## Files / Paths Impacted
- src/melder/aether/
- src/melder/aether/aetheric_rift/
- tests/

## Validation
- Not run.
- Recommended commands:
  - `pytest tests -k aethericrift_runtime_core -v`

## Risks / Rollback Notes
- Risk: AR-local substrate creation conflicts with current `Aether` ownership
  semantics.
  Rollback: stop and revise the patch docs before widening code scope.
- Risk: shell/state boundaries blur and public Rift objects become accidental
  canonical state owners.
  Rollback: keep canonical state in the system layer and narrow the public Rift
  shell again before continuing.

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
  CLAIM: This task implements the first architecture-patch rollout step:
    establish `AethericRiftSystem` / `AethericRiftState` plus the public
    `AethericRift` shell-to-live lifecycle, then give the live Rift the
    AR-local Spellbook, root conduit, and configuration instead of reviving the
    stale facade/context split.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/architecture_patch.md:27-41
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_aetheric_rift_core.md:1-35
  IMPACT: Completing this task creates the runtime substrate every downstream AR
    task depends on.
  NEXT: begin implementation at the core AR runtime boundary only, using the
    existing `Aether` accessor surface instead of direct frame-internals access.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
First implementation task for the patch-driven AR v1 stack. This task is only
about the top-level runtime object and its local substrate ownership.
