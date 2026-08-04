# Task: Expand Shared CommandSystem Manual Runtime Surface
- Completed: 2026-04-13T22:24:59Z
- Summary: Completed the shared manual-runtime command-surface expansion after the widened base vocabulary and explicit static denials landed and validated.

## Metadata
- Task ID: TASK-2026-04-12-expand-shared-command-system-manual-runtime-surface
- Story: STORY-2026-04-12-investigate-capability-rift-space-runtime-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T20:44:35Z
- Updated: 2026-04-13T22:24:59Z

## Objective
Widen the shared manual-runtime command vocabulary on base `CommandSystem`,
deny unsafe runtime-topology operations in `StaticCommandSystem`, and keep
`CapabilityCommandSystem` / `DynamicCommandSystem` thin.

## Ticket Contract
- ENTRY_GATE: the capability room model and focused capability operation slice
  are already landed, and the user explicitly approved implementing the shared
  command-surface direction.
- EXECUTION_BOUNDARY: base/static command system methods, shared command
  protocol surface, focused tests, patch docs, and board/artifact sync only.
- DEPENDENCIES:
  - tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py
  - src/melder/aether/nexus/rift/rift_space/command_system/dynamic_command_system.py
  - src/melder/utilities/interfaces/interfaces.py
  - tests/unit/melder/aether/test_nexus.py
- EXIT_GATE: shared manual-runtime operations exist on base `CommandSystem`,
  static explicitly denies the unsafe ones, capability/dynamic inherit the
  surface, and the focused test ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the shared command-surface
  expansion requires a broader room/runtime redesign or a public API rename.

## Scope Boundaries
- In scope:
  - shared manual-runtime command methods
  - static denials for unsafe topology-mutation methods
  - command-surface introspection helper
  - focused unit/runtime tests
- Out of scope:
  - codegen-only command methods
  - capability integration harness
  - viewer redesign
  - broader Rift/RiftSpace API redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the capability lane now has a durable shared-command
  direction and the user explicitly approved implementing it.

## Steps / Checklist
- [x] Stage patch docs and route the task from the board.
- [x] Add shared manual-runtime methods to `CommandSystem`.
- [x] Deny unsafe topology-mutation methods in `StaticCommandSystem`.
- [x] Update shared command protocol/introspection surface.
- [x] Add focused tests for capability/dynamic allow and static deny behavior.
- [x] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- widened base command surface for shared manual-runtime operations
- explicit static denial behavior for unsafe topology mutation
- focused test coverage for the new command-surface contract

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift_space/command_system/command_system.py
- src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/test_nexus.py
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Ran:
  - `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system/command_system.py src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Rollback Notes
- Risk: the new methods drift into capability-only wrappers instead of a real
  shared command vocabulary.
  Rollback: keep the surface in base `CommandSystem` and use static overrides
  for denials instead of duplicating the API.
- Risk: static denials are incomplete and the room semantics become uneven.
  Rollback: keep one explicit deny helper and test the deny set directly.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md
  - system_docs/patches/active/shared_command_system_manual_runtime_surface/architecture_patch.md
  - system_docs/patches/active/shared_command_system_manual_runtime_surface/component_patch_command_system.md
  - system_docs/patches/active/shared_command_system_manual_runtime_surface/component_patch_static_command_system.md
  - system_docs/patches/active/shared_command_system_manual_runtime_surface/component_patch_interfaces.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the shared command-surface behavior is merged
  into canonical docs or intentionally superseded.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T20:44:35Z
  TYPE: PLAN
  CLAIM: The current room split already proves the right ownership seam for the
    next expansion. `CommandSystem` owns the shared manual-runtime vocabulary,
    `StaticCommandSystem` already specializes behavior on top of it, and both
    `CapabilityCommandSystem` and `DynamicCommandSystem` are now thin pass-throughs.
    So the clean move is to widen the base command surface, not to add another
    capability-only API family.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:252-789
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:9-382
  - src/melder/aether/nexus/rift/rift_space/command_system/capability_command_system.py:6-37
  - src/melder/aether/nexus/rift/rift_space/command_system/dynamic_command_system.py:6-21
  - tickets/artifacts/2026-04-12_capability_rift_space_runtime_model.md:107-149
  IMPACT: The next patch should stay in the shared command layer with static
    overrides, not capability-only drift.
  NEXT: add the new task route + patch docs, then patch the shared command
    surface and static deny set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T21:04:50Z
  TYPE: FACT
  CLAIM: The shared command-surface code patch is now in place. Base
    `CommandSystem` owns the new manual-runtime operations for cloud access,
    lesser creation, cluster operations, and conduit linking, plus one
    `list_supported_command_methods()` helper. `StaticCommandSystem` now
    denies the topology-mutation subset explicitly, and `ICommandSystem` is
    updated to match the widened runtime surface.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:306-715
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:1166-1210
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:1313-1335
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:46-63
  - src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py:467-486
  - src/melder/utilities/interfaces/interfaces.py:6824-6997
  - src/melder/utilities/interfaces/interfaces.py:7083-7088
  IMPACT: The implementation tranche is ready for focused validation against
    capability direct methods, static denials, and command-surface
    introspection.
  NEXT: run the focused `test_nexus` + nearby Rift runtime ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T21:05:16Z
  TYPE: MEASURE
  CLAIM: The shared command-surface expansion is green on the focused and
    nearby Rift runtime unit ring. The new direct command methods, static deny
    behavior, and command-surface introspection all passed in the same ring.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift_space/command_system/command_system.py src/melder/aether/nexus/rift/rift_space/command_system/static_command_system.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> 120 passed
  - tests/unit/melder/aether/test_nexus.py:2789-3119
  IMPACT: The shared command-surface slice is stable enough to return for
    review and acceptance.
  NEXT: summarize the landed command-surface expansion and confirm whether the
    next lane is capability integration coverage or more shared command helpers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the next capability-command expansion: shared manual-runtime
operations in base `CommandSystem`, explicit static denials, no codegen creep.
The slice is now landed and green on the focused test ring.
