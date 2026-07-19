# Task: Document Rift Room Mode Matrix And Runtime Contracts
- Completed: 2026-04-13T11:09:48Z
- Summary: Landed and accepted the explicit static/capability/dynamic room-mode documentation tranche in Rift/RiftSpace and the canonical source docs.

## Metadata
- Task ID: TASK-2026-04-12-document-rift-room-mode-matrix-and-runtime-contracts
- Story: STORY-2026-04-12-investigate-capability-rift-space-runtime-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T22:52:16Z
- Updated: 2026-04-13T11:09:48Z

## Objective
Bring the Rift-side docs and canonical source docs up to the current room-mode
implementation by documenting the static/capability/dynamic matrix directly in
the Rift layer and in the architecture/components docs.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for deep documentation, a matrix in the
  Rift layer, and canonical docs that match the current implemented room split.
- EXECUTION_BOUNDARY: Rift-side docstrings/comments and canonical
  `src_architecture.md` / `src_components.md` only.
- DEPENDENCIES:
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/aether/nexus/rift/rift_space/rift_space.py
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
- EXIT_GATE: the Rift-side code and canonical source docs both describe the
  implemented room-mode split accurately and concretely.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a doc claim would require
  asserting a behavior that is still ambiguous in code.

## Scope Boundaries
- In scope:
  - room-mode matrix in Rift-side docs
  - static/capability/dynamic contract updates in room class docstrings
  - canonical source-doc updates for the current room model
- Out of scope:
  - runtime behavior changes
  - ACL/compiler redesign
  - mutation work

## State Transition Event
- from_state: draft
- to_state: done
- transition_reason: the room-mode matrix and canonical doc updates are landed
  and the user explicitly asked to close the documentation tickets.

## Steps / Checklist
- [x] Route the documentation task from the board.
- [x] Patch Rift-side room docs with an explicit room-mode matrix.
- [x] Patch `src_architecture.md` for the current room model.
- [x] Patch `src_components.md` for the current room model.
- [x] Re-read the touched docs and record the result.
- [x] Run focused validation (py_compile for touched code files if needed).
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- deep Rift-side room-mode documentation
- updated source architecture doc
- updated source components doc

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/rift/rift_space/rift_space.py
- src/melder/aether/nexus/rift/rift_space/static_rift_space.py
- src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
- src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md
- codex/context_compass/attention_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py`

## Risks / Rollback Notes
- Risk: the docs restate stale “capability is placeholder” language that is no
  longer true.
  Rollback: ground every room-mode claim in the implemented command/viewer/workstation behavior.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T22:52:16Z
  TYPE: PLAN
  CLAIM: The current docs still understate or misstate the room split. In the
    canonical source docs, capability is still described as placeholder-only in
    a few places even though the runtime now supports broad manual access,
    direct spell activation, topology operations, and runtime introspection.
    The Rift-side code also lacks one explicit matrix that shows the static /
    capability / dynamic split in one place.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:_create_primary_space_from_configuration
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:__init__
  - codex/context_compass/system_docs/src_architecture.md:300-360
  - codex/context_compass/system_docs/src_components.md:360-460
  IMPACT: The next pass should be documentation-first, not another runtime
    feature pass.
  NEXT: patch the Rift/RiftSpace docstrings and the two canonical source docs
    with the implemented room-mode matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T22:52:16Z
  TYPE: MEASURE
  CLAIM: The documentation tranche is landed. `Rift` and `RiftSpace` now carry
    an explicit room-mode matrix in code, the three room classes now describe
    their actual implemented posture, and the two canonical source docs no
    longer describe capability as placeholder-only.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:27-62
  - src/melder/aether/nexus/rift/rift.py:1077-1111
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:19-55
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:16-31
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:15-31
  - src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py:13-27
  - codex/context_compass/system_docs/src_architecture.md:242-321
  - codex/context_compass/system_docs/src_components.md:409-459
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/rift/rift_space/rift_space.py src/melder/aether/nexus/rift/rift_space/static_rift_space.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py` -> success
  IMPACT: The room-mode story is finally visible in the code and the canonical
    docs instead of only in tickets/chat.
  NEXT: return to the next genuinely new capability/runtime seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:09:48Z
  TYPE: DECISION
  CLAIM: This documentation tranche is complete and accepted. The explicit
    room-mode matrix is now present in Rift-side code docs, the three room
    classes describe their real posture, and the canonical source docs no
    longer need this ticket to explain the implemented static/capability/dynamic
    split.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:27-62
  - src/melder/aether/nexus/rift/rift.py:1077-1111
  - src/melder/aether/nexus/rift/rift_space/rift_space.py:19-55
  - src/melder/aether/nexus/rift/rift_space/static_rift_space.py:16-31
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:15-31
  - src/melder/aether/nexus/rift/rift_space/dynamic_rift_space.py:13-27
  - codex/context_compass/system_docs/src_architecture.md:421-475
  - codex/context_compass/system_docs/src_components.md:489-607
  IMPACT: The room-mode story no longer needs to remain in the active task lane.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task documents the implemented Rift room-mode model in both the code and
the canonical source docs.
