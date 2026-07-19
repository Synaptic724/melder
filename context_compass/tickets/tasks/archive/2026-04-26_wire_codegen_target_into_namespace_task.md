# Task: Wire Codegen Target Into Namespace

## Metadata
- Task ID: TASK-2026-04-26-wire-codegen-target-into-namespace
- Story:
- Status: review
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-04-26T11:39:24Z
- Updated: 2026-04-26T12:26:01Z

## Objective
Wire the existing `CodegenTargetStrategy` into the live namespace builder and
extend the namespace configuration/tests so codegen can consume the current
workstation target directly as `target`.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved implementing the missing `target`
  namespace surface after a source-backed review of the codegen runtime.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/namespace/`
  - `tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py`
  - this task ticket and `attention_board.md`
- DEPENDENCIES:
  - `src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py`
  - `src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py`
  - `src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_target_strategy.py`
  - `tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py`
- EXIT_GATE: the live namespace builder exposes `target` when enabled,
  configuration/tests understand the new name, and the focused unit ring is
  green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if wiring `target` requires a
  broader namespace-policy redesign instead of the intended bounded change.

## Scope Boundaries
- In scope:
  - namespace builder wiring
  - namespace configuration exposure contract
  - focused unit tests
- Out of scope:
  - broader codegen iteration helpers
  - command-system or runtime policy redesign
  - crystallizer work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the source-backed review showed that
  `CodegenTargetStrategy` exists but the builder does not wire it and the
  namespace config does not expose `target`.

## Steps / Checklist
- [ ] Add `target` to the namespace configuration contract.
- [ ] Wire `CodegenTargetStrategy` into the namespace builder.
- [ ] Extend focused unit coverage for the new namespace entry.
- [ ] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- live `target` namespace support
- focused unit-test coverage
- focused validation results

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-26_wire_codegen_target_into_namespace_task.md
- codex/context_compass/attention_board.md
- src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py
- src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py
- tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py

## Validation
- Executed:
  - `python -m pytest -q tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py`
- Result:
  - `79 passed, 2 warnings`

## Risks / Rollback Notes
- Risk: exposing `target` by default could surprise code paths that assume the
  namespace only contains viewer/workstation/command/codegen.
  Rollback: keep the change bounded to the config/namespace layer and verify
  the unit matrix explicitly.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-26T11:39:24Z
  TYPE: FACT
  CLAIM: The current codegen namespace has a real wiring gap. The repo already
    contains `CodegenTargetStrategy`, but `CodegenNamespaceBuilder` never
    instantiates or calls it, and `CodegenNamespaceConfiguration` does not
    expose a `target` toggle/name. So the current namespace cannot surface the
    active workstation target even though the strategy file exists.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/namespace/strategies/codegen_target_strategy.py:1-76
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:1-162
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:1-293
  IMPACT: A bounded namespace-contract patch is justified and does not require
    a larger iteration-system redesign.
  NEXT: wire `target` into the configuration and builder, then extend the unit
    matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T11:39:24Z
  TYPE: FACT
  CLAIM: The bounded namespace patch is now implemented. The namespace
    configuration has an explicit `include_target` toggle and exposes `target`
    in the stable name order, the builder now wires `CodegenTargetStrategy`,
    and the focused support/unit surfaces now exercise both the present-target
    and missing-target cases.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:30-30
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:49-49
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:235-236
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:22-23
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:58-58
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:79-79
  - src/melder\aether\nexus\rift\codegen_system\namespace\codegen_namespace_builder.py:162-166
  - tests/_codegen_system_support.py:84-95
  - tests/_codegen_system_support.py:191-205
  - tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py:103-113
  - tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py:201-249
  IMPACT: The live codegen namespace can now expose the current workstation
    target directly without widening into a bigger iteration-system design.
  NEXT: run the focused namespace unit ring and record the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T11:39:24Z
  TYPE: MEASURE
  CLAIM: The bounded `target` namespace patch is green on the focused unit
    ring. The namespace configuration, builder wiring, support double, and
    unit matrix all pass together after adding `target` to the live contract.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_codegen_namespace_runtime_unit_matrix.py` -> `79 passed, 2 warnings`
  IMPACT: The patch is stable enough to return for review instead of widening
    the lane further.
  NEXT: present the landed `target` namespace support and ask whether to close
    the task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded codegen namespace fix for exposing the current
workstation target as `target`.
