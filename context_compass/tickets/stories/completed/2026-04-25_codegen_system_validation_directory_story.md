# Story: Implement Codegen System Validation Directory
- Completed: 2026-04-25T10:37:18Z
- Summary: Closed during cleanup after the validator, validation reporter, and
  validation result slice landed and the focused codegen ring stayed green.

## Metadata
- Story ID: STORY-2026-04-25-codegen-system-validation-directory
- Epic: EPIC-2026-04-25-implement-codegen-system-runtime
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-25T10:37:18Z

## User Narrative
As an engineer, I want a real validation subsystem, so that codegen validation
has one owner, one result type, and one reporting path before execution begins.

## Value / MRP Alignment
Validation is not a helper. It is one of the core governance boundaries, so it
deserves a real directory story instead of being buried in the root.

## Ticket Contract
- ENTRY_GATE: the root story is staged and validation is a first-class
  subsystem in the investigation epic.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/validation/`
- DEPENDENCIES:
  - `tickets/tasks/2026-04-25_implement_codegen_validator_py_task.md`
  - `tickets/tasks/2026-04-25_implement_codegen_validation_result_py_task.md`
  - `tickets/tasks/2026-04-25_implement_codegen_validation_reporter_py_task.md`
- EXIT_GATE: validator, validation result, and validation reporter are all
  implemented with clear ownership.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if validation result and
  validation reporting need to merge instead of staying separate.

## Requirements (Functional)
- Implement `CodegenValidator`.
- Implement `CodegenValidationResult`.
- Implement `CodegenValidationReporter`.

## Requirements (Non-Functional)
- Keep validation output separate from execution output.
- Keep reporting separate from rule enforcement.

## Scope Boundaries
- In scope:
  - validator
  - validation result
  - validation reporting
- Out of scope:
  - strategy implementations
  - execution
  - namespace building

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: validation file ownership is explicit enough to stage as a
  standalone story.

## Dependencies / Related Work
- `tickets/stories/2026-04-25_codegen_system_validation_strategies_directory_story.md`

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-25-implement-codegen-validator-py - implement validator ownership
- [ ] Task: TASK-2026-04-25-implement-codegen-validation-result-py - implement validation result type
- [ ] Task: TASK-2026-04-25-implement-codegen-validation-reporter-py - implement validation reporting
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- Validation has one owner.
- Validation results are returned as a dedicated type.
- Validation reporting is separated from validation logic.

## Validation / Test Plan
- Focused validator and reporting tests.

## UX / API / Data Notes
- `validate_codegen(...)` should return the validation-layer result shape, not
  an execution-layer result.

## Risks / Mitigations
- Risk: validation result and execution result drift into one mixed object.
  Mitigation: keep them in separate directories and stories.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Whether validation reporting should include summarized categories or only the
  raw validation issue list.

## Decision Log
- 2026-04-25: Validation result and validation reporter stay separate.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/codegen_validation_foundation/architecture_patch.md
  - system_docs/patches/active/codegen_validation_foundation/component_patch_codegen_validation.md
  - system_docs/patches/active/codegen_validation_foundation/component_patch_codegen_system_validation_wiring.md
  - system_docs/patches/active/codegen_validation_foundation/code_description_patch_codegen_validation_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the first validation subsystem slice is merged
  into canonical docs or intentionally superseded.

## Notes
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: PLAN
  CLAIM: Validation should be implemented before execution because it defines
    the pre-exec boundary and the result shape used by `validate_codegen(...)`.
  EVIDENCE:
  - tickets/epics/2026-04-25_implement_codegen_system_runtime_epic.md:1-119
  IMPACT: This story should run before the execution directory story.
  NEXT: start with `codegen_validator.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: PLAN
  CLAIM: The first validation slice will stay bounded to validator ownership,
    validation reporting, and root engine wiring. Strategy files remain deferred
    to the next validation-strategy story.
  EVIDENCE:
  - system_docs/patches/active/codegen_validation_foundation/architecture_patch.md:1-24
  - system_docs/patches/active/codegen_validation_foundation/component_patch_codegen_validation.md:1-16
  - system_docs/patches/active/codegen_validation_foundation/component_patch_codegen_system_validation_wiring.md:1-14
  IMPACT: We can make validation real now without prematurely exploding into the
    full strategy family.
  NEXT: implement `CodegenValidator`, `CodegenValidationReporter`, and the root
    engine wiring, then validate the focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: FACT
  CLAIM: The first validation subsystem slice is now implemented. The package
    now has a real `CodegenValidator` and `CodegenValidationReporter`, the
    validation result type has a syntax-failure path, the execution result type
    has a validation-failure path, and `CodegenSystem` / `CodegenCommandSystem`
    now consume the validator and reporter instead of manufacturing validation
    payloads directly.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/validation/codegen_validator.py:1-88
  - src/melder/aether/nexus/rift/codegen_system/validation/codegen_validation_reporter.py:1-41
  - src/melder/aether/nexus/rift/codegen_system/validation/codegen_validation_result.py:1-160
  - src/melder/aether/nexus/rift/codegen_system/execution/codegen_execution_result.py:1-190
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:1-282
  - src/melder/aether/nexus/rift/command_system/codegen_command_system.py:1-609
  IMPACT: Validation is now a real subsystem boundary instead of a placeholder
    result factory.
  NEXT: move to the namespace builder directory story so the live namespace stops
    being a placeholder too.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: MEASURE
  CLAIM: The focused codegen ring is green after the validation slice landed.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/codegen_system/validation/codegen_validator.py src/melder/aether/nexus/rift/codegen_system/validation/codegen_validation_reporter.py src/melder/aether/nexus/rift/codegen_system/validation/codegen_validation_result.py src/melder/aether/nexus/rift/codegen_system/execution/codegen_execution_result.py src/melder/aether/nexus/rift/codegen_system/codegen_system.py src/melder/aether/nexus/rift/command_system/codegen_command_system.py tests/unit/melder/aether/test_nexus.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "codegen"` -> `17 passed, 105 deselected`
  IMPACT: The validation slice is stable enough to hand off to the namespace builder story.
  NEXT: ask whether to continue directly into namespace builder implementation.
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
This story owns the top-level validation subsystem files, not the strategy
family beneath them.
