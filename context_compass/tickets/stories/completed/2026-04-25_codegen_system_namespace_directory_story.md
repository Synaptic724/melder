# Story: Implement Codegen System Namespace Directory
- Completed: 2026-04-25T10:37:18Z
- Summary: Closed during cleanup after the namespace configuration, live
  namespace, builder, and minimal stable namespace contract landed and
  validated.

## Metadata
- Story ID: STORY-2026-04-25-codegen-system-namespace-directory
- Epic: EPIC-2026-04-25-implement-codegen-system-runtime
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-25T10:37:18Z

## User Narrative
As an engineer, I want a real namespace subsystem, so that codegen execution
uses an explicit namespace contract instead of ad hoc dict assembly.

## Value / MRP Alignment
Namespace exposure is part of the governance boundary. It should be an explicit
subsystem with its own config and output objects.

## Ticket Contract
- ENTRY_GATE: the investigation epic already established namespace exposure as
  a first-class codegen concern.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/namespace/`
- DEPENDENCIES:
  - `tickets/tasks/2026-04-25_implement_codegen_namespace_configuration_py_task.md`
  - `tickets/tasks/2026-04-25_implement_codegen_namespace_py_task.md`
  - `tickets/tasks/2026-04-25_implement_codegen_namespace_builder_py_task.md`
- EXIT_GATE: namespace configuration, built namespace, and namespace builder
  are all ticketed and ready to implement.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if namespace configuration needs
  to merge into the root transaction context instead of staying separate.

## Requirements (Functional)
- Implement `CodegenNamespaceConfiguration`.
- Implement `CodegenNamespace`.
- Implement `CodegenNamespaceBuilder`.

## Requirements (Non-Functional)
- Keep namespace configuration separate from the live namespace object.
- Keep built namespace output explicit and inspectable.

## Scope Boundaries
- In scope:
  - namespace configuration
  - live namespace object
  - namespace builder
- Out of scope:
  - namespace exposure strategies
  - validator internals
  - execution internals

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the namespace subsystem boundaries are explicit enough to
  stage separately from the strategy family beneath them.

## Dependencies / Related Work
- `tickets/stories/2026-04-25_codegen_system_namespace_strategies_directory_story.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-25-implement-codegen-namespace-configuration-py - implement namespace contract object
- [ ] Task: TASK-2026-04-25-implement-codegen-namespace-py - implement built namespace object
- [ ] Task: TASK-2026-04-25-implement-codegen-namespace-builder-py - implement namespace builder
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Namespace configuration, namespace, and builder all exist as separate tasks.
- The story makes the policy-vs-live-namespace split explicit.

## Validation / Test Plan
- Focused namespace builder and configuration tests.

## UX / API / Data Notes
- The live namespace should expose stable room/runtime objects only unless a
  later task explicitly expands it.

## Risks / Mitigations
- Risk: live namespace assembly and policy config drift into one class.
  Mitigation: keep configuration and built namespace separate.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether `result` should be preseeded in the live namespace or treated as
  purely user code output.

## Decision Log
- 2026-04-25: namespace configuration and built namespace remain separate.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/codegen_namespace_foundation/architecture_patch.md
  - system_docs/patches/active/codegen_namespace_foundation/component_patch_codegen_namespace.md
  - system_docs/patches/active/codegen_namespace_foundation/component_patch_codegen_system_namespace_wiring.md
  - system_docs/patches/active/codegen_namespace_foundation/code_description_patch_codegen_namespace_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the first namespace foundation slice is merged
  into canonical docs or intentionally superseded.

## Notes
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: PLAN
  CLAIM: Namespace configuration and the built namespace are separate
    responsibilities and should not collapse into one object.
  EVIDENCE:
  - tickets/epics/2026-04-25_implement_codegen_system_runtime_epic.md:1-119
  IMPACT: Namespace policy can stay explicit before execution touches live objects.
  NEXT: stage the three namespace directory tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: PLAN
  CLAIM: The first namespace slice will stay bounded to the top-level builder
    and the minimal exposure strategies required for the stable namespace
    contract. The builtins strategy remains deferred.
  EVIDENCE:
  - system_docs/patches/active/codegen_namespace_foundation/architecture_patch.md:1-24
  - system_docs/patches/active/codegen_namespace_foundation/component_patch_codegen_namespace.md:1-16
  IMPACT: We can replace the placeholder namespace path now without widening
    into the full strategy family.
  NEXT: implement the builder plus room-objects, workstation, command, and
    target strategies, then validate the focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: FACT
  CLAIM: The first namespace slice is now implemented. The package now has a
    real `CodegenNamespaceBuilder` and four minimal exposure strategies
    (`room_objects`, `workstation`, `command`, `target`). `CodegenSystem` now
    owns the builder and builds a real live namespace instead of manufacturing
    the placeholder namespace directly.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:1-106
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_room_objects_strategy.py:1-76
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_workstation_strategy.py:1-51
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_command_strategy.py:1-52
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_target_strategy.py:1-58
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:1-280
  IMPACT: The codegen runtime now has a real namespace assembly boundary instead
    of a hardcoded placeholder path.
  NEXT: move to compile/executor implementation or the validation strategy family,
    depending on which subsystem you want next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: MEASURE
  CLAIM: The focused codegen ring is green after the namespace slice landed.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_room_objects_strategy.py src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_workstation_strategy.py src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_command_strategy.py src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_target_strategy.py src/melder/aether/nexus/rift/codegen_system/codegen_system.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "codegen"` -> `19 passed, 105 deselected`
  IMPACT: The namespace slice is stable enough to hand off to the next codegen subsystem.
  NEXT: ask whether to continue directly into compile/executor or the validation-strategy directory.
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
This story owns the top-level namespace subsystem files.
