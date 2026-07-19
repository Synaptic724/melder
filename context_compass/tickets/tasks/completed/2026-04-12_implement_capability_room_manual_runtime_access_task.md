# Task: Implement Capability Room Manual Runtime Access
- Completed: 2026-04-13T22:24:59Z
- Summary: Completed the first real capability-room implementation slice after broad manual runtime access landed and the focused capability ring passed.

## Metadata
- Task ID: TASK-2026-04-12-implement-capability-room-manual-runtime-access
- Story: STORY-2026-04-12-investigate-capability-rift-space-runtime-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T19:50:00Z
- Updated: 2026-04-13T22:24:59Z

## Objective
Turn capability from a placeholder into the first real non-codegen room by
opening broad manual runtime access on the existing command/workstation
surface while leaving frame truth as the lower runtime floor.

## Ticket Contract
- ENTRY_GATE: the capability model artifact is written and the user explicitly
  asked to build it out.
- EXECUTION_BOUNDARY: `CapabilityCommandSystem`, `CapabilityRiftSpace`,
  focused tests, patch docs, and board/artifact sync only.
- DEPENDENCIES:
  - tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: capability room exposes broad manual runtime access without
  codegen, and the focused Rift/capability ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if implementation requires a
  broader room/codegen redesign.

## Scope Boundaries
- In scope:
  - capability command surface
  - capability room contract/docs
  - focused tests
- Out of scope:
  - codegen surfaces
  - capability viewer redesign
  - broad integration harness work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved building the first real
  capability runtime cut.

## Steps / Checklist
- [x] Stage patch docs and route the task from the board.
- [x] Relax `CapabilityCommandSystem` to broad manual runtime access.
- [x] Update focused capability tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- capability room manual runtime access
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py
- src/melder/aether/nexus/rift/rift_space/capability_rift_space.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Rollback Notes
- Risk: capability drifts back into a fake restrictive middle layer instead of
  the simpler broad manual-access room the user asked for.
  Rollback: keep the first cut minimal and honest, with no handle/proxy work.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md
  - system_docs/patches/active/capability_room_manual_runtime_access/architecture_patch.md
  - system_docs/patches/active/capability_room_manual_runtime_access/component_patch_capability_command_system.md
  - system_docs/patches/active/capability_room_manual_runtime_access/component_patch_capability_rift_space.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until capability runtime behavior is merged into
  canonical docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T19:50:00Z
  TYPE: PLAN
  CLAIM: The first capability cut should be deliberately small. The existing
    room/workstation surface already gives broad manual power once raw runtime
    getters are allowed, because callers can fetch real objects, bind them, set
    targets, and call methods through the existing command/workstation seam.
    So the first cut is mostly removing the placeholder denial and proving the
    frame-truth boundary in tests.
  EVIDENCE:
  - tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md:1-104
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py:1-42
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:1-1234
  IMPACT: We can make capability real without a second architecture pass.
  NEXT: patch the capability command surface and the focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T20:05:00Z
  TYPE: FACT
  CLAIM: The first real capability cut is now landed in source.
    `CapabilityCommandSystem` no longer denies raw runtime-object access and
    now behaves like the broad manual command/runtime surface. The room docs
    now describe `CapabilityRiftSpace` as the non-codegen manual runtime room,
    not a restrictive placeholder.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py:1-28
  - src/melder/aether/nexus/rift/rift_space/capability_rift_space.py:1-72
  - tests/unit/melder/aether/test_nexus.py:2618-2770
  IMPACT: Capability is now a real room mode instead of only a typed shell.
  NEXT: record validation and return the first cut for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T20:05:00Z
  TYPE: MEASURE
  CLAIM: The first capability cut is green on the focused and nearby
    Rift/capability unit ring.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py src/melder/aether/nexus/rift/rift_space/capability_rift_space.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> 113 passed
  IMPACT: The room is stable enough for review before widening into more
    capability-specific operations or integration coverage.
  NEXT: summarize the landed capability surface and decide whether the next
    step is more focused capability operations/tests or an integration harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the first real capability room cut: broad manual runtime
access without codegen.
